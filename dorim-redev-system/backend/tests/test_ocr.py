# dorim-redev-system/backend/tests/test_ocr.py
import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ocr_receipt_rejects_non_image():
    """이미지 아닌 파일 업로드 시 400 반환."""
    file_content = b"not an image"
    resp = client.post(
        "/api/ocr/receipt",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert resp.status_code == 400

def test_ocr_receipt_accepts_image():
    """이미지 파일 업로드 시 200 반환 + 필수 필드 존재."""
    # 1x1 흰색 PNG (최소 유효 이미지)
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
        b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05'
        b'\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    resp = client.post(
        "/api/ocr/receipt",
        files={"file": ("receipt.png", io.BytesIO(png_bytes), "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    for field in ["date", "store_name", "supply_amount", "vat", "total_amount"]:
        assert field in data

def test_ocr_generate_pdf_returns_pdf():
    """지출결의서 PDF 생성 테스트."""
    receipt_data = {
        "date": "2026-04-30",
        "store_name": "테스트 상점",
        "supply_amount": 9090,
        "vat": 910,
        "total_amount": 10000,
    }
    resp = client.post("/api/ocr/generate-pdf", json=receipt_data)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
