"""Ingest statutory PDFs into regulation_chunks (pgvector).   [v7]

Location in repo: backend/scripts/ingest_regulations.py
Run from backend/ with the venv active:

    python -m scripts.ingest_regulations --dry-run      # inspect chunking only (no model, no DB writes)
    python -m scripts.ingest_regulations                # embed + load every document in DOCS
    python -m scripts.ingest_regulations --only KPBR    # just one document

Put the PDFs in  <repo>/data/raw/regulations/  and edit DOCS below.
Re-running a document replaces its old chunks (safe).

v7 adds: short REAL rules (e.g. "94. Application fee: ... as specified in Schedule I.") are kept; only
"Omitted/Deleted/Repealed" stubs and fragments under 30 chars are dropped.

v6 adds: number alone on a line + title on the next line ("95\nDecision to be intimated: - (1)").

v5 adds: inserted rules such as "49.1" / "49 .1" / "49. 2." (labelled Rule 49.1, Rule 49.2).

v4 adds: headings written without a full stop ("6 Plans to be submitted - (1)"), and the dry run lists
short/omitted rules it dropped.

v3 adds: all Unicode whitespace normalised, looser heading pattern (number alone on a line, lowercase
titles), narrower contents-line filter, and --probe N / --page N diagnostics.

v2 changes: clause headings are now found with a longest-increasing-run search (one missed
heading can no longer swallow the rest of the document), every sub-chunk gets its own page
number, the Gazette footer is stripped, and --dry-run reports missing clause numbers.
"""
import argparse
import re
from bisect import bisect_right
from pathlib import Path

try:
    import pymupdf as fitz  # PyMuPDF (new import name)
except ImportError:  # older installs
    import fitz
from sqlalchemy import create_engine, text

from app.config import settings

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "data" / "raw" / "regulations"

# Must match app/rag.py. 384 dims = the VECTOR(384) column.
# Same 384 dims, multilingual (use if some PDFs are Malayalam):
#   "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

MAX_CHARS = 1500   # longest chunk
MIN_CHARS = 80     # drop tiny fragments (table-of-contents lines, stray headers)

# EDIT THIS: exact PDF file name -> metadata.
#   kind: "rule"    -> chunks labelled "Rule N"
#         "section" -> chunks labelled "Section N"
#   applies_to: panchayat | municipality | all
DOCS = {
    "Kerala building rules for panchayat 2019.pdf": {
        "doc_code": "KPBR",
        "title": "Kerala Panchayat Building Rules",
        "kind": "rule",
        "applies_to": "panchayat",
    },
    "Kerala building rules for muncipality 2019.pdf": {
        "doc_code": "KMBR",
        "title": "Kerala Municipality Building Rules",
        "kind": "rule",
        "applies_to": "municipality",
    },
    "The-Kerala-Conservation-of-Paddy-Land-and-Wetland-Act-2008.pdf": {
        "doc_code": "PADDY_ACT",
        "title": "Kerala Conservation of Paddy Land and Wetland Act",
        "kind": "section",
        "applies_to": "all",
    },
}

# --- PDF reading ---------------------------------------------------------------
# Every Gazette page ends with: "<page no> This is a digitally signed Gazette. Authenticity may be ..."
GAZETTE_FOOTER = re.compile(
    r"(?:^[ ]*\d{1,3}[ ]*\n)?[ ]*This is a digitally signed Gazette\.\s+"
    r"Authenticity may be verified through\s+https?://\S+",
    re.I | re.M,
)


def read_pages(pdf_path: Path):
    pages = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            t = page.get_text("text") or ""
            t = t.replace("\u00a0", " ").replace("\x00", "")
            t = GAZETTE_FOOTER.sub("", t)
            t = re.sub(r"-\n(?=[a-z])", "", t)      # re-join hyphenated words
            t = re.sub(r"[^\S\n]+", " ", t)   # any horizontal whitespace -> one space
            pages.append((i, t))
    return pages


