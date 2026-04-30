# dorim-redev-system/backend/tests/test_sync.py
import pytest
import pandas as pd
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.sync import ExcelSyncDB

TEST_EXCEL = Path("tests/fixtures/test_members.xlsx")

@pytest.fixture(autouse=True)
def setup_fixtures():
    TEST_EXCEL.parent.mkdir(exist_ok=True)
    df = pd.DataFrame([
        {"member_id": 1, "address": "도림동 1", "birth_date": "1960-01-01",
         "is_sale_target": True, "rights_value": 100000000, "consent": False},
        {"member_id": 2, "address": "도림동 2", "birth_date": "1970-01-01",
         "is_sale_target": True, "rights_value": 200000000, "consent": True},
    ])
    df.to_excel(TEST_EXCEL, index=False)
    yield
    if TEST_EXCEL.exists():
        TEST_EXCEL.unlink()

def test_load_creates_sqlite(tmp_path):
    db = ExcelSyncDB(excel_path=TEST_EXCEL, db_path=tmp_path / "test.db")
    db.load_excel_to_sqlite()
    members = db.get_members()
    assert len(members) == 2
    assert members[0]["member_id"] == 1

def test_update_consent_writes_back_to_excel(tmp_path):
    db = ExcelSyncDB(excel_path=TEST_EXCEL, db_path=tmp_path / "test.db")
    db.load_excel_to_sqlite()
    db.update_consent(member_id=1, consent=True)
    # Excel 파일 다시 읽어서 확인
    df = pd.read_excel(TEST_EXCEL)
    row = df[df["member_id"] == 1].iloc[0]
    assert row["consent"] == True

def test_consent_rate_calculation(tmp_path):
    db = ExcelSyncDB(excel_path=TEST_EXCEL, db_path=tmp_path / "test.db")
    db.load_excel_to_sqlite()
    rate = db.get_consent_rate()
    assert rate["total"] == 2
    assert rate["consented"] == 1
    assert rate["rate"] == 50.0
