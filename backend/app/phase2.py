"""GeoRAG+ Phase 2: pre-construction checks before a building permit application.

Location in repo: backend/app/phase2.py

Checks: building inside plot, front/rear/side setbacks, plot coverage, floor area ratio,
distance to road centre, special zones (CRZ / railway / airport, if data is loaded),
utility distances, construction workers welfare cess.

Rule: every number is computed here, in shapely or in PostGIS. Required values come from the
rule_params table (typed from the PDFs), and each result quotes the exact clause it used.
The LLM never calculates and never invents a clause.
"""
import json
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from shapely.geometry import shape as shp_shape
from sqlalchemy import text

from . import phase2_geom as geom
from .db import engine
from .phase1 import _rate
from .rag import clause_text, docs_for

router = APIRouter(prefix="/phase2", tags=["phase2"])

TOL = 0.005                    # numeric slack when comparing (metres / percent)
MAX_ROAD_DIST_M = 300.0        # a road further than this is ignored for front/rear detection
DEFAULT_FLOOR_HEIGHT_M = 3.0   # ASSUMPTION used only when no height is given
REQUIRED_PARAMS = [
    "front_setback_min", "rear_setback_min", "side_setback_min",
    "max_plot_coverage_pct", "max_far", "road_centre_min",
]


class Phase2Request(BaseModel):
    footprint: dict | None = Field(
        None, description="GeoJSON Polygon (lon/lat) of the proposed building. Omit = demo mode: use the OSM building inside the parcel."
    )
    floors: int = Field(1, ge=1, le=30)
    height_m: float | None = Field(None, gt=0, description="Building height in metres. Default: 3 m per floor (assumption).")
    use_group: str = Field("A1", description="Occupancy group. A1 = residential.")
    category: Literal["I", "II"] | None = Field(
        None, description="Category used in KPBR Table 6 (coverage / FSI). Omit = the stricter of both is used.")
    floor_area_sqm: float | None = Field(None, gt=0, description="Total built-up area. Default: footprint x floors.")
    estimated_cost: float | None = Field(None, gt=0, description="Estimated construction cost in INR.")
    cost_per_sqm: float | None = Field(None, gt=0, description="INR per sq m (used if estimated_cost is not given).")


# --- helpers -----------------------------------------------------------------
def _rules(conn, docs, param, ctx):
    """Rule rows that apply to this case. Only the most specific rows are kept."""
    rows = conn.execute(
        text("""
            SELECT id, doc_code, clause_ref, table_ref, category, proviso, value, unit, verified,
                   (use_group IS NOT NULL)::int
                 + (height_min_m IS NOT NULL OR height_max_m IS NOT NULL)::int
                 + (plot_min_sqm IS NOT NULL OR plot_max_sqm IS NOT NULL)::int
                 + (builtup_min_sqm IS NOT NULL OR builtup_max_sqm IS NOT NULL)::int
                 + (category IS NOT NULL)::int
                 + (road_class IS NOT NULL)::int AS specificity
            FROM rule_params
            WHERE doc_code = ANY(:docs) AND param = :param
              AND (use_group IS NULL OR use_group = CAST(:ug AS text))
              AND (height_min_m IS NULL OR CAST(:h AS numeric) >  height_min_m)
              AND (height_max_m IS NULL OR CAST(:h AS numeric) <= height_max_m)
              AND (plot_min_sqm IS NULL OR CAST(:a AS numeric) >  plot_min_sqm)
              AND (plot_max_sqm IS NULL OR CAST(:a AS numeric) <= plot_max_sqm)
              AND (builtup_min_sqm IS NULL OR CAST(:b AS numeric) >  builtup_min_sqm)
              AND (builtup_max_sqm IS NULL OR CAST(:b AS numeric) <= builtup_max_sqm)
              AND (CAST(:cat AS text) IS NULL OR category IS NULL OR category = CAST(:cat AS text))
              AND (road_class IS NULL OR road_class = CAST(:rc AS text))
        """),
        {"docs": list(docs), "param": param, "ug": ctx["use_group"], "h": ctx["height"],
         "a": ctx["plot_area"], "b": ctx["builtup"], "cat": ctx.get("category"), "rc": ctx.get("road_class")},
    ).mappings().all()
    if not rows:
        return []
    best = max(r["specificity"] for r in rows)
    return [r for r in rows if r["specificity"] == best]


