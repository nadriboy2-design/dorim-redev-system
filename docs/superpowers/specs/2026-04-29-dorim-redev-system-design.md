# 도림사거리 역세권 재개발 통합 관리 시스템 — 설계 명세서

**날짜**: 2026-04-29  
**프로젝트**: 도림사거리 역세권 재개발 (도림동 239-12 일원, 59,607.59㎡)  
**현재 단계**: 서울시 사전검토회의 (정비구역 입안 초기)  
**버전**: 1.0 (승인 완료)

---

## 1. 프로젝트 개요 및 핵심 제약사항

### 사업 대상지

| 항목 | 내용 |
|------|------|
| 사업명 | 도림사거리 역세권 장기전세주택 재개발 |
| 대상지 | 서울특별시 영등포구 도림동 239-12 일원 |
| 구역 면적 | 59,607.59㎡ |
| 현재 단계 | 서울시 사전검토회의 (정비구역 입안 초기) |
| 적용 기준 | 역세권 장기전세주택 건립 운영기준 (2026.3.6. 시행) |

### 절대 배제 구역

**도림동 133-1번지 일대 (63,654㎡)는 별개 사업이며 이 시스템과 완전히 무관하다.**  
지도 폴리곤, 조합원 DB, RAG 검색 등 시스템 전 영역에서 133-1 데이터 혼입을 금지한다.

### 법적 하드락 규칙 (절대 우선)

| 규칙 | 조건 | 동작 |
|------|------|------|
| 하드락 A | 용적률 입력값 > 700% | Exception 발생 + UI 경고 + 작업 차단 |
| 하드락 B | 조합설립 전 시공사 입찰 문서 생성 시도 | 403 에러 반환 + 명시적 차단 메시지 |
| 하드락 C | 공사비 검증 결과서 없이 분양공고 시도 | 403 에러 반환 + 작업 차단 |

---

## 2. 시스템 아키텍처

### 기술 스택

| 레이어 | 기술 | 포트 |
|--------|------|------|
| Frontend | Next.js 14 (TypeScript) + MUI v5 | 3000 |
| Backend | FastAPI (Python 3.11) + uvicorn | 8000 |
| 캐시 DB | SQLite (로컬) | - |
| 벡터 DB | ChromaDB (로컬) | - |
| 지도 | react-leaflet + OpenStreetMap | - |
| OCR | PaddleOCR (한글 최적화) | - |
| PDF 생성 | reportlab | - |
| Excel | pandas + openpyxl | - |

### 3-레이어 구조

```
브라우저 (Next.js :3000)
        ↕ REST API / JSON
FastAPI (:8000) + 컴플라이언스 미들웨어 (모든 요청 검사)
        ↕ read/write
members.xlsx (Single Source of Truth)
SQLite (읽기 캐시)
ChromaDB (법령 벡터 DB)
workflow.yaml (상태머신)
```

### 데이터 격리 원칙

- `members.xlsx` = 단일 진실 공급원 (Single Source of Truth)
- SQLite = 읽기 성능 캐시 (앱 시작 시 xlsx → SQLite 로드, 수정 시 즉시 역동기화)
- PostgreSQL 미사용 (설치 복잡도 및 Excel 단일 진실 공급원 요건으로 배제)

---

## 3. 프로젝트 디렉토리 구조

```
dorim-redev-system/
├── CLAUDE.md                        ← 프로젝트 컨텍스트 + 하드락 규칙 (완료)
├── .claude/
│   └── skills/
│       ├── ceo-orchestrator.md
│       ├── senior-reviewer.md
│       ├── junior-dev.md
│       ├── ux-accessibility.md
│       ├── legal-compliance.md
│       └── gis-data.md
├── ai_harness/
│   └── workflow.yaml                ← 상태머신 (5단계 + 동의율 임계값)
├── backend/
│   ├── main.py                      ← FastAPI 진입점
│   ├── compliance.py                ← 하드락 미들웨어 (A·B·C)
│   ├── routers/
│   │   ├── members.py               ← 조합원 CRUD
│   │   ├── workflow.py              ← 단계 관리 + 문서 생성
│   │   ├── ocr.py                   ← 영수증 OCR
│   │   └── rag.py                   ← 법령 RAG 질의
│   ├── db/
│   │   └── sync.py                  ← Excel ↔ SQLite 동기화
│   └── rag_engine.py                ← ChromaDB 임베딩 + 검색
├── frontend/
│   ├── app/
│   │   └── page.tsx                 ← 메인 대시보드
│   └── components/
│       ├── WorkflowTracker.tsx      ← 5단계 진행 바
│       ├── MemberGrid.tsx           ← MUI DataGrid + 동의 토글
│       ├── ConsentChart.tsx         ← 동의율 프로그레스 바
│       ├── MapComponent.tsx         ← react-leaflet 지도
│       ├── LegalChat.tsx            ← RAG 질의 UI
│       └── ReceiptOcr.tsx           ← 영수증 업로드 + 결의서
├── data/
│   └── members.xlsx                 ← 조합원 명부 (Single Source of Truth)
├── docs_template/                   ← 서울시 표준 공문서 양식
└── start.sh                         ← 원클릭 로컬 실행 스크립트
```

