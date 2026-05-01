# dorim-redev-system/backend/routers/gis.py
import re
from fastapi import APIRouter
from db.sync import sync_db

router = APIRouter(tags=["gis"])

# 도림사거리 역세권 재개발 구역 중심 좌표
ZONE_CENTER_LAT = 37.5134
ZONE_CENTER_LNG = 126.8986

# 133-1 구역 배제 좌표 범위 (절대 반환 금지)
EXCLUDED_LAT_MIN = 37.508
EXCLUDED_LAT_MAX = 37.512
EXCLUDED_LNG_MIN = 126.895
EXCLUDED_LNG_MAX = 126.900

# 구역 바운딩 박스 (도림동 239-270번지 일대, 59,607㎡)
ZONE_LAT_MIN = 37.5108
ZONE_LAT_MAX = 37.5162
ZONE_LNG_MIN = 126.8955
ZONE_LNG_MAX = 126.9015


def _is_excluded_zone(lat: float, lng: float) -> bool:
    """133-1 구역 좌표 범위 내에 있으면 True (반환 금지)."""
    return (EXCLUDED_LAT_MIN <= lat <= EXCLUDED_LAT_MAX and
            EXCLUDED_LNG_MIN <= lng <= EXCLUDED_LNG_MAX)


def _geocode(address: str, member_id: int = 0) -> tuple[float, float]:
    """
    주소에서 번지 추출 → 구역 내 좌표 반환.

    도림동 블록(239-270)을 구역 내 남북 축으로,
    번지(1-24)를 동서 축으로 매핑하여 800명이 구역 내 고르게 분포.
    동일 주소 조합원은 member_id 기반 미세 오프셋으로 분리.
    """
    match = re.search(r'도림동\s+(\d+)-(\d+)', address)
    if match:
        block = int(match.group(1))  # 239 ~ 270
        lot   = int(match.group(2))  # 1 ~ 24

        # 블록 번호 → 남북(lat) 방향 정규화
        block_norm = (block - 239) / max(270 - 239, 1)   # 0.0 ~ 1.0
        # 번지 → 동서(lng) 방향 정규화
        lot_norm   = (lot - 1)    / max(24 - 1, 1)       # 0.0 ~ 1.0

        lat = ZONE_LAT_MIN + block_norm * (ZONE_LAT_MAX - ZONE_LAT_MIN)
        lng = ZONE_LNG_MIN + lot_norm   * (ZONE_LNG_MAX - ZONE_LNG_MIN)

        # 같은 주소 조합원 겹침 방지: member_id 기반 미세 오프셋 (±15m 이내)
        offset_lat = ((member_id * 7 + block) % 31 - 15) * 0.000013
        offset_lng = ((member_id * 13 + lot)  % 31 - 15) * 0.000015

        return (lat + offset_lat, lng + offset_lng)

    # 번지 파싱 실패 → 구역 중심 근처에 분산 배치
    offset_lat = ((member_id * 11) % 41 - 20) * 0.000013
    offset_lng = ((member_id * 17) % 41 - 20) * 0.000015
    return (ZONE_CENTER_LAT + offset_lat, ZONE_CENTER_LNG + offset_lng)


@router.get("/gis/markers")
def get_gis_markers():
    """조합원 주소 → 좌표 변환 + 동의여부 마커 반환. 133-1 구역 자동 필터링."""
    members = sync_db.get_members()
    markers = []
    for m in members:
        lat, lng = _geocode(m["address"], m.get("member_id", 0))
        if _is_excluded_zone(lat, lng):
            continue  # 133-1 구역 데이터 완전 배제
        markers.append({
            "member_id": m["member_id"],
            "name": m.get("name", ""),
            "address": m["address"],
            "ownership_type": m.get("ownership_type", ""),
            "rights_value": m.get("rights_value", 0),
            "lat": lat,
            "lng": lng,
            "consent": bool(m["consent"]),
            "color": "#3b82f6" if m["consent"] else "#ef4444",
        })
    return {"data": markers, "error": None}


@router.get("/gis/zone-polygon")
def get_zone_polygon():
    """도림동 239-12 역세권 재개발 구역계 GeoJSON 반환 (실제 구역 근사)."""
    # 도림동 239-12 일대 59,607.59㎡ — 불규칙 다각형 근사
    geojson = {
        "type": "Feature",
        "properties": {
            "name": "도림사거리 역세권 재개발 구역",
            "zone": "도림동 239-12",
            "area_sqm": 59607.59,
            "stage": "정비계획 입안 (계획검토 중)",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [126.8955, 37.5108],
                [126.8985, 37.5105],
                [126.9015, 37.5112],
                [126.9018, 37.5145],
                [126.9005, 37.5162],
                [126.8975, 37.5160],
                [126.8958, 37.5150],
                [126.8950, 37.5128],
                [126.8955, 37.5108],
            ]],
        },
    }
    return {"data": geojson, "error": None}
