# dorim-redev-system/backend/main.py
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.sync import sync_db
from routers import members, workflow, gis, ocr, rag, project_info

# Windows cp949 콘솔에서 유니코드 출력 보장
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 Excel → SQLite 로드."""
    try:
        count = sync_db.load_excel_to_sqlite()
        print(f"[OK] 조합원 명부 로드 완료: {count}명")
    except Exception as e:
        print(f"[WARN] 엑셀 로드 실패 (시드 데이터 사용): {e}")
    yield
    print("[종료] 서버 종료")


app = FastAPI(
    title="도림사거리 역세권 재개발 통합 관리 API",
    description="도림동 239-12 역세권 재개발 추진위원회 전용",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: 환경변수 ALLOWED_ORIGINS 또는 기본값 (로컬 + Vercel 와일드카드)
_extra_origins = os.environ.get("ALLOWED_ORIGINS", "").split(",")
_allow_origins = [o.strip() for o in _extra_origins if o.strip()] or [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Vercel 모든 서브도메인 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")
app.include_router(gis.router, prefix="/api")
app.include_router(ocr.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(project_info.router, prefix="/api")


@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="https://dorim-redev-system.vercel.app")


@app.get("/health")
def health():
    return {"status": "ok", "project": "도림사거리 역세권 재개발"}
