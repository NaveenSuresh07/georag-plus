"""Load rule values typed from the PDFs (data/rule_params.csv) into rule_params.

Location in repo: backend/scripts/load_rule_params.py
Run from backend/ (venv active):

    python -m scripts.load_rule_params --check    # validate only, writes nothing
    python -m scripts.load_rule_params            # replace all CSV rows in the database

Rows whose `value` is empty are skipped. Every row is checked:
  * param must be one the engine understands
  * doc_code must be KPBR or KMBR
  * clause_ref must exist in regulation_chunks (so the citation will really resolve)
Re-running is safe: it replaces the old CSV rows.
"""
import argparse
import csv
from pathlib import Path

from sqlalchemy import create_engine, text

from app.config import settings

ROOT = Path(__file__).resolve().parents[2]
CSV_FILES = sorted((ROOT / "data").glob("rule_params*.csv"))   # every data/rule_params*.csv is loaded

# What the Phase 2 engine knows how to use. 'min_distance_<ZONE_TYPE>' is also allowed (e.g. min_distance_CRZ).
KNOWN_PARAMS = {
    "front_setback_min",       # metres
    "rear_setback_min",        # metres
    "side_setback_min",        # metres
    "max_plot_coverage_pct",   # percent
    "max_far",                 # ratio
    "road_centre_min",         # metres from the road centre line
    "max_far_with_fee",        # FSI limit if the additional fee is paid (Table 6)
    "far_extra_fee_per_sqm",   # rupees per sq m of additional floor area (Table 6)
    "max_floors",              # number of floors (e.g. small plots, Rule 50)
    "max_height_m",            # building height in metres
    "exempt_coverage_far",     # 1 = coverage and FSI limits do not apply (Rule 50(3))
}
DOCS = {"KPBR", "KMBR"}


def num(value: str):
    value = (value or "").strip()
    return None if value == "" else float(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only")
    args = ap.parse_args()

    if not CSV_FILES:
        raise SystemExit(f"no rule_params*.csv found in {ROOT / 'data'}")
    print("CSV files:", ", ".join(f.name for f in CSV_FILES))

    engine = create_engine(settings.db_url)
    with engine.connect() as conn:
        known_clauses = {
            (r[0], r[1])
            for r in conn.execute(text("SELECT DISTINCT doc_code, clause_ref FROM regulation_chunks"))
        }

    rows, problems, skipped = [], [], 0
    sources = [(f.name, open(f, newline="", encoding="utf-8-sig")) for f in CSV_FILES]
    for fname, f in sources:
        for n, raw in enumerate(csv.DictReader(f), start=2):      # line 1 is the header
            n = f"{fname} line {n}"
            if (raw.get("value") or "").strip() == "":
                skipped += 1
                continue
            doc, ref, param = raw["doc_code"].strip(), raw["clause_ref"].strip(), raw["param"].strip()
            if doc not in DOCS:
                problems.append(f"{n}: doc_code '{doc}' must be one of {sorted(DOCS)}")
            if not (param in KNOWN_PARAMS or param.startswith("min_distance_")):
                problems.append(f"{n}: unknown param '{param}'")
            if not ref:
                problems.append(f"{n}: clause_ref is empty (needed for the citation)")
            elif (doc, ref) not in known_clauses:
                problems.append(f"{n}: '{doc} {ref}' not found in regulation_chunks (check /rag/search)")
            try:
                rows.append(
                    {
                        "doc": doc, "ref": ref, "tbl": raw.get("table_ref") or None,
                        "ug": (raw.get("use_group") or "").strip() or None, "param": param,
                        "hmin": num(raw["height_min_m"]), "hmax": num(raw["height_max_m"]),
                        "pmin": num(raw["plot_min_sqm"]), "pmax": num(raw["plot_max_sqm"]),
                        "bmin": num(raw.get("builtup_min_sqm")), "bmax": num(raw.get("builtup_max_sqm")),
                        "rc": (raw.get("road_class") or "").strip() or None,
                        "cat": (raw.get("category") or "").strip() or None,
                        "prov": (raw.get("proviso") or "").strip() or None,
                        "val": float(raw["value"]), "unit": raw.get("unit") or None,
                        "ver": (raw.get("verified") or "").strip().lower() in ("yes", "y", "true", "1"),
                        "note": raw.get("note") or None,
                    }
                )
            except ValueError as exc:
                problems.append(f"{n}: bad number ({exc})")
        f.close()

    print(f"rows with a value: {len(rows)}   empty rows skipped: {skipped}")
    print(f"verified rows: {sum(r['ver'] for r in rows)} of {len(rows)}")
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  -", p)
    if args.check or problems:
        print("\n(nothing written)" if args.check else "\nFix the problems above, then run again. Nothing written.")
        return

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM rule_params WHERE source = 'csv'"))
        if rows:
            conn.execute(
                text(
                    """
                    INSERT INTO rule_params
                      (doc_code, clause_ref, table_ref, use_group, param, height_min_m, height_max_m,
                       plot_min_sqm, plot_max_sqm, builtup_min_sqm, builtup_max_sqm,
                       road_class, category, proviso, value, unit, verified, note, source)
                    VALUES (:doc, :ref, :tbl, :ug, :param, :hmin, :hmax, :pmin, :pmax, :bmin, :bmax, :rc, :cat, :prov,
                            :val, :unit, :ver, :note, 'csv')
                    """
                ),
                rows,
            )
    print(f"loaded {len(rows)} rule rows into rule_params")


if __name__ == "__main__":
    main()