def _rule_check(conn, name, param, measured, kind, unit, docs, ctx):
    """Compare one measured value with the rule table. kind: 'min' (at least) or 'max' (at most)."""
    chk = {
        "check": name, "param": param, "unit": unit, "kind": kind,
        "measured": None if measured is None else round(float(measured), 2),
        "required": None, "verdict": "WARN", "detail": "", "rules_used": [], "clauses": [], "warnings": [],
    }
    if measured is None:
        chk["detail"] = "Could not be measured (no road nearby, or no plot edge on that side)."
        return chk
    rules = _rules(conn, docs, param, ctx)
    if not rules:
        chk["detail"] = (f"No row for '{param}' in rule_params matches this use group, height and plot size. "
                         "Add it from the PDF (data/rule_params.csv).")
        return chk

    values = [Decimal(r["value"]) for r in rules]
    required = float(max(values) if kind == "min" else min(values))   # strictest if several rows match
    ok = (measured >= required - TOL) if kind == "min" else (measured <= required + TOL)
    chk["required"] = required
    chk["verdict"] = "PASS" if ok else "FAIL"
    word = "at least" if kind == "min" else "at most"
    chk["detail"] = f"Measured {chk['measured']} {unit}; the rule requires {word} {required:g} {unit}."
    if not ok:
        provisos = [r.get("proviso") for r in rules if r.get("proviso")]
        if provisos:
            chk["proviso"] = provisos[0]
            chk["warnings"].append("A proviso may relax this rule (see 'proviso'). The engine does not apply it.")
    chk["rules_used"] = [{"doc_code": r["doc_code"], "clause_ref": r["clause_ref"],
                          "table_ref": r["table_ref"], "category": r.get("category"),
                          "value": float(r["value"]), "verified": bool(r["verified"])} for r in rules]
    if ctx.get("category") is None and len({r.get("category") for r in rules if r.get("category")}) > 1:
        chk["warnings"].append("Category not given: the stricter of Category I and II was used.")
    if len(rules) > 1:
        chk["warnings"].append(f"{len(rules)} rule rows matched; the strictest value was used.")
    if not all(r["verified"] for r in rules):
        chk["warnings"].append("Rule value not yet marked verified against the PDF.")
    try:   # cite the exact clause the number came from
        first = rules[0]
        chk["clauses"] = clause_text(first["doc_code"], first["clause_ref"], limit=1, contains=first.get("table_ref"))
    except Exception as exc:  # noqa: BLE001
        chk["clauses_error"] = f"{type(exc).__name__}: {exc}"
    return chk


def _optional_rule_check(conn, name, param, measured, kind, unit, docs, ctx):
    """Like _rule_check, but silent (None) when no rule row applies: for rules that exist only for some plots."""
    if not _rules(conn, docs, param, ctx):
        return None
    return _rule_check(conn, name, param, measured, kind, unit, docs, ctx)


def _far_check(conn, far, plot_area, docs, ctx):
    """Floor space index with the Table 6 'additional fee' tier.
    Within the free limit = PASS. Above it but within the with-fee limit = WARN with a fee estimate.
    Above both (or no with-fee limit exists) = FAIL."""
    chk = _rule_check(conn, "floor_area_ratio", "max_far", far, "max", "ratio", docs, ctx)
    if chk["verdict"] != "FAIL":
        return chk
    tier = _rules(conn, docs, "max_far_with_fee", ctx)
    if not tier:
        return chk
    limit = float(min(Decimal(r["value"]) for r in tier))          # strictest if several rows match
    if far > limit + TOL:
        chk["detail"] += f" Even with the additional fee the limit is {limit:g}."
        return chk
    free = chk["required"]
    extra_area = (far - free) * plot_area
    rate_rows = _rules(conn, docs, "far_extra_fee_per_sqm", ctx)
    fee = extra_area * float(rate_rows[0]["value"]) if rate_rows else None
    chk["verdict"] = "WARN"
    chk["with_fee_limit"] = limit
    chk["additional_area_sqm"] = round(extra_area, 1)
    chk["additional_fee_inr"] = None if fee is None else round(fee, 2)
    chk["detail"] = (f"FSI {chk['measured']:g} is above the free limit {free:g} but within {limit:g} if the additional "
                     f"fee is paid for the extra {extra_area:.1f} sq m" + (f" (about Rs {fee:,.0f})." if fee is not None else "."))
    if rate_rows and not all(r["verified"] for r in rate_rows):
        chk["warnings"].append("Additional-fee rate not yet marked verified against the PDF.")
    return chk


