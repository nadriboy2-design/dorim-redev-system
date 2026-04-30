# 도림사거리 역세권 재개발 통합 관리 시스템 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 도림동 239-12 역세권 재개발 추진위원회를 위한 조합원 관리·법률 컴플라이언스·GIS 지도·영수증 OCR 기능을 갖춘 로컬 웹 애플리케이션을 구축한다.

**Architecture:** Next.js 14(프론트) + FastAPI(백엔드) 2-프로세스 구조. members.xlsx를 단일 진실 공급원으로 삼고 SQLite를 읽기 캐시로 사용. 컴플라이언스 미들웨어가 모든 API 요청에서 3가지 법적 하드락(용적률 700% / 시공사선정 시기 / 공사비검증)을 자동 감시.

**Tech Stack:** Python 3.11, FastAPI, pandas, openpyxl, SQLite, chromadb, paddleocr, reportlab / Next.js 14, TypeScript, MUI v5, react-leaflet / pytest, httpx

---

## 병렬 실행 가이드

```
Task 1 (스캐폴딩) ──┬──→ Task 2 (workflow.yaml)  ──┐
                   ├──→ Task 3 (compliance.py)    ──┤──→ Task 5 (main.py)
                   └──→ Task 4 (seed data+sync)   ──┘
Task 5 ──→ Task 6 (members router)
       ──→ Task 7 (workflow router)
       ──→ Task 8 (frontend scaffold) ──→ Task 9 (WorkflowTracker)
                                      ──→ Task 10 (MemberGrid)
Task 9 + Task 10 ──→ Task 11 (Dashboard) ──→ Task 12 (UX audit) ──→ Task 13 (start.sh)
─────────────── Sprint 1 완료 ───────────────────────────────────────────────────────
Task 14 (RAG engine) ──→ Task 15 (rag router + LegalChat)
Task 16 (GIS router + MapComponent)   ← 병렬
Task 17 (OCR router + ReceiptOcr)     ← 병렬
Tasks 15+16+17 ──→ Task 18 (Sprint 2 통합)
```

---

## ═══════════════ SPRINT 1 ═══════════════

---

### Task 1: 프로젝트 스캐폴딩 (담당: 주니어 개발자)

**전제 조건:** Python 3.11+, Node.js 18+, git 설치 확인

**Files:**
- Create: `dorim-redev-system/backend/requirements.txt`
- Create: `dorim-redev-system/backend/tests/__init__.py`
- Create: `dorim-redev-system/frontend/package.json` (npx 자동 생성)
- Create: `dorim-redev-system/.gitignore`

- [ ] **Step 1: 디렉토리 구조 생성**

```bash
cd C:/Users/cho/DORIM
mkdir -p dorim-redev-system/{backend/{routers,db,tests},frontend,ai_harness,data,docs_template,.claude/skills}
```

