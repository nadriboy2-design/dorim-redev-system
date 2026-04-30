# dorim-redev-system/backend/routers/members.py
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.sync import sync_db

router = APIRouter(tags=["members"])


class ConsentUpdate(BaseModel):
    consent: bool


class MemberUpdate(BaseModel):
    """조합원 전체 필드 수정 모델."""
    name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    address: Optional[str] = None
    current_address: Optional[str] = None
    ownership_type: Optional[str] = None        # 토지+건물/토지만/건물만/무허가건물
    land_area: Optional[float] = None           # 토지면적(㎡)
    building_area: Optional[float] = None       # 건물면적(㎡)
    has_illegal_building: Optional[bool] = None
    prev_asset_value: Optional[int] = None      # 종전자산평가액(원)
    proportional_rate: Optional[float] = None   # 비례율(%)
    rights_value: Optional[int] = None          # 권리가액(원)
    is_sale_target: Optional[bool] = None       # 분양대상 여부
    alloc_area_type: Optional[str] = None       # 분양신청타입
    estimated_alloc_price: Optional[int] = None # 분양예정가액(원)
    relocation_cost: Optional[int] = None       # 이주비(원)
    settlement_amount: Optional[int] = None     # 청산금(원)
    consent: Optional[bool] = None
    consent_date: Optional[str] = None
    memo: Optional[str] = None


@router.get("/members")
def get_members():
    """조합원 전체 목록 반환."""
    members = sync_db.get_members()
    return {"data": members, "error": None}


@router.get("/members/{member_id}")
def get_member(member_id: int):
    """단일 조합원 상세 반환."""
    member = sync_db.get_member(member_id)
    if member is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"조합원 {member_id} 없음"}
        )
    return {"data": member, "error": None}


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


@router.put("/members/{member_id}")
def update_member(member_id: int, body: MemberUpdate):
    """조합원 전체 필드 수정 — 비례율 변경 시 권리가액·이주비·청산금 자동 재계산."""
    member = sync_db.get_member(member_id)
    if member is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"조합원 {member_id} 없음"}
        )

    fields = {k: v for k, v in body.model_dump().items() if v is not None}

    # 비례율 또는 종전자산평가액이 변경되면 권리가액·이주비·청산금 자동 재계산
    prop_rate = fields.get("proportional_rate", member.get("proportional_rate", 110.0))
    prev_val = fields.get("prev_asset_value", member.get("prev_asset_value", 0))
    alloc_price = fields.get("estimated_alloc_price", member.get("estimated_alloc_price", 0))

    if "proportional_rate" in fields or "prev_asset_value" in fields:
        rights_val = int(prev_val * prop_rate / 100)
        fields["rights_value"] = rights_val
        fields["relocation_cost"] = int(rights_val * 0.60)
        if alloc_price:
            fields["settlement_amount"] = alloc_price - rights_val

    if fields:
        sync_db.update_member(member_id, fields)

    updated = sync_db.get_member(member_id)
    return {"data": updated, "error": None}


@router.get("/consent-rate")
def get_consent_rate():
    """동의율 통계 (total / consented / rate%)."""
    stats = sync_db.get_consent_rate()
    return {"data": stats, "error": None}


@router.get("/proportional-stats")
def get_proportional_stats():
    """비례율·이주비·청산금 집계 통계."""
    stats = sync_db.get_proportional_stats()
    return {"data": stats, "error": None}
