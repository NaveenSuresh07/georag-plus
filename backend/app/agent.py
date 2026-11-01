"""GeoRAG+ Batch 7: AI Legal Explainer Agent.

Location in repo: backend/app/agent.py

The agent synthesizes the results of Phase 1 (Buying), Phase 2 (Building),
and Phase 3 (Selling) rule engines, and retrieved statutory law clauses (pgvector / full text),
into structured, plain-language legal reports.

STRICT PRINCIPLES:
1. The computer calculates; the AI only explains and cites.
2. The agent NEVER computes a number, changes a measurement, or invents a clause.
3. Every verdict and cited clause is grounded directly in the engine output.
4. Operates with Gemini, OpenAI, local Ollama, or a high-precision deterministic explainer fallback.
"""
from datetime import datetime
import json
import re
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
import httpx
from pydantic import BaseModel, Field

from .config import settings
from .phase1 import phase1_report, test_cases as phase1_test_cases
from .phase2 import Phase2Request, run_phase2
from .phase3 import Phase3Request, run_phase3
from .rag import clause_text, retrieve

router = APIRouter(prefix="/agent", tags=["agent"])

DISCLAIMER = (
    "> [!NOTE]\n"
    "> **Statutory Disclaimer**: GeoRAG+ is an automated compliance verification prototype "
    "operating on spatial data, synthetic revenue records, and gazetted building regulations. "
    "It does not substitute for certified legal counsel, structural engineering, or revenue survey validation."
)


class AgentQueryRequest(BaseModel):
    query: str = Field(..., description="User question or instruction (e.g. 'Can I build a 2-storey house on Plot 1?')")
    parcel_id: int | None = Field(None, description="Cadastral parcel ID (if omitted, extracted from query or defaults to 1)")
    floors: int | None = Field(None, ge=1, le=30, description="Number of floors for building checks")
    height_m: float | None = Field(None, gt=0, description="Building height in metres")
    sale_price: float | None = Field(None, gt=0, description="Declared sale consideration in INR")
    acquisition_cost: float | None = Field(None, gt=0, description="Original acquisition price in INR")
    acquisition_date: str | None = Field(None, description="Date of acquisition (YYYY-MM-DD)")
    cost_per_sqm: float | None = Field(None, gt=0, description="Construction cost per sq m in INR")
    phase: Literal[1, 2, 3] | None = Field(None, description="Force a specific phase (1=Buying, 2=Building, 3=Selling)")
    language: Literal["en", "ml"] = Field("en", description="Output language ('en' = English, 'ml' = Malayalam)")


class AgentResponse(BaseModel):
    query: str
    intent: str
    parcel_id: int | None
    overall_verdict: str
    explanation: str
    key_findings: list[str]
    statutory_citations: list[dict]
    raw_data: dict[str, Any]
    llm_provider: str
    model: str | None = None


