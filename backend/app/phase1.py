"""GeoRAG+ Phase 1: land-purchase checks (EC, wetland / Data Bank, stamp duty).

Location in repo: backend/app/phase1.py

Rule: every number is computed here or in PostGIS. The LLM never calculates;
later (Batch 4/7) it only explains these verdicts and cites clauses.
"""
import json
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from .db import engine
from .rag import retrieve

router = APIRouter(prefix="/phase1", tags=["phase1"])

SQM_PER_ARE = Decimal("100")        # 1 Are = 100 square metres
SQM_PER_CENT = Decimal("40.4686")   # 1 cent = 40.4686 square metres


def _money(x: Decimal) -> float:
    return float(x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _get_parcel(conn, parcel_id: int) -> dict:
    row = conn.execute(
        text("""
            SELECT parcel_id, survey_no, thandaper_no, land_type, data_bank_status,
                   fair_value_per_are, local_body_type,
                   ST_Area(geom::geography) AS area_sqm
            FROM cadastral_parcels
            WHERE parcel_id = :pid
        """),
        {"pid": parcel_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="parcel not found")
    parcel = dict(row)
    parcel["area_sqm"] = Decimal(str(parcel["area_sqm"]))
    return parcel


def _rate(conn, code: str):
    r = conn.execute(
        text("SELECT rate, verified FROM fee_rates WHERE code = :c"), {"c": code}
    ).first()
    if r is None:
        raise HTTPException(500, f"fee rate '{code}' missing: run 04_batch3_schema.sql")
    return Decimal(r[0]), bool(r[1])


# --- Check 1: Encumbrance Certificate (mock PEARL) ---------------------------
def ec_check(conn, parcel: dict, years: int) -> dict:
    rows = conn.execute(
        text("""
            SELECT doc_no, doc_type, doc_date, party_from, party_to
            FROM ec_records WHERE parcel_id = :pid ORDER BY doc_date
        """),
        {"pid": parcel["parcel_id"]},
    ).mappings().all()

    since = date.today() - timedelta(days=365 * years)
    window = [dict(r) for r in rows if r["doc_date"] >= since]

    mortgages = sum(1 for r in rows if r["doc_type"] == "Mortgage")
    releases = sum(1 for r in rows if r["doc_type"] == "Release")
    open_liens = max(mortgages - releases, 0)   # judged on the full history

    if not rows:
        verdict = "WARN"
        detail = "No EC records on file for this survey/thandaper number; cannot verify."
    elif open_liens:
        verdict = "FAIL"
        detail = f"{open_liens} mortgage(s) without a matching release. Clear before purchase."
    else:
        verdict = "PASS"
        detail = f"No open encumbrances across {len(rows)} recorded transaction(s)."

    return {
        "check": "encumbrance_certificate",
        "verdict": verdict,
        "detail": detail,
        "period_years": years,
        "open_liens": open_liens,
        "transactions": window,
        "clauses": [],  # filled by RAG in Batch 4
    }


# --- Check 2: Paddy Data Bank / wetland -------------------------------------
def wetland_check(conn, parcel: dict) -> dict:
    row = conn.execute(
        text("""
            SELECT COALESCE(SUM(ST_Area(ST_Intersection(p.geom, d.geom)::geography)), 0) AS overlap_sqm,
                   COUNT(d.id) AS n_polygons
            FROM cadastral_parcels p
            LEFT JOIN paddy_data_bank d ON ST_Intersects(p.geom, d.geom)
            WHERE p.parcel_id = :pid
        """),
        {"pid": parcel["parcel_id"]},
    ).mappings().first()

    overlap = Decimal(str(row["overlap_sqm"]))
    pct = (overlap / parcel["area_sqm"] * 100) if parcel["area_sqm"] else Decimal(0)
    in_bank = overlap > 0
    conflict = in_bank and parcel["land_type"] == "Purayidom"

    if not in_bank:
        verdict, detail = "PASS", "Parcel does not overlap the Paddy Data Bank layer."
    else:
        verdict = "FAIL"
        detail = (
            f"{float(pct):.1f}% of the parcel lies inside the Data Bank layer. "
            "Construction or conversion needs prior clearance from the competent authority."
        )
        if conflict:
            detail += " Records conflict: land type is recorded as Purayidom."

    return {
        "check": "paddy_wetland_audit",
        "verdict": verdict,
        "detail": detail,
        "recorded_land_type": parcel["land_type"],
        "in_data_bank": in_bank,
        "overlap_sqm": round(float(overlap), 1),
        "overlap_pct": round(float(pct), 1),
        "record_conflict": conflict,
        # Form numbers / section citations are NOT hardcoded: verify first (implementation.md, Section 4)
        "clearance_forms": "TO BE VERIFIED against the Act and Rules",
        "clauses": [],  # filled by RAG in Batch 4
    }


# --- Stamp duty and registration fee ----------------------------------------
def stamp_duty(conn, parcel: dict, consideration: Decimal | None) -> dict:
    stamp_pct, v1 = _rate(conn, "stamp_duty_pct")
    reg_pct, v2 = _rate(conn, "registration_fee_pct")

    area_are = parcel["area_sqm"] / SQM_PER_ARE
    area_cents = parcel["area_sqm"] / SQM_PER_CENT
    fair_value = (parcel["fair_value_per_are"] or Decimal(0)) * area_are

    # Assumption (verify): duty is charged on the higher of declared price and Fair Value
    basis = max(consideration, fair_value) if consideration else fair_value
    stamp = basis * stamp_pct / 100
    reg = basis * reg_pct / 100

    warnings = []
    if not (v1 and v2):
        warnings.append("Rates in fee_rates are unverified placeholders. Do not rely on these figures.")
    warnings.append("Mock fair value per Are is synthetic data.")

    return {
        "check": "stamp_duty",
        "verdict": "INFO",
        "area_are": round(float(area_are), 3),
        "area_cents": round(float(area_cents), 2),
        "fair_value_total": _money(fair_value),
        "declared_consideration": _money(consideration) if consideration else None,
        "duty_basis": _money(basis),
        "stamp_duty_pct": float(stamp_pct),
        "registration_fee_pct": float(reg_pct),
        "stamp_duty": _money(stamp),
        "registration_fee": _money(reg),
        "total_payable": _money(stamp + reg),
        "rates_verified": bool(v1 and v2),
        "warnings": warnings,
        "clauses": [],
    }


# --- Audit log ---------------------------------------------------------------
def _audit(conn, parcel_id: int, check: dict) -> None:
    inputs = {k: v for k, v in check.items() if k not in ("detail", "clauses", "verdict")}
    conn.execute(
        text("""
            INSERT INTO audit_log (phase, parcel_id, check_name, verdict, inputs, cited_clauses, details)
            VALUES (1, :pid, :name, :verdict, CAST(:inputs AS jsonb), CAST(:clauses AS jsonb), :details)
        """),
        {
            "pid": parcel_id,
            "name": check["check"],
            "verdict": check["verdict"],
            "inputs": json.dumps(inputs, default=str),
            "clauses": json.dumps(check.get("clauses", [])),
            "details": check.get("detail"),
        },
    )


# --- Endpoints ---------------------------------------------------------------
@router.get("/test-cases")
def test_cases():
    """Handy parcel ids for each planted scenario (defined BEFORE /{parcel_id})."""
    sql = text("""
        WITH m AS (
          SELECT parcel_id,
                 sum((doc_type = 'Mortgage')::int) - sum((doc_type = 'Release')::int) AS open_liens
          FROM ec_records GROUP BY parcel_id
        )
        (SELECT 'clean' AS kind, p.parcel_id FROM cadastral_parcels p
           LEFT JOIN m USING (parcel_id)
           WHERE NOT p.data_bank_status AND COALESCE(m.open_liens, 0) = 0
           ORDER BY p.parcel_id LIMIT 2)
        UNION ALL
        (SELECT 'in_data_bank', p.parcel_id FROM cadastral_parcels p
           WHERE p.data_bank_status ORDER BY p.parcel_id LIMIT 2)
        UNION ALL
        (SELECT 'open_mortgage', p.parcel_id FROM cadastral_parcels p
           JOIN m USING (parcel_id) WHERE m.open_liens > 0 ORDER BY p.parcel_id LIMIT 2)
        UNION ALL
        (SELECT 'record_conflict', p.parcel_id FROM cadastral_parcels p
           WHERE p.data_bank_status AND p.land_type = 'Purayidom' ORDER BY p.parcel_id LIMIT 2)
    """)
    out: dict = {}
    with engine.connect() as conn:
        for kind, pid in conn.execute(sql):
            out.setdefault(kind, []).append(pid)
    return out


@router.get("/{parcel_id}")
def phase1_report(
    parcel_id: int,
    consideration: float | None = Query(None, description="Declared sale price in INR"),
    ec_years: int = Query(30, ge=1, le=60, description="EC look-back period in years"),
):
    with engine.begin() as conn:
        parcel = _get_parcel(conn, parcel_id)
        consideration_d = Decimal(str(consideration)) if consideration else None

        checks = [ec_check(conn, parcel, ec_years), wetland_check(conn, parcel)]
        duty = stamp_duty(conn, parcel, consideration_d)

        # Attach statutory citations (best effort: Phase 1 must still work if RAG is unavailable)
        wet = checks[1]
        if wet["verdict"] != "PASS":
            try:
                wet["clauses"] = retrieve(
                    "restriction on conversion or reclamation of paddy land and wetland",
                    ["PADDY_ACT"],
                    k=2,
                )
            except Exception as exc:  # noqa: BLE001
                wet["clauses_error"] = f"{type(exc).__name__}: {exc}"

        for c in (*checks, duty):
            _audit(conn, parcel_id, c)

    verdicts = {c["verdict"] for c in checks}
    overall = "FAIL" if "FAIL" in verdicts else ("WARN" if "WARN" in verdicts else "PASS")

    return {
        "parcel": {
            "parcel_id": parcel["parcel_id"],
            "survey_no": parcel["survey_no"],
            "thandaper_no": parcel["thandaper_no"],
            "local_body_type": parcel["local_body_type"],
            "area_sqm": round(float(parcel["area_sqm"]), 1),
        },
        "overall": overall,
        "checks": checks,
        "stamp_duty": duty,
        "note": "Prototype on synthetic data. Not legal advice.",
    }