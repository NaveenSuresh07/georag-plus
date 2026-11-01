"""Flow tests for app/phase2.py with a FAKE database: no Docker, no real data needed.
Location in repo: backend/tests/test_phase2_flow.py
"""
import json
from contextlib import contextmanager
from decimal import Decimal

import pytest
from pyproj import Transformer
from shapely.geometry import LineString, Polygon
from shapely.ops import transform

from app import phase2 as p2

# shapely's old transform() warns; irrelevant for these tests
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.fixture(autouse=True)
def isolate_from_real_services(monkeypatch):
    """The engine also looks up rulebooks and clause text in the real database. Replace both."""
    monkeypatch.setattr(p2, "docs_for", lambda local_body_type: ["KMBR"] if local_body_type == "municipality" else ["KPBR"])
    monkeypatch.setattr(
        p2, "clause_text",
        lambda doc, ref, limit=1, contains=None: [{"doc_code": doc, "clause_ref": ref, "page": 49, "text": "stub", "match": "exact clause"}],
    )

TO_LL = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)
def ll_wkt(g): return transform(TO_LL.transform, g).wkt

# metric world: a 20x30 m plot at the origin of a local grid shifted to a real UTM spot
X0, Y0 = 300000.0, 961000.0
def shift(g, dx=0, dy=0):
    return transform(lambda x, y, z=None: (x + X0 + dx, y + Y0 + dy), g)
PLOT = shift(Polygon([(0, 0), (20, 0), (20, 30), (0, 30)]))
HOUSE = shift(Polygon([(5, 4), (15, 4), (15, 14), (5, 14)]))
ROAD = shift(LineString([(-50, -5), (50, -5)]))

def inside(v, lo, hi):
    """Same convention as the SQL: lower bound exclusive, upper bound inclusive."""
    v = float(v)
    return (lo is None or v > float(lo)) and (hi is None or v <= float(hi))

def matches(r, p):
    """Python copy of the WHERE clause in phase2._rules (the SQL itself needs a real database)."""
    return (r.get("use_group") in (None, p["ug"])
            and inside(p["h"], r.get("height_min_m"), r.get("height_max_m"))
            and inside(p["a"], r.get("plot_min_sqm"), r.get("plot_max_sqm"))
            and inside(p["b"], r.get("builtup_min_sqm"), r.get("builtup_max_sqm"))
            and (p["cat"] is None or r.get("category") in (None, p["cat"]))
            and r.get("road_class") in (None, p["rc"]))

def spec(r):
    return sum([r.get("use_group") is not None,
                r.get("height_min_m") is not None or r.get("height_max_m") is not None,
                r.get("plot_min_sqm") is not None or r.get("plot_max_sqm") is not None,
                r.get("builtup_min_sqm") is not None or r.get("builtup_max_sqm") is not None,
                r.get("category") is not None, r.get("road_class") is not None])

class Res:
    def __init__(self, rows=None, scalar=None): self.rows, self._s = rows or [], scalar
    def mappings(self): return self
    def first(self): return self.rows[0] if self.rows else None
    def all(self): return self.rows
    def scalar(self): return self._s
    def __iter__(self): return iter(self.rows)

