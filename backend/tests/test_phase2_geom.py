"""Tests for app/phase2_geom.py.   Location in repo: backend/tests/test_phase2_geom.py
Run from backend/ (venv active):   python -m pytest tests -q
"""
import pytest
from shapely.geometry import LineString, Polygon

from app import phase2_geom as g

# A 20 m x 30 m plot with the corner at (0, 0); a 10 m x 10 m house in it.
PLOT = Polygon([(0, 0), (20, 0), (20, 30), (0, 30)])
HOUSE = Polygon([(5, 4), (15, 4), (15, 14), (5, 14)])      # 4 m from the bottom, 5 m from the sides


def test_road_below_plot():
    road = LineString([(-50, -5), (50, -5)])               # road runs along the bottom
    m = g.measure(PLOT, HOUSE, road)
    assert m["inside_plot"]
    assert m["front_m"] == pytest.approx(4.0)              # bottom edge = front
    assert m["rear_m"] == pytest.approx(16.0)              # top edge = rear (30 - 14)
    assert m["side_min_m"] == pytest.approx(5.0)           # left and right = 5 m
    assert m["edge_counts"] == {"front": 1, "rear": 1, "side": 2}


def test_road_on_the_right_swaps_the_roles():
    road = LineString([(25, -50), (25, 50)])               # road runs along the right side
    m = g.measure(PLOT, HOUSE, road)
    assert m["front_m"] == pytest.approx(5.0)              # right edge = front (20 - 15)
    assert m["rear_m"] == pytest.approx(5.0)               # left edge = rear
    assert m["side_min_m"] == pytest.approx(4.0)           # bottom 4 m, top 16 m -> closest is 4


def test_clockwise_polygon_gives_same_answer():
    cw = Polygon(list(reversed(list(PLOT.exterior.coords))))
    road = LineString([(-50, -5), (50, -5)])
    m = g.measure(cw, HOUSE, road)
    assert (m["front_m"], m["rear_m"], m["side_min_m"]) == (4.0, 16.0, 5.0)


def test_building_outside_plot_is_flagged():
    sticking_out = Polygon([(15, 4), (25, 4), (25, 14), (15, 14)])
    m = g.measure(PLOT, sticking_out, LineString([(-50, -5), (50, -5)]))
    assert m["inside_plot"] is False


def test_no_road_means_unknown_setbacks_not_a_guess():
    m = g.measure(PLOT, HOUSE, None)
    assert m["front_m"] is None and m["rear_m"] is None and m["side_min_m"] is None
    assert m["front_known"] is False and m["inside_plot"]


def test_many_tiny_edges_like_a_buffered_plot():
    plot = Polygon([(0, 0), (20, 0), (20, 30), (0, 30)]).buffer(3, quad_segs=16)   # rounded corners
    house = Polygon([(5, 4), (15, 4), (15, 14), (5, 14)])
    m = g.measure(plot, house, LineString([(-50, -10), (50, -10)]))
    assert m["front_m"] == pytest.approx(7.0, abs=0.1)     # plot now starts at y = -3
    assert m["rear_m"] == pytest.approx(19.0, abs=0.1)


def test_coverage_and_far():
    r = g.coverage_and_far(plot_area=600, footprint_area=100, floors=2)
    assert r["coverage_pct"] == pytest.approx(100 / 600 * 100)
    assert r["far"] == pytest.approx(200 / 600)
    r2 = g.coverage_and_far(600, 100, 2, floor_area=150)
    assert r2["far"] == pytest.approx(0.25)


def test_lonlat_to_metres_is_close_to_real_size():
    # about 20 m x 30 m near Attingal
    lon, lat = 76.815, 8.695
    poly = g.from_wkt_metres(
        f"POLYGON(({lon} {lat}, {lon + 0.000182} {lat}, {lon + 0.000182} {lat + 0.00027}, {lon} {lat + 0.00027}, {lon} {lat}))"
    )
    assert poly.area == pytest.approx(600, rel=0.03)