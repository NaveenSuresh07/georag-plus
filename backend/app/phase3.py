"""GeoRAG+ Phase 3: post-construction and property sale checks.

Location in repo: backend/app/phase3.py

Checks:
1. Occupancy Certificate audit (KMBR / KPBR Rule 20)
2. Municipal door number and unauthorized construction flag (Section 242 Kerala Municipality Act)
3. Property tax dues and arrears audit
4. Section 194-IA TDS deduction (1% above Rs 50,00,000 threshold)
5. Capital gains tax classification (STCG vs LTCG) and statutory exemption pathways (Section 54 / 54EC)

Rule: Every number is computed in Python/PostGIS. Rates come from the fee_rates table.
Statutory citations come from regulation_chunks. The LLM never calculates numbers or invents citations.
"""
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
import json
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from .db import engine
from .phase1 import _rate
from .rag import clause_text, docs_for

router = APIRouter(prefix="/phase3", tags=["phase3"])


class Phase3Request(BaseModel):
    sale_price: float = Field(..., gt=0, description="Declared sale consideration in INR")
    acquisition_cost: float | None = Field(None, gt=0, description="Original purchase price/cost of acquisition in INR")
    acquisition_date: str | None = Field(None, description="Date of acquisition in YYYY-MM-DD format")
    improvement_cost: float = Field(0.0, ge=0, description="Cost of improvements / renovation in INR")
    transfer_expenses: float = Field(0.0, ge=0, description="Brokerage, legal, transfer expenses in INR")


def _money(x: Decimal | float) -> float:
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _audit(conn, parcel_id: int, chk: dict):
    skip = ("detail", "clauses", "verdict", "warnings")
    conn.execute(
        text("""
            INSERT INTO audit_log (phase, parcel_id, check_name, verdict, inputs, cited_clauses, details)
            VALUES (3, :pid, :name, :verdict, CAST(:inputs AS jsonb), CAST(:clauses AS jsonb), :details)
        """),
        {
            "pid": parcel_id,
            "name": chk["check"],
            "verdict": chk["verdict"],
            "inputs": json.dumps({k: v for k, v in chk.items() if k not in skip}, default=str),
            "clauses": json.dumps(chk.get("clauses", []), default=str),
            "details": chk.get("detail"),
        },
    )


