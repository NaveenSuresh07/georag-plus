"""Unit and flow tests for app/agent.py (Batch 7: AI Legal Explainer Agent).
Location in repo: backend/tests/test_agent_flow.py
"""
import pytest
from app import agent


def test_agent_intent_detection():
    assert agent._detect_intent("Can I buy this land? Any mortgage?", None) == "phase1_buying"
    assert agent._detect_intent("Check setbacks for a 2-storey house", None) == "phase2_building"
    assert agent._detect_intent("Is the occupancy certificate valid to sell?", None) == "phase3_selling"
    assert agent._detect_intent("Give me a full due diligence report", None) == "full_due_diligence"
    assert agent._detect_intent("Anything", phase_override=1) == "phase1_buying"


def test_agent_parcel_extraction():
    assert agent._extract_parcel_id("Can I build on plot 4?") == 4
    assert agent._extract_parcel_id("Check parcel #12 please") == 12
    assert agent._extract_parcel_id("No parcel mentioned", default=1) == 1


def test_agent_phase1_flow():
    res = agent.run_agent_query(
        agent.AgentQueryRequest(query="Is plot 1 safe to buy? Any encumbrance?")
    )
    assert res.intent == "phase1_buying"
    assert res.parcel_id == 1
    assert res.overall_verdict == "PASS"
    assert "Encumbrance Certificate" in res.explanation
    assert len(res.key_findings) > 0


def test_agent_phase2_flow():
    res = agent.run_agent_query(
        agent.AgentQueryRequest(
            query="Can I build a 2-floor house on plot 1?",
            floors=2,
            cost_per_sqm=30000,
        )
    )
    assert res.intent == "phase2_building"
    assert res.parcel_id == 1
    assert "KMBR" in res.explanation
    assert "Front Setback" in res.explanation
    assert len(res.statutory_citations) > 0


def test_agent_phase3_unauthorized_flow():
    res = agent.run_agent_query(
        agent.AgentQueryRequest(query="Check selling status for plot 2 with 40 lakhs price")
    )
    assert res.intent == "phase3_selling"
    assert res.parcel_id == 2
    assert res.overall_verdict == "FAIL"
    assert "UA-12/402" in res.explanation
    assert "Occupancy Certificate" in res.explanation


def test_agent_full_due_diligence_flow():
    res = agent.run_agent_query(
        agent.AgentQueryRequest(query="Give me a complete due diligence report for plot 1")
    )
    assert res.intent == "full_due_diligence"
    assert res.parcel_id == 1
    assert "Phase 1" in res.explanation
    assert "Phase 2" in res.explanation
    assert "Phase 3" in res.explanation


def test_agent_status_endpoint():
    status = agent.agent_status()
    assert "configured_provider" in status
    assert "active_fallback" in status
    assert status["active_fallback"] == "deterministic_rule_explainer"
