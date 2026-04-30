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

    def load_excel_to_sqlite(self) -> int:
        """Called at app startup. Load full Excel -> SQLite. Returns row count."""
        df = pd.read_excel(self.excel_path)
        conn = sqlite3.connect(self.db_path)
        df.to_sql("members", conn, if_exists="replace", index=False)
        conn.close()
        return len(df)

    def get_members(self) -> list[dict]:
        """Return full member list (read from SQLite)."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM members ORDER BY member_id", conn)
        conn.close()
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
        return df.iloc[0].to_dict()

    def update_consent(self, member_id: int, consent: bool) -> None:
        """Update consent: SQLite immediately + Excel bidirectional sync."""
        # 1) SQLite update
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE members SET consent = ? WHERE member_id = ?",
            (1 if consent else 0, member_id),
        )
        conn.commit()

        # 2) Excel bidirectional sync (maintain Single Source of Truth)
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


# Global singleton - initialized in main.py lifespan
sync_db = ExcelSyncDB()
