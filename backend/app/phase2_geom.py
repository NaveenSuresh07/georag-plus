"""GeoRAG+ Phase 2: pure geometry (no database, no LLM).

Location in repo: backend/app/phase2_geom.py

Everything is measured in METRES: lon/lat is projected to UTM zone 43N (EPSG:32643),
which covers Kerala with an error far below what the rules care about.

How "front / rear / side" is decided (a simple, explainable rule):
  1. Find the point ON THE ROAD closest to the plot centre.
  2. The "road direction" is the arrow from the plot centre to that point.
  3. Every boundary segment looks outward. If it faces within 45 degrees of the road
     direction it is FRONT, if it faces the opposite way it is REAR, otherwise SIDE.
Limits: corner plots (two roads) and very irregular plots are simplified to ONE road.
"""
from math import cos, hypot, radians

import numpy as np
import shapely
from pyproj import Transformer
from shapely import wkt as _wkt
from shapely.geometry import LineString, MultiLineString, MultiPolygon
from shapely.geometry.polygon import orient

_TO_METRES = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)

INSIDE_TOLERANCE_M = 0.05   # 5 cm slack when checking "building is inside the plot"


def to_metres(geom):
    def project(coords):
        x, y = _TO_METRES.transform(coords[:, 0], coords[:, 1])
        return np.column_stack([x, y])

    return shapely.transform(geom, project)      # needs shapely 2.x


def from_wkt_metres(wkt_text: str):
    return to_metres(_wkt.loads(wkt_text))


def largest_polygon(geom):
    if isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda p: p.area)
    return geom


def classify_edges(parcel, road, half_angle_deg: float = 45.0):
    """Split the plot boundary into front / rear / side segments. Returns None if undecidable."""
    plot = orient(largest_polygon(parcel), 1.0)          # outer ring counter-clockwise
    centre = plot.centroid
    # Closest point ON THE ROAD to the plot centre. (Using the closest point of the plot would be
    # arbitrary when the road runs parallel to a plot edge: every point of that edge ties.)
    target = road.interpolate(road.project(centre))
    vx, vy = target.x - centre.x, target.y - centre.y
    norm = hypot(vx, vy)
    if norm < 0.5:                                       # road passes through the plot centre: undecidable
        return None
    vx, vy = vx / norm, vy / norm

    threshold = cos(radians(half_angle_deg))
    edges = {"front": [], "rear": [], "side": []}
    pts = list(plot.exterior.coords)
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        length = hypot(dx, dy)
        if length < 0.05:
            continue
        nx, ny = dy / length, -dx / length               # outward normal of a CCW ring
        facing = nx * vx + ny * vy                       # 1 = faces the road, -1 = faces away
        key = "front" if facing >= threshold else ("rear" if facing <= -threshold else "side")
        edges[key].append(LineString([(x1, y1), (x2, y2)]))
    return edges


def measure(parcel, building, road):
    """Setbacks and areas for one building on one plot. All values in metres / square metres."""
    plot = largest_polygon(parcel)
    bldg = largest_polygon(building)
    result = {
        "inside_plot": bool(plot.buffer(INSIDE_TOLERANCE_M).contains(bldg)),
        "plot_area_sqm": plot.area,
        "footprint_area_sqm": bldg.area,
        "front_m": None,
        "rear_m": None,
        "side_min_m": None,
        "front_known": False,
        "edge_counts": None,
    }
    if road is None:
        return result
    edges = classify_edges(plot, road)
    if edges is None:
        return result

    def dist(lines):
        return round(bldg.distance(MultiLineString(lines)), 2) if lines else None

    result["front_m"] = dist(edges["front"])
    result["rear_m"] = dist(edges["rear"])
    result["side_min_m"] = dist(edges["side"])     # the closest of all side boundaries (conservative)
    result["front_known"] = True
    result["edge_counts"] = {k: len(v) for k, v in edges.items()}
    return result


def coverage_and_far(plot_area: float, footprint_area: float, floors: int, floor_area=None):
    """Plot coverage (%) and Floor Area Ratio. Total floor area defaults to footprint x floors."""
    total = floor_area if floor_area else footprint_area * floors
    return {
        "coverage_pct": footprint_area / plot_area * 100 if plot_area else None,
        "far": total / plot_area if plot_area else None,
        "total_floor_area_sqm": total,
    }