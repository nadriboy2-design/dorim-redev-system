#!/bin/bash
# dorim-redev-system/start.sh
# 도림사거리 역세권 재개발 통합관리 시스템 원클릭 실행

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo " 도림사거리 역세권 재개발 통합관리 시스템"
echo "=========================================="

# 1) 백엔드 시작
echo "[1/2] 백엔드 시작 (FastAPI :8000)..."
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
  python -m venv venv
  source venv/Scripts/activate  # Windows Git Bash
  pip install -r requirements.txt -q
else
  source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null || true
fi

# 시드 데이터 없으면 생성
if [ ! -f "../data/members.xlsx" ]; then
  echo "  시드 데이터 생성 중..."
  python seed_data.py
fi

uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "  ✅ 백엔드 PID: $BACKEND_PID"

# 2) 프론트엔드 시작
echo "[2/2] 프론트엔드 시작 (Next.js :3000)..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install -q
fi
npm run dev &
FRONTEND_PID=$!
echo "  ✅ 프론트엔드 PID: $FRONTEND_PID"

echo ""
echo "=========================================="
echo " 시스템 기동 완료!"
echo " 브라우저에서 http://localhost:3000 접속"
echo "=========================================="
echo " 종료: Ctrl+C"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