# --- Chunking -----------------------------------------------------------------
# A heading looks like "24. Front yard" at the start of a line.
# Also accepts: number alone on its line ("7." then the title below), lowercase/quoted titles,
# and "7 ." spacing. "7.5" (a decimal in a table cell) is NOT a heading.
HEAD = re.compile(r"""(?m)^[ ]*(\d{1,3}[A-Z]?)[ ]?\.(?!\d)(?=[ ]*(?:\n[ ]*)?[A-Za-z("'\u2018\u201c])""")


# Some rules are written with NO full stop after the number: "6 Plans to be submitted - (1) ..."
# To avoid table cells ("6 X 6", "6 for first 1000") the title must start Capital+lowercase
# and a dash must follow within the same line.
HEAD_NODOT = re.compile(r"(?m)^[ ]*(\d{1,3}[A-Z]?)[ ](?=[A-Z][a-z][^\n]{2,110}?[ ]?[-\u2013\u2014])")


# Inserted rules like "49.1 Special provisions ...", "49 .1Special ...", "49. 2. Special ...".
# Title must be Capital+lowercase with a dash on the same line (keeps "7.5 metres" decoys out).
HEAD_SUB = re.compile(
    r"(?m)^[ ]*(\d{1,3})[ ]?\.[ ]?(\d{1,2})\.?[ ]*(?=[A-Z][a-z][^\n]{2,110}?[-\u2013\u2014:])"
)


# Number alone on its line, title on the NEXT line: "95 \nDecision to be intimated: - (1)"
# The next line must be Capital+lowercase with a dash/colon (keeps bare table-cell numbers out).
HEAD_ALONE = re.compile(
    r"(?m)^[ ]*(\d{1,3}[A-Z]?)[ ]*\n[ ]*(?=[A-Z][a-z][^\n]{2,110}?[-\u2013\u2014:])"
)


def ref_of(m) -> str:
    """Clause number text for a heading match: '49.1' for inserted rules, else '24' / '24A'."""
    return f"{m.group(1)}.{m.group(2)}" if m.re is HEAD_SUB else m.group(1)


def is_toc_line(line: str) -> bool:
    """Table-of-contents entry: dot leaders, or a SHORT line ending in a page number.
    (Real headings are long physical lines, so a long line ending in a digit is kept.)"""
    if re.search(r"\.{4,}|(?:\. ){4,}", line):
        return True
    return len(line) < 70 and bool(re.search(r"\s\d{1,3}\s*$", line))


def longest_chain(cands):
    """Longest non-decreasing run of clause numbers (patience sorting + reconstruction).

    Stray numbered lines (list items, table rows, a mis-read heading) cannot derail the
    result, because the real headings form the longest increasing sequence in the document.
    """
    tails, tails_idx, prev = [], [], [-1] * len(cands)
    for i, (n, _) in enumerate(cands):
        pos = bisect_right(tails, n)
        if pos > 0:
            prev[i] = tails_idx[pos - 1]
        if pos == len(tails):
            tails.append(n)
            tails_idx.append(i)
        else:
            tails[pos] = n
            tails_idx[pos] = i
    chain, k = [], (tails_idx[-1] if tails_idx else -1)
    while k != -1:
        chain.append(cands[k][1])
        k = prev[k]
    return chain[::-1]


def find_headings(full: str):
    cands = []
    matches = {m.start(): m for m in HEAD.finditer(full)}
    for pat in (HEAD_NODOT, HEAD_SUB, HEAD_ALONE):
        for m in pat.finditer(full):
            matches.setdefault(m.start(), m)
    for _, m in sorted(matches.items()):
        line_end = full.find("\n", m.start())
        line = full[m.start(): line_end if line_end != -1 else len(full)]
        if m.re is not HEAD_ALONE and is_toc_line(line):
            continue
        cands.append((int(re.match(r"\d+", m.group(1)).group()), m))
    return longest_chain(cands)


SKIPPED: list = []   # short/omitted clauses dropped by the last clause_chunks() call