---

## 4. 6개 에이전트팀 설계

### 팀 구성 및 역할

| # | 팀 | 역할 | 모델 | 스킬 파일 |
|---|---|---|---|---|
| ① | CEO | 전략·의사결정·단계 전환 승인·팀 조율 | claude-sonnet-4-5 | ceo-orchestrator.md |
| ② | 부장급 (10년↑) | 아키텍처 감리·API 스펙 표준화·코드 리뷰 | claude-sonnet-4-5 | senior-reviewer.md |
| ③ | 주니어 개발자 (5년↓) | Next.js 컴포넌트·FastAPI CRUD·단위 테스트 | claude-haiku-3-5 | junior-dev.md |
| ④ | UX/접근성 | 폰트 16px↑ 강제·WCAG AA·44px 터치 영역 | claude-haiku-3-5 | ux-accessibility.md |
| ⑤ | 법률 컴플라이언스 | RAG 세팅·하드락 미들웨어·법령 임베딩 | claude-sonnet-4-5 | legal-compliance.md |
| ⑥ | 데이터/GIS | Excel 동기화·OCR 파이프라인·지도 매핑 | claude-haiku-3-5 | gis-data.md |

### 모델 선택 원칙

- **Sonnet 4.5**: 법적 판단·아키텍처 결정·전략적 의사결정 (복합 추론 필요)
- **Haiku 3.5**: 반복 코드 구현·UI 검사·데이터 처리 (경량 작업)

### SendMessage 협업 프로토콜

| 발신 | 수신 | 내용 |
|------|------|------|
| 주니어 → 부장급 | API 구현 완료 시 | 엔드포인트 스펙 공유·리뷰 요청 |
| 법률 → 전체 | 컴플라이언스 규칙 변경 시 | 하드락 규칙 브로드캐스트 |
| GIS → 주니어 | 지오코딩 API 확정 시 | `/api/gis/markers` 스펙 전달 |
| UX → 주니어 | 접근성 위반 발견 시 | 구체적 수정 지시 (px 단위) |

---

## 5. 스프린트 계획

### 스프린트 1 — 하네스 인프라 + 조합원 대시보드 (즉시 착수)

**목표**: 엑셀 업무를 웹으로 대체, 동의율 실시간 확인

| 구성요소 | 담당팀 | 세부 내용 |
|---------|--------|----------|
| `workflow.yaml` | CEO + 부장급 | 5단계 상태머신·동의율 임계값·필수서류 목록 |
| `compliance.py` | 법률 에이전트 | 하드락 A·B·C 미들웨어 |
| `sync.py` | GIS/데이터 | Excel ↔ SQLite 양방향 동기화 |
| `members.xlsx` | GIS/데이터 | 가데이터 샘플 20명 생성 |
| `MemberGrid.tsx` | 주니어 + UX | MUI DataGrid·동의 토글·즉시 Excel 저장 |
| `WorkflowTracker.tsx` | 주니어 | 5단계 진행 바·현재 단계 하이라이트 |
| `ConsentChart.tsx` | 주니어 | 동의율 % 계산·40%/75% 임계값 경고 |
| `start.sh` | 주니어 | 프론트엔드 + 백엔드 원클릭 구동 |

**스프린트 1 API 엔드포인트:**

| 메서드 | 경로 | 기능 |
|--------|------|------|
| GET | `/api/members` | 조합원 전체 목록 (SQLite) |
| PATCH | `/api/members/{id}/consent` | 동의여부 토글 → Excel 즉시 저장 |
| GET | `/api/consent-rate` | 동의율 % 실시간 계산 |
| GET | `/api/workflow/status` | 현재 사업 단계 + 체크리스트 |
| POST | `/api/workflow/generate-doc` | 서울시 표준 양식 PDF 생성 |

### 스프린트 2 — 법률 RAG + GIS 지도 + 영수증 OCR (스프린트 1 완료 후)

**목표**: 법적 보호막 구축 + 공간 데이터 시각화 + 영수증 자동화

#### 법률 RAG 모듈

- **임베딩 대상**: 역세권 장기전세주택 운영기준(2026.3.6), 서울시 도시정비조례, 도시정비법, 영등포구 질의회신 사례, 관련 판례 요약
- **파이프라인**: 사용자 질의 → ChromaDB 벡터 검색 → Top-3 관련 조항 → claude-sonnet-4-5 답변 → UI 출력 + 출처 표시
- **백그라운드 데몬**: 문서 생성 시 자동 법령 위반 스캔