def _info(name, detail, **extra):
    return {"check": name, "verdict": "INFO", "detail": detail, "clauses": [], **extra}


def _audit(conn, parcel_id, chk):
    skip = ("detail", "clauses", "verdict", "warnings")
    conn.execute(
        text("""
            INSERT INTO audit_log (phase, parcel_id, check_name, verdict, inputs, cited_clauses, details)
            VALUES (2, :pid, :name, :verdict, CAST(:inputs AS jsonb), CAST(:clauses AS jsonb), :details)
        """),
        {"pid": parcel_id, "name": chk["check"], "verdict": chk["verdict"],
         "inputs": json.dumps({k: v for k, v in chk.items() if k not in skip}, default=str),
         "clauses": json.dumps(chk.get("clauses", []), default=str), "details": chk.get("detail")},
    )


# --- the engine --------------------------------------------------------------
def run_phase2(parcel_id: int, req: Phase2Request) -> dict:
    assumptions = ["Distances use projected metres (UTM 43N). Corner plots are simplified to one road."]
    orig_area = None   # demo mode only: full area of the OSM building before it is cut at the plot boundary

    with engine.begin() as conn:
        parcel = conn.execute(
            text("""
                SELECT parcel_id, survey_no, local_body_type, panchayat_category,
                       elevation_min_m, elevation_max_m, avg_slope_pct, has_retaining_wall,
                       ST_AsText(geom) AS wkt
                FROM cadastral_parcels WHERE parcel_id = :p
            """), {"p": parcel_id}
        ).mappings().first()
        if parcel is None:
            raise HTTPException(404, "parcel not found")
        docs = docs_for(parcel["local_body_type"] or "municipality")

        # Table 6 category: only relevant for panchayats (KPBR Rule 3(5)). KMBR applies uniformly.
        if (parcel["local_body_type"] or "").lower() == "municipality":
            category = req.category or None
            assumptions.append("Attingal Municipality: Kerala Municipality Building Rules (KMBR) apply.")
        else:
            category = req.category or parcel["panchayat_category"]
            if req.category:
                assumptions.append(f"Table 6 category {req.category} was given in the request.")
            elif category:
                assumptions.append(f"Table 6 category {category} comes from the parcel record (Rule 3(5): set by Government notification).")
            else:
                assumptions.append("Panchayat category is not set: Table 6 uses the stricter of Category I and II.")

        # 1) the proposed building
        if req.footprint:
            try:
                fp = shp_shape(req.footprint)
            except Exception:  # noqa: BLE001
                raise HTTPException(422, "footprint must be a GeoJSON Polygon in lon/lat")
            if fp.geom_type != "Polygon":
                raise HTTPException(422, "footprint must be a GeoJSON Polygon")
            fp_wkt = fp.wkt
        else:
            row = conn.execute(
                text("""
                    SELECT ST_AsText(ST_CollectionExtract(ST_MakeValid(ST_Intersection(b.geom, p.geom)), 3)) AS wkt,
                           ST_Area(b.geom::geography) AS orig_area_sqm
                    FROM study_area_buildings b, cadastral_parcels p
                    WHERE p.parcel_id = :p AND ST_Intersects(b.geom, p.geom)
                    ORDER BY ST_Area(ST_Intersection(b.geom, p.geom)) DESC LIMIT 1
                """), {"p": parcel_id}
            ).mappings().first()
            if not row or not row["wkt"]:
                raise HTTPException(404, "no building found inside this parcel: send a footprint")
            fp_wkt, orig_area = row["wkt"], row["orig_area_sqm"]
            assumptions.append("Demo mode: the footprint is the OSM building inside the parcel, clipped to the parcel.")

        # 2) the nearest road
        road = conn.execute(
            text("""
                SELECT r.road_id, r.name, r.road_class, ST_AsText(r.geom) AS wkt,
                       ST_Distance(r.geom::geography, p.geom::geography) AS dist_m
                FROM roads r, cadastral_parcels p WHERE p.parcel_id = :p
                ORDER BY r.geom <-> p.geom LIMIT 1
            """), {"p": parcel_id}
        ).mappings().first()
        road_m, road_class = None, None
        if road and road["dist_m"] is not None and road["dist_m"] <= MAX_ROAD_DIST_M:
            road_m = geom.from_wkt_metres(road["wkt"])
            road_class = road["road_class"]
            assumptions.append("Road class comes from OSM tags and defaults to 'Local'; check it for NH/SH roads.")
        else:
            assumptions.append(f"No road within {MAX_ROAD_DIST_M:.0f} m: front and rear cannot be told apart.")

        # 3) measurements
        parcel_m = geom.from_wkt_metres(parcel["wkt"])
        bldg_m = geom.from_wkt_metres(fp_wkt)
        m = geom.measure(parcel_m, bldg_m, road_m)

        if req.height_m:
            height = req.height_m
        else:
            height = req.floors * DEFAULT_FLOOR_HEIGHT_M
            assumptions.append(f"Height not given: assumed {DEFAULT_FLOOR_HEIGHT_M:g} m per floor = {height:g} m.")
        cf = geom.coverage_and_far(m["plot_area_sqm"], m["footprint_area_sqm"], req.floors, req.floor_area_sqm)
        if not req.floor_area_sqm:
            assumptions.append("Total floor area not given: assumed footprint x number of floors.")
        ctx = {"use_group": req.use_group, "height": height, "plot_area": m["plot_area_sqm"],
               "builtup": cf["total_floor_area_sqm"], "road_class": road_class, "category": category}

        checks = [{
            "check": "building_inside_plot",
            "verdict": "PASS" if m["inside_plot"] else "FAIL",
            "detail": "Building lies inside the plot." if m["inside_plot"]
                      else "Part of the building lies outside the plot boundary.",
            "clauses": [],
        }]
        if orig_area and m["footprint_area_sqm"] < orig_area * 0.98:
            cut = (1 - m["footprint_area_sqm"] / orig_area) * 100
            checks.append({
                "check": "demo_footprint_clipped", "verdict": "WARN", "clauses": [],
                "detail": (f"{cut:.0f}% of the OSM building lies outside this mock plot, so the footprint was cut at "
                           "the plot boundary. A side or rear distance of 0 m is then probably an artefact of the mock "
                           "plot shape, not a real violation. Try a plot where the whole building lies inside, or send your own footprint."),
            })
        checks += [
            _rule_check(conn, "front_setback", "front_setback_min", m["front_m"], "min", "m", docs, ctx),
            _rule_check(conn, "rear_setback", "rear_setback_min", m["rear_m"], "min", "m", docs, ctx),
            _rule_check(conn, "side_setback", "side_setback_min", m["side_min_m"], "min", "m", docs, ctx),
            _rule_check(conn, "distance_to_road_centre", "road_centre_min",
                        bldg_m.distance(road_m) if road_m is not None else None, "min", "m", docs, ctx),
        ]

        # coverage and FSI: some plots are exempt (KPBR Rule 50(3): plots up to 125 sq m)
        exempt = _rules(conn, docs, "exempt_coverage_far", ctx)
        if exempt:
            ex = exempt[0]
            try:
                ex_clause = clause_text(ex["doc_code"], ex["clause_ref"], limit=1)
            except Exception:  # noqa: BLE001
                ex_clause = []
            for name in ("plot_coverage", "floor_area_ratio"):
                checks.append({"check": name, "verdict": "INFO", "clauses": ex_clause,
                               "detail": f"Not applicable: {ex['clause_ref']} exempts this kind of plot from the "
                                         "coverage and floor space index limits (see the cited clause).",
                               "rules_used": [{"doc_code": ex["doc_code"], "clause_ref": ex["clause_ref"],
                                               "verified": bool(ex["verified"])}]})
        else:
            checks.append(_rule_check(conn, "plot_coverage", "max_plot_coverage_pct", cf["coverage_pct"],
                                      "max", "percent", docs, ctx))
            checks.append(_far_check(conn, cf["far"], m["plot_area_sqm"], docs, ctx))

        # limits that exist only for some plots (e.g. small plots: at most 3 floors and 10 m high)
        for name, param, value, unit in (("number_of_floors", "max_floors", req.floors, "floors"),
                                         ("building_height", "max_height_m", height, "m")):
            extra = _optional_rule_check(conn, name, param, value, "max", unit, docs, ctx)
            if extra:
                checks.append(extra)

        # 4) special zones (CRZ / railway / airport ...) from restricted_zones
        ewkt = "SRID=4326;" + fp_wkt
        zones = conn.execute(
            text("SELECT zone_type, min(ST_Distance(geom::geography, ST_GeogFromText(:g))) AS d "
                 "FROM restricted_zones GROUP BY zone_type"), {"g": ewkt}
        ).mappings().all()
        if not zones:
            checks.append(_info("restricted_zones",
                                "No CRZ / railway / airport layers are loaded for this area, so those checks were not run."))
        for z in zones:
            checks.append(_rule_check(conn, f"distance_to_{z['zone_type']}", f"min_distance_{z['zone_type']}",
                                      z["d"], "min", "m", docs, ctx))

        # 5) utilities (distances for information; HT-line clearance only if a rule row exists)
        util = {r["asset_type"]: r["d"] for r in conn.execute(
            text("SELECT asset_type, min(ST_Distance(geom::geography, ST_GeogFromText(:g))) AS d "
                 "FROM utility_assets GROUP BY asset_type"), {"g": ewkt}).mappings()}
        for asset, label in (("Transformer", "nearest_kseb_transformer"),
                             ("KSEB_HT_Line", "nearest_kseb_ht_line"), ("KWA_Main", "nearest_kwa_main")):
            d = util.get(asset)
            if d is None:
                checks.append(_info(label, f"No {asset} data loaded for this area."))
                continue
            if asset == "KSEB_HT_Line" and _rules(conn, docs, "min_distance_KSEB_HT_Line", ctx):
                checks.append(_rule_check(conn, label, "min_distance_KSEB_HT_Line", d, "min", "m", docs, ctx))
            else:
                checks.append(_info(label, f"{asset} is {d:.0f} m from the building.", distance_m=round(d, 1)))

        # 6) construction workers welfare cess
        pct, v1 = _rate(conn, "bocw_cess_pct")
        threshold, v2 = _rate(conn, "bocw_cess_threshold_sqm")
        area = cf["total_floor_area_sqm"]
        cost = req.estimated_cost or (req.cost_per_sqm * area if req.cost_per_sqm else None)
        cess_warn = [] if (v1 and v2) else ["Cess rate and threshold are unverified placeholders."]
        if area <= float(threshold):
            checks.append(_info("construction_cess", f"Built-up area {area:.1f} sq m is not above {float(threshold):g} sq m: no cess.",
                                cess=0.0, warnings=cess_warn))
        elif cost is None:
            checks.append({"check": "construction_cess", "verdict": "WARN", "clauses": [], "warnings": cess_warn,
                           "detail": "Cess applies (area above the threshold). Send estimated_cost or cost_per_sqm to compute it."})
        else:
            checks.append(_info("construction_cess",
                                f"{float(pct):g}% of Rs {cost:,.0f} = Rs {cost * float(pct) / 100:,.2f}.",
                                cess=round(cost * float(pct) / 100, 2), cost_basis=round(cost, 2), warnings=cess_warn))

        # 7) terrain slope & ground stabilization check (KMBR Rule 26(4) / KPBR Rule 26)
        slope_pct = float(parcel.get("avg_slope_pct") or 4.5)
        has_rw = bool(parcel.get("has_retaining_wall"))
        elev_min = float(parcel.get("elevation_min_m") or 18.0)
        elev_max = float(parcel.get("elevation_max_m") or 22.0)

        slope_chk = {
            "check": "terrain_slope",
            "verdict": "PASS",
            "slope_pct": slope_pct,
            "elevation_range_m": [elev_min, elev_max],
            "has_retaining_wall": has_rw,
            "detail": f"Average natural slope is {slope_pct:.1f}%. Permissible without special stabilization (<= 20% / 1:5 slope).",
            "clauses": [],
            "warnings": [],
        }

        try:
            slope_chk["clauses"] = clause_text(docs[0], "Rule 26", limit=1, contains="slope")
        except Exception:
            pass

        if slope_pct > 20.0:
            if has_rw:
                slope_chk["verdict"] = "WARN"
                slope_chk["detail"] = (
                    f"Steep terrain slope ({slope_pct:.1f}% > 20% / 1:5 gradient limit under KMBR Rule 26(4)). "
                    "Certified retaining wall / ground stabilization certificate recorded."
                )
            else:
                slope_chk["verdict"] = "FAIL"
                slope_chk["detail"] = (
                    f"Steep terrain slope ({slope_pct:.1f}% > 20% / 1:5 gradient limit under KMBR Rule 26(4)). "
                    "Mandatory retaining wall, terracing, and geo-technical ground stability clearance required before permit approval."
                )
        checks.append(slope_chk)

        for c in checks:
            _audit(conn, parcel_id, c)

    verdicts = {c["verdict"] for c in checks}
    overall = "FAIL" if "FAIL" in verdicts else ("WARN" if "WARN" in verdicts else "PASS")
    return {
        "parcel": {"parcel_id": parcel_id, "survey_no": parcel["survey_no"], "local_body_type": parcel["local_body_type"],
                   "rulebooks": docs},
        "overall": overall,
        "inputs": {"floors": req.floors, "height_m": height, "use_group": req.use_group, "category": category,
                   "road": None if not road_m else {"name": road["name"], "class": road_class,
                                                    "distance_to_plot_m": round(road["dist_m"], 1)}},
        "measurements": {
            "plot_area_sqm": round(m["plot_area_sqm"], 1), "footprint_area_sqm": round(m["footprint_area_sqm"], 1),
            "front_m": m["front_m"], "rear_m": m["rear_m"], "side_min_m": m["side_min_m"],
            "coverage_pct": None if cf["coverage_pct"] is None else round(cf["coverage_pct"], 2),
            "far": None if cf["far"] is None else round(cf["far"], 3),
            "total_floor_area_sqm": round(cf["total_floor_area_sqm"], 1),
            "edge_counts": m["edge_counts"],
            "avg_slope_pct": slope_pct,
            "elevation_range_m": [elev_min, elev_max],
            "has_retaining_wall": has_rw,
        },
        "checks": checks,
        "assumptions": assumptions,
        "note": "Prototype on synthetic parcels. Not legal advice.",
    }


