# dorim-redev-system/backend/routers/gis.py
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

# 주소 → 좌표 간이 매핑 테이블 (도림동 번지별)
ADDRESS_COORDS = {
    "239-12": (37.5134, 126.8986),
    "239-14": (37.5136, 126.8988),
    "239-16": (37.5132, 126.8984),
    "240-1":  (37.5140, 126.8990),
    "240-3":  (37.5138, 126.8992),
    "241-2":  (37.5142, 126.8994),
    "241-5":  (37.5144, 126.8996),
    "242-1":  (37.5128, 126.8980),
    "242-3":  (37.5126, 126.8978),
    "243-2":  (37.5150, 126.8998),
    "243-4":  (37.5148, 126.8976),
    "244-1":  (37.5146, 126.8974),
    "244-6":  (37.5120, 126.8970),
    "245-3":  (37.5118, 126.8968),
    "245-7":  (37.5116, 126.8966),
    "246-1":  (37.5114, 126.8964),
    "246-4":  (37.5112, 126.8962),
    "247-2":  (37.5110, 126.8960),
    "247-8":  (37.5108, 126.8958),
    "248-1":  (37.5106, 126.8956),
}


def _is_excluded_zone(lat: float, lng: float) -> bool:
    """133-1 구역 좌표 범위 내에 있으면 True (반환 금지)."""
    return (EXCLUDED_LAT_MIN <= lat <= EXCLUDED_LAT_MAX and
            EXCLUDED_LNG_MIN <= lng <= EXCLUDED_LNG_MAX)


def _geocode(address: str) -> tuple[float, float]:
    """주소에서 번지 추출 → 좌표 반환. 실패 시 구역 중심 좌표로 폴백."""
    for lot_num, coords in ADDRESS_COORDS.items():
        if lot_num in address:
            return coords
    return (ZONE_CENTER_LAT, ZONE_CENTER_LNG)


@router.get("/gis/markers")
def get_gis_markers():
    """조합원 주소 → 좌표 변환 + 동의여부 마커 반환. 133-1 구역 자동 필터링."""
    members = sync_db.get_members()
    markers = []
    for m in members:
        lat, lng = _geocode(m["address"])
        if _is_excluded_zone(lat, lng):
            continue  # 133-1 구역 데이터 완전 배제
        markers.append({
            "member_id": m["member_id"],
            "address": m["address"],
            "lat": lat,
            "lng": lng,
            "consent": bool(m["consent"]),
            "color": "#3b82f6" if m["consent"] else "#ef4444",
        })
    return {"data": markers, "error": None}


@router.get("/gis/zone-polygon")
def get_zone_polygon():
    """도림동 239-12 역세권 재개발 구역계 GeoJSON 반환."""
    # 실제 구역계 폴리곤 (단순화된 근사치 - 59,607.59㎡)
    geojson = {
        "type": "Feature",
        "properties": {
            "name": "도림사거리 역세권 재개발 구역",
            "zone": "도림동 239-12",
            "area_sqm": 59607.59,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [126.8960, 37.5110],
                [126.9010, 37.5110],
                [126.9010, 37.5160],
                [126.8960, 37.5160],
                [126.8960, 37.5110],
            ]],
        },
    }
    return {"data": geojson, "error": None}
