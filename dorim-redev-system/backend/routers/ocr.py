# dorim-redev-system/backend/routers/ocr.py
import io
import re
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["ocr"])

# PaddleOCR 선택적 임포트 (Python 3.14에서 paddlepaddle 미지원 시 폴백)
try:
    from paddleocr import PaddleOCR
    _ocr = PaddleOCR(use_angle_cls=True, lang="korean", show_log=False)
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False


def _extract_with_paddleocr(image_bytes: bytes) -> str:
    """PaddleOCR로 텍스트 추출."""
    import numpy as np
    import cv2
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result = _ocr.ocr(img, cls=True)
    lines = []
    for line in result:
        for word_info in line:
            lines.append(word_info[1][0])
    return "\n".join(lines)


def _parse_receipt_text(text: str) -> dict:
    """텍스트에서 영수증 필드 추출."""
    # 날짜 패턴: 2024-01-15, 2024.01.15, 24/01/15
    date_pattern = r'(\d{4}[-./]\d{2}[-./]\d{2}|\d{2}[-./]\d{2}[-./]\d{2})'
    date_match = re.search(date_pattern, text)
    date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    # 금액 패턴: 12,000원, ₩12000, 합계 12000
    amount_pattern = r'(?:합계|총액|금액|total)[^\d]*(\d{1,3}(?:,\d{3})*)'
    amount_match = re.search(amount_pattern, text, re.IGNORECASE)
    if not amount_match:
        amount_pattern2 = r'(\d{1,3}(?:,\d{3})+)'
        amounts = re.findall(amount_pattern2, text)
        total_amount = max([int(a.replace(",", "")) for a in amounts], default=0) if amounts else 0
    else:
        total_amount = int(amount_match.group(1).replace(",", ""))

    # 부가세 (총액의 10/110)
    vat = round(total_amount * 10 / 110)
    supply = total_amount - vat

    # 상호명 (첫 번째 줄 또는 텍스트 첫 부분)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    store_name = lines[0] if lines else "상호명 미확인"

    return {
        "date": date_str,
        "store_name": store_name,
        "supply_amount": supply,
        "vat": vat,
        "total_amount": total_amount,
        "ocr_available": OCR_AVAILABLE,
    }


def _generate_expense_pdf(receipt_data: dict) -> bytes:
    """서울시 표준 지출결의서 PDF 생성."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 제목
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 60, "Expense Report")

    # 부제목 (한글은 기본 폰트로 ASCII 표기)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 85, "Dorim Station Area Redevelopment Committee")

    # 구분선
    c.line(50, height - 100, width - 50, height - 100)

    # 내용
    y = height - 140
    line_height = 28
    fields = [
        ("Date / 일자", receipt_data["date"]),
        ("Store / 상호명", receipt_data["store_name"]),
        ("Supply Amount / 공급가액", f"{receipt_data['supply_amount']:,} KRW"),
        ("VAT / 부가세", f"{receipt_data['vat']:,} KRW"),
        ("Total / 합계금액", f"{receipt_data['total_amount']:,} KRW"),
    ]

    c.setFont("Helvetica-Bold", 11)
    for label, value in fields:
        c.drawString(60, y, label + ":")
        c.setFont("Helvetica", 11)
        c.drawString(250, y, str(value))
        c.setFont("Helvetica-Bold", 11)
        y -= line_height

    # 서명란
    y -= 20
    c.line(50, y, width - 50, y)
    y -= 25
    c.setFont("Helvetica", 10)
    c.drawString(60, y, "Approved by: ___________________")
    c.drawString(350, y, "Date: ___________________")

    c.save()
    buffer.seek(0)
    return buffer.read()


@router.post("/ocr/receipt")
async def process_receipt(file: UploadFile = File(...)):
    """영수증 이미지 업로드 → 텍스트 추출 → 지출결의서 JSON 반환."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_FILE",
                                                       "message": "이미지 파일만 업로드 가능합니다"})

    image_bytes = await file.read()

    if OCR_AVAILABLE:
        try:
            text = _extract_with_paddleocr(image_bytes)
        except Exception:
            text = ""
    else:
        # OCR 미사용 시 빈 텍스트로 파싱 (사용자가 수동 입력 가능)
        text = ""

    receipt_data = _parse_receipt_text(text)
    return {"data": receipt_data, "error": None}


@router.post("/ocr/generate-pdf")
async def generate_expense_pdf(receipt_data: dict):
    """지출결의서 데이터 → PDF 다운로드."""
    pdf_bytes = _generate_expense_pdf(receipt_data)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=expense_report.pdf"},
    )