# --- endpoints (static routes first so '/rules/status' is not read as a parcel id) -----
@router.get("/rules/status")
def rules_status():
    """Which rule values are loaded, and which required ones are still missing."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT doc_code, param, count(*) AS rows, sum(verified::int) AS verified_rows "
                 "FROM rule_params GROUP BY 1, 2 ORDER BY 1, 2")
        ).mappings().all()
    have = {(r["doc_code"], r["param"]) for r in rows}
    return {
        "loaded": [dict(r) for r in rows],
        "missing_params": {d: [p for p in REQUIRED_PARAMS if (d, p) not in have] for d in ("KPBR", "KMBR")},
    }


@router.post("/{parcel_id}")
def phase2_post(parcel_id: int, req: Phase2Request):
    """Full control: send your own footprint (GeoJSON polygon), floors, height, cost ..."""
    return run_phase2(parcel_id, req)


@router.get("/{parcel_id}")
def phase2_get(
    parcel_id: int,
    floors: int = Query(1, ge=1, le=30),
    height_m: float | None = Query(None, gt=0),
    use_group: str = "A1",
    category: Literal["I", "II"] | None = None,
    floor_area_sqm: float | None = Query(None, gt=0),
    estimated_cost: float | None = Query(None, gt=0),
    cost_per_sqm: float | None = Query(None, gt=0),
):
    """Quick demo: uses the OSM building inside the parcel as the proposed building."""
    return run_phase2(parcel_id, Phase2Request(
        floors=floors, height_m=height_m, use_group=use_group, category=category,
        floor_area_sqm=floor_area_sqm, estimated_cost=estimated_cost, cost_per_sqm=cost_per_sqm))