#### GIS 지도 모듈

- **중심 좌표**: 37.5134°N, 126.8986°E (도림동 239-12)
- **줌 레벨**: 17 (필지 식별 가능)
- **레이어**: 구역계 폴리곤 + 동의 필지(파란 마커) + 미동의 필지(붉은 마커)
- **인터랙션**: 마커 클릭 시 조합원 권리 내역 팝업
- **차단**: 133-1 구역 좌표 API 레벨에서 완전 차단

#### 영수증 OCR 모듈

- **파이프라인**: 영수증 이미지 업로드 → PaddleOCR 텍스트 추출 → 정규식 파싱 (날짜/상호/공급가액/부가세) → reportlab PDF 생성 → 브라우저 다운로드
- **출력**: 서울시 표준 지출결의서 양식

---

## 6. 대시보드 UI 설계

### 레이아웃

```
┌─────────────────────────────────────────────────────┐
│  [① 정비구역 입안 ◀현재] [② 추진위] [③ 조합] [④ 시공] [⑤ 관리처분]  │
├─────────────────────────┬───────────────────────────┤
│  빠른 실행 (좌측)         │  지도 + 통계 (우측)         │
│                         │                           │
│  🤖 AI 비서에게 묻기      │  🗺️ react-leaflet 지도     │
│  📋 필수 서류 뽑기        │  (동의: 🔵 / 미동의: 🔴)   │
│  🧾 영수증 지출결의        │                           │
│                         │  전체: 373명               │
│  ━━━━━━━━━━━━━━━        │  동의: 127명 (34%)         │
│  동의율 34% [██░░░░] 40%  │                           │
│  ↑ 6% 부족              │                           │
└─────────────────────────┴───────────────────────────┘
```

### 접근성 요구사항 (UX 에이전트 강제)

- 최소 폰트 크기: **16px 이상**
- 버튼 최소 터치 영역: **44 × 44px**
- 텍스트-배경 대비: **WCAG AA (4.5:1) 이상**
- 색상만으로 정보 전달 금지 (레이블 병행)

---

## 7. 정비사업 단계별 동의율 임계값

| 단계 | 임계값 | 근거 |
|------|--------|------|
| 정비구역 입안 (사전검토) | **40% 이상** | 역세권 운영기준 2026.3.6. 개정 |
| 추진위원회 구성 | **50% 이상** | 도시정비법 |
| 조합 설립 인가 | **75% 이상** | 도시정비법 제35조 (토지등소유자 3/4) |
| 관리처분계획 변경 (사업비 증가 시) | **66.7% 이상** | 도시정비법 |

---

## 8. workflow.yaml 상태머신 핵심 구조

```yaml
project:
  name: "도림사거리 역세권 재개발"
  zone: "도림동 239-12"
  area_sqm: 59607.59
  excluded_zone: "도림동 133-1 (무관 구역 — 절대 혼입 금지)"

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
      - contractor_selection: BLOCKED  # 조합설립 전 시공사 선정 불가
    next_stage: STAGE_2_COMMITTEE

  STAGE_2_COMMITTEE:
    name: "추진위원회 구성"
    consent_threshold: 0.50
    required_docs:
      - "추진위원장·위원 명부"
      - "운영규정"
      - "창립총회 회의록"
    next_stage: STAGE_3_ASSOCIATION

  STAGE_3_ASSOCIATION:
    name: "조합 설립 인가"
    consent_threshold: 0.75
    required_docs:
      - "정관 초안"
      - "조합원 명부 (분양대상자·무허가 소유자)"
    unlocks:
      - contractor_selection: ALLOWED  # 이 단계부터 시공사 선정 가능
    next_stage: STAGE_4_CONTRACTOR

  STAGE_4_CONTRACTOR:
    name: "시공사 선정"
    required_docs:
      - "기본설계도서"
      - "공동주택 성능요구서"
      - "물량내역서·산출내역서"
    hard_locks:
      - sale_announcement:
          condition: "공사비_검증_결과서 == NULL"
          action: BLOCKED
    next_stage: STAGE_5_DISPOSAL

  STAGE_5_DISPOSAL:
    name: "관리처분계획 인가"
    required_docs:
      - "관리처분계획서"
      - "한국부동산원 타당성 검토 신청서"
    consent_threshold_for_change: 0.667
```

---

## 9. 범위 외 항목 (이번 구현에서 제외)

- 사용자 로그인/인증 (로컬 전용 시스템으로 불필요)
- 모바일 앱 (웹 반응형으로 대체)
- 클라우드 배포 (로컬 Windows 환경만 지원)
- 실시간 다중 사용자 동시 편집 (단일 PC 사용 가정)
- 카카오/네이버 지도 API (OpenStreetMap + react-leaflet으로 대체, 무료)

---

*설계 승인일: 2026-04-29 | 도림사거리 역세권 재개발 추진위원회*