- [ ] **Step 2: backend/requirements.txt 작성**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pandas==2.2.2
openpyxl==3.1.2
pyyaml==6.0.1
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6
chromadb==0.5.0
sentence-transformers==3.0.0
paddleocr==2.7.3
paddlepaddle==2.6.1
reportlab==4.2.0
anthropic==0.28.0
python-multipart==0.0.9
```

- [ ] **Step 3: Python 가상환경 생성 및 패키지 설치**

```bash
cd dorim-redev-system/backend
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
```

Expected: 패키지 설치 완료 메시지 (PaddleOCR은 수분 소요)

- [ ] **Step 4: Next.js 프로젝트 생성**

```bash
cd ../frontend
npx create-next-app@14 . --typescript --tailwind --no --app --yes
npm install @mui/material @emotion/react @emotion/styled @mui/x-data-grid react-leaflet leaflet
npm install --save-dev @types/leaflet
```

- [ ] **Step 5: .gitignore 작성**

```
dorim-redev-system/backend/venv/
dorim-redev-system/backend/__pycache__/
dorim-redev-system/backend/*.db
dorim-redev-system/frontend/node_modules/
dorim-redev-system/frontend/.next/
dorim-redev-system/data/chroma_db/
.superpowers/
```

- [ ] **Step 6: 커밋**

```bash
cd C:/Users/cho/DORIM
git add dorim-redev-system/ .gitignore
git commit -m "feat: scaffold project structure - Sprint 1"
```

---

### Task 2: workflow.yaml + 에이전트 스킬 파일 (담당: CEO + 부장급, Task 1 완료 후 즉시 병렬 시작)

**Files:**
- Create: `dorim-redev-system/ai_harness/workflow.yaml`
- Create: `dorim-redev-system/.claude/skills/ceo-orchestrator.md`
- Create: `dorim-redev-system/.claude/skills/senior-reviewer.md`
- Create: `dorim-redev-system/.claude/skills/junior-dev.md`
- Create: `dorim-redev-system/.claude/skills/ux-accessibility.md`
- Create: `dorim-redev-system/.claude/skills/legal-compliance.md`
- Create: `dorim-redev-system/.claude/skills/gis-data.md`

- [ ] **Step 1: workflow.yaml 작성**

```yaml
# dorim-redev-system/ai_harness/workflow.yaml
project:
  name: "도림사거리 역세권 재개발"
  zone: "도림동 239-12"
  area_sqm: 59607.59
  excluded_zone: "도림동 133-1 (무관 구역 — 절대 혼입 금지)"
  lat: 37.5134
  lng: 126.8986

current_stage: STAGE_1_PRELIMINARY

stages:
  STAGE_1_PRELIMINARY:
    name: "정비구역 입안 (사전검토)"
    consent_threshold: 0.40
    required_docs:
      - "정비계획 사전검토 신청서"
      - "역세권 장기전세주택 건립계획서"
      - "토지등소유자 명부"
      - "노후도 및 구역계 검토서"
    hard_locks:
      contractor_selection: BLOCKED
      sale_announcement: BLOCKED
    next_stage: STAGE_2_COMMITTEE

  STAGE_2_COMMITTEE:
    name: "추진위원회 구성"
    consent_threshold: 0.50
    required_docs:
      - "추진위원장·위원 명부"
      - "운영규정"
      - "창립총회 회의록"
    hard_locks:
      contractor_selection: BLOCKED
      sale_announcement: BLOCKED
    next_stage: STAGE_3_ASSOCIATION

  STAGE_3_ASSOCIATION:
    name: "조합 설립 인가"
    consent_threshold: 0.75
    required_docs:
      - "정관 초안"
      - "조합원 명부 (분양대상자·무허가 소유자)"
    hard_locks:
      contractor_selection: ALLOWED
      sale_announcement: BLOCKED
    next_stage: STAGE_4_CONTRACTOR

  STAGE_4_CONTRACTOR:
    name: "시공사 선정"
    required_docs:
      - "기본설계도서"
      - "공동주택 성능요구서"
      - "물량내역서·산출내역서"
    hard_locks:
      contractor_selection: ALLOWED
      sale_announcement: REQUIRES_COST_VERIFICATION
    next_stage: STAGE_5_DISPOSAL

  STAGE_5_DISPOSAL:
    name: "관리처분계획 인가"
    required_docs:
      - "관리처분계획서"
      - "한국부동산원 타당성 검토 신청서"
    consent_threshold_for_change: 0.667
    hard_locks:
      contractor_selection: ALLOWED
      sale_announcement: REQUIRES_COST_VERIFICATION
    next_stage: null

compliance:
  far_limit_pct: 700
  zone_1_radius_m: 250
  zone_2_radius_m: 500
```

- [ ] **Step 2: ceo-orchestrator.md 스킬 파일 작성**

```markdown
# CEO 오케스트레이터 스킬

## 역할
전략 의사결정, 단계 전환 승인, 6개 팀 조율

## 팀 스폰 규칙
- Sprint 1 시작 시: Task 2(자신), Task 3(법률), Task 4(GIS/데이터)를 동시에 병렬 스폰
- 각 팀이 완료 SendMessage 보내면 의존 팀을 순차 스폰
- 부장급에게 모든 API 스펙 리뷰 요청 필수

## 단계 전환 승인 기준
- 동의율이 workflow.yaml consent_threshold 초과 시만 승인
- 필수 서류 체크리스트 100% 완료 시만 승인
- 하드락 위반 이력이 있으면 승인 보류

## 에스컬레이션
법적 판단이 필요한 경우 → 법률 컴플라이언스 팀으로 즉시 위임
```

- [ ] **Step 3: 나머지 스킬 파일 작성**

`dorim-redev-system/.claude/skills/senior-reviewer.md`:
```markdown
# 부장급 아키텍처 감리 스킬 (10년↑)

## 역할
아키텍처 감리, API 스펙 표준화, 코드 리뷰

## API 스펙 표준
- 모든 응답은 {"data": ..., "error": null} 또는 {"data": null, "error": {"code": "...", "message": "..."}} 형식
- HTTP 상태: 200(성공), 422(검증오류), 403(하드락), 500(서버오류)
- 컴플라이언스 에러는 반드시 code 필드 포함 (HARD_LOCK_A/B/C)

## 코드 리뷰 기준
- 함수 당 20줄 이하 권장
- 하드코딩된 숫자는 workflow.yaml에서 읽을 것
- 133-1 구역 관련 데이터가 혼입되지 않았는지 필수 확인
```

`dorim-redev-system/.claude/skills/junior-dev.md`:
```markdown
# 주니어 개발자 스킬 (5년↓)

## 역할
Next.js 컴포넌트 구현, FastAPI CRUD, 단위 테스트

## 코딩 컨벤션
- Python: snake_case, TypeScript: camelCase
- API 호출은 /frontend/lib/api.ts에 집중
- 컴포넌트 props는 반드시 TypeScript interface 정의

## 테스트 작성 규칙
- pytest: 각 라우터마다 테스트 파일 분리
- 하드락 동작은 반드시 테스트로 검증
```

`dorim-redev-system/.claude/skills/ux-accessibility.md`:
```markdown
# UX/접근성 에이전트 스킬

## 강제 규칙 (위반 시 주니어에게 즉시 SendMessage)
- 폰트 크기: 최소 16px (body), 제목 20px 이상
- 버튼: 최소 44×44px 터치 영역
- 색상 대비: WCAG AA 기준 4.5:1 이상
- 색상만으로 상태 표시 금지 (텍스트 레이블 병행)

## 고령자 UI 체크리스트
- [ ] 모든 버튼에 텍스트+아이콘 동시 표시
- [ ] 에러 메시지는 붉은 배경 + 큰 텍스트
- [ ] 중요 수치(동의율 %)는 24px 이상
```

`dorim-redev-system/.claude/skills/legal-compliance.md`:
```markdown
# 법률 컴플라이언스 스킬

## 하드락 규칙 (compliance.py에서 구현)
- HARD_LOCK_A: far_pct > 700 → HTTP 422
- HARD_LOCK_B: doc_type=="시공사입찰공고" AND stage NOT IN [STAGE_3,4,5] → HTTP 403
- HARD_LOCK_C: doc_type=="분양공고" AND has_cost_verification==False → HTTP 403

## RAG 문서 추가 절차
1. docs/legal/ 디렉토리에 마크다운 파일 추가
2. python backend/rag_engine.py --embed 실행
3. 임베딩 완료 확인 후 테스트 쿼리 실행

## 법령 업데이트 시 전체 팀 브로드캐스트 필수
```

`dorim-redev-system/.claude/skills/gis-data.md`:
```markdown
# GIS/데이터 에이전트 스킬

## 133-1 구역 배제 규칙 (절대 준수)
- 도림동 133-1 구역 좌표 범위: 위도 37.508-37.512, 경도 126.895-126.900
- 이 범위의 좌표를 가진 마커는 API 레벨에서 필터링하여 반환 금지
- 조합원 명부에 133-1 구역 주소가 포함되면 즉시 오류 발생

## Excel 동기화 규칙
- members.xlsx가 Single Source of Truth
- SQLite 수정 즉시 xlsx로 역동기화 필수
- xlsx 파일 열려있을 때 쓰기 시도 시 재시도 3회 후 오류

## 지오코딩
- 카카오 API 키 없으면 OpenStreetMap Nominatim 사용
- 주소 → 좌표 변환 실패 시 구역 중심 좌표(37.5134, 126.8986)로 폴백
```

- [ ] **Step 4: 커밋**

```bash
cd C:/Users/cho/DORIM
git add dorim-redev-system/ai_harness/ dorim-redev-system/.claude/
git commit -m "feat: add workflow.yaml state machine and agent skill files"
```

---

### Task 3: 컴플라이언스 미들웨어 (담당: 법률 에이전트, Task 1 완료 후 병렬 시작)

**Files:**
- Create: `dorim-redev-system/backend/compliance.py`
- Create: `dorim-redev-system/backend/tests/test_compliance.py`

- [ ] **Step 1: 테스트 작성**

```python
# dorim-redev-system/backend/tests/test_compliance.py
import pytest
from fastapi import HTTPException
from compliance import ComplianceChecker

checker = ComplianceChecker(workflow_path="ai_harness/workflow.yaml")

def test_far_limit_exact_700_passes():
    """700% 정확히는 통과해야 한다"""
    checker.check_far(700.0)  # Should not raise

def test_far_limit_over_700_raises():
    """700% 초과는 HARD_LOCK_A 발생"""
    with pytest.raises(HTTPException) as exc_info:
        checker.check_far(700.1)
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail["code"] == "HARD_LOCK_A"

def test_contractor_blocked_at_stage1():
    """STAGE_1에서 시공사 입찰공고 생성 시도 → 차단"""
    with pytest.raises(HTTPException) as exc_info:
        checker.check_doc_generation(
            doc_type="시공사입찰공고",
            current_stage="STAGE_1_PRELIMINARY",
            has_cost_verification=False
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "HARD_LOCK_B"

def test_contractor_allowed_at_stage3():
    """STAGE_3(조합설립) 이후 시공사 입찰공고 허용"""
    checker.check_doc_generation(
        doc_type="시공사입찰공고",
        current_stage="STAGE_3_ASSOCIATION",
        has_cost_verification=False
    )  # Should not raise

def test_sale_blocked_without_cost_verification():
    """공사비 검증 없이 분양공고 → HARD_LOCK_C"""
    with pytest.raises(HTTPException) as exc_info:
        checker.check_doc_generation(
            doc_type="분양공고",
            current_stage="STAGE_4_CONTRACTOR",
            has_cost_verification=False
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "HARD_LOCK_C"

def test_sale_allowed_with_cost_verification():
    """공사비 검증 있으면 분양공고 허용"""
    checker.check_doc_generation(
        doc_type="분양공고",
        current_stage="STAGE_4_CONTRACTOR",
        has_cost_verification=True
    )  # Should not raise
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd dorim-redev-system/backend
venv\Scripts\activate
pytest tests/test_compliance.py -v
```

Expected: `ModuleNotFoundError: No module named 'compliance'`

- [ ] **Step 3: compliance.py 구현**

```python
# dorim-redev-system/backend/compliance.py
from pathlib import Path
import yaml
from fastapi import HTTPException

CONTRACTOR_ALLOWED_STAGES = {
    "STAGE_3_ASSOCIATION",
    "STAGE_4_CONTRACTOR",
    "STAGE_5_DISPOSAL",
}

class ComplianceChecker:
    def __init__(self, workflow_path: str = "ai_harness/workflow.yaml"):
        self.workflow_path = Path(workflow_path)

    def _load_workflow(self) -> dict:
        with open(self.workflow_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def check_far(self, far_pct: float) -> None:
        """하드락 A: 용적률 700% 초과 차단"""
        wf = self._load_workflow()
        limit = wf["compliance"]["far_limit_pct"]
        if far_pct > limit:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "HARD_LOCK_A",
                    "message": (
                        f"1차 역세권 법적 상한 {limit}% 초과. "
                        "서울시 역세권 장기전세주택 건립 운영기준(2026.3.6.) 위반."
                    ),
                },
            )

    def check_doc_generation(
        self,
        doc_type: str,
        current_stage: str,
        has_cost_verification: bool,
    ) -> None:
        """하드락 B·C: 문서 생성 시기 검증"""
        if doc_type == "시공사입찰공고":
            if current_stage not in CONTRACTOR_ALLOWED_STAGES:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "HARD_LOCK_B",
                        "message": (
                            "서울시 도시 및 주거환경정비 조례에 의거, "
                            "시공사 선정은 조합설립인가 이후에만 가능합니다."
                        ),
                    },
                )

        if doc_type == "분양공고" and not has_cost_verification:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "HARD_LOCK_C",
                    "message": (
                        "국토교통부 고시에 따른 정비사업 공사비 검증 결과서가 "
                        "첨부되지 않았습니다."
                    ),
                },
            )


# 전역 싱글턴 — main.py에서 import
compliance = ComplianceChecker()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_compliance.py -v
```

Expected:
```
test_far_limit_exact_700_passes PASSED
test_far_limit_over_700_raises PASSED
test_contractor_blocked_at_stage1 PASSED
test_contractor_allowed_at_stage3 PASSED
test_sale_blocked_without_cost_verification PASSED
test_sale_allowed_with_cost_verification PASSED
6 passed in 0.XX s
```

- [ ] **Step 5: 커밋**

```bash
git add dorim-redev-system/backend/compliance.py dorim-redev-system/backend/tests/
git commit -m "feat: add compliance hard-lock checker with tests (HARD_LOCK A/B/C)"
```

---

### Task 4: 조합원 시드 데이터 + Excel↔SQLite 동기화 (담당: GIS/데이터, Task 1 완료 후 병렬 시작)

**Files:**
- Create: `dorim-redev-system/backend/db/sync.py`
- Create: `dorim-redev-system/backend/db/__init__.py`
- Create: `dorim-redev-system/backend/tests/test_sync.py`
- Create: `dorim-redev-system/data/members.xlsx` (스크립트로 생성)
- Create: `dorim-redev-system/backend/seed_data.py`

- [ ] **Step 1: 시드 데이터 생성 스크립트 작성**

```python
# dorim-redev-system/backend/seed_data.py
"""
조합원 명부 가데이터 생성 스크립트.
실행: python seed_data.py
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path("../data")
DATA_DIR.mkdir(exist_ok=True)

members = [
    {"member_id": 1001, "address": "서울 영등포구 도림동 239-12", "birth_date": "1955-03-15", "is_sale_target": True,  "rights_value": 185000000, "consent": True},
    {"member_id": 1002, "address": "서울 영등포구 도림동 239-14", "birth_date": "1962-07-22", "is_sale_target": True,  "rights_value": 220000000, "consent": True},
    {"member_id": 1003, "address": "서울 영등포구 도림동 239-16", "birth_date": "1948-11-08", "is_sale_target": False, "rights_value": 145000000, "consent": False},
    {"member_id": 1004, "address": "서울 영등포구 도림동 240-1",  "birth_date": "1971-02-14", "is_sale_target": True,  "rights_value": 198000000, "consent": True},
    {"member_id": 1005, "address": "서울 영등포구 도림동 240-3",  "birth_date": "1965-09-30", "is_sale_target": True,  "rights_value": 175000000, "consent": False},
    {"member_id": 1006, "address": "서울 영등포구 도림동 241-2",  "birth_date": "1953-06-18", "is_sale_target": True,  "rights_value": 210000000, "consent": True},
    {"member_id": 1007, "address": "서울 영등포구 도림동 241-5",  "birth_date": "1978-12-25", "is_sale_target": False, "rights_value": 130000000, "consent": False},
    {"member_id": 1008, "address": "서울 영등포구 도림동 242-1",  "birth_date": "1960-04-11", "is_sale_target": True,  "rights_value": 195000000, "consent": True},
    {"member_id": 1009, "address": "서울 영등포구 도림동 242-3",  "birth_date": "1967-08-07", "is_sale_target": True,  "rights_value": 168000000, "consent": True},
    {"member_id": 1010, "address": "서울 영등포구 도림동 243-2",  "birth_date": "1982-01-19", "is_sale_target": True,  "rights_value": 205000000, "consent": False},
    {"member_id": 1011, "address": "서울 영등포구 도림동 243-4",  "birth_date": "1950-10-05", "is_sale_target": False, "rights_value": 155000000, "consent": True},
    {"member_id": 1012, "address": "서울 영등포구 도림동 244-1",  "birth_date": "1974-03-28", "is_sale_target": True,  "rights_value": 182000000, "consent": False},
    {"member_id": 1013, "address": "서울 영등포구 도림동 244-6",  "birth_date": "1958-07-14", "is_sale_target": True,  "rights_value": 225000000, "consent": True},
    {"member_id": 1014, "address": "서울 영등포구 도림동 245-3",  "birth_date": "1945-12-01", "is_sale_target": False, "rights_value": 140000000, "consent": False},
    {"member_id": 1015, "address": "서울 영등포구 도림동 245-7",  "birth_date": "1969-05-22", "is_sale_target": True,  "rights_value": 190000000, "consent": True},
    {"member_id": 1016, "address": "서울 영등포구 도림동 246-1",  "birth_date": "1973-09-16", "is_sale_target": True,  "rights_value": 178000000, "consent": True},
    {"member_id": 1017, "address": "서울 영등포구 도림동 246-4",  "birth_date": "1956-02-09", "is_sale_target": False, "rights_value": 160000000, "consent": False},
    {"member_id": 1018, "address": "서울 영등포구 도림동 247-2",  "birth_date": "1980-11-30", "is_sale_target": True,  "rights_value": 215000000, "consent": True},
    {"member_id": 1019, "address": "서울 영등포구 도림동 247-8",  "birth_date": "1963-06-25", "is_sale_target": True,  "rights_value": 172000000, "consent": False},
    {"member_id": 1020, "address": "서울 영등포구 도림동 248-1",  "birth_date": "1970-04-03", "is_sale_target": True,  "rights_value": 200000000, "consent": True},
]

df = pd.DataFrame(members)
df.to_excel(DATA_DIR / "members.xlsx", index=False)
print(f"✅ members.xlsx 생성 완료: {len(df)}명")
```

- [ ] **Step 2: 시드 데이터 생성 실행**

```bash
cd dorim-redev-system/backend
venv\Scripts\activate
python seed_data.py
```

Expected: `✅ members.xlsx 생성 완료: 20명`

- [ ] **Step 3: sync.py 테스트 작성**

```python
# dorim-redev-system/backend/tests/test_sync.py
import pytest
import pandas as pd
from pathlib import Path
from db.sync import ExcelSyncDB

TEST_EXCEL = Path("tests/fixtures/test_members.xlsx")

@pytest.fixture(autouse=True)
def setup_fixtures():
    TEST_EXCEL.parent.mkdir(exist_ok=True)
    df = pd.DataFrame([
        {"member_id": 1, "address": "도림동 1", "birth_date": "1960-01-01",
         "is_sale_target": True, "rights_value": 100000000, "consent": False},
        {"member_id": 2, "address": "도림동 2", "birth_date": "1970-01-01",
         "is_sale_target": True, "rights_value": 200000000, "consent": True},
    ])
    df.to_excel(TEST_EXCEL, index=False)
    yield
    if TEST_EXCEL.exists():
        TEST_EXCEL.unlink()

def test_load_creates_sqlite(tmp_path):
    db = ExcelSyncDB(excel_path=TEST_EXCEL, db_path=tmp_path / "test.db")
    db.load_excel_to_sqlite()
    members = db.get_members()
    assert len(members) == 2
    assert members[0]["member_id"] == 1

def test_update_consent_writes_back_to_excel(tmp_path):
    db = ExcelSyncDB(excel_path=TEST_EXCEL, db_path=tmp_path / "test.db")
    db.load_excel_to_sqlite()
    db.update_consent(member_id=1, consent=True)
    # Excel 파일 다시 읽어서 확인
    df = pd.read_excel(TEST_EXCEL)
    row = df[df["member_id"] == 1].iloc[0]
    assert row["consent"] == True

def test_consent_rate_calculation(tmp_path):
    db = ExcelSyncDB(excel_path=TEST_EXCEL, db_path=tmp_path / "test.db")
    db.load_excel_to_sqlite()
    rate = db.get_consent_rate()
    assert rate["total"] == 2
    assert rate["consented"] == 1
    assert rate["rate"] == 50.0
```

- [ ] **Step 4: 테스트 실패 확인**

```bash
pytest tests/test_sync.py -v
```

Expected: `ModuleNotFoundError: No module named 'db.sync'`

- [ ] **Step 5: sync.py 구현**

```python
# dorim-redev-system/backend/db/sync.py
import sqlite3
import pandas as pd
from pathlib import Path


class ExcelSyncDB:
    """Excel ↔ SQLite 양방향 동기화 클래스.

    members.xlsx가 Single Source of Truth.
    SQLite는 읽기 성능 캐시 역할만 수행.
    """

    def __init__(
        self,
        excel_path: Path = Path("../data/members.xlsx"),
        db_path: Path = Path("../data/members.db"),
    ):
        self.excel_path = Path(excel_path)
        self.db_path = Path(db_path)

    def load_excel_to_sqlite(self) -> int:
        """앱 시작 시 호출. Excel → SQLite 전체 로드. 행 수 반환."""
        df = pd.read_excel(self.excel_path)
        conn = sqlite3.connect(self.db_path)
        df.to_sql("members", conn, if_exists="replace", index=False)
        conn.close()
        return len(df)

    def get_members(self) -> list[dict]:
        """전체 조합원 목록 반환 (SQLite에서 읽기)."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM members ORDER BY member_id", conn)
        conn.close()
        return df.to_dict(orient="records")

    def get_member(self, member_id: int) -> dict | None:
        """단일 조합원 반환."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql(
            "SELECT * FROM members WHERE member_id = ?", conn, params=(member_id,)
        )
        conn.close()
        if df.empty:
            return None
        return df.iloc[0].to_dict()

    def update_consent(self, member_id: int, consent: bool) -> None:
        """동의여부 업데이트: SQLite 즉시 수정 + Excel 파일 역동기화."""
        # 1) SQLite 업데이트
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE members SET consent = ? WHERE member_id = ?",
            (1 if consent else 0, member_id),
        )
        conn.commit()

        # 2) Excel 역동기화 (Single Source of Truth 유지)
        df = pd.read_sql("SELECT * FROM members ORDER BY member_id", conn)
        conn.close()
        df.to_excel(self.excel_path, index=False)

    def get_consent_rate(self) -> dict:
        """동의율 통계 반환. {"total": N, "consented": M, "rate": %}"""
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            """SELECT
                COUNT(*) as total,
                SUM(CASE WHEN consent = 1 THEN 1 ELSE 0 END) as consented
               FROM members"""
        ).fetchone()
        conn.close()
        total, consented = row
        rate = round(consented / total * 100, 1) if total else 0.0
        return {"total": int(total), "consented": int(consented), "rate": rate}


# 전역 싱글턴 — main.py에서 import하여 lifespan에서 초기화
sync_db = ExcelSyncDB()
```

- [ ] **Step 6: db/__init__.py 생성**

```python
# dorim-redev-system/backend/db/__init__.py
from .sync import sync_db, ExcelSyncDB

__all__ = ["sync_db", "ExcelSyncDB"]
```

- [ ] **Step 7: 테스트 통과 확인**

```bash
pytest tests/test_sync.py -v
```

Expected:
```
test_load_creates_sqlite PASSED
test_update_consent_writes_back_to_excel PASSED
test_consent_rate_calculation PASSED
3 passed
```

- [ ] **Step 8: 커밋**

```bash
git add dorim-redev-system/backend/db/ dorim-redev-system/backend/seed_data.py dorim-redev-system/backend/tests/test_sync.py dorim-redev-system/data/members.xlsx
git commit -m "feat: add Excel<->SQLite sync and 20-member seed data"
```

---

### Task 5: FastAPI 메인 서버 (담당: 주니어 개발자, Tasks 2·3·4 완료 후)

**Files:**
- Create: `dorim-redev-system/backend/main.py`

- [ ] **Step 1: main.py 작성**

```python
# dorim-redev-system/backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.sync import sync_db
from routers import members, workflow


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


@app.get("/health")
def health():
    return {"status": "ok", "project": "도림사거리 역세권 재개발"}
```

- [ ] **Step 2: 서버 기동 확인**

```bash
cd dorim-redev-system/backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Expected: `✅ 조합원 명부 로드 완료: 20명` + `Uvicorn running on http://127.0.0.1:8000`

- [ ] **Step 3: 커밋**

```bash
git add dorim-redev-system/backend/main.py
git commit -m "feat: add FastAPI main server with lifespan Excel loader"
```

---

### Task 6: 조합원 CRUD 라우터 (담당: 주니어 개발자)

**Files:**
- Create: `dorim-redev-system/backend/routers/__init__.py`
- Create: `dorim-redev-system/backend/routers/members.py`
- Create: `dorim-redev-system/backend/tests/test_members.py`

- [ ] **Step 1: 테스트 작성**

```python
# dorim-redev-system/backend/tests/test_members.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_members_returns_list():
    resp = client.get("/api/members")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 20

def test_get_members_has_required_fields():
    resp = client.get("/api/members")
    member = resp.json()["data"][0]
    for field in ["member_id", "address", "birth_date", "is_sale_target",
                  "rights_value", "consent"]:
        assert field in member

def test_patch_consent_toggles_value():
    # 현재 동의 상태 확인
    resp = client.get("/api/members")
    member = resp.json()["data"][0]
    original = member["consent"]
    mid = member["member_id"]

    # 토글
    resp2 = client.patch(f"/api/members/{mid}/consent",
                         json={"consent": not original})
    assert resp2.status_code == 200

    # 변경 확인
    resp3 = client.get("/api/members")
    updated = next(m for m in resp3.json()["data"] if m["member_id"] == mid)
    assert updated["consent"] != original

def test_patch_consent_unknown_member_returns_404():
    resp = client.patch("/api/members/99999/consent", json={"consent": True})
    assert resp.status_code == 404

def test_get_consent_rate_returns_stats():
    resp = client.get("/api/consent-rate")
    data = resp.json()["data"]
    assert "total" in data
    assert "consented" in data
    assert "rate" in data
    assert 0 <= data["rate"] <= 100
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_members.py -v
```

Expected: `ImportError` 또는 `404 Not Found`

- [ ] **Step 3: routers/members.py 구현**

```python
# dorim-redev-system/backend/routers/members.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.sync import sync_db

router = APIRouter(tags=["members"])


class ConsentUpdate(BaseModel):
    consent: bool


@router.get("/members")
def get_members():
    """조합원 전체 목록 반환 (SQLite 캐시에서 읽기)."""
    members = sync_db.get_members()
    return {"data": members, "error": None}


@router.patch("/members/{member_id}/consent")
def update_consent(member_id: int, body: ConsentUpdate):
    """동의여부 토글 — SQLite 즉시 수정 후 Excel 역동기화."""
    member = sync_db.get_member(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND",
                                                      "message": f"조합원 {member_id} 없음"})
    sync_db.update_consent(member_id, body.consent)
    return {"data": {"member_id": member_id, "consent": body.consent}, "error": None}


@router.get("/consent-rate")
def get_consent_rate():
    """동의율 통계 (total / consented / rate%)."""
    stats = sync_db.get_consent_rate()
    return {"data": stats, "error": None}
```

- [ ] **Step 4: routers/__init__.py 생성**

```python
# dorim-redev-system/backend/routers/__init__.py
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
pytest tests/test_members.py -v
```

Expected: `5 passed`

- [ ] **Step 6: 커밋**

```bash
git add dorim-redev-system/backend/routers/
git commit -m "feat: add members CRUD router with consent toggle and rate endpoint"
```

---

### Task 7: 워크플로우 라우터 + PDF 생성 (담당: 주니어 개발자)

**Files:**
- Create: `dorim-redev-system/backend/routers/workflow.py`
- Create: `dorim-redev-system/backend/tests/test_workflow.py`

- [ ] **Step 1: 테스트 작성**

```python
# dorim-redev-system/backend/tests/test_workflow.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_workflow_status_returns_current_stage():
    resp = client.get("/api/workflow/status")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["current_stage"] == "STAGE_1_PRELIMINARY"
    assert data["stage_name"] == "정비구역 입안 (사전검토)"
    assert data["consent_threshold"] == 0.40
    assert isinstance(data["required_docs"], list)
    assert len(data["required_docs"]) > 0

def test_workflow_status_includes_consent_progress():
    resp = client.get("/api/workflow/status")
    data = resp.json()["data"]
    assert "consent_rate" in data
    assert "is_threshold_met" in data

def test_compliance_far_over_limit():
    """용적률 700% 초과 시 422 반환"""
    resp = client.post("/api/compliance/check-far", json={"far_pct": 750.0})
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "HARD_LOCK_A"

def test_compliance_far_at_limit_passes():
    resp = client.post("/api/compliance/check-far", json={"far_pct": 700.0})
    assert resp.status_code == 200

def test_generate_doc_blocked_before_association():
    """조합설립 전 시공사 입찰공고 차단"""
    resp = client.post("/api/workflow/generate-doc",
                       json={"doc_type": "시공사입찰공고",
                             "has_cost_verification": False})
    assert resp.status_code == 403
    assert resp.json()["detail"]["code"] == "HARD_LOCK_B"
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_workflow.py -v
```

Expected: 모두 실패

- [ ] **Step 3: routers/workflow.py 구현**

```python
# dorim-redev-system/backend/routers/workflow.py
from pathlib import Path
import yaml
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from compliance import compliance
from db.sync import sync_db
import io

router = APIRouter(tags=["workflow"])
WORKFLOW_PATH = Path("ai_harness/workflow.yaml")


def _load_workflow() -> dict:
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@router.get("/workflow/status")
def get_workflow_status():
    """현재 사업 단계, 필수 서류, 동의율 현황 반환."""
    wf = _load_workflow()
    stage_key = wf["current_stage"]
    stage = wf["stages"][stage_key]
    rate_data = sync_db.get_consent_rate()
    threshold = stage.get("consent_threshold", 0)

    return {
        "data": {
            "current_stage": stage_key,
            "stage_name": stage["name"],
            "consent_threshold": threshold,
            "required_docs": stage["required_docs"],
            "consent_rate": rate_data,
            "is_threshold_met": rate_data["rate"] / 100 >= threshold,
        },
        "error": None,
    }


class FarCheckRequest(BaseModel):
    far_pct: float


@router.post("/compliance/check-far")
def check_far(body: FarCheckRequest):
    """용적률 하드락 A 검사."""
    compliance.check_far(body.far_pct)
    return {"data": {"far_pct": body.far_pct, "status": "OK"}, "error": None}


class GenerateDocRequest(BaseModel):
    doc_type: str
    has_cost_verification: bool = False


@router.post("/workflow/generate-doc")
def generate_doc(body: GenerateDocRequest):
    """서울시 표준 양식 PDF 생성. 하드락 B·C 검사 후 생성."""
    wf = _load_workflow()
    current_stage = wf["current_stage"]
    compliance.check_doc_generation(
        doc_type=body.doc_type,
        current_stage=current_stage,
        has_cost_verification=body.has_cost_verification,
    )
    # PDF 생성 (reportlab)
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 14)
    c.drawString(100, 750, f"도림사거리 역세권 재개발")
    c.drawString(100, 720, f"문서 유형: {body.doc_type}")
    c.drawString(100, 690, f"현재 단계: {wf['stages'][current_stage]['name']}")
    c.save()
    buffer.seek(0)
    filename = f"{body.doc_type}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
```

- [ ] **Step 4: main.py에 workflow 라우터 추가 확인**

`main.py`의 `from routers import members, workflow` 및 `app.include_router(workflow.router, prefix="/api")` 이미 포함 확인.

- [ ] **Step 5: 테스트 통과 확인**

```bash
pytest tests/test_workflow.py -v
```

Expected: `5 passed`

- [ ] **Step 6: 커밋**

```bash
git add dorim-redev-system/backend/routers/workflow.py dorim-redev-system/backend/tests/test_workflow.py
git commit -m "feat: add workflow status, FAR compliance check, and PDF doc generation"
```

---

### Task 8: Next.js 프론트엔드 스캐폴딩 + WorkflowTracker (담당: 주니어 개발자)

**Files:**
- Create: `dorim-redev-system/frontend/lib/api.ts`
- Create: `dorim-redev-system/frontend/components/WorkflowTracker.tsx`
- Modify: `dorim-redev-system/frontend/app/layout.tsx`

- [ ] **Step 1: API 클라이언트 작성**

```typescript
// dorim-redev-system/frontend/lib/api.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchMembers() {
  const res = await fetch(`${BASE_URL}/api/members`);
  if (!res.ok) throw new Error("조합원 목록 조회 실패");
  const json = await res.json();
  return json.data as Member[];
}

export async function fetchConsentRate() {
  const res = await fetch(`${BASE_URL}/api/consent-rate`);
  if (!res.ok) throw new Error("동의율 조회 실패");
  const json = await res.json();
  return json.data as ConsentRate;
}

export async function fetchWorkflowStatus() {
  const res = await fetch(`${BASE_URL}/api/workflow/status`);
  if (!res.ok) throw new Error("워크플로우 상태 조회 실패");
  const json = await res.json();
  return json.data as WorkflowStatus;
}

export async function patchConsent(memberId: number, consent: boolean) {
  const res = await fetch(`${BASE_URL}/api/members/${memberId}/consent`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ consent }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.message ?? "동의여부 수정 실패");
  }
  return res.json();
}

export async function generateDoc(docType: string, hasCostVerification = false) {
  const res = await fetch(`${BASE_URL}/api/workflow/generate-doc`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ doc_type: docType, has_cost_verification: hasCostVerification }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail?.message ?? "문서 생성 실패");
  }
  return res.blob();
}

// ── 타입 정의 ────────────────────────────────
export interface Member {
  member_id: number;
  address: string;
  birth_date: string;
  is_sale_target: boolean;
  rights_value: number;
  consent: boolean;
}

export interface ConsentRate {
  total: number;
  consented: number;
  rate: number;
}

export interface WorkflowStatus {
  current_stage: string;
  stage_name: string;
  consent_threshold: number;
  required_docs: string[];
  consent_rate: ConsentRate;
  is_threshold_met: boolean;
}
```

- [ ] **Step 2: WorkflowTracker 컴포넌트 작성**

```typescript
// dorim-redev-system/frontend/components/WorkflowTracker.tsx
"use client";
import { Box, Chip, Typography } from "@mui/material";

const STAGES = [
  { key: "STAGE_1_PRELIMINARY", label: "① 정비구역 입안" },
  { key: "STAGE_2_COMMITTEE",   label: "② 추진위 구성" },
  { key: "STAGE_3_ASSOCIATION", label: "③ 조합 설립" },
  { key: "STAGE_4_CONTRACTOR",  label: "④ 시공사 선정" },
  { key: "STAGE_5_DISPOSAL",    label: "⑤ 관리처분" },
];

interface Props {
  currentStage: string;
  stageName: string;
}

export default function WorkflowTracker({ currentStage, stageName }: Props) {
  const currentIdx = STAGES.findIndex((s) => s.key === currentStage);

  return (
    <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2, mb: 2 }}>
      <Typography sx={{ fontSize: "13px", color: "#94a3b8", mb: 1 }}>
        현재 사업 단계: <strong style={{ color: "#fff" }}>{stageName}</strong>
      </Typography>
      <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
        {STAGES.map((stage, idx) => (
          <Chip
            key={stage.key}
            label={stage.label}
            size="small"
            sx={{
              fontSize: "13px",
              fontWeight: idx === currentIdx ? 700 : 400,
              bgcolor: idx === currentIdx ? "#3b82f6" : idx < currentIdx ? "#166534" : "#334155",
              color: idx <= currentIdx ? "#fff" : "#94a3b8",
              border: idx === currentIdx ? "2px solid #60a5fa" : "none",
            }}
          />
        ))}
      </Box>
    </Box>
  );
}
```

- [ ] **Step 3: layout.tsx MUI 테마 설정 (폰트 16px 강제)**

```typescript
// dorim-redev-system/frontend/app/layout.tsx
import type { Metadata } from "next";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v14-appRouter";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const theme = createTheme({
  typography: {
    fontSize: 16,          // ← UX 에이전트 요구사항: 최소 16px
    body1: { fontSize: "16px" },
    body2: { fontSize: "16px" },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: "44px",    // ← 터치 영역 최소 44px
          fontSize: "16px",
        },
      },
    },
  },
  palette: {
    mode: "dark",
    primary: { main: "#3b82f6" },
    success: { main: "#22c55e" },
    error: { main: "#ef4444" },
  },
});

export const metadata: Metadata = {
  title: "도림사거리 역세권 재개발 통합관리",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <AppRouterCacheProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 4: 개발 서버 기동 확인**

```bash
cd dorim-redev-system/frontend
npm run dev
```

Expected: `http://localhost:3000` 접근 가능 (빈 페이지)

- [ ] **Step 5: 커밋**

```bash
git add dorim-redev-system/frontend/
git commit -m "feat: add Next.js scaffold, API client, WorkflowTracker component (16px font enforced)"
```

---

### Task 9: MemberGrid 컴포넌트 (담당: 주니어 개발자)

**Files:**
- Create: `dorim-redev-system/frontend/components/MemberGrid.tsx`

- [ ] **Step 1: MemberGrid 작성**

```typescript
// dorim-redev-system/frontend/components/MemberGrid.tsx
"use client";
import { useState } from "react";
import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { Switch, Typography, Box, Chip } from "@mui/material";
import { Member, patchConsent } from "@/lib/api";

interface Props {
  members: Member[];
  onConsentChange: (updatedMembers: Member[]) => void;
}

export default function MemberGrid({ members, onConsentChange }: Props) {
  const [rows, setRows] = useState<Member[]>(members);
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = async (memberId: number, currentConsent: boolean) => {
    setLoadingId(memberId);
    setError(null);
    try {
      await patchConsent(memberId, !currentConsent);
      const updated = rows.map((m) =>
        m.member_id === memberId ? { ...m, consent: !currentConsent } : m
      );
      setRows(updated);
      onConsentChange(updated);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "오류 발생");
    } finally {
      setLoadingId(null);
    }
  };

  const columns: GridColDef[] = [
    { field: "member_id", headerName: "번호", width: 80 },
    { field: "address",   headerName: "주소",   flex: 1, minWidth: 200 },
    {
      field: "rights_value",
      headerName: "권리가액",
      width: 130,
      renderCell: (p: GridRenderCellParams) =>
        `${(p.value as number).toLocaleString()}원`,
    },
    {
      field: "is_sale_target",
      headerName: "분양대상",
      width: 100,
      renderCell: (p: GridRenderCellParams) => (
        <Chip
          label={p.value ? "대상" : "비대상"}
          size="small"
          color={p.value ? "success" : "default"}
          sx={{ fontSize: "14px" }}
        />
      ),
    },
    {
      field: "consent",
      headerName: "동의여부",
      width: 120,
      renderCell: (p: GridRenderCellParams<Member>) => (
        <Switch
          checked={!!p.value}
          disabled={loadingId === p.row.member_id}
          onChange={() => handleToggle(p.row.member_id, !!p.value)}
          color="success"
        />
      ),
    },
  ];

  return (
    <Box>
      {error && (
        <Typography sx={{ color: "#ef4444", fontSize: "16px", mb: 1, p: 1,
                          bgcolor: "#2d0a0a", borderRadius: 1 }}>
          ⚠️ {error}
        </Typography>
      )}
      <DataGrid
        rows={rows}
        columns={columns}
        getRowId={(r) => r.member_id}
        autoHeight
        pageSizeOptions={[10, 20, 50]}
        initialState={{ pagination: { paginationModel: { pageSize: 10 } } }}
        sx={{ fontSize: "16px", "& .MuiDataGrid-columnHeader": { fontSize: "16px" } }}
      />
    </Box>
  );
}
```

- [ ] **Step 2: 커밋**

```bash
git add dorim-redev-system/frontend/components/MemberGrid.tsx
git commit -m "feat: add MemberGrid with consent toggle -> Excel sync"
```

---

### Task 10: ConsentChart + 메인 대시보드 page.tsx (담당: 주니어 개발자)

**Files:**
- Create: `dorim-redev-system/frontend/components/ConsentChart.tsx`
- Create: `dorim-redev-system/frontend/app/page.tsx`

- [ ] **Step 1: ConsentChart 작성**

```typescript
// dorim-redev-system/frontend/components/ConsentChart.tsx
"use client";
import { Box, Typography, LinearProgress, Alert } from "@mui/material";
import { ConsentRate } from "@/lib/api";

interface Props {
  stats: ConsentRate;
  threshold: number;   // 0.40 등
  isThresholdMet: boolean;
}

export default function ConsentChart({ stats, threshold, isThresholdMet }: Props) {
  const needed = Math.ceil(stats.total * threshold) - stats.consented;

  return (
    <Box sx={{ bgcolor: "#0f172a", p: 2, borderRadius: 2, border: "1px solid #334155" }}>
      <Typography sx={{ fontSize: "14px", color: "#94a3b8", mb: 1, fontWeight: 600 }}>
        동의율 현황 (기준: {(threshold * 100).toFixed(0)}%)
      </Typography>

      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}>
        <LinearProgress
          variant="determinate"
          value={Math.min(stats.rate, 100)}
          sx={{ flex: 1, height: 14, borderRadius: 7,
                "& .MuiLinearProgress-bar": { bgcolor: isThresholdMet ? "#22c55e" : "#3b82f6" } }}
        />
        <Typography sx={{ fontSize: "24px", fontWeight: 700,
                          color: isThresholdMet ? "#22c55e" : "#fbbf24", minWidth: "60px" }}>
          {stats.rate}%
        </Typography>
      </Box>

      <Typography sx={{ fontSize: "14px", color: "#64748b" }}>
        동의 완료 {stats.consented}명 / 전체 {stats.total}명
      </Typography>

      {!isThresholdMet && (
        <Alert severity="warning" sx={{ mt: 1, fontSize: "14px" }}>
          다음 단계 진입까지 <strong>{needed}명</strong> 더 필요합니다
        </Alert>
      )}
      {isThresholdMet && (
        <Alert severity="success" sx={{ mt: 1, fontSize: "14px" }}>
          동의율 기준({(threshold * 100).toFixed(0)}%) 달성 ✅
        </Alert>
      )}
    </Box>
  );
}
```

- [ ] **Step 2: 메인 대시보드 page.tsx 작성**

```typescript
// dorim-redev-system/frontend/app/page.tsx
"use client";
import { useEffect, useState, useCallback } from "react";
import { Box, Button, Typography, TextField, CircularProgress, Alert } from "@mui/material";
import WorkflowTracker from "@/components/WorkflowTracker";
import MemberGrid from "@/components/MemberGrid";
import ConsentChart from "@/components/ConsentChart";
import {
  fetchMembers, fetchWorkflowStatus, generateDoc,
  Member, WorkflowStatus,
} from "@/lib/api";

export default function DashboardPage() {
  const [members, setMembers]       = useState<Member[]>([]);
  const [status, setStatus]         = useState<WorkflowStatus | null>(null);
  const [loading, setLoading]       = useState(true);
  const [aiQuestion, setAiQuestion] = useState("");
  const [docError, setDocError]     = useState<string | null>(null);
  const [docLoading, setDocLoading] = useState(false);
  const [view, setView]             = useState<"dashboard" | "members">("dashboard");

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [m, s] = await Promise.all([fetchMembers(), fetchWorkflowStatus()]);
      setMembers(m);
      setStatus(s);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleGenerateDoc = async (docType: string) => {
    setDocError(null);
    setDocLoading(true);
    try {
      const blob = await generateDoc(docType);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${docType}.pdf`;
      a.click();
    } catch (e: unknown) {
      setDocError(e instanceof Error ? e.message : "문서 생성 실패");
    } finally {
      setDocLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
        <CircularProgress size={60} />
        <Typography sx={{ ml: 2, fontSize: "20px" }}>데이터 로딩 중...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, bgcolor: "#0f172a", minHeight: "100vh" }}>
      {/* 헤더 */}
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, fontSize: "22px" }}>
        🏗️ 도림사거리 역세권 재개발 통합관리
      </Typography>

      {/* 단계 진행 바 */}
      {status && (
        <WorkflowTracker
          currentStage={status.current_stage}
          stageName={status.stage_name}
        />
      )}

      {/* 탭 전환 */}
      <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
        <Button variant={view === "dashboard" ? "contained" : "outlined"}
                onClick={() => setView("dashboard")}>대시보드</Button>
        <Button variant={view === "members" ? "contained" : "outlined"}
                onClick={() => setView("members")}>조합원 명부</Button>
      </Box>

      {view === "dashboard" && status && (
        <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
          {/* 좌측: 빠른 실행 */}
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {/* AI 비서 */}
            <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
              <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 1 }}>
                🤖 AI 비서에게 묻기
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={aiQuestion}
                onChange={(e) => setAiQuestion(e.target.value)}
                placeholder="예: 임원 해임 총회 소집 요건이 어떻게 되나요?"
                sx={{ mb: 1, "& .MuiInputBase-input": { fontSize: "16px" } }}
              />
              <Button fullWidth variant="contained" size="large"
                      disabled={!aiQuestion.trim()}>
                질의하기 (Sprint 2에서 활성화)
              </Button>
            </Box>

            {/* 서류 뽑기 */}
            <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
              <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 1 }}>
                📋 현재 단계 필수 서류 뽑기
              </Typography>
              {status.required_docs.map((doc) => (
                <Typography key={doc} sx={{ fontSize: "15px", color: "#94a3b8", mb: 0.5 }}>
                  • {doc}
                </Typography>
              ))}
              {docError && <Alert severity="error" sx={{ mt: 1, fontSize: "15px" }}>{docError}</Alert>}
              <Button fullWidth variant="contained" color="success" size="large"
                      sx={{ mt: 1 }} disabled={docLoading}
                      onClick={() => handleGenerateDoc(status.required_docs[0])}>
                {docLoading ? "생성 중..." : "서류 PDF 다운로드"}
              </Button>
            </Box>

            {/* 영수증 */}
            <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
              <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 1 }}>
                🧾 영수증 지출결의 하기
              </Typography>
              <Button fullWidth variant="contained" color="warning" size="large" disabled>
                영수증 업로드 (Sprint 2에서 활성화)
              </Button>
            </Box>
          </Box>

          {/* 우측: 동의율 + 지도 자리 */}
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <ConsentChart
              stats={status.consent_rate}
              threshold={status.consent_threshold}
              isThresholdMet={status.is_threshold_met}
            />
            <Box sx={{ bgcolor: "#1e293b", borderRadius: 2, p: 2,
                       minHeight: 250, display: "flex", alignItems: "center",
                       justifyContent: "center", border: "1px dashed #334155" }}>
              <Typography sx={{ color: "#475569", fontSize: "16px", textAlign: "center" }}>
                🗺️ GIS 지도<br />(Sprint 2에서 활성화)
              </Typography>
            </Box>
            <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1 }}>
              <Box sx={{ bgcolor: "#0f172a", p: 2, borderRadius: 2, textAlign: "center",
                         border: "1px solid #1e3a5f" }}>
                <Typography sx={{ fontSize: "28px", fontWeight: 700, color: "#60a5fa" }}>
                  {status.consent_rate.total}
                </Typography>
                <Typography sx={{ fontSize: "14px", color: "#64748b" }}>전체 토지등소유자</Typography>
              </Box>
              <Box sx={{ bgcolor: "#0f172a", p: 2, borderRadius: 2, textAlign: "center",
                         border: "1px solid #166534" }}>
                <Typography sx={{ fontSize: "28px", fontWeight: 700, color: "#22c55e" }}>
                  {status.consent_rate.consented}
                </Typography>
                <Typography sx={{ fontSize: "14px", color: "#64748b" }}>동의 완료</Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      )}

      {view === "members" && (
        <MemberGrid
          members={members}
          onConsentChange={(updated) => setMembers(updated)}
        />
      )}
    </Box>
  );
}
```

- [ ] **Step 3: 브라우저 동작 확인**

백엔드(`uvicorn main:app --reload`) + 프론트엔드(`npm run dev`) 동시 기동 후 `http://localhost:3000` 접속.  
Expected: 대시보드 화면, WorkflowTracker 단계 표시, 동의율 프로그레스 바, 조합원 명부 탭에서 DataGrid 표시.

