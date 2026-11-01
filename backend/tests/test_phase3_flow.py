"""Unit and flow tests for app/phase3.py (Phase 3: Selling & Compliance Engine).
Location in repo: backend/tests/test_phase3_flow.py
"""
import pytest
from app import phase3 as p3


def test_clean_authorized_sale():
    res = p3.run_phase3(
        1,
        p3.Phase3Request(
            sale_price=4000000,
            acquisition_cost=2500000,
            acquisition_date="2020-01-15",
        ),
    )
    by_check = {c["check"]: c for c in res["checks"]}
    assert by_check["occupancy_certificate"]["verdict"] == "PASS"
    assert by_check["building_door_number"]["verdict"] == "PASS"
    assert by_check["property_tax_dues"]["verdict"] == "PASS"
    assert by_check["section_194ia_tds"]["verdict"] == "INFO"
    assert by_check["section_194ia_tds"]["tds_applicable"] is False
    assert by_check["capital_gains_estimate"]["gain_type"] == "LTCG"
    assert by_check["capital_gains_estimate"]["net_capital_gain_inr"] == 1500000.0
    assert by_check["capital_gains_estimate"]["estimated_tax_inr"] == 187500.0


def test_unauthorized_construction_fails():
    res = p3.run_phase3(2, p3.Phase3Request(sale_price=3500000))
    by_check = {c["check"]: c for c in res["checks"]}
    assert res["overall"] == "FAIL"
    assert by_check["occupancy_certificate"]["verdict"] == "FAIL"
    assert by_check["building_door_number"]["verdict"] == "FAIL"
    assert "punitive double property tax" in by_check["building_door_number"]["detail"]


def test_pending_oc_warns():
    res = p3.run_phase3(3, p3.Phase3Request(sale_price=3500000))
    by_check = {c["check"]: c for c in res["checks"]}
    assert by_check["occupancy_certificate"]["verdict"] == "WARN"
    assert by_check["building_door_number"]["verdict"] == "WARN"


def test_tax_arrears_warns():
    res = p3.run_phase3(4, p3.Phase3Request(sale_price=3500000))
    by_check = {c["check"]: c for c in res["checks"]}
    assert by_check["property_tax_dues"]["verdict"] == "WARN"
    assert by_check["property_tax_dues"]["tax_arrears"] == 14500.0


def test_tds_applicable_above_50_lakhs():
    res = p3.run_phase3(1, p3.Phase3Request(sale_price=6000000))
    by_check = {c["check"]: c for c in res["checks"]}
    tds = by_check["section_194ia_tds"]
    assert tds["verdict"] == "WARN"
    assert tds["tds_applicable"] is True
    assert tds["tds_deductible_inr"] == 60000.0
    assert "Form 26QB" in tds["compliance_form"]


def test_tds_on_fair_value_when_higher_than_price():
    # Parcel 5 has fair value > 70 Lakhs even with low sale price
    res = p3.run_phase3(5, p3.Phase3Request(sale_price=3000000))
    by_check = {c["check"]: c for c in res["checks"]}
    tds = by_check["section_194ia_tds"]
    assert tds["verdict"] == "WARN"
    assert tds["tds_applicable"] is True
    assert tds["taxable_consideration_inr"] > 5000000


def test_stcg_when_held_less_than_24_months():
    res = p3.run_phase3(
        1,
        p3.Phase3Request(
            sale_price=4000000,
            acquisition_cost=3000000,
            acquisition_date="2026-05-01",  # Recent
        ),
    )
    cg = {c["check"]: c for c in res["checks"]}["capital_gains_estimate"]
    assert cg["gain_type"] == "STCG"
    assert cg["holding_period_months"] <= 24
    assert cg["estimated_tax_inr"] is None  # Slab rate
    assert "individual income tax slab" in cg["detail"]


def test_phase3_test_cases_endpoint():
    cases = p3.phase3_test_cases()
    assert "clean_authorized" in cases
    assert "unauthorized" in cases
    assert "pending_oc" in cases
    assert "tax_arrears" in cases
    assert "no_building" in cases
    assert 1 in cases["clean_authorized"]
    assert 2 in cases["unauthorized"]
    assert 3 in cases["pending_oc"]
    assert 4 in cases["tax_arrears"]
    assert 5 in cases["no_building"]