class FakeConn:
    def __init__(self, rules, zones=(), util=()):
        self.rules, self.zones, self.util, self.audit = rules, list(zones), list(util), []
        self.rule_calls = []
        self.parcel_category = None   # the 'panchayat_category' stored on the plot record
        self.local_body_type = "panchayat"
        self.orig_factor = 1.0      # 1.3 = the real building is 30% bigger than the clipped footprint
    def execute(self, stmt, params=None):
        sql = str(stmt)
        if "INSERT INTO audit_log" in sql:
            self.audit.append(params); return Res()
        if "FROM cadastral_parcels WHERE parcel_id" in sql and "ST_AsText(geom)" in sql:
            return Res([{"parcel_id": 1, "survey_no": "100/1", "local_body_type": self.local_body_type,
                         "panchayat_category": self.parcel_category, "wkt": ll_wkt(PLOT)}])
        if "FROM study_area_buildings" in sql:
            return Res([{"wkt": ll_wkt(HOUSE), "orig_area_sqm": HOUSE.area * self.orig_factor}])
        if "FROM roads r" in sql:
            return Res([{"road_id": 1, "name": "Test Rd", "road_class": "Local", "wkt": ll_wkt(ROAD), "dist_m": 5.0}])
        if "FROM rule_params" in sql:
            self.rule_calls.append(params)
            rows = [{**r, "specificity": spec(r)} for r in self.rules
                    if r["param"] == params["param"] and matches(r, params)]
            return Res(rows)
        if "FROM fee_rates" in sql:     # cess rate and threshold: unverified placeholders
            rate = {"bocw_cess_pct": 1, "bocw_cess_threshold_sqm": 100}[params["c"]]
            return Res([(Decimal(rate), False)])
        if "FROM restricted_zones" in sql: return Res(self.zones)
        if "FROM utility_assets" in sql: return Res(self.util)
        raise AssertionError("unexpected SQL: " + sql[:80])

def rule(param, value, verified=True, **kw):
    base = dict(id=1, doc_code="KPBR", clause_ref="Rule 26", table_ref="Table 4", value=Decimal(str(value)),
                unit="m", verified=verified, param=param,
                use_group=None, height_min_m=None, height_max_m=None, plot_min_sqm=None, plot_max_sqm=None,
                builtup_min_sqm=None, builtup_max_sqm=None, category=None, road_class=None, proviso=None)
    base.update(kw); return base

class FakeEngine:
    def __init__(self, conn): self.conn = conn
    @contextmanager
    def begin(self): yield self.conn

def run(conn, **req):
    p2.engine = FakeEngine(conn)
    return p2.run_phase2(1, p2.Phase2Request(**req))

GOOD_RULES = [rule("front_setback_min", 3), rule("rear_setback_min", 2), rule("side_setback_min", 1.5),
              rule("max_plot_coverage_pct", 60), rule("max_far", 1.5), rule("road_centre_min", 3)]

def by(res): return {c["check"]: c for c in res["checks"]}

def test_without_a_cost_the_cess_check_warns():
    res = run(FakeConn(GOOD_RULES), floors=2)           # 200 sq m is above the 100 sq m threshold
    warned = [k for k, v in by(res).items() if v["verdict"] == "WARN"]
    assert warned == ["construction_cess"] and res["overall"] == "WARN"

def test_all_pass_and_measurements():
    res = run(FakeConn(GOOD_RULES), floors=2, cost_per_sqm=30000)
    c = by(res)
    assert res["overall"] == "PASS", [(k, v["verdict"], v["detail"]) for k, v in c.items()]
    assert res["measurements"]["front_m"] == pytest.approx(4.0, abs=0.05)
    assert res["measurements"]["rear_m"] == pytest.approx(16.0, abs=0.1)
    assert res["measurements"]["side_min_m"] == pytest.approx(5.0, abs=0.05)
    assert res["measurements"]["coverage_pct"] == pytest.approx(16.67, abs=0.1)
    assert res["measurements"]["far"] == pytest.approx(0.333, abs=0.01)
    assert c["front_setback"]["clauses"][0]["clause_ref"] == "Rule 26"
    assert c["distance_to_road_centre"]["measured"] == pytest.approx(9.0, abs=0.1)

def test_front_setback_fail_when_rule_is_stricter():
    rules = [r for r in GOOD_RULES if r["param"] != "front_setback_min"] + [rule("front_setback_min", 6)]
    res = run(FakeConn(rules))
    assert res["overall"] == "FAIL"
    assert by(res)["front_setback"]["verdict"] == "FAIL" and by(res)["front_setback"]["required"] == 6.0