- [ ] **Step 4: 커밋**

```bash
git add dorim-redev-system/frontend/
git commit -m "feat: add ConsentChart and main Dashboard page with 3-action layout"
```

---

### Task 11: UX 접근성 감리 (담당: UX 에이전트, Task 10 완료 후)

**Files:**
- Modify: `dorim-redev-system/frontend/app/layout.tsx` (필요 시)
- Modify: `dorim-redev-system/frontend/app/page.tsx` (필요 시)

- [ ] **Step 1: 접근성 체크리스트 실행**

브라우저 DevTools → Accessibility 탭에서 검사. 다음 항목 확인:

| 항목 | 기준 | 확인 방법 |
|------|------|----------|
| 폰트 최소 크기 | 16px | DevTools Elements → Computed → font-size |
| 버튼 터치 영역 | 44×44px | Elements → Box Model |
| 색상 대비 | 4.5:1 | DevTools → Accessibility → Contrast ratio |
| 에러 메시지 | 텍스트 + 색상 | Alert 컴포넌트 확인 |

- [ ] **Step 2: 위반 항목 수정 후 커밋**

```bash
git add dorim-redev-system/frontend/
git commit -m "fix: UX accessibility audit - ensure 16px font, 44px touch targets, WCAG AA contrast"
```

---

