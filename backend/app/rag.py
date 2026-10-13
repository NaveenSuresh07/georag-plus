"""GeoRAG+ retrieval over statutory text (pgvector + Postgres full-text).

Location in repo: backend/app/rag.py

Hybrid search: vector similarity (meaning) + keyword match (exact rule numbers and terms),
merged with Reciprocal Rank Fusion. The LLM never invents clause references; citations
always come from rows in regulation_chunks.
"""
import re
from functools import lru_cache

from fastapi import APIRouter, Query
from sqlalchemy import text

from .db import engine

router = APIRouter(prefix="/rag", tags=["rag"])

# Must match scripts/ingest_regulations.py
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL)  # loaded once, on first use


def _vec_literal(vec) -> str:
    return "[" + ",".join(f"{float(x):.6f}" for x in vec) + "]"


def docs_for(local_body_type: str) -> list[str]:
    """doc_codes that apply to a local body: KPBR for panchayats, KMBR for municipalities."""
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT DISTINCT doc_code FROM regulation_chunks "
                "WHERE applies_to IN (:t, 'all') AND doc_code IS NOT NULL"
            ),
            {"t": local_body_type},
        )
        return [r[0] for r in rows]


def retrieve(query: str, doc_codes: list[str] | None = None, k: int = 5, pool: int = 20) -> list[dict]:
    qv = _vec_literal(_model().encode(query, normalize_embeddings=True))

    # 1) vector search
    vec_params: dict = {"qv": qv, "pool": pool}
    vec_where = ""
    if doc_codes:
        vec_where = "WHERE doc_code = ANY(:codes)"
        vec_params["codes"] = list(doc_codes)
    vec_sql = text(
        f"SELECT chunk_id FROM regulation_chunks {vec_where} "
        "ORDER BY embedding <=> CAST(:qv AS vector) LIMIT :pool"
    )

    # 2) keyword search (OR of the query words; words are alphanumeric only, so it is safe)
    words = re.findall(r"[A-Za-z0-9]+", query)
    kw_sql, kw_params = None, {}
    if words:
        kw_params = {"tsq": " | ".join(words), "pool": pool}
        kw_where = "WHERE content_tsv @@ to_tsquery('english', :tsq)"
        if doc_codes:
            kw_where += " AND doc_code = ANY(:codes)"
            kw_params["codes"] = list(doc_codes)
        kw_sql = text(
            f"SELECT chunk_id FROM regulation_chunks {kw_where} "
            "ORDER BY ts_rank_cd(content_tsv, to_tsquery('english', :tsq)) DESC LIMIT :pool"
        )

    with engine.connect() as conn:
        vec_ids = [r[0] for r in conn.execute(vec_sql, vec_params)]
        kw_ids = [r[0] for r in conn.execute(kw_sql, kw_params)] if kw_sql is not None else []

        # 3) Reciprocal Rank Fusion
        scores: dict[int, float] = {}
        for ids in (vec_ids, kw_ids):
            for rank, cid in enumerate(ids, start=1):
                scores[cid] = scores.get(cid, 0.0) + 1.0 / (60 + rank)
        top = sorted(scores, key=scores.get, reverse=True)[:k]
        if not top:
            return []

        rows = conn.execute(
            text(
                "SELECT chunk_id, doc_code, doc_title, clause_ref, page_start, content "
                "FROM regulation_chunks WHERE chunk_id = ANY(:ids)"
            ),
            {"ids": top},
        ).mappings().all()

    by_id = {r["chunk_id"]: r for r in rows}
    return [
        {
            "chunk_id": cid,
            "doc_code": by_id[cid]["doc_code"],
            "doc_title": by_id[cid]["doc_title"],
            "clause_ref": by_id[cid]["clause_ref"],
            "page": by_id[cid]["page_start"],
            "text": by_id[cid]["content"][:1500],
            "score": round(scores[cid], 5),
            "in_vector_top": cid in vec_ids,
            "in_keyword_top": cid in kw_ids,
        }
        for cid in top
    ]


@router.get("/docs")
def list_docs():
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT doc_code, doc_title, applies_to, count(*) AS chunks, "
                "min(page_start) AS first_page, max(page_start) AS last_page "
                "FROM regulation_chunks GROUP BY doc_code, doc_title, applies_to ORDER BY doc_code"
            )
        ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/search")
def search(
    q: str = Query(..., min_length=3, description="Question or keywords"),
    doc: str | None = Query(None, description="Limit to one doc_code, e.g. KPBR"),
    local_body: str | None = Query(None, description="panchayat | municipality (picks the right rulebook)"),
    k: int = Query(5, ge=1, le=15),
):
    codes = [doc] if doc else (docs_for(local_body) if local_body else None)
    return {"query": q, "doc_codes": codes, "results": retrieve(q, codes, k=k)}