# --- Intent & Entity Extraction ---
def _extract_parcel_id(query: str, default: int = 1) -> int:
    m = re.search(r"\b(?:plot|parcel|lot)\s*(?:no\.?|#)?\s*(\d+)\b", query, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return default


def _detect_intent(query: str, phase_override: int | None) -> str:
    if phase_override == 1:
        return "phase1_buying"
    if phase_override == 2:
        return "phase2_building"
    if phase_override == 3:
        return "phase3_selling"

    q = query.lower()
    if any(k in q for k in ("due diligence", "full report", "complete report", "all phases", "everything", "full check")):
        return "full_due_diligence"
    if any(k in q for k in ("sell", "selling", "occupancy", "door number", "unauthorized", "tax arrears", "tds", "194ia", "194-ia", "capital gain", "ltcg", "stcg")):
        return "phase3_selling"
    if any(k in q for k in ("build", "building", "house", "construct", "setback", "yard", "front", "rear", "side", "coverage", "far", "fsi", "cess", "height", "floors")):
        return "phase2_building"
    if any(k in q for k in ("buy", "buying", "purchase", "loan", "mortgage", "encumbrance", "ec", "paddy", "wetland", "data bank", "stamp duty", "nilam", "purayidom")):
        return "phase1_buying"
    if any(k in q for k in ("what is rule", "what does rule", "explain rule", "kmbr rule", "kpbr rule", "clause")):
        return "law_inquiry"

    return "phase2_building"  # Default to building check if ambiguous


# --- LLM Providers ---
def _call_gemini(prompt: str, api_key: str, model_name: str) -> str | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        pass
    return None


def _call_openai(prompt: str, api_key: str, model_name: str) -> str | None:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model_name or "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are GeoRAG+ Legal Explainer. Ground strictly in the provided data. Never calculate or invent rules."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception:
        pass
    return None


def _call_ollama(prompt: str, base_url: str, model_name: str) -> str | None:
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {"model": model_name or "llama3", "prompt": prompt, "stream": False}
    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json().get("response")
    except Exception:
        pass
    return None


# --- High-Precision Deterministic Explainer ---
def _generate_deterministic_explanation(intent: str, parcel_id: int, data: dict, query: str) -> tuple[str, list[str]]:
    findings = []
    lines = []

    if intent == "phase1_buying":
        p = data["parcel"]
        overall = data["overall"]
        lines.append(f"### Land Purchase Due Diligence (Phase 1 Report) for Plot #{parcel_id}")
        lines.append(f"**Jurisdiction**: {p.get('village', 'Attingal')} ({p.get('local_body_type', 'municipality').title()}) | **Survey No**: {p.get('survey_no')} | **Area**: {p.get('area_sqm')} sq m")
        lines.append(f"**Overall Land Fitness Verdict**: **`{overall}`**\n")

        for c in data.get("checks", []):
            badge = f"[{c['verdict']}]"
            chk_name = c["check"].replace("_", " ").title()
            lines.append(f"- **{chk_name}** {badge}: {c['detail']}")
            findings.append(f"{chk_name}: {c['verdict']} - {c['detail']}")

        duty = data.get("stamp_duty", {})
        if duty:
            lines.append(f"\n#### Stamp Duty & Registration Expenses")
            lines.append(f"- **Taxable Consideration**: Rs {duty.get('consideration', 0):,.2f} (Stamp duty base: Rs {duty.get('taxable_basis', 0):,.2f})")
            lines.append(f"- **Stamp Duty ({duty.get('stamp_duty_pct', 8):g}%)**: Rs {duty.get('stamp_duty_inr', 0):,.2f}")
            lines.append(f"- **Registration Fee ({duty.get('registration_fee_pct', 2):g}%)**: Rs {duty.get('registration_fee_inr', 0):,.2f}")
            lines.append(f"- **Total Government Duty**: Rs {duty.get('total_fees_inr', 0):,.2f}")
            findings.append(f"Total Government Fee: Rs {duty.get('total_fees_inr', 0):,.2f}")

    elif intent == "phase2_building":
        p = data["parcel"]
        overall = data["overall"]
        meas = data["measurements"]
        inp = data["inputs"]
        rulebook = p.get("rulebooks", ["KMBR"])[0]

        lines.append(f"### Pre-Construction Building Rules Check (Phase 2 Report) for Plot #{parcel_id}")
        lines.append(f"**Applicable Rulebook**: {rulebook} ({p.get('local_body_type', 'municipality').title()} Jurisdiction) | **Floors**: {inp.get('floors')} | **Height**: {inp.get('height_m')} m")
        lines.append(f"**Overall Compliance Verdict**: **`{overall}`**\n")

        lines.append("#### Setback & Spatial Measurements")
        for c in data.get("checks", []):
            if c["check"] in ("demo_footprint_clipped", "restricted_zones"):
                continue
            badge = f"[{c['verdict']}]"
            chk_name = c["check"].replace("_", " ").title()
            lines.append(f"- **{chk_name}** {badge}: {c['detail']}")
            findings.append(f"{chk_name}: {c['verdict']} - {c['detail']}")

        lines.append(f"\n#### Plot Dimensions Summary")
        lines.append(f"- **Plot Area**: {meas.get('plot_area_sqm')} sq m | **Footprint Area**: {meas.get('footprint_area_sqm')} sq m")
        lines.append(f"- **Plot Coverage**: {meas.get('coverage_pct')}% | **FAR / FSI**: {meas.get('far')}")
        lines.append(f"- **Clearances**: Front: {meas.get('front_m')} m | Rear: {meas.get('rear_m')} m | Side Min: {meas.get('side_min_m')} m")

    elif intent == "phase3_selling":
        p = data["parcel"]
        overall = data["overall"]
        ass = data.get("assessment", {})

        lines.append(f"### Property Sale & Compliance Check (Phase 3 Report) for Plot #{parcel_id}")
        lines.append(f"**Jurisdiction**: {p.get('village', 'Attingal')} | **Survey No**: {p.get('survey_no')} | **Door No**: {ass.get('door_no') or 'Unassigned'}")
        lines.append(f"**Overall Selling Fitness Verdict**: **`{overall}`**\n")

        lines.append("#### Municipal Assessment & Legal Status")
        for c in data.get("checks", []):
            badge = f"[{c['verdict']}]"
            chk_name = c["check"].replace("_", " ").title()
            lines.append(f"- **{chk_name}** {badge}: {c['detail']}")
            findings.append(f"{chk_name}: {c['verdict']} - {c['detail']}")

    elif intent == "full_due_diligence":
        lines.append(f"### Comprehensive 3-Phase Due Diligence Report for Plot #{parcel_id}")
        p1, p2, p3 = data["phase1"], data["phase2"], data["phase3"]
        lines.append(f"| Phase | Stage | Verdict | Key Finding |")
        lines.append(f"|---|---|---|---|")
        lines.append(f"| Phase 1 | Land Purchase (Title/Wetland) | **`{p1['overall']}`** | {p1['checks'][0]['detail'][:60]}... |")
        lines.append(f"| Phase 2 | Construction Rules (KMBR) | **`{p2['overall']}`** | Front: {p2['measurements']['front_m']}m, Coverage: {p2['measurements']['coverage_pct']}% |")
        lines.append(f"| Phase 3 | Selling Compliance & Tax | **`{p3['overall']}`** | Status: {p3['assessment']['status']}, TDS: {p3['checks'][3]['verdict']} |")

        findings.append(f"Phase 1 Buying: {p1['overall']}")
        findings.append(f"Phase 2 Building: {p2['overall']}")
        findings.append(f"Phase 3 Selling: {p3['overall']}")

    lines.append("\n" + DISCLAIMER)
    return "\n".join(lines), findings


# --- Agent Core Runner ---
def run_agent_query(req: AgentQueryRequest) -> AgentResponse:
    pid = req.parcel_id or _extract_parcel_id(req.query, default=1)
    intent = _detect_intent(req.query, req.phase)

    raw_data: dict[str, Any] = {}
    citations: list[dict] = []
    overall_verdict = "PASS"

    if intent == "phase1_buying":
        raw = phase1_report(pid, consideration=req.sale_price or 3000000, ec_years=30)
        raw_data = raw
        overall_verdict = raw["overall"]
        for c in raw.get("checks", []):
            citations.extend(c.get("clauses", []))

    elif intent == "phase2_building":
        p2_req = Phase2Request(
            floors=req.floors or 1,
            height_m=req.height_m,
            cost_per_sqm=req.cost_per_sqm or 30000,
        )
        raw = run_phase2(pid, p2_req)
        raw_data = raw
        overall_verdict = raw["overall"]
        for c in raw.get("checks", []):
            citations.extend(c.get("clauses", []))

    elif intent == "phase3_selling":
        p3_req = Phase3Request(
            sale_price=req.sale_price or 5000000,
            acquisition_cost=req.acquisition_cost,
            acquisition_date=req.acquisition_date,
        )
        raw = run_phase3(pid, p3_req)
        raw_data = raw
        overall_verdict = raw["overall"]
        for c in raw.get("checks", []):
            citations.extend(c.get("clauses", []))

    elif intent == "full_due_diligence":
        p1 = phase1_report(pid, consideration=req.sale_price or 3000000, ec_years=30)
        p2 = run_phase2(pid, Phase2Request(floors=req.floors or 1, cost_per_sqm=30000))
        p3 = run_phase3(pid, Phase3Request(sale_price=req.sale_price or 5000000, acquisition_cost=req.acquisition_cost, acquisition_date=req.acquisition_date))
        raw_data = {"phase1": p1, "phase2": p2, "phase3": p3}
        verdicts = {p1["overall"], p2["overall"], p3["overall"]}
        overall_verdict = "FAIL" if "FAIL" in verdicts else ("WARN" if "WARN" in verdicts else "PASS")
        for r in (p1, p2, p3):
            for c in r.get("checks", []):
                citations.extend(c.get("clauses", []))

    elif intent == "law_inquiry":
        res = retrieve(req.query, k=3)
        raw_data = {"results": res}
        citations = res

    # Deduplicate citations
    dedup_citations = []
    seen = set()
    for c in citations:
        key = (c.get("doc_code") or c.get("statute"), c.get("clause_ref") or c.get("section"))
        if key not in seen and key[0] and key[1]:
            seen.add(key)
            dedup_citations.append(c)

    # Generate explanation
    llm_choice = settings.LLM_PROVIDER.lower()
    explanation = None
    active_provider = "deterministic_rule_explainer"
    active_model = None

    prompt = (
        f"You are GeoRAG+ Legal Explainer, an AI pair-programmer and statutory advisor for Kerala land compliance.\n"
        f"User Query: {req.query}\n"
        f"Language: {'Malayalam' if req.language == 'ml' else 'English'}\n\n"
        f"STRICT INSTRUCTIONS:\n"
        f"1. You must ONLY explain the exact numbers, measurements, and verdicts from the engine data below.\n"
        f"2. NEVER invent or recalculate any number, setback, fee, or law clause.\n"
        f"3. Quote the exact clauses provided in statutory citations.\n"
        f"4. Format clearly in Markdown with headers, bullet points, and actionable next steps.\n"
        f"5. End with the statutory disclaimer.\n\n"
        f"ENGINE VERDICTS & MEASUREMENTS:\n{json.dumps(raw_data, default=str, indent=2)}\n\n"
        f"STATUTORY CITATIONS:\n{json.dumps(dedup_citations, default=str, indent=2)}"
    )

    if (llm_choice in ("auto", "gemini")) and settings.GEMINI_API_KEY:
        explanation = _call_gemini(prompt, settings.GEMINI_API_KEY, settings.LLM_MODEL)
        if explanation:
            active_provider = "gemini"
            active_model = settings.LLM_MODEL

    if not explanation and (llm_choice in ("auto", "openai")) and settings.OPENAI_API_KEY:
        explanation = _call_openai(prompt, settings.OPENAI_API_KEY, settings.LLM_MODEL)
        if explanation:
            active_provider = "openai"
            active_model = "gpt-4o-mini"

    if not explanation and (llm_choice in ("auto", "ollama")):
        explanation = _call_ollama(prompt, settings.OLLAMA_BASE_URL, settings.LLM_MODEL)
        if explanation:
            active_provider = "ollama"
            active_model = settings.LLM_MODEL

    # Fallback to deterministic high-precision rule explainer
    if not explanation:
        explanation, findings = _generate_deterministic_explanation(intent, pid, raw_data, req.query)
        active_provider = "deterministic_rule_explainer"
    else:
        findings = [f"Overall Verdict: {overall_verdict}", f"Intent: {intent}"]

    return AgentResponse(
        query=req.query,
        intent=intent,
        parcel_id=pid,
        overall_verdict=overall_verdict,
        explanation=explanation,
        key_findings=findings,
        statutory_citations=dedup_citations,
        raw_data=raw_data,
        llm_provider=active_provider,
        model=active_model,
    )


# --- Endpoints ---
@router.post("/query", response_model=AgentResponse)
def query_agent_post(req: AgentQueryRequest):
    """Execute AI Legal Explainer Agent via POST JSON payload."""
    return run_agent_query(req)


@router.get("/query", response_model=AgentResponse)
def query_agent_get(
    q: str = Query(..., description="User query"),
    parcel_id: int | None = Query(None, description="Plot ID"),
    floors: int | None = Query(None, ge=1, le=30),
    height_m: float | None = Query(None, gt=0),
    sale_price: float | None = Query(None, gt=0),
    acquisition_cost: float | None = Query(None, gt=0),
    acquisition_date: str | None = Query(None),
    cost_per_sqm: float | None = Query(None, gt=0),
    phase: Literal[1, 2, 3] | None = Query(None),
    language: Literal["en", "ml"] = Query("en"),
):
    """Execute AI Legal Explainer Agent via GET query parameters for quick browser interaction."""
    return run_agent_query(
        AgentQueryRequest(
            query=q,
            parcel_id=parcel_id,
            floors=floors,
            height_m=height_m,
            sale_price=sale_price,
            acquisition_cost=acquisition_cost,
            acquisition_date=acquisition_date,
            cost_per_sqm=cost_per_sqm,
            phase=phase,
            language=language,
        )
    )


@router.get("/status")
def agent_status():
    """Returns the current LLM provider configuration and status."""
    return {
        "configured_provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL,
        "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        "openai_api_key_set": bool(settings.OPENAI_API_KEY),
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "active_fallback": "deterministic_rule_explainer",
    }