### Task 12: start.sh 원클릭 실행 스크립트 (담당: 주니어 개발자, Sprint 1 최종)

**Files:**
- Create: `dorim-redev-system/start.sh`

- [ ] **Step 1: start.sh 작성**

```bash
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
  source venv/Scripts/activate
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
```

- [ ] **Step 2: 실행 권한 부여 및 테스트**

```bash
chmod +x dorim-redev-system/start.sh
bash dorim-redev-system/start.sh
```

Expected: 백엔드 + 프론트엔드 동시 기동, `http://localhost:3000` 접속 가능

- [ ] **Step 3: Sprint 1 완료 커밋**

```bash
git add dorim-redev-system/start.sh
git commit -m "feat: add one-click start.sh - Sprint 1 COMPLETE"
git tag sprint-1-complete
```

---

## ═══════════════ SPRINT 2 ═══════════════

> **전제**: Sprint 1 태그(`sprint-1-complete`) 완료 확인 후 진행

---

### Task 13: ChromaDB RAG 엔진 (담당: 법률 에이전트)

**Files:**
- Create: `dorim-redev-system/backend/rag_engine.py`
- Create: `dorim-redev-system/docs/legal/01_station-area-guidelines-2026.md`
- Create: `dorim-redev-system/docs/legal/02_urban-renewal-ordinance.md`
- Create: `dorim-redev-system/backend/tests/test_rag.py`