def clause_chunks(pages, kind: str):
    SKIPPED.clear()
    label = "Rule" if kind == "rule" else "Section"
    full, offsets = "", []
    for pno, t in pages:
        offsets.append((len(full), pno))
        full += t + "\n"
    starts = [o for o, _ in offsets]

    def page_of(pos: int) -> int:
        return offsets[bisect_right(starts, pos) - 1][1]

    hits = find_headings(full)
    if len(hits) < 5:
        return None, full, page_of  # layout not recognised: caller falls back to page windows
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(full)
        body = full[m.start(): end].strip()
        is_stub = len(body) < MIN_CHARS and re.search(r"omitted|deleted|repealed", body, re.I)
        if len(body) < 30 or is_stub:
            SKIPPED.append(f"{label} {ref_of(m)}: {body[:50]!r}")
            continue
        out.append(
            {"clause_ref": f"{label} {ref_of(m)}", "page": page_of(m.start()),
             "content": body, "start": m.start()}
        )
    return out, full, page_of


def window_chunks(pages, size: int = 900, overlap: int = 150):
    """Fallback: plain text windows. Cited by PAGE only (we never invent clause numbers)."""
    out = []
    for pno, t in pages:
        t = t.strip()
        i = 0
        while i < len(t):
            piece = t[i: i + size].strip()
            if len(piece) >= MIN_CHARS:
                out.append({"clause_ref": f"Page {pno}", "page": pno, "content": piece})
            i += size - overlap
    return out


def split_long(chunk: dict, full=None, page_of=None):
    body = chunk["content"]
    if len(body) <= MAX_CHARS:
        return [chunk]
    parts, cur = [], ""
    for para in re.split(r"\n(?=\s*\(\d+\)|\s*\([a-z]\))|\n\n", body):
        if cur and len(cur) + len(para) > MAX_CHARS:
            parts.append(cur)
            cur = ""
        cur += para + "\n"
        while len(cur) > MAX_CHARS * 2:          # one giant paragraph
            parts.append(cur[:MAX_CHARS])
            cur = cur[MAX_CHARS:]
    if cur.strip():
        parts.append(cur)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) < 30:
            continue
        page = chunk["page"]
        if full is not None and "start" in chunk:
            pos = full.find(p[:60], chunk["start"])   # each sub-chunk gets its OWN page
            if pos != -1:
                page = page_of(pos)
        out.append({**chunk, "content": p, "page": page})
    return out


def build_chunks(pdf_path: Path, kind: str):
    pages = read_pages(pdf_path)
    total = sum(len(t) for _, t in pages)
    avg = total / max(len(pages), 1)
    chunks, full, page_of = clause_chunks(pages, kind)
    strategy = "clause headings"
    if chunks is None:
        chunks, strategy = window_chunks(pages), "page windows (fallback)"
    final = [c for ch in chunks for c in split_long(ch, full, page_of)]
    for idx, c in enumerate(final):
        c["chunk_index"] = idx
    return pages, avg, strategy, final


def missing_numbers(chunks):
    nums = set()
    for c in chunks:
        parts = c["clause_ref"].split()
        if len(parts) == 2 and parts[0] in ("Rule", "Section"):
            nums.add(int(re.match(r"\d+", parts[1]).group()))
    if not nums:
        return []
    return [n for n in range(min(nums), max(nums) + 1) if n not in nums]


# --- Diagnostics --------------------------------------------------------------
def probe(full: str, page_of, n: int):
    """Show every line that starts with the number n, and how the heading rules treat it."""
    pat = re.compile(rf"(?m)^[^\S\n]*{n}[A-Z]?(?!\d).*$")
    found = 0
    for m in pat.finditer(full):
        line = m.group(0)
        hm = HEAD.match(full, m.start()) or HEAD_NODOT.match(full, m.start()) or HEAD_SUB.match(full, m.start()) or HEAD_ALONE.match(full, m.start())
        print(f"  p{page_of(m.start()):>3} | HEAD={'yes' if hm else 'no ':3} TOC={'yes' if is_toc_line(line) else 'no ':3} | {line[:95]!r}")
        found += 1
        if found >= 15:
            print("  ... (more not shown)")
            break
    if not found:
        print(f"  no line starts with {n}")


