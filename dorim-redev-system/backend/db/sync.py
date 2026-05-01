# dorim-redev-system/backend/db/sync.py
import sqlite3
import pandas as pd
from pathlib import Path


class ExcelSyncDB:
    """Excel <-> SQLite dual-direction sync class.

    members.xlsx is the Single Source of Truth.
    SQLite serves only as a read-performance cache.
    """

    def __init__(
        self,
        excel_path: Path = Path("../data/members.xlsx"),
        db_path: Path = Path("../data/members.db"),
    ):
        self.excel_path = Path(excel_path)
        self.db_path = Path(db_path)

    def _seed_df(self) -> pd.DataFrame:
        """Excel 없을 때 사용할 기본 시드 데이터."""
        members = [
            {"member_id": 1001, "address": "서울 영등포구 도림동 239-12", "birth_date": "1955-03-15", "is_sale_target": True,  "rights_value": 185000000, "consent": True,  "name": "김도림", "phone": "010-1111-0001", "has_illegal_building": False},
            {"member_id": 1002, "address": "서울 영등포구 도림동 239-14", "birth_date": "1962-07-22", "is_sale_target": True,  "rights_value": 220000000, "consent": True,  "name": "이역세", "phone": "010-1111-0002", "has_illegal_building": False},
            {"member_id": 1003, "address": "서울 영등포구 도림동 239-16", "birth_date": "1948-11-08", "is_sale_target": False, "rights_value": 145000000, "consent": False, "name": "박재개", "phone": "010-1111-0003", "has_illegal_building": True},
            {"member_id": 1004, "address": "서울 영등포구 도림동 240-1",  "birth_date": "1971-02-14", "is_sale_target": True,  "rights_value": 198000000, "consent": True,  "name": "최발", "phone": "010-1111-0004", "has_illegal_building": False},
            {"member_id": 1005, "address": "서울 영등포구 도림동 240-3",  "birth_date": "1965-09-30", "is_sale_target": True,  "rights_value": 175000000, "consent": False, "name": "정토지", "phone": "010-1111-0005", "has_illegal_building": False},
            {"member_id": 1006, "address": "서울 영등포구 도림동 241-2",  "birth_date": "1953-06-18", "is_sale_target": True,  "rights_value": 210000000, "consent": True,  "name": "강조합", "phone": "010-1111-0006", "has_illegal_building": False},
            {"member_id": 1007, "address": "서울 영등포구 도림동 241-5",  "birth_date": "1978-12-25", "is_sale_target": False, "rights_value": 130000000, "consent": False, "name": "윤동의", "phone": "010-1111-0007", "has_illegal_building": True},
            {"member_id": 1008, "address": "서울 영등포구 도림동 242-1",  "birth_date": "1960-04-11", "is_sale_target": True,  "rights_value": 195000000, "consent": True,  "name": "임영등", "phone": "010-1111-0008", "has_illegal_building": False},
            {"member_id": 1009, "address": "서울 영등포구 도림동 242-3",  "birth_date": "1967-08-07", "is_sale_target": True,  "rights_value": 168000000, "consent": True,  "name": "한포구", "phone": "010-1111-0009", "has_illegal_building": False},
            {"member_id": 1010, "address": "서울 영등포구 도림동 243-2",  "birth_date": "1982-01-19", "is_sale_target": True,  "rights_value": 205000000, "consent": False, "name": "오사거", "phone": "010-1111-0010", "has_illegal_building": False},
        ]
        return pd.DataFrame(members)

    def load_excel_to_sqlite(self) -> int:
        """Called at app startup. Load full Excel -> SQLite. Returns row count."""
        if self.excel_path.exists():
            df = pd.read_excel(self.excel_path)
        else:
            # 클라우드 환경: Excel 없음 → 시드 데이터 사용
            print("[INFO] members.xlsx 없음 — 시드 데이터로 초기화")
            df = self._seed_df()

        # 결측값 처리
        df = df.fillna({
            "name": "", "phone": "", "current_address": "",
            "memo": "", "consent_date": "", "alloc_area_type": "",
            "land_area": 0.0, "building_area": 0.0,
            "prev_asset_value": 0, "proportional_rate": 110.0,
            "rights_value": 0, "estimated_alloc_price": 0,
            "relocation_cost": 0, "settlement_amount": 0,
        })
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        df.to_sql("members", conn, if_exists="replace", index=False)
        conn.close()
        return len(df)

    def get_members(self) -> list[dict]:
        """Return full member list (read from SQLite)."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM members ORDER BY member_id", conn)
        conn.close()
        # bool 변환
        for col in ("consent", "is_sale_target", "has_illegal_building"):
            if col in df.columns:
                df[col] = df[col].astype(bool)
        return df.to_dict(orient="records")

    def get_member(self, member_id: int) -> dict | None:
        """Return single member."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql(
            "SELECT * FROM members WHERE member_id = ?", conn, params=(member_id,)
        )
        conn.close()
        if df.empty:
            return None
        row = df.iloc[0].to_dict()
        for col in ("consent", "is_sale_target", "has_illegal_building"):
            if col in row:
                row[col] = bool(row[col])
        return row

    def update_consent(self, member_id: int, consent: bool) -> None:
        """Update consent: SQLite immediately + Excel bidirectional sync."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE members SET consent = ? WHERE member_id = ?",
            (1 if consent else 0, member_id),
        )
        conn.commit()
        df = pd.read_sql("SELECT * FROM members ORDER BY member_id", conn)
        conn.close()
        df.to_excel(self.excel_path, index=False)

    def update_member(self, member_id: int, fields: dict) -> None:
        """Update arbitrary fields for a member — SQLite + Excel sync."""
        if not fields:
            return
        conn = sqlite3.connect(self.db_path)
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [member_id]
        conn.execute(
            f"UPDATE members SET {set_clause} WHERE member_id = ?", values
        )
        conn.commit()
        df = pd.read_sql("SELECT * FROM members ORDER BY member_id", conn)
        conn.close()
        df.to_excel(self.excel_path, index=False)

    def get_consent_rate(self) -> dict:
        """Return consent statistics. {"total": N, "consented": M, "rate": %}"""
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            """SELECT
                COUNT(*) as total,
                SUM(CASE WHEN consent = 1 THEN 1 ELSE 0 END) as consented
               FROM members"""
        ).fetchone()
        conn.close()
        total, consented = row
        rate = round(consented / total * 100, 1) if total else 0.0
        return {"total": int(total), "consented": int(consented), "rate": rate}

    def get_proportional_stats(self) -> dict:
        """비례율·이주비·청산금 집계 통계."""
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            """SELECT
                AVG(proportional_rate)       AS avg_prop_rate,
                SUM(prev_asset_value)        AS total_prev_asset,
                SUM(rights_value)            AS total_rights,
                SUM(relocation_cost)         AS total_reloc,
                SUM(CASE WHEN settlement_amount > 0 THEN settlement_amount ELSE 0 END) AS total_payment,
                SUM(CASE WHEN settlement_amount < 0 THEN settlement_amount ELSE 0 END) AS total_refund,
                COUNT(*) AS total
               FROM members"""
        ).fetchone()
        conn.close()
        (avg_pr, total_prev, total_rights, total_reloc,
         total_payment, total_refund, total) = row
        return {
            "proportional_rate": round(float(avg_pr or 110.0), 2),
            "total_prev_asset_value": int(total_prev or 0),
            "total_rights_value": int(total_rights or 0),
            "total_relocation_cost": int(total_reloc or 0),
            "total_settlement_payment": int(total_payment or 0),
            "total_settlement_refund": int(total_refund or 0),
            "member_count": int(total or 0),
        }


# Global singleton - initialized in main.py lifespan
sync_db = ExcelSyncDB()
