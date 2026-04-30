# dorim-redev-system/backend/routers/members.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.sync import sync_db

router = APIRouter(tags=["members"])


class ConsentUpdate(BaseModel):
    consent: bool


@router.get("/members")
def get_members():
    """조합원 전체 목록 반환 (SQLite 캐시에서 읽기)."""
    members = sync_db.get_members()
    return {"data": members, "error": None}


@router.patch("/members/{member_id}/consent")
def update_consent(member_id: int, body: ConsentUpdate):
    """동의여부 토글 — SQLite 즉시 수정 후 Excel 역동기화."""
    member = sync_db.get_member(member_id)
    if member is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"조합원 {member_id} 없음"}
        )
    sync_db.update_consent(member_id, body.consent)
    return {"data": {"member_id": member_id, "consent": body.consent}, "error": None}


@router.get("/consent-rate")
def get_consent_rate():
    """동의율 통계 (total / consented / rate%)."""
    stats = sync_db.get_consent_rate()
    return {"data": stats, "error": None}
