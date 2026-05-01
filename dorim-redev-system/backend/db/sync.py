# dorim-redev-system/backend/db/sync.py
import random
import sqlite3
import pandas as pd
from pathlib import Path


# ── 시드 데이터 생성 상수 ────────────────────────────────────────────────────
_LAST_NAMES = [
    "김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
    "한", "오", "서", "신", "권", "황", "안", "송", "류", "전",
    "홍", "고", "문", "양", "손", "배", "백", "허", "유", "남",
    "심", "노", "하", "곽", "성", "차", "주", "우", "구", "민",
    "나", "진", "지", "엄", "채", "원", "천", "방", "공", "현",
]

_FIRST_NAMES = [
    "도림", "역세", "재개", "토지", "조합", "동의", "영등", "포구",
    "사거", "건물", "정비", "입안", "추진", "위원", "관리", "처분",
    "사업", "시행", "분양", "시공", "설계", "감정", "평가", "권리",
    "청산", "이주", "비용", "보상", "계획", "인가", "승인", "협의",
    "민준", "서준", "도윤", "예준", "시우", "하준", "주원", "지호",
    "지우", "지민", "서현", "지윤", "서연", "하은", "수현", "지안",
    "건우", "우진", "현준", "태양", "수호", "우현", "태준", "준서",
    "은지", "미래", "다은", "나은", "가은", "소연", "혜진", "수진",
    "성현", "명진", "병철", "광호", "기수", "영철", "종현", "창수",
    "순자", "영자", "정자", "명자", "분이", "복순", "옥순", "정순",
]

# 도림동 일대 실제 지번 범위 (239 ~ 270번지)
_BLOCKS = list(range(239, 271))
_LOTS = list(range(1, 25))
_STREETS = [
    "도림동", "대림동", "신길동", "당산동", "영등포동",
]

_OWNERSHIP = ["토지+건물", "토지만", "건물만", "집합건물"]
_ALLOC_TYPES = ["59A", "59B", "84A", "84B", "109A", ""]


def _make_name(rng: random.Random) -> str:
    return rng.choice(_LAST_NAMES) + rng.choice(_FIRST_NAMES)


def _make_address(rng: random.Random, member_id: int) -> str:
    block = rng.choice(_BLOCKS)
    lot = rng.choice(_LOTS)
    dong = "도림동"
    return f"서울 영등포구 {dong} {block}-{lot}"


def _make_phone(member_id: int) -> str:
    mid = str(member_id).zfill(4)
    return f"010-{mid[:2]}{mid[2:]}-{str(member_id % 10000).zfill(4)}"


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

    def _seed_df(self, n: int = 800) -> pd.DataFrame:
        """Excel 없을 때 사용할 기본 시드 데이터 (기본 800명).

        실제 재개발 구역 통계에 근거한 현실적 분포:
        - 동의율: ~75% (사전검토 임계값 40% 초과)
        - 분양대상자: ~70%
        - 무허가 건물: ~8%
        - 권리가액: 1.2억 ~ 5.5억 (영등포구 평균 반영)
        """
        rng = random.Random(42)  # 재현 가능한 시드

        # 현실적인 분포 설정
        consent_rate = 0.75        # 동의율 75%
        sale_target_rate = 0.70    # 분양대상자 70%
        illegal_bldg_rate = 0.08   # 무허가 8%

        # 생년 분포: 1940~1995 (고령자 많음)
        birth_years = (
            [y for y in range(1940, 1960)] * 3 +   # 60~80대 비중 높음
            [y for y in range(1960, 1975)] * 4 +
            [y for y in range(1975, 1990)] * 2 +
            [y for y in range(1990, 1996)] * 1
        )

        members = []
        for i in range(n):
            member_id = 1001 + i
            rng_consent = rng.random() < consent_rate
            rng_sale = rng.random() < sale_target_rate
            rng_illegal = rng.random() < illegal_bldg_rate

            birth_year = rng.choice(birth_years)
            birth_month = rng.randint(1, 12)
            birth_day = rng.randint(1, 28)
            birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

            # 권리가액: 1.2억~5.5억, 정규분포 근사
            rights_base = rng.gauss(2.8, 0.9)  # 평균 2.8억, 표준편차 0.9억
            rights_value = int(max(1.2, min(5.5, rights_base)) * 1e8)

            # 토지/건물 면적
            land_area = round(rng.uniform(20.0, 180.0), 1)
            building_area = round(rng.uniform(30.0, 220.0), 1) if rng_sale else 0.0

            # 비례율 (106~114%)
            prop_rate = round(rng.uniform(106.0, 114.0), 1)

            # 이전 자산가치
            prev_asset = int(rights_value * rng.uniform(0.85, 1.10))

            # 분양 면적 타입
            alloc_type = rng.choice(_ALLOC_TYPES) if rng_sale else ""

            # 추정 분양가 (59㎡: 5.5억, 84㎡: 7.5억, 109㎡: 9.5억)
            alloc_price_map = {"59A": 550_000_000, "59B": 560_000_000,
                               "84A": 750_000_000, "84B": 760_000_000,
                               "109A": 950_000_000, "": 0}
            est_alloc_price = alloc_price_map.get(alloc_type, 0)

            # 이주비 (권리가액의 40~60%)
            reloc_cost = int(rights_value * rng.uniform(0.40, 0.60)) if rng_sale else 0

            # 청산금 (+: 조합원 납부, -: 조합 환급)
            if est_alloc_price > 0:
                settlement = est_alloc_price - rights_value + reloc_cost
            else:
                settlement = 0

            address = _make_address(rng, member_id)

            members.append({
                "member_id": member_id,
                "name": _make_name(rng),
                "phone": f"010-{str(member_id % 10000).zfill(4)}-{str((member_id * 7) % 10000).zfill(4)}",
                "birth_date": birth_date,
                "address": address,
                "current_address": address,
                "ownership_type": rng.choice(_OWNERSHIP),
                "land_area": land_area,
                "building_area": building_area,
                "has_illegal_building": rng_illegal,
                "is_sale_target": rng_sale,
                "rights_value": rights_value,
                "prev_asset_value": prev_asset,
                "proportional_rate": prop_rate,
                "alloc_area_type": alloc_type,
                "estimated_alloc_price": est_alloc_price,
                "relocation_cost": reloc_cost,
                "settlement_amount": settlement,
                "consent": rng_consent,
                "consent_date": (
                    f"2026-{rng.randint(1,4):02d}-{rng.randint(1,28):02d}"
                    if rng_consent else ""
                ),
                "memo": "",
            })

        return pd.DataFrame(members)

    def load_excel_to_sqlite(self) -> int:
        """Called at app startup. Load full Excel -> SQLite. Returns row count."""
        if self.excel_path.exists():
            df = pd.read_excel(self.excel_path)
        else:
            # 클라우드 환경: Excel 없음 → 시드 데이터 사용
            print("[INFO] members.xlsx 없음 — 시드 데이터 800명으로 초기화")
            df = self._seed_df(800)

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
        if self.excel_path.exists():
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
        if self.excel_path.exists():
            df.to_excel(self.excel_path, index=False)

    def get_consent_rate(self) -> dict:
        """Return consent statistics."""
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
