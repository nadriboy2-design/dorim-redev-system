# dorim-redev-system/backend/routers/project_info.py
"""
도림2동 역세권 장기전세주택사업 정비계획 수립(안) (2023.6 사전검토)
PDF 핵심 지표를 API로 노출
"""
from fastapi import APIRouter

router = APIRouter(tags=["project_info"])

# ─────────────────────────────────────────────────────────────────────────────
# PDF에서 추출한 확정 수치
# 출처: 도림 역세권 시프트 재개발 정비사업 정비계획 수립(안) 2023.6
# ─────────────────────────────────────────────────────────────────────────────
PROJECT_DATA = {
    "project_name": "도림2동 역세권 장기전세주택사업",
    "zone": "도림동 239-12 일원",
    "area_sqm": 59607.59,               # 사업구역 전체 면적
    "land_area_sqm": 58621.43,          # 사업구역 (국공유지 포함)
    "lot_area_sqm": 49908.91,           # 획지 면적 (건축 가능 대지)
    "station_zone_1_m": 350,            # 1차 역세권 반경 (m)
    "station_zone_2_m": 500,            # 2차 역세권 반경 (m)
    "far": {
        "base_far_pct": 202.21,         # 기준용적률 (가중평균)
        "base_far_after_donation_pct": 204.87,  # 공공기여 후 기준용적률
        "legal_max_far_pct": 377.86,    # 법적상한용적률 (가중평균)
        "planned_far_pct": 377.81,      # 계획 용적률
        "far_increase_pct": 172.99,     # 용적률 증가분
        "public_rental_ratio_pct": 86.47,  # 장기전세주택 확보 비율
        "far_formula": (
            "((19,193.31㎡ × 500%) + (3,627.66㎡ × 500%) + (35,800.46㎡ × 300%)) "
            "/ 58,621.43㎡ = 377.86%"
        ),
    },
    "public_contribution": {
        "donated_area_sqm": 504.52,     # 공공시설 순부담 면적
        "donation_ratio_pct": 0.86,     # 순부담률
    },
    "housing_plan": {
        # ── 최신 업데이트 (2025년 건축계획 기준) ──────────────────────────────────
        "total_units": 1640,            # 전체 세대수 (최신)
        "rental_units": 514,            # 임대 합계 (장기전세 + 재개발임대)
        "sale_units": 1126,             # 분양 합계
        # 이전 수치 (2023.6 정비계획안 기준, 참고용)
        "long_term_lease_units": 465,   # 구 장기전세주택 세대수 (참고)
        "redev_rental_units": 129,      # 구 재개발 공공임대주택 세대수 (참고)
        "total_rental_units": 514,      # 총 임대주택
        "general_sale_units": 1126,     # 일반분양
        "unit_types": [
            # type / area_sqm / rental_units / sale_units / total_units / ratio_pct
            {"type": "39형",  "area_sqm": 54.594,  "rental_units": 41,  "sale_units": 18,  "total_units": 59,   "ratio_pct": 3.60},
            {"type": "49형",  "area_sqm": 67.607,  "rental_units": 41,  "sale_units": 16,  "total_units": 57,   "ratio_pct": 3.47},
            {"type": "59형",  "area_sqm": 83.256,  "rental_units": 262, "sale_units": 391, "total_units": 653,  "ratio_pct": 39.82},
            {"type": "74형",  "area_sqm": 102.442, "rental_units": 53,  "sale_units": 142, "total_units": 195,  "ratio_pct": 11.89},
            {"type": "84형",  "area_sqm": 115.896, "rental_units": 117, "sale_units": 467, "total_units": 584,  "ratio_pct": 35.61},
            {"type": "103형", "area_sqm": 143.0,   "rental_units": 0,   "sale_units": 92,  "total_units": 92,   "ratio_pct": 5.61},
        ],
    },
    "height_plan": {
        "max_height_m": 102.85,         # 최고 높이 (사업대상지 기준)
        "max_floors": 35,               # 최고 층수
        "zone_limits": [
            {"zone": "제3종일반주거지역", "frontage_m": 60, "rear_m": 40},
            {"zone": "준주거지역/준공업지역", "frontage_m": 80, "rear_m": 50},
        ],
    },
    "parking": {
        "total_spaces": 2200,           # 지하주차장 총 대수 (추정)
        "basement_floors": 4,
        "residential_spaces": 2200,
        "commercial_spaces": 92,
    },
    "schedule": [
        # 다. 정비계획 수립 절차 (사업추진 절차도 기준)
        {"step": 1,  "name": "사전검토",                  "actor": "영등포구",         "current": False},
        {"step": 2,  "name": "정비계획 입안 제안",         "actor": "사업자 → 영등포구", "current": True},   # ← 현재 단계 ✓
        {"step": 3,  "name": "계획검토",                  "actor": "영등포구",         "current": False},
        {"step": 4,  "name": "주민설명회, 주민공람",        "actor": "영등포구",         "current": False},
        {"step": 5,  "name": "구의회 의견청취",            "actor": "구의회",           "current": False},
        {"step": 6,  "name": "정비계획 결정 요청 (區→市)", "actor": "영등포구 → 서울시", "current": False},
        {"step": 7,  "name": "감정평가",                  "actor": "감정평가법인",      "current": False},
        {"step": 8,  "name": "市 도시계획위원회 심의",     "actor": "서울시",           "current": False},
        {"step": 9,  "name": "정비계획 결정·고시 (市)",    "actor": "서울시",           "current": False},
        {"step": 10, "name": "건축심의 등 인허가 절차",    "actor": "서울시·영등포구",  "current": False},
        {"step": 11, "name": "준공인가",                  "actor": "영등포구",         "current": False},
    ],
    "surrounding_buildings": [
        {"name": "신길우성1차아파트", "height_m": 52.5, "floors": 14},
        {"name": "우성5차아파트", "height_m": 75, "floors": 20},
        {"name": "현대3차아이파크", "height_m": 112.5, "floors_range": "13~30"},
        {"name": "영등포아트자이아파트(사업대상지)", "height_m": 102.85, "floors": 35},
        {"name": "신도림디큐브시티", "height_m": 178.5, "floors_range": "9~51"},
    ],
}


@router.get("/project/info")
def get_project_info():
    """PDF 정비계획 수립(안) 핵심 지표 반환."""
    return {"data": PROJECT_DATA, "error": None}


@router.get("/project/housing-plan")
def get_housing_plan():
    """세대수 계획 및 형별 분양 현황 반환."""
    return {"data": PROJECT_DATA["housing_plan"], "error": None}


@router.get("/project/far")
def get_far_info():
    """용적률 계획 정보 반환."""
    return {"data": PROJECT_DATA["far"], "error": None}


@router.get("/project/schedule")
def get_schedule():
    """향후 추진 일정 반환."""
    return {"data": PROJECT_DATA["schedule"], "error": None}
