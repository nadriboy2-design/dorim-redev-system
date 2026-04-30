# dorim-redev-system/backend/tests/test_workflow.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_workflow_status_returns_current_stage():
    resp = client.get("/api/workflow/status")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["current_stage"] == "STAGE_1_PRELIMINARY"
    assert data["stage_name"] == "정비구역 입안 (사전검토)"
    assert data["consent_threshold"] == 0.40
    assert isinstance(data["required_docs"], list)
    assert len(data["required_docs"]) > 0


def test_workflow_status_includes_consent_progress():
    resp = client.get("/api/workflow/status")
    data = resp.json()["data"]
    assert "consent_rate" in data
    assert "is_threshold_met" in data


def test_compliance_far_over_limit():
    """용적률 700% 초과 시 422 반환"""
    resp = client.post("/api/compliance/check-far", json={"far_pct": 750.0})
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "HARD_LOCK_A"


def test_compliance_far_at_limit_passes():
    resp = client.post("/api/compliance/check-far", json={"far_pct": 700.0})
    assert resp.status_code == 200


def test_generate_doc_blocked_before_association():
    """조합설립 전 시공사 입찰공고 차단"""
    resp = client.post(
        "/api/workflow/generate-doc",
        json={"doc_type": "시공사입찰공고", "has_cost_verification": False},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "HARD_LOCK_B"