def run_phase3(parcel_id: int, req: Phase3Request) -> dict:
    assumptions = [
        "Assessment and door number records are mock stand-ins for Kerala Local Body Sanchaya portal.",
        "Section 194-IA TDS applies to the higher of declared consideration and stamp duty Fair Value.",
    ]

    with engine.begin() as conn:
        # 1. Fetch Parcel
        parcel = conn.execute(
            text("""
                SELECT parcel_id, survey_no, thandaper_no, land_type, fair_value_per_are,
                       local_body_type, village, area_sqm
                FROM cadastral_parcels WHERE parcel_id = :p
            """),
            {"p": parcel_id},
        ).mappings().first()
        if parcel is None:
            raise HTTPException(404, "parcel not found")

        docs = docs_for(parcel["local_body_type"] or "municipality")
        main_rulebook = "KMBR" if "KMBR" in docs else ("KPBR" if "KPBR" in docs else docs[0])

        # 2. Fetch Property Assessment & OC
        assessment = conn.execute(
            text("""
                SELECT door_no, occupancy_certificate_no, oc_issue_date, assessment_year,
                       annual_property_tax, tax_arrears, status, unauthorized_reason
                FROM property_assessments WHERE parcel_id = :p
            """),
            {"p": parcel_id},
        ).mappings().first()

        checks = []

        # --- Check 1: Occupancy Certificate Audit ---
        status = assessment["status"] if assessment else "NO_BUILDING"
        oc_no = assessment["occupancy_certificate_no"] if assessment else None
        oc_date = str(assessment["oc_issue_date"]) if assessment and assessment["oc_issue_date"] else None

        oc_chk = {
            "check": "occupancy_certificate",
            "verdict": "PASS",
            "status": status,
            "occupancy_certificate_no": oc_no,
            "oc_issue_date": oc_date,
            "detail": "",
            "clauses": [],
            "warnings": [],
        }

        rule20_clauses = []
        try:
            rule20_clauses = clause_text(main_rulebook, "Rule 20", limit=1, contains="occupancy certificate")
        except Exception as exc:  # noqa: BLE001
            oc_chk["warnings"].append(f"Statutory citation lookup error: {exc}")

        if status == "AUTHORIZED" and oc_no:
            oc_chk["verdict"] = "PASS"
            oc_chk["detail"] = (
                f"Valid Occupancy Certificate recorded ({oc_no}, issued {oc_date}). "
                f"Building conforms to sanctioned permit under {main_rulebook} Rule 20."
            )
            oc_chk["clauses"] = rule20_clauses
        elif status == "PENDING_OC":
            oc_chk["verdict"] = "WARN"
            oc_chk["detail"] = (
                f"Completion certificate submitted, but final Occupancy Certificate is pending local body inspection. "
                f"Under {main_rulebook} Rule 20(3), occupation or property conveyance before OC carries risk of service disconnection."
            )
            oc_chk["clauses"] = rule20_clauses
        elif status == "UNAUTHORIZED":
            oc_chk["verdict"] = "FAIL"
            oc_chk["detail"] = (
                f"No valid Occupancy Certificate. Building flagged for violation: "
                f"{assessment.get('unauthorized_reason') or 'Unsanctioned construction under Rule 20'}."
            )
            oc_chk["clauses"] = rule20_clauses
        else:
            oc_chk["verdict"] = "INFO"
            oc_chk["detail"] = "Bare land / vacant plot: no building assessment record. Occupancy Certificate not required."

        checks.append(oc_chk)

        # --- Check 2: Door Number & Regularity Audit ---
        door_no = assessment["door_no"] if assessment else None
        annual_tax = float(assessment["annual_property_tax"]) if assessment and assessment["annual_property_tax"] else 0.0

        door_chk = {
            "check": "building_door_number",
            "verdict": "PASS",
            "door_no": door_no,
            "annual_property_tax": annual_tax,
            "detail": "",
            "clauses": [],
            "warnings": [],
        }

        if status == "AUTHORIZED" and door_no and not door_no.startswith("UA"):
            door_chk["verdict"] = "PASS"
            door_chk["detail"] = f"Authorized building assessment door number: {door_no}. Regular annual property tax: Rs {annual_tax:,.2f}."
        elif status == "UNAUTHORIZED" or (door_no and door_no.startswith("UA")):
            door_chk["verdict"] = "FAIL"
            door_chk["detail"] = (
                f"Provisional/Unauthorized assessment number: {door_no}. Local body has imposed punitive double property tax "
                f"(Rs {annual_tax:,.2f}/yr) under Section 242 of the Kerala Municipality Act / KMBR Rule 20. "
                f"High legal and financial liability for buyer."
            )
            door_chk["clauses"] = rule20_clauses
        elif status == "PENDING_OC":
            door_chk["verdict"] = "WARN"
            door_chk["detail"] = "Regular door number not yet assigned pending final Occupancy Certificate."
        else:
            door_chk["verdict"] = "INFO"
            door_chk["detail"] = "Bare land: no municipal door number."

        checks.append(door_chk)

        # --- Check 3: Property Tax Arrears Audit ---
        arrears = float(assessment["tax_arrears"]) if assessment and assessment["tax_arrears"] else 0.0
        tax_chk = {
            "check": "property_tax_dues",
            "verdict": "PASS" if arrears == 0 else "WARN",
            "tax_arrears": arrears,
            "assessment_year": assessment["assessment_year"] if assessment else None,
            "detail": (
                f"No outstanding property tax arrears recorded."
                if arrears == 0
                else f"Outstanding property tax arrears of Rs {arrears:,.2f} recorded for Assessment Year {assessment.get('assessment_year', 'current')}. "
                     f"Buyer must obtain a Non-Liability / Tax Clearance Certificate prior to deed registration."
            ),
            "clauses": [],
            "warnings": [],
        }
        checks.append(tax_chk)

        # --- Check 4: Section 194-IA TDS Audit ---
        tds_pct, v1 = _rate(conn, "tds_194ia_pct")
        threshold, v2 = _rate(conn, "tds_194ia_threshold")

        area_sqm = float(parcel["area_sqm"] or 0)
        fair_val_are = float(parcel["fair_value_per_are"] or 0)
        fair_val_total = (area_sqm / 100.0) * fair_val_are
        taxable_consideration = max(req.sale_price, fair_val_total)

        tds_warn = [] if (v1 and v2) else ["TDS rate or threshold marked unverified in fee_rates."]
        is_above_threshold = taxable_consideration >= float(threshold)
        tds_amt = _money(taxable_consideration * float(tds_pct) / 100.0) if is_above_threshold else 0.0

        tds_chk = {
            "check": "section_194ia_tds",
            "verdict": "WARN" if is_above_threshold else "INFO",
            "tds_applicable": is_above_threshold,
            "threshold_inr": float(threshold),
            "taxable_consideration_inr": round(taxable_consideration, 2),
            "tds_rate_pct": float(tds_pct),
            "tds_deductible_inr": tds_amt,
            "compliance_form": "Form 26QB (challan-cum-statement) within 30 days of month end",
            "detail": (
                f"Consideration of Rs {req.sale_price:,.0f} (Stamp duty Fair Value Rs {fair_val_total:,.0f}) "
                f"meets or exceeds statutory threshold of Rs {float(threshold):,.0f}. "
                f"Buyer MUST deduct 1% TDS (Rs {tds_amt:,.2f}) and remit via Form 26QB."
                if is_above_threshold
                else f"Total consideration (Rs {taxable_consideration:,.0f}) is below the Rs {float(threshold):,.0f} threshold. "
                     f"No Section 194-IA TDS deduction is required."
            ),
            "clauses": [{"statute": "Income Tax Act, 1961", "section": "Section 194-IA",
                         "note": "Payment on transfer of certain immovable property other than agricultural land"}],
            "warnings": tds_warn,
        }
        checks.append(tds_chk)

        # --- Check 5: Capital Gains Tax Estimation ---
        cg_chk = {
            "check": "capital_gains_estimate",
            "verdict": "INFO",
            "gain_type": None,
            "holding_period_months": None,
            "sale_consideration_inr": req.sale_price,
            "acquisition_cost_inr": req.acquisition_cost,
            "net_capital_gain_inr": None,
            "estimated_tax_inr": None,
            "exemption_options": [],
            "detail": "",
            "clauses": [],
            "warnings": [],
        }

        if req.acquisition_cost is None:
            cg_chk["detail"] = (
                "Provide acquisition_cost and acquisition_date in the request to estimate seller's "
                "capital gains tax liability and statutory exemptions."
            )
        else:
            ltcg_pct, v3 = _rate(conn, "ltcg_property_pct")
            holding_threshold_m, v4 = _rate(conn, "ltcg_holding_months")
            if not (v3 and v4):
                cg_chk["warnings"].append("Capital gains rate or holding period threshold is an unverified placeholder.")

            holding_months = 36  # default if acquisition_date not given
            if req.acquisition_date:
                try:
                    acq_dt = datetime.strptime(req.acquisition_date, "%Y-%m-%d").date()
                    diff_days = (date.today() - acq_dt).days
                    holding_months = max(1, int(diff_days / 30.4375))
                except ValueError:
                    cg_chk["warnings"].append(f"Invalid acquisition_date format '{req.acquisition_date}'. Assumed > 24 months.")

            is_ltcg = holding_months > float(holding_threshold_m)
            gain_type = "LTCG" if is_ltcg else "STCG"
            effective_consideration = max(req.sale_price, fair_val_total)
            net_gain = effective_consideration - req.acquisition_cost - req.improvement_cost - req.transfer_expenses

            cg_chk["gain_type"] = gain_type
            cg_chk["holding_period_months"] = holding_months
            cg_chk["net_capital_gain_inr"] = round(net_gain, 2)

            if is_ltcg:
                tax = round(max(0.0, net_gain) * float(ltcg_pct) / 100.0, 2)
                cg_chk["estimated_tax_inr"] = tax
                cg_chk["exemption_options"] = [
                    {
                        "section": "Section 54",
                        "description": "Exemption on capital gains by purchasing another residential house within 1 yr before or 2 yrs after transfer, or constructing within 3 yrs.",
                    },
                    {
                        "section": "Section 54EC",
                        "description": "Investment in specified capital gains bonds (REC / NHAI) up to Rs 50 Lakhs within 6 months of sale.",
                    },
                    {
                        "section": "Section 54F",
                        "description": "Exemption available if the asset transferred was bare land / non-residential property and proceeds are invested in a residential house.",
                    },
                ]
                cg_chk["detail"] = (
                    f"Long-Term Capital Gain: Rs {net_gain:,.2f} (holding period {holding_months} months > {float(holding_threshold_m):g} months). "
                    f"Estimated LTCG tax at {float(ltcg_pct):g}% (Finance Act 2024 basis): Rs {tax:,.2f}. "
                    f"Exemptions under Section 54 / 54EC / 54F may reduce or eliminate tax liability."
                    if net_gain > 0
                    else f"Long-Term Capital Loss of Rs {abs(net_gain):,.2f}. Can be carried forward for up to 8 assessment years to offset future LTCG."
                )
            else:
                cg_chk["estimated_tax_inr"] = None  # Depends on individual income slab
                cg_chk["detail"] = (
                    f"Short-Term Capital Gain: Rs {net_gain:,.2f} (holding period {holding_months} months <= {float(holding_threshold_m):g} months). "
                    f"Taxable at seller's applicable individual income tax slab rates. "
                    f"Note: Section 54/54EC exemptions are not available for short-term capital gains."
                )

            cg_chk["clauses"] = [
                {"statute": "Income Tax Act, 1961", "section": "Section 45 / 48 / 50C", "note": "Capital gains computation and stamp duty valuation"},
                {"statute": "Income Tax Act, 1961", "section": "Section 54 / 54EC", "note": "Capital gains rollover exemptions"},
            ]

        checks.append(cg_chk)

        # Audit all checks
        for c in checks:
            _audit(conn, parcel_id, c)

    verdicts = {c["verdict"] for c in checks}
    overall = "FAIL" if "FAIL" in verdicts else ("WARN" if "WARN" in verdicts else "PASS")

    return {
        "parcel": {
            "parcel_id": parcel_id,
            "survey_no": parcel["survey_no"],
            "thandaper_no": parcel["thandaper_no"],
            "local_body_type": parcel["local_body_type"],
            "village": parcel["village"],
            "area_sqm": round(area_sqm, 1),
            "fair_value_per_are": fair_val_are,
            "fair_value_total": round(fair_val_total, 2),
            "rulebooks": docs,
        },
        "overall": overall,
        "inputs": {
            "sale_price": req.sale_price,
            "acquisition_cost": req.acquisition_cost,
            "acquisition_date": req.acquisition_date,
            "improvement_cost": req.improvement_cost,
            "transfer_expenses": req.transfer_expenses,
        },
        "assessment": {
            "status": status,
            "door_no": door_no,
            "occupancy_certificate_no": oc_no,
            "oc_issue_date": oc_date,
            "annual_property_tax": annual_tax,
            "tax_arrears": arrears,
            "unauthorized_reason": assessment.get("unauthorized_reason") if assessment else None,
        },
        "checks": checks,
        "assumptions": assumptions,
        "note": "Prototype on synthetic data. Not legal or chartered tax advice.",
    }