# --- Main ---------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="doc_code to process, e.g. KPBR")
    ap.add_argument("--probe", type=int, help="with --only: show how clause number N appears in the text")
    ap.add_argument("--page", type=int, help="with --only: print the cleaned text of PDF page N (repr)")
    args = ap.parse_args()

    found = sorted(p.name for p in PDF_DIR.glob("*.pdf"))
    print(f"PDF folder: {PDF_DIR}")
    print("PDFs found:", found or "NONE")
    for f in found:
        if f not in DOCS:
            print(f"  not in DOCS (skipped): {f}  <- add it to DOCS if you want it")

    todo = [(f, m) for f, m in DOCS.items() if not args.only or m["doc_code"] == args.only]
    model = engine = None
    if not args.dry_run and not (args.probe or args.page):
        from sentence_transformers import SentenceTransformer

        print(f"Loading embedding model {EMBED_MODEL} (first run downloads it)...")
        model = SentenceTransformer(EMBED_MODEL)
        engine = create_engine(settings.db_url)

    for fname, meta in todo:
        path = PDF_DIR / fname
        if not path.exists():
            print(f"\n[{meta['doc_code']}] MISSING: {path}")
            continue

        if args.probe or args.page:
            pages = read_pages(path)
            if args.page:
                print(f"\n[{meta['doc_code']}] page {args.page} (repr):")
                print(repr(pages[args.page - 1][1][:1800]))
            if args.probe:
                _, full, page_of = clause_chunks(pages, meta["kind"])
                print(f"\n[{meta['doc_code']}] lines starting with {args.probe}:")
                probe(full, page_of, args.probe)
            continue

        pages, avg, strategy, chunks = build_chunks(path, meta["kind"])
        refs = list(dict.fromkeys(c["clause_ref"] for c in chunks))   # unique, in order
        print(f"\n[{meta['doc_code']}] {fname}")
        print(f"  pages={len(pages)}  avg chars/page={avg:.0f}  strategy={strategy}")
        print(f"  chunks={len(chunks)}  distinct clauses={len(refs)}")
        if avg < 200:
            print("  WARNING: very little text per page. This PDF may be scanned (needs OCR).")
        if not chunks:
            continue
        print("  first refs:", ", ".join(refs[:15]))
        print("  last refs: ", ", ".join(refs[-8:]))
        if strategy == "clause headings":
            miss = missing_numbers(chunks)
            print(f"  missing numbers ({len(miss)}):", miss[:60] if miss else "none")
            print("  (a few gaps can be repealed/omitted rules; long runs of gaps mean undetected headings)")
            if SKIPPED:
                print(f"  short clauses dropped ({len(SKIPPED)}):", "; ".join(SKIPPED[:12]))
        print(f"  longest chunk: {max(len(c['content']) for c in chunks)} chars;"
              f"  last chunk starts on page {chunks[-1]['page']} of {len(pages)}")
        for c in (chunks[0], chunks[len(chunks) // 2]):
            print(f"  --- sample: {c['clause_ref']} (page {c['page']}) ---")
            print("  " + c["content"][:300].replace("\n", " "))

        if args.dry_run:
            continue

        texts = [f"{meta['title']} {c['clause_ref']}. {c['content']}" for c in chunks]
        embs = model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=True)
        rows = [
            {
                "src": meta["doc_code"],
                "ref": c["clause_ref"],
                "content": c["content"],
                "emb": "[" + ",".join(f"{x:.6f}" for x in e) + "]",
                "code": meta["doc_code"],
                "title": meta["title"],
                "page": c["page"],
                "idx": c["chunk_index"],
                "applies": meta["applies_to"],
            }
            for c, e in zip(chunks, embs)
        ]
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM regulation_chunks WHERE doc_code = :c"), {"c": meta["doc_code"]})
            conn.execute(
                text(
                    """
                    INSERT INTO regulation_chunks
                      (source_doc, clause_ref, content, embedding, doc_code, doc_title,
                       page_start, chunk_index, applies_to)
                    VALUES (:src, :ref, :content, CAST(:emb AS vector), :code, :title,
                            :page, :idx, :applies)
                    """
                ),
                rows,
            )
        print(f"  loaded {len(rows)} chunks into regulation_chunks")

    print("\nDone." + (" (dry run: nothing written)" if args.dry_run else ""))


if __name__ == "__main__":
    main()