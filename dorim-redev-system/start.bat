@echo off
echo ==========================================
echo  도림사거리 역세권 재개발 통합관리 시스템
echo ==========================================

echo [1/2] 백엔드 시작 (FastAPI :8000)...
cd /d "%~dp0backend"
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt -q
) else (
    call venv\Scripts\activate
)

if not exist "..\data\members.xlsx" (
    echo   시드 데이터 생성 중...
    python seed_data.py
)

start "Backend" uvicorn main:app --host 0.0.0.0 --port 8000
echo   ✅ 백엔드 시작됨

echo [2/2] 프론트엔드 시작 (Next.js :3000)...
cd /d "%~dp0frontend"
if not exist node_modules (
    npm install -q
)
start "Frontend" npm run dev
echo   ✅ 프론트엔드 시작됨

echo.
echo ==========================================
echo  시스템 기동 완료!
echo  브라우저에서 http://localhost:3000 접속
echo ==========================================
pause