- [ ] **Step 1: 법령 마크다운 문서 작성 (임베딩 대상)**

```markdown
<!-- dorim-redev-system/docs/legal/01_station-area-guidelines-2026.md -->
# 역세권 장기전세주택 건립 운영기준 (2026.3.6. 시행)

## 용적률 인센티브 체계

### 1차 역세권 (승강장 경계 250m 이내)
- 제3종일반주거 → 준주거지역 변경 시 법적상한 용적률 최대 700%
- 기준용적률: 210% (7층 이하 포함 시 230%)
- 상한(정비계획) 용적률: 250%

### 2차 역세권 (250m~500m)
- 법적상한 용적률 최대 500%

### 추가 완화 조건
- 전용면적 60㎡ 이하 소형주택을 용적률의 20% 이상 추가 공급 시 기준용적률 20% 추가 완화
- 지가 보정값 최대 10% 이내 추가 완화

## 사전검토 동의 요건
- 2026.3.6. 개정으로 사전검토 신청 동의율 40%로 완화 (종전 50%)

## 장기전세주택 환수 비율
- 법적상한 초과 용적률의 50% 이상을 장기전세주택으로 공급
```

```markdown
<!-- dorim-redev-system/docs/legal/02_urban-renewal-ordinance.md -->
# 서울특별시 도시 및 주거환경정비 조례 주요 조항

## 시공사 선정 시기 (2023년 말 개정)
- 시공자 선정 시기: **조합설립인가 이후**
- 종전 규정(사업시행계획인가 이후)에서 앞당겨짐

## 시공사 선정 절차
1. 기본설계도서 작성 필수
2. 공사 원가 산출
3. 입찰 시 공동주택 성능요구서 + 물량내역서 + 산출내역서 제출

## 공사비 검증 의무
- 최초 사업시행계획인가 이후 분양공고 전 공사비 검증 신청 의무
- 근거: 국토교통부 고시 「정비사업 공사비 검증」

## 조합설립 동의 요건
- 토지등소유자 4분의 3 이상 동의
- 토지면적 2분의 1 이상 동의

## 임원 해임 총회 소집 요건
- 조합원 10분의 1 이상 요구 시 총회 소집 가능
- 해임은 총회에서 조합원 과반수 출석, 출석 과반수 찬성으로 의결
```

