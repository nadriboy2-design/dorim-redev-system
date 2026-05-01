# dorim-redev-system/backend/routers/workflow.py
import io
from pathlib import Path
import yaml
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from compliance import compliance
from db.sync import sync_db

router = APIRouter(tags=["workflow"])
WORKFLOW_PATH = Path(__file__).parent.parent.parent / "ai_harness" / "workflow.yaml"


def _load_workflow() -> dict:
    """workflow.yaml를 로드하고 반환"""
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@router.get("/workflow/status")
def get_workflow_status():
    """현재 사업 단계, 필수 서류, 동의율 현황 반환."""
    wf = _load_workflow()
    stage_key = wf["current_stage"]
    stage = wf["stages"][stage_key]
    rate_data = sync_db.get_consent_rate()
    threshold = stage.get("consent_threshold", 0)

    return {
        "data": {
            "current_stage": stage_key,
            "stage_name": stage["name"],
            "current_sub_stage": wf.get("current_sub_stage", ""),
            "current_sub_stage_detail": wf.get("current_sub_stage_detail", ""),
            "consent_threshold": threshold,
            "required_docs": stage["required_docs"],
            "cautions": stage.get("cautions", []),
            "consent_rate": rate_data,
            "is_threshold_met": (rate_data["rate"] / 100) >= threshold,
        },
        "error": None,
    }


class FarCheckRequest(BaseModel):
    far_pct: float


@router.post("/compliance/check-far")
def check_far(body: FarCheckRequest):
    """용적률 하드락 A 검사."""
    compliance.check_far(body.far_pct)
    return {"data": {"far_pct": body.far_pct, "status": "OK"}, "error": None}


class GenerateDocRequest(BaseModel):
    doc_type: str
    has_cost_verification: bool = False


@router.post("/workflow/generate-doc")
def generate_doc(body: GenerateDocRequest):
    """서울시 표준 양식 PDF 생성. 하드락 B·C 검사 후 생성."""
    wf = _load_workflow()
    current_stage = wf["current_stage"]
    compliance.check_doc_generation(
        doc_type=body.doc_type,
        current_stage=current_stage,
        has_cost_verification=body.has_cost_verification,
    )

    # PDF 생성
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        # reportlab이 없으면 간단한 바이너리 응답으로 대체
        buffer = io.BytesIO()
        buffer.write(b"%PDF-1.4\n")
        buffer.write(f"도림사거리 역세권 재개발\n문서: {body.doc_type}\n단계: {wf['stages'][current_stage]['name']}\n".encode("utf-8"))
        buffer.seek(0)
    else:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.setFont("Helvetica", 14)
        c.drawString(100, 750, "도림사거리 역세권 재개발")
        c.drawString(100, 720, f"문서 유형: {body.doc_type}")
        c.drawString(100, 690, f"현재 단계: {wf['stages'][current_stage]['name']}")
        c.save()
        buffer.seek(0)

    filename = f"{body.doc_type}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