def test_missing_rule_is_a_warning_not_a_guess():
    res = run(FakeConn([]))
    assert by(res)["front_setback"]["verdict"] == "WARN"
    assert "rule_params" in by(res)["front_setback"]["detail"]
    assert res["overall"] == "WARN"

def test_unverified_rule_warns_and_strictest_of_several_wins():
    rules = [r for r in GOOD_RULES if r["param"] != "max_plot_coverage_pct"] + [
        rule("max_plot_coverage_pct", 65, verified=False), rule("max_plot_coverage_pct", 10, verified=True)]
    res = run(FakeConn(rules))
    chk = by(res)["plot_coverage"]
    assert chk["required"] == 10.0 and chk["verdict"] == "FAIL"          # 16.7% > 10%
    assert any("strictest" in w for w in chk["warnings"]) and any("verified" in w for w in chk["warnings"])

def test_cess():
    res = run(FakeConn(GOOD_RULES), floors=2, floor_area_sqm=250, cost_per_sqm=30000)
    cess = by(res)["construction_cess"]
    assert cess["cess"] == pytest.approx(75000.0) and any("placeholder" in w for w in cess["warnings"])
    small = by(run(FakeConn(GOOD_RULES), floors=1, floor_area_sqm=80))["construction_cess"]
    assert small["cess"] == 0.0
    needs = by(run(FakeConn(GOOD_RULES), floors=1, floor_area_sqm=250))["construction_cess"]
    assert needs["verdict"] == "WARN"

def test_zone_and_utility_checks():
    conn = FakeConn(GOOD_RULES + [rule("min_distance_CRZ", 50)],
                    zones=[{"zone_type": "CRZ", "d": 30.0}], util=[{"asset_type": "Transformer", "d": 120.0}])
    c = by(run(conn))
    assert c["distance_to_CRZ"]["verdict"] == "FAIL" and c["distance_to_CRZ"]["required"] == 50.0
    assert c["nearest_kseb_transformer"]["distance_m"] == 120.0
    assert c["nearest_kwa_main"]["verdict"] == "INFO"

def test_every_check_is_written_to_the_audit_log():
    conn = FakeConn(GOOD_RULES)
    res = run(conn)
    assert len(conn.audit) == len(res["checks"])
    assert all(a["pid"] == 1 for a in conn.audit)
    json.loads(conn.audit[1]["inputs"])      # valid JSON


def test_builtup_area_and_plot_area_are_passed_to_the_rule_lookup():
    """KPBR Table 4 depends on built-up area (and plot area for small plots)."""
    conn = FakeConn(GOOD_RULES)
    res = run(conn, floors=2, floor_area_sqm=180)
    call = [c for c in conn.rule_calls if c["param"] == "front_setback_min"][0]
    assert float(call["b"]) == pytest.approx(180.0)                                  # built-up area
    assert float(call["a"]) == pytest.approx(res["measurements"]["plot_area_sqm"], abs=0.2)
    assert call["ug"] == "A1" and float(call["h"]) == pytest.approx(6.0)             # 2 floors x 3 m


def test_clipped_demo_footprint_is_flagged():
    conn = FakeConn(GOOD_RULES)
    conn.orig_factor = 1.3                       # 23% of the real building was cut off by the plot edge
    res = run(conn, floors=2, cost_per_sqm=30000)
    flag = by(res)["demo_footprint_clipped"]
    assert flag["verdict"] == "WARN" and "artefact" in flag["detail"] and res["overall"] == "WARN"

def test_unclipped_demo_footprint_is_not_flagged():
    res = run(FakeConn(GOOD_RULES), floors=2, cost_per_sqm=30000)
    assert "demo_footprint_clipped" not in by(res)

def test_a_footprint_sent_by_the_user_is_never_flagged_as_clipped():
    from shapely.geometry import mapping
    from shapely.ops import transform as shp_transform
    gj = mapping(shp_transform(TO_LL.transform, HOUSE))
    res = run(FakeConn(GOOD_RULES), floors=2, cost_per_sqm=30000, footprint=gj)
    assert "demo_footprint_clipped" not in by(res) and res["overall"] == "PASS"