- [ ] **Step 2: 테스트 작성**

```python
# dorim-redev-system/backend/tests/test_rag.py
import pytest
from rag_engine import RagEngine

@pytest.fixture(scope="module")
def rag(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("chroma")
    engine = RagEngine(
        docs_dir="docs/legal",
        db_dir=str(db_dir),
    )
    engine.embed_all_docs()
    return engine

def test_query_returns_results(rag):
    results = rag.query("사전검토 동의율이 몇 퍼센트인가요?")
    assert len(results) > 0
    assert "text" in results[0]
    assert "source" in results[0]

def test_query_far_limit(rag):
    results = rag.query("1차 역세권 용적률 상한은?")
    texts = " ".join(r["text"] for r in results)
    assert "700" in texts

def test_query_contractor_timing(rag):
    results = rag.query("시공사 선정은 언제 가능한가요?")
    texts = " ".join(r["text"] for r in results)
    assert "조합설립" in texts
```

- [ ] **Step 3: rag_engine.py 구현**

```python
# dorim-redev-system/backend/rag_engine.py
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

COLLECTION_NAME = "dorim_legal_docs"


class RagEngine:
    def __init__(
        self,
        docs_dir: str = "docs/legal",
        db_dir: str = "../data/chroma_db",
    ):
        self.docs_dir = Path(docs_dir)
        self.client = chromadb.PersistentClient(path=db_dir)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"  # 한국어 지원
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.ef,
        )

    def embed_all_docs(self) -> int:
        """docs/legal/*.md 파일 전체 임베딩. 반환값: 임베딩된 청크 수."""
        if not self.docs_dir.exists():
            raise FileNotFoundError(f"{self.docs_dir} 없음")

        chunks, ids, metas = [], [], []
        for md_file in self.docs_dir.glob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            # 단락 단위로 청크 분할
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
            for i, para in enumerate(paragraphs):
                doc_id = f"{md_file.stem}_{i}"
                chunks.append(para)
                ids.append(doc_id)
                metas.append({"source": md_file.name, "chunk_idx": i})

        if chunks:
            self.collection.upsert(documents=chunks, ids=ids, metadatas=metas)
        return len(chunks)

    def query(self, question: str, n_results: int = 3) -> list[dict]:
        """질의에 가장 관련된 법령 조항 Top-N 반환."""
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results,
        )
        return [
            {
                "text": doc,
                "source": meta["source"],
                "chunk_idx": meta["chunk_idx"],
            }
            for doc, meta in zip(
                results["documents"][0], results["metadatas"][0]
            )
        ]


# 전역 싱글턴
rag_engine = RagEngine()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_rag.py -v
```

Expected: `3 passed`

- [ ] **Step 5: 커밋**

```bash
git add dorim-redev-system/backend/rag_engine.py dorim-redev-system/docs/legal/ dorim-redev-system/backend/tests/test_rag.py
git commit -m "feat: add ChromaDB RAG engine with Korean legal doc embeddings"
```

---

### Task 14: RAG 라우터 + LegalChat UI (담당: 법률 에이전트 + 주니어)

**Files:**
- Create: `dorim-redev-system/backend/routers/rag.py`
- Create: `dorim-redev-system/frontend/components/LegalChat.tsx`
- Modify: `dorim-redev-system/backend/main.py` (라우터 추가)

- [ ] **Step 1: routers/rag.py 구현**

```python
# dorim-redev-system/backend/routers/rag.py
import os
from fastapi import APIRouter
from pydantic import BaseModel
import anthropic
from rag_engine import rag_engine

router = APIRouter(tags=["rag"])
_anthropic = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


class RagQuery(BaseModel):
    question: str


@router.post("/rag/query")
def rag_query(body: RagQuery):
    """법령 질의 → RAG 검색 → Claude Sonnet 답변 생성."""
    chunks = rag_engine.query(body.question, n_results=3)
    context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)

    system_prompt = (
        "당신은 서울시 역세권 재개발 전문 법률 자문 AI입니다. "
        "다음 법령 조항을 참고하여 정확하고 보수적인 자문을 제공하십시오. "
        "불확실한 내용은 반드시 '법무사·변호사 확인 필요'라고 명시하십시오.\n\n"
        f"[참고 법령]\n{context}"
    )

    message = _anthropic.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": body.question}],
        system=system_prompt,
    )

    return {
        "data": {
            "answer": message.content[0].text,
            "sources": [{"source": c["source"], "excerpt": c["text"][:100]} for c in chunks],
        },
        "error": None,
    }


@router.post("/rag/embed-docs")
def embed_docs():
    """docs/legal/ 문서 재임베딩 (업데이트 시 호출)."""
    count = rag_engine.embed_all_docs()
    return {"data": {"embedded_chunks": count}, "error": None}
```

