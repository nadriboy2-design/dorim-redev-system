"""
온라인 접속 시작 스크립트 — 도림사거리 역세권 재개발 통합관리
==============================================================
실행: python online_start.py
------------------------------
1. 백엔드(8000) Cloudflare 터널 시작 → URL 획득
2. .env.local에 백엔드 URL 주입
3. 프론트엔드 dev 서버 시작 (next.cmd)
4. 프론트엔드(3000) Cloudflare 터널 시작 → URL 획득
5. 공유 URL 표시
"""
import subprocess
import sys
import time
import re
import threading
from pathlib import Path

ROOT       = Path(__file__).parent / "dorim-redev-system"
FRONTEND   = ROOT / "frontend"
BACKEND    = ROOT / "backend"
CLOUDFLARED = Path.home() / "cloudflared.exe"
PYTHON_VENV = BACKEND / "venv" / "Scripts" / "python.exe"
NEXT_CMD    = FRONTEND / "node_modules" / ".bin" / "next.cmd"


def find_tunnel_url(log_path: Path, timeout=45) -> str:
    """cloudflared 로그 파일에서 tunnel URL 추출"""
    url_re = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com")
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        if log_path.exists():
            content = log_path.read_text(encoding="utf-8", errors="replace")
            m = url_re.search(content)
            if m:
                return m.group(0)
    return ""


def main():
    print("\n" + "=" * 62)
    print("  🌐 도림사거리 역세권 재개발 — 온라인 접속 시작")
    print("=" * 62)

    log_dir = ROOT.parent  # C:\Users\cho\DORIM\

    # ── 1. 백엔드 시작 ───────────────────────────────────────────
    print("\n[1/5] 백엔드 서버 시작 중 (포트 8000)...")
    backend_proc = subprocess.Popen(
        [str(PYTHON_VENV), "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(BACKEND),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(4)
    print("    ✅ 백엔드 실행 중 (PID {})".format(backend_proc.pid))

    # ── 2. 백엔드 터널 ───────────────────────────────────────────
    print("\n[2/5] 백엔드 Cloudflare 터널 연결 중...")
    be_log = log_dir / "backend_tunnel.log"
    be_log.unlink(missing_ok=True)
    backend_tunnel = subprocess.Popen(
        [str(CLOUDFLARED), "tunnel", "--url", "http://localhost:8000"],
        stdout=subprocess.DEVNULL,
        stderr=open(str(be_log), "w"),
    )
    backend_url = find_tunnel_url(be_log, timeout=45)
    if not backend_url:
        print("    ❌ 백엔드 터널 실패 — localhost 모드로 계속합니다.")
        backend_url = "http://localhost:8000"
    else:
        print(f"    ✅ 백엔드 URL: {backend_url}")

    # ── 3. .env.local 업데이트 ──────────────────────────────────
    print(f"\n[3/5] 프론트엔드 환경변수 업데이트...")
    env_local = FRONTEND / ".env.local"
    env_local.write_text(f"NEXT_PUBLIC_API_URL={backend_url}\n", encoding="utf-8")
    print(f"    ✅ NEXT_PUBLIC_API_URL={backend_url}")

    # ── 4. 프론트엔드 시작 ──────────────────────────────────────
    print(f"\n[4/5] 프론트엔드 서버 시작 중 (포트 3000)...")
    fe_log = log_dir / "frontend2.log"
    fe_log.unlink(missing_ok=True)
    frontend_proc = subprocess.Popen(
        [str(NEXT_CMD), "dev", "--port", "3000"],
        cwd=str(FRONTEND),
        stdout=open(str(fe_log), "w", encoding="utf-8"),
        stderr=subprocess.DEVNULL,
    )
    # 프론트엔드 준비 대기
    deadline = time.time() + 30
    while time.time() < deadline:
        time.sleep(2)
        if fe_log.exists() and "Ready" in fe_log.read_text(encoding="utf-8", errors="replace"):
            break
    print(f"    ✅ 프론트엔드 실행 중 (PID {frontend_proc.pid})")

    # ── 5. 프론트엔드 터널 ──────────────────────────────────────
    print(f"\n[5/5] 프론트엔드 Cloudflare 터널 연결 중...")
    fe_tlog = log_dir / "frontend_tunnel.log"
    fe_tlog.unlink(missing_ok=True)
    frontend_tunnel = subprocess.Popen(
        [str(CLOUDFLARED), "tunnel", "--url", "http://localhost:3000"],
        stdout=subprocess.DEVNULL,
        stderr=open(str(fe_tlog), "w"),
    )
    frontend_url = find_tunnel_url(fe_tlog, timeout=45)

    print("\n" + "=" * 62)
    print("  ✅ 온라인 접속 준비 완료!")
    print("=" * 62)
    if frontend_url:
        print(f"\n  🌐 공유 URL: {frontend_url}")
        print(f"\n  ☝️  이 URL을 카카오톡, 문자, 이메일로 공유하세요!")
        print(f"     누구나 스마트폰·PC로 바로 접속 가능합니다.")
    print(f"\n  🔧 백엔드 API: {backend_url}")
    print("\n  종료: Ctrl+C")
    print("=" * 62 + "\n")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n종료 중...")
        for p in [backend_proc, backend_tunnel, frontend_proc, frontend_tunnel]:
            try: p.terminate()
            except: pass
        print("✅ 종료 완료.")


if __name__ == "__main__":
    main()
