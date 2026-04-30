# dorim-redev-system/backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.sync import sync_db
from routers import members, workflow, gis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 Excel → SQLite 로드."""
    count = sync_db.load_excel_to_sqlite()
    print(f"✅ 조합원 명부 로드 완료: {count}명")
    yield
    print("🛑 서버 종료")


app = FastAPI(
    title="도림사거리 역세권 재개발 통합 관리 API",
    description="도림동 239-12 역세권 재개발 추진위원회 전용",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(members.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")
app.include_router(gis.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "project": "도림사거리 역세권 재개발"}