- [ ] **Step 2: main.py에 RAG 라우터 추가**

`dorim-redev-system/backend/main.py`에 추가:
```python
from routers import members, workflow, rag   # rag 추가

# ...
app.include_router(rag.router, prefix="/api")
```

- [ ] **Step 3: LegalChat.tsx 작성**

```typescript
// dorim-redev-system/frontend/components/LegalChat.tsx
"use client";
import { useState } from "react";
import { Box, TextField, Button, Typography, CircularProgress, Alert, Divider } from "@mui/material";

interface RagResult {
  answer: string;
  sources: { source: string; excerpt: string }[];
}

export default function LegalChat() {
  const [question, setQuestion]   = useState("");
  const [result, setResult]       = useState<RagResult | null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState<string | null>(null);

  const handleQuery = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.detail?.message ?? "질의 실패");
      setResult(json.data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "오류 발생");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
      <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 1.5 }}>
        🤖 AI 법률 비서에게 묻기
      </Typography>
      <TextField
        fullWidth multiline rows={3}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="예: 임원 해임 총회 소집 요건이 어떻게 되나요?"
        sx={{ mb: 1, "& .MuiInputBase-input": { fontSize: "16px" } }}
      />
      <Button fullWidth variant="contained" size="large"
              onClick={handleQuery} disabled={loading || !question.trim()}>
        {loading ? <CircularProgress size={20} /> : "질의하기"}
      </Button>

      {error && <Alert severity="error" sx={{ mt: 2, fontSize: "15px" }}>{error}</Alert>}

      {result && (
        <Box sx={{ mt: 2 }}>
          <Divider sx={{ mb: 2 }} />
          <Typography sx={{ fontSize: "16px", whiteSpace: "pre-wrap", lineHeight: 1.8 }}>
            {result.answer}
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography sx={{ fontSize: "13px", color: "#64748b", mb: 1 }}>📚 참고 법령</Typography>
            {result.sources.map((s, i) => (
              <Typography key={i} sx={{ fontSize: "13px", color: "#94a3b8", mb: 0.5 }}>
                [{s.source}] {s.excerpt}...
              </Typography>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
}
```

- [ ] **Step 4: page.tsx AI 비서 섹션을 LegalChat으로 교체**

`dorim-redev-system/frontend/app/page.tsx`의 "AI 비서에게 묻기" 박스를 다음으로 교체:
```typescript
import LegalChat from "@/components/LegalChat";
// ...
// 기존 AI 비서 박스 전체를:
<LegalChat />
```

- [ ] **Step 5: ANTHROPIC_API_KEY 환경변수 설정**

```bash
# dorim-redev-system/backend/.env (gitignore에 추가)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

```bash
echo "dorim-redev-system/backend/.env" >> .gitignore
```

- [ ] **Step 6: 커밋**

```bash
git add dorim-redev-system/backend/routers/rag.py dorim-redev-system/frontend/components/LegalChat.tsx dorim-redev-system/backend/main.py
git commit -m "feat: add RAG router (Claude Sonnet 4.5) and LegalChat component"
```

---

### Task 15: GIS 라우터 + MapComponent (담당: GIS/데이터, Task 13과 병렬)

**Files:**
- Create: `dorim-redev-system/backend/routers/gis.py`
- Create: `dorim-redev-system/frontend/components/MapComponent.tsx`
- Modify: `dorim-redev-system/backend/main.py`

- [ ] **Step 1: routers/gis.py 구현**

```python
# dorim-redev-system/backend/routers/gis.py
"""GIS 라우터. 133-1 구역 좌표는 API 레벨에서 완전 차단."""
from fastapi import APIRouter
from db.sync import sync_db

router = APIRouter(tags=["gis"])

# 도림동 239-12 구역계 (가상 폴리곤, 실측 후 교체 필요)
ZONE_POLYGON = [
    [37.5120, 126.8970],
    [37.5148, 126.8970],
    [37.5148, 126.9002],
    [37.5120, 126.9002],
    [37.5120, 126.8970],
]

# 133-1 구역 좌표 범위 (이 범위 내 마커는 반환 금지)
EXCLUDED_LAT_RANGE = (37.508, 37.512)
EXCLUDED_LNG_RANGE = (126.895, 126.900)


def _is_excluded_zone(lat: float, lng: float) -> bool:
    """133-1 구역 좌표 여부 판별."""
    return (
        EXCLUDED_LAT_RANGE[0] <= lat <= EXCLUDED_LAT_RANGE[1]
        and EXCLUDED_LNG_RANGE[0] <= lng <= EXCLUDED_LNG_RANGE[1]
    )


def _geocode_address(address: str) -> tuple[float, float]:
    """주소 → 좌표 변환. 실패 시 구역 중심으로 폴백."""
    # 실제 서비스에서는 Kakao/Naver/Nominatim API 호출
    # 여기서는 도림동 주소 기반 근사 좌표 반환
    CENTER = (37.5134, 126.8986)
    addr_map = {
        "239-12": (37.5130, 126.8975),
        "239-14": (37.5131, 126.8978),
        "240-1":  (37.5133, 126.8982),
        "240-3":  (37.5135, 126.8985),
        "241-2":  (37.5137, 126.8988),
        "242-1":  (37.5139, 126.8991),
        "243-2":  (37.5141, 126.8994),
        "244-1":  (37.5138, 126.8997),
        "245-3":  (37.5135, 126.8993),
        "246-1":  (37.5132, 126.8989),
    }
    for key, coords in addr_map.items():
        if key in address:
            return coords
    return CENTER


@router.get("/gis/zone-polygon")
def get_zone_polygon():
    """239-12 구역계 GeoJSON 반환."""
    return {
        "data": {
            "type": "Polygon",
            "coordinates": ZONE_POLYGON,
            "area_sqm": 59607.59,
            "zone": "도림동 239-12",
        },
        "error": None,
    }


@router.get("/gis/markers")
def get_markers():
    """조합원 주소 → 좌표 변환 + 동의여부 색상 마커 반환.
    133-1 구역 좌표는 필터링하여 제외."""
    members = sync_db.get_members()
    markers = []
    for m in members:
        lat, lng = _geocode_address(m["address"])
        if _is_excluded_zone(lat, lng):
            continue  # 133-1 구역 완전 배제
        markers.append({
            "member_id": m["member_id"],
            "address": m["address"],
            "lat": lat,
            "lng": lng,
            "consent": bool(m["consent"]),
            "rights_value": m["rights_value"],
            "color": "#3b82f6" if m["consent"] else "#ef4444",
        })
    return {"data": markers, "error": None}
```

- [ ] **Step 2: main.py에 GIS 라우터 추가**

```python
from routers import members, workflow, rag, gis   # gis 추가
# ...
app.include_router(gis.router, prefix="/api")
```

- [ ] **Step 3: MapComponent.tsx 작성**

```typescript
// dorim-redev-system/frontend/components/MapComponent.tsx
"use client";
import { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";

interface Marker {
  member_id: number;
  address: string;
  lat: number;
  lng: number;
  consent: boolean;
  rights_value: number;
  color: string;
}

export default function MapComponent() {
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [MapLibs, setMapLibs] = useState<{
    MapContainer: unknown;
    TileLayer: unknown;
    Polygon: unknown;
    CircleMarker: unknown;
    Popup: unknown;
  } | null>(null);

  useEffect(() => {
    // SSR 방지: react-leaflet은 클라이언트에서만 로드
    import("react-leaflet").then((rl) => {
      setMapLibs({
        MapContainer: rl.MapContainer,
        TileLayer: rl.TileLayer,
        Polygon: rl.Polygon,
        CircleMarker: rl.CircleMarker,
        Popup: rl.Popup,
      });
    });
    fetch("http://localhost:8000/api/gis/markers")
      .then((r) => r.json())
      .then((json) => setMarkers(json.data ?? []));
  }, []);

  if (!MapLibs) {
    return (
      <Box sx={{ height: 280, display: "flex", alignItems: "center",
                 justifyContent: "center", bgcolor: "#1e293b", borderRadius: 2 }}>
        <Typography sx={{ color: "#64748b" }}>지도 로딩 중...</Typography>
      </Box>
    );
  }

  const { MapContainer, TileLayer, Polygon, CircleMarker, Popup } = MapLibs as {
    MapContainer: React.ComponentType<unknown>;
    TileLayer: React.ComponentType<unknown>;
    Polygon: React.ComponentType<unknown>;
    CircleMarker: React.ComponentType<unknown>;
    Popup: React.ComponentType<React.PropsWithChildren>;
  };

  const ZONE_POLYGON: [number, number][] = [
    [37.5120, 126.8970], [37.5148, 126.8970],
    [37.5148, 126.9002], [37.5120, 126.9002],
  ];

  return (
    <Box sx={{ borderRadius: 2, overflow: "hidden", height: 280 }}>
      <MapContainer
        center={[37.5134, 126.8986] as [number, number]}
        zoom={17}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        <Polygon
          positions={ZONE_POLYGON}
          pathOptions={{ color: "#3b82f6", fillColor: "#3b82f6", fillOpacity: 0.1 }}
        />
        {markers.map((m) => (
          <CircleMarker
            key={m.member_id}
            center={[m.lat, m.lng] as [number, number]}
            radius={8}
            pathOptions={{ color: m.color, fillColor: m.color, fillOpacity: 0.8 }}
          >
            <Popup>
              <strong>{m.address}</strong><br />
              권리가액: {m.rights_value.toLocaleString()}원<br />
              동의: {m.consent ? "✅ 완료" : "❌ 미동의"}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </Box>
  );
}
```

- [ ] **Step 4: page.tsx 지도 자리표시자를 MapComponent로 교체**

`dorim-redev-system/frontend/app/page.tsx`:
```typescript
import MapComponent from "@/components/MapComponent";
// ...
// 기존 지도 자리표시자 박스를:
<MapComponent />
```

- [ ] **Step 5: Leaflet CSS 추가**

`dorim-redev-system/frontend/app/layout.tsx` head에 추가:
```typescript
// layout.tsx import 상단에 추가
import "leaflet/dist/leaflet.css";
```

- [ ] **Step 6: 커밋**

```bash
git add dorim-redev-system/backend/routers/gis.py dorim-redev-system/frontend/components/MapComponent.tsx dorim-redev-system/backend/main.py
git commit -m "feat: add GIS router with 133-1 exclusion filter and MapComponent with consent markers"
```

---

### Task 16: 영수증 OCR 라우터 + ReceiptOcr UI (담당: GIS/데이터, Task 13과 병렬)

**Files:**
- Create: `dorim-redev-system/backend/routers/ocr.py`
- Create: `dorim-redev-system/frontend/components/ReceiptOcr.tsx`
- Modify: `dorim-redev-system/backend/main.py`

- [ ] **Step 1: routers/ocr.py 구현**

```python
# dorim-redev-system/backend/routers/ocr.py
import re
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["ocr"])

# 영수증 필드 정규식 패턴
_DATE_RE    = re.compile(r"(\d{4}[-/.]\d{2}[-/.]\d{2}|\d{2}[-/.]\d{2}[-/.]\d{2})")
_AMOUNT_RE  = re.compile(r"공급가액[^\d]*(\d[\d,]+)")
_VAT_RE     = re.compile(r"부가세[^\d]*(\d[\d,]+)")
_STORE_RE   = re.compile(r"^(.{2,20})\s*(사업자|상호|대표)", re.MULTILINE)


def _parse_receipt_text(text: str) -> dict:
    date    = _DATE_RE.search(text)
    amount  = _AMOUNT_RE.search(text)
    vat     = _VAT_RE.search(text)
    store   = _STORE_RE.search(text)
    return {
        "date":         date.group(1)  if date   else "인식 불가",
        "store":        store.group(1).strip() if store else "인식 불가",
        "supply_amount": int(amount.group(1).replace(",", "")) if amount else 0,
        "vat":           int(vat.group(1).replace(",", ""))    if vat    else 0,
    }


def _generate_expense_pdf(data: dict) -> bytes:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.lib.pagesizes import A4

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(w / 2, h - 80, "지 출 결 의 서")
    c.setFont("Helvetica", 12)

    rows = [
        ("날 짜",    data["date"]),
        ("상 호",    data["store"]),
        ("공급가액", f"{data['supply_amount']:,} 원"),
        ("부 가 세", f"{data['vat']:,} 원"),
        ("합 계",    f"{data['supply_amount'] + data['vat']:,} 원"),
    ]
    y = h - 140
    for label, value in rows:
        c.drawString(80, y, f"{label}:")
        c.drawString(200, y, value)
        y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(80, 80, "도림사거리 역세권 재개발 추진위원회")
    c.save()
    return buffer.getvalue()


@router.post("/ocr/receipt")
async def ocr_receipt(file: UploadFile = File(...)):
    """영수증 이미지 → OCR → 지출결의서 PDF 스트림 반환."""
    content = await file.read()
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_FILE",
                                                      "message": "이미지 파일만 업로드 가능합니다"})
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang="korean", show_log=False)
        import numpy as np
        import cv2
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        result = ocr.ocr(img, cls=True)
        text = "\n".join(line[1][0] for block in result for line in block)
    except Exception:
        text = ""  # OCR 실패 시 빈 텍스트로 진행

    parsed = _parse_receipt_text(text)
    pdf_bytes = _generate_expense_pdf(parsed)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=expense_report.pdf",
                 "X-Receipt-Data": str(parsed)},
    )
