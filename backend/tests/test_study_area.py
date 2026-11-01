"""Tests for GeoRAG+ Study Area GIS & GeoJSON Endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_study_area_summary():
    response = client.get("/study-area/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "study_area" in data
    assert data["study_area"]["village"] == "Attingal"
    assert data["study_area"]["local_body_type"] == "municipality"
    table_names = [item["table"] for item in data["summary"]]
    assert "cadastral_parcels" in table_names
    assert "roads" in table_names


def test_parcels_geojson():
    response = client.get("/study-area/parcels-geojson")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert data["total_features"] == 534
    assert len(data["features"]) == 534

    # Validate first feature structure
    f0 = data["features"][0]
    assert f0["type"] == "Feature"
    assert "geometry" in f0
    assert f0["geometry"]["type"] in ("Polygon", "MultiPolygon")
    props = f0["properties"]
    assert "parcel_id" in props
    assert "survey_no" in props
    assert "area_sqm" in props
    assert "compliance_status" in props
    assert props["compliance_status"] in ("PASS", "WARN", "FAIL")


def test_parcels_geojson_filter():
    response_fail = client.get("/study-area/parcels-geojson?status_filter=FAIL")
    assert response_fail.status_code == 200
    data_fail = response_fail.json()
    assert data_fail["total_features"] > 0
    for f in data_fail["features"]:
        assert f["properties"]["compliance_status"] == "FAIL"

    response_pass = client.get("/study-area/parcels-geojson?status_filter=PASS")
    assert response_pass.status_code == 200
    data_pass = response_pass.json()
    assert data_pass["total_features"] > 0
    for f in data_pass["features"]:
        assert f["properties"]["compliance_status"] == "PASS"


def test_layers_geojson():
    response = client.get("/study-area/layers-geojson")
    assert response.status_code == 200
    data = response.json()
    assert "roads" in data
    assert "paddy_data_bank" in data
    assert "utility_assets" in data
    assert "buildings" in data
    assert data["roads"]["type"] == "FeatureCollection"
    assert len(data["roads"]["features"]) > 0
    assert len(data["utility_assets"]["features"]) > 0
    assert len(data["buildings"]["features"]) > 0


def test_parcels_search():
    response = client.get("/study-area/parcels?q=1")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) > 0
    assert any(item["parcel_id"] == 1 for item in items)
