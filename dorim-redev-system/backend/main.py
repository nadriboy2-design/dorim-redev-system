# dorim-redev-system/backend/main.py
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.sync import sync_db
from routers import members, workflow, gis, ocr, rag

# Windows cp949 콘솔에서 유니코드 출력 보장
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 Excel → SQLite 로드."""
    count = sync_db.load_excel_to_sqlite()
    print(f"[OK] 조합원 명부 로드 완료: {count}명")
    yield
    print("[종료] 서버 종료")


app = FastAPI(
    title="도림사거리 역세권 재개발 통합 관리 API",
    description="도림동 239-12 역세권 재개발 추진위원회 전용",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")
app.include_router(gis.router, prefix="/api")
app.include_router(ocr.router, prefix="/api")
app.include_router(rag.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "project": "도림사거리 역세권 재개발"}