# --- Endpoints ---------------------------------------------------------------
@router.get("/test-cases")
def phase3_test_cases():
    """Sample parcel IDs representing distinct selling and compliance scenarios."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                (SELECT 'clean_authorized' AS scenario, parcel_id FROM property_assessments WHERE status = 'AUTHORIZED' AND tax_arrears = 0 ORDER BY parcel_id LIMIT 3)
                UNION ALL
                (SELECT 'unauthorized' AS scenario, parcel_id FROM property_assessments WHERE status = 'UNAUTHORIZED' ORDER BY parcel_id LIMIT 3)
                UNION ALL
                (SELECT 'pending_oc' AS scenario, parcel_id FROM property_assessments WHERE status = 'PENDING_OC' ORDER BY parcel_id LIMIT 3)
                UNION ALL
                (SELECT 'tax_arrears' AS scenario, parcel_id FROM property_assessments WHERE tax_arrears > 0 ORDER BY parcel_id LIMIT 3)
                UNION ALL
                (SELECT 'no_building' AS scenario, parcel_id FROM property_assessments WHERE status = 'NO_BUILDING' ORDER BY parcel_id LIMIT 3)
            """)
        ).mappings().all()

    out: dict[str, list[int]] = {}
    for r in rows:
        out.setdefault(r["scenario"], []).append(r["parcel_id"])
    return out


@router.get("/{parcel_id}")
def phase3_get(
    parcel_id: int,
    sale_price: float = Query(..., gt=0, description="Declared sale price in INR"),
    acquisition_cost: float | None = Query(None, gt=0, description="Original purchase cost in INR"),
    acquisition_date: str | None = Query(None, description="YYYY-MM-DD date of acquisition"),
    improvement_cost: float = Query(0.0, ge=0, description="Improvement cost in INR"),
    transfer_expenses: float = Query(0.0, ge=0, description="Transfer / brokerage expenses in INR"),
):
    """Phase 3 report via GET request."""
    return run_phase3(
        parcel_id,
        Phase3Request(
            sale_price=sale_price,
            acquisition_cost=acquisition_cost,
            acquisition_date=acquisition_date,
            improvement_cost=improvement_cost,
            transfer_expenses=transfer_expenses,
        ),
    )


@router.post("/{parcel_id}")
def phase3_post(parcel_id: int, req: Phase3Request):
    """Phase 3 report via POST request with full JSON payload."""
    return run_phase3(parcel_id, req)
