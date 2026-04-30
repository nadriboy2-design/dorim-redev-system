# dorim-redev-system/backend/tests/test_gis.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_gis_markers_returns_list():
    resp = client.get("/api/gis/markers")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0

def test_gis_markers_no_133_zone():
    """133-1 구역 좌표가 마커에 포함되지 않아야 한다."""
    resp = client.get("/api/gis/markers")
    markers = resp.json()["data"]
    for m in markers:
        lat, lng = m["lat"], m["lng"]
        in_excluded = (37.508 <= lat <= 37.512 and 126.895 <= lng <= 126.900)
        assert not in_excluded, f"133-1 구역 마커 발견: {m}"

def test_gis_markers_has_color():
    """마커는 consent 여부에 따라 색상이 달라야 한다."""
    resp = client.get("/api/gis/markers")
    markers = resp.json()["data"]
    for m in markers:
        assert m["color"] in ["#3b82f6", "#ef4444"]
        if m["consent"]:
            assert m["color"] == "#3b82f6"
        else:
            assert m["color"] == "#ef4444"

def test_gis_zone_polygon_returns_geojson():
    resp = client.get("/api/gis/zone-polygon")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["type"] == "Feature"
    assert data["geometry"]["type"] == "Polygon"
    assert data["properties"]["zone"] == "도림동 239-12"