# ---- Table 6 (coverage / FSI by category), the additional-fee tier, and Rule 50 (small plots) ----
def table6_rules():
    cov = lambda cat, v: rule("max_plot_coverage_pct", v, use_group="A1", category=cat, clause_ref="Rule 27", table_ref="Table 6")
    far = lambda cat, v: rule("max_far", v, use_group="A1", category=cat, clause_ref="Rule 27", table_ref="Table 6")
    fee = lambda cat, v: rule("max_far_with_fee", v, use_group="A1", category=cat, clause_ref="Rule 27", table_ref="Table 6")
    rate = rule("far_extra_fee_per_sqm", 5000, clause_ref="Rule 27", table_ref="Table 6")
    base = [r for r in GOOD_RULES if r["param"] not in ("max_plot_coverage_pct", "max_far")]
    return base + [cov("I", 65), cov("II", 60), far("I", 3), far("II", 2.5), fee("I", 4), rate]

def test_category_picks_the_matching_row_and_no_category_uses_the_stricter():
    conn = FakeConn(table6_rules())
    for cat, expected in (("I", 65.0), ("II", 60.0)):
        chk = by(run(conn, floors=1, category=cat))["plot_coverage"]
        assert chk["required"] == expected and chk["rules_used"][0]["category"] == cat
    chk = by(run(conn, floors=1))["plot_coverage"]                       # category not given
    assert chk["required"] == 60.0
    assert any("Category not given" in w for w in chk["warnings"])

def test_fsi_free_tier_fee_tier_and_fail():
    plot = 600.0
    def fsi(floor_area, cat="I"):
        return by(run(FakeConn(table6_rules()), floors=1, floor_area_sqm=floor_area, category=cat))["floor_area_ratio"]
    ok = fsi(1700)                                  # FSI 2.83 <= 3
    assert ok["verdict"] == "PASS"
    paid = fsi(2100)                                # FSI 3.5: above 3, within 4 -> allowed with the fee
    assert paid["verdict"] == "WARN" and paid["with_fee_limit"] == 4.0
    assert paid["additional_area_sqm"] == pytest.approx((3.5 - 3.0) * 600, abs=2)
    assert paid["additional_fee_inr"] == pytest.approx(paid["additional_area_sqm"] * 5000, rel=1e-6)
    over = fsi(2700)                                # FSI 4.5: above both
    assert over["verdict"] == "FAIL"
    no_tier = fsi(1700, cat="II")                   # Category II has no with-fee row; 2.83 > 2.5
    assert no_tier["verdict"] == "FAIL" and "additional_fee_inr" not in no_tier

def test_small_plot_rule_exempts_coverage_and_fsi_and_limits_floors_and_height():
    small = [r for r in GOOD_RULES if r["param"] not in ("max_plot_coverage_pct", "max_far")] + [
        rule("exempt_coverage_far", 1, clause_ref="Rule 50", table_ref=None, use_group="A1", plot_max_sqm=1000),
        rule("max_floors", 3, clause_ref="Rule 50", table_ref=None, use_group="A1", plot_max_sqm=1000),
        rule("max_height_m", 10, clause_ref="Rule 50", table_ref=None, use_group="A1", plot_max_sqm=1000),
    ]
    res = run(FakeConn(small), floors=4, height_m=13, cost_per_sqm=30000)   # plot is 600 sq m -> "small" here
    c = by(res)
    assert c["plot_coverage"]["verdict"] == "INFO" and c["floor_area_ratio"]["verdict"] == "INFO"
    assert "Not applicable" in c["plot_coverage"]["detail"] and c["plot_coverage"]["clauses"][0]["clause_ref"] == "Rule 50"
    assert c["number_of_floors"]["verdict"] == "FAIL" and c["number_of_floors"]["required"] == 3.0
    assert c["building_height"]["verdict"] == "FAIL" and c["building_height"]["required"] == 10.0
    ok = by(run(FakeConn(small), floors=3, height_m=9, cost_per_sqm=30000))
    assert ok["number_of_floors"]["verdict"] == "PASS" and ok["building_height"]["verdict"] == "PASS"

