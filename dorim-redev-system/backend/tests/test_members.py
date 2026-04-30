# dorim-redev-system/backend/tests/test_members.py
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_members_returns_list():
    resp = client.get("/api/members")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 20

def test_get_members_has_required_fields():
    resp = client.get("/api/members")
    member = resp.json()["data"][0]
    for field in ["member_id", "address", "birth_date", "is_sale_target",
                  "rights_value", "consent"]:
        assert field in member

def test_patch_consent_toggles_value():
    resp = client.get("/api/members")
    member = resp.json()["data"][0]
    original = member["consent"]
    mid = member["member_id"]
    resp2 = client.patch(f"/api/members/{mid}/consent",
                         json={"consent": not original})
    assert resp2.status_code == 200
    resp3 = client.get("/api/members")
    updated = next(m for m in resp3.json()["data"] if m["member_id"] == mid)
    assert updated["consent"] != original

def test_patch_consent_unknown_member_returns_404():
    resp = client.patch("/api/members/99999/consent", json={"consent": True})
    assert resp.status_code == 404

def test_get_consent_rate_returns_stats():
    resp = client.get("/api/consent-rate")
    data = resp.json()["data"]
    assert "total" in data
    assert "consented" in data
    assert "rate" in data
    assert 0 <= data["rate"] <= 100
