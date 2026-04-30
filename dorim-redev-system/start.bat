@echo off
chcp 65001 >nul
echo ==========================================
echo  도림사거리 역세권 재개발 통합관리 시스템
echo ==========================================

echo [1/2] 백엔드 시작 (FastAPI :8000)...
echo   (PaddleOCR 모델 로딩으로 약 20초 소요됩니다)
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

start "Backend - FastAPI :8000" cmd /k "chcp 65001 >nul && cd /d "%~dp0backend" && call venv\Scripts\activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo   [OK] 백엔드 창 열림 (20초 후 준비 완료)

echo [2/2] 프론트엔드 시작 (Next.js :3000)...
cd /d "%~dp0frontend"
if not exist node_modules (
    npm install
)
start "Frontend - Next.js :3000" cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo   [OK] 프론트엔드 창 열림

echo.
echo ==========================================
echo  백엔드: 20초 후 http://localhost:8000
echo  프론트엔드: 10초 후 http://localhost:3000
echo ==========================================
echo  두 창이 모두 뜨면 localhost:3000 접속하세요
pause