def test_floor_and_height_checks_are_absent_when_no_rule_applies():
    c = by(run(FakeConn(GOOD_RULES), floors=2, cost_per_sqm=30000))
    assert "number_of_floors" not in c and "building_height" not in c


def test_category_comes_from_the_parcel_record_and_the_request_overrides_it():
    conn = FakeConn(table6_rules())
    conn.parcel_category = "II"
    res = run(conn, floors=1)                                    # no category in the request
    assert by(res)["plot_coverage"]["required"] == 60.0 and res["inputs"]["category"] == "II"
    assert any("parcel record" in a for a in res["assumptions"])
    res = run(conn, floors=1, category="I")                      # request wins
    assert by(res)["plot_coverage"]["required"] == 65.0 and res["inputs"]["category"] == "I"
    conn2 = FakeConn(table6_rules())                             # nothing set anywhere
    res = run(conn2, floors=1)
    assert res["inputs"]["category"] is None and any("not set" in a for a in res["assumptions"])
    assert any("Category not given" in w for w in by(res)["plot_coverage"]["warnings"])

def test_a_failing_setback_shows_its_proviso():
    prov = "any one yard other than the front yard can be reduced to 0.5 m if there is no opening on that side."
    rules = [r for r in GOOD_RULES if r["param"] != "front_setback_min"] + [rule("front_setback_min", 6, proviso=prov)]
    chk = by(run(FakeConn(rules)))["front_setback"]                # measured 4.09 < 6 -> FAIL
    assert chk["verdict"] == "FAIL" and chk["proviso"] == prov
    assert any("proviso" in w for w in chk["warnings"])
    ok = by(run(FakeConn(GOOD_RULES)))["front_setback"]            # passes: no proviso shown
    assert ok["verdict"] == "PASS" and "proviso" not in ok


def test_municipality_kmbr_flow():
    kmbr_rules = [
        rule("front_setback_min", 3, doc_code="KMBR", clause_ref="Rule 26", table_ref="Table 4"),
        rule("rear_setback_min", 1.5, doc_code="KMBR", clause_ref="Rule 26", table_ref="Table 4"),
        rule("side_setback_min", 1, doc_code="KMBR", clause_ref="Rule 26", table_ref="Table 4"),
        rule("max_plot_coverage_pct", 65, doc_code="KMBR", clause_ref="Rule 27", table_ref="Table 6", unit="percent"),
        rule("max_far", 3.0, doc_code="KMBR", clause_ref="Rule 27", table_ref="Table 6", unit="ratio"),
    ]
    conn = FakeConn(kmbr_rules)
    conn.local_body_type = "municipality"
    res = run(conn, floors=2, cost_per_sqm=30000)
    assert res["parcel"]["local_body_type"] == "municipality"
    assert res["parcel"]["rulebooks"] == ["KMBR"]
    assert any("Attingal Municipality: Kerala Municipality Building Rules (KMBR) apply" in a for a in res["assumptions"])
    c = by(res)
    assert c["front_setback"]["verdict"] == "PASS" and c["front_setback"]["required"] == 3.0
    assert c["rear_setback"]["verdict"] == "PASS" and c["rear_setback"]["required"] == 1.5
    assert c["side_setback"]["verdict"] == "PASS" and c["side_setback"]["required"] == 1.0
    assert c["plot_coverage"]["verdict"] == "PASS" and c["plot_coverage"]["required"] == 65.0
    assert c["floor_area_ratio"]["verdict"] == "PASS" and c["floor_area_ratio"]["required"] == 3.0