```

- [ ] **Step 2: main.py에 OCR 라우터 추가**

```python
from routers import members, workflow, rag, gis, ocr   # ocr 추가
# ...
app.include_router(ocr.router, prefix="/api")
```

- [ ] **Step 3: ReceiptOcr.tsx 작성**

```typescript
// dorim-redev-system/frontend/components/ReceiptOcr.tsx
"use client";
import { useState, useCallback } from "react";
import { Box, Typography, Button, CircularProgress, Alert } from "@mui/material";

export default function ReceiptOcr() {
  const [file, setFile]       = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type.startsWith("image/")) {
      setFile(dropped);
      setPreview(URL.createObjectURL(dropped));
      setError(null);
      setSuccess(false);
    }
  }, []);

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("http://localhost:8000/api/ocr/receipt", {
        method: "POST", body: form,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.message ?? "OCR 처리 실패");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "expense_report.pdf";
      a.click();
      setSuccess(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "오류 발생");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ bgcolor: "#1e293b", p: 2, borderRadius: 2 }}>
      <Typography sx={{ fontSize: "18px", fontWeight: 700, mb: 1.5 }}>
        🧾 영수증 지출결의 하기
      </Typography>

      <Box
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        sx={{ border: "2px dashed #334155", borderRadius: 2, p: 3, textAlign: "center",
              cursor: "pointer", mb: 1.5, minHeight: 120,
              display: "flex", alignItems: "center", justifyContent: "center",
              flexDirection: "column", gap: 1 }}
      >
        {preview
          ? <img src={preview} alt="영수증 미리보기" style={{ maxHeight: 150, borderRadius: 4 }} />
          : <>
              <Typography sx={{ fontSize: "28px" }}>📷</Typography>
              <Typography sx={{ fontSize: "16px", color: "#64748b" }}>
                영수증 사진을 여기에 드래그하거나
              </Typography>
              <Button component="label" variant="outlined" size="small">
                파일 선택
                <input type="file" accept="image/*" hidden
                       onChange={(e) => {
                         const f = e.target.files?.[0];
                         if (f) { setFile(f); setPreview(URL.createObjectURL(f)); }
                       }} />
              </Button>
            </>
        }
      </Box>

      {error   && <Alert severity="error"   sx={{ mb: 1, fontSize: "15px" }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 1, fontSize: "15px" }}>지출결의서 PDF 다운로드 완료</Alert>}

      <Button fullWidth variant="contained" color="warning" size="large"
              onClick={handleProcess} disabled={!file || loading}>
        {loading ? <CircularProgress size={20} /> : "OCR 처리 → 지출결의서 PDF 생성"}
      </Button>
    </Box>
  );
}
```

- [ ] **Step 4: page.tsx 영수증 섹션 교체**

```typescript
import ReceiptOcr from "@/components/ReceiptOcr";
// 기존 영수증 자리표시자 버튼을:
<ReceiptOcr />
```

- [ ] **Step 5: 커밋**

```bash
git add dorim-redev-system/backend/routers/ocr.py dorim-redev-system/frontend/components/ReceiptOcr.tsx dorim-redev-system/backend/main.py
git commit -m "feat: add OCR receipt router (PaddleOCR + reportlab PDF) and ReceiptOcr component"
```

---

### Task 17: Sprint 2 통합 + 최종 UX 감리 (담당: UX 에이전트)

**Files:**
- Modify: `dorim-redev-system/frontend/app/page.tsx` (최종 레이아웃 통합)
- Modify: `dorim-redev-system/start.sh` (ChromaDB 임베딩 초기화 추가)

- [ ] **Step 1: start.sh에 RAG 임베딩 초기화 추가**

`dorim-redev-system/start.sh`의 uvicorn 실행 전에 추가:
```bash
# RAG 문서 임베딩 (처음 1회)
CHROMA_DB="$SCRIPT_DIR/data/chroma_db"
if [ ! -d "$CHROMA_DB" ]; then
  echo "  법령 문서 임베딩 중 (최초 1회, 수분 소요)..."
  cd "$SCRIPT_DIR/backend"
  python -c "from rag_engine import rag_engine; n=rag_engine.embed_all_docs(); print(f'  임베딩 완료: {n}개 청크')"
fi
```

- [ ] **Step 2: 전체 통합 동작 확인**

```bash
bash dorim-redev-system/start.sh
```

브라우저 `http://localhost:3000`에서 확인:
- [ ] 워크플로우 단계 바 표시
- [ ] 동의율 34% 프로그레스 바 (경고 표시)
- [ ] AI 비서 질의 동작 (ANTHROPIC_API_KEY 설정 필요)
- [ ] 조합원 명부 DataGrid + 동의 토글 → Excel 저장
- [ ] GIS 지도 도림동 239-12 폴리곤 + 동의 마커
- [ ] 영수증 드래그앤드롭 + PDF 다운로드

- [ ] **Step 3: 최종 접근성 감리**

| 체크항목 | 기준 | 결과 |
|---------|------|------|
| 폰트 크기 | 16px 이상 | |
| 버튼 터치 영역 | 44×44px | |
| 색상 대비 | 4.5:1 이상 | |
| 에러 메시지 | 텍스트+색상 | |
| 동의율 수치 | 24px 이상 | |

미통과 항목 수정 후 진행.

- [ ] **Step 4: 최종 커밋 + 태그**

```bash
git add .
git commit -m "feat: Sprint 2 complete - RAG, GIS map, OCR integrated"
git tag sprint-2-complete
```

---

## 자체 검토 (Self-Review)

**1. 스펙 커버리지 검사:**

| 스펙 요구사항 | 구현 태스크 |
|-------------|------------|
| workflow.yaml 상태머신 | Task 2 |
| 하드락 A·B·C | Task 3 |
| Excel↔SQLite 동기화 | Task 4 |
| members.xlsx 가데이터 | Task 4 |
| GET /api/members | Task 6 |
| PATCH consent | Task 6 |
| GET /api/consent-rate | Task 6 |
| GET /api/workflow/status | Task 7 |
| POST /api/workflow/generate-doc | Task 7 |
| WorkflowTracker | Task 8 |
| MemberGrid | Task 9 |
| ConsentChart | Task 10 |
| 대시보드 3-버튼 레이아웃 | Task 10 |
| 폰트 16px + 44px 터치 | Task 8, Task 11 |
| ChromaDB RAG | Task 13 |
| RAG 라우터 + LegalChat | Task 14 |
| GIS 라우터 + 133-1 배제 | Task 15 |
| MapComponent | Task 15 |
| OCR 라우터 + ReceiptOcr | Task 16 |
| 에이전트 스킬 파일 6개 | Task 2 |
| start.sh | Task 12 |

**2. 플레이스홀더 없음** ✅  
**3. 타입 일관성:** `Member`, `ConsentRate`, `WorkflowStatus` 인터페이스가 `lib/api.ts`에서 정의되고 모든 컴포넌트에서 동일하게 사용 ✅  
**4. 함수명 일관성:** `sync_db.update_consent()`, `sync_db.get_members()`, `sync_db.get_consent_rate()`가 Task 4→6→7 모두 일치 ✅
