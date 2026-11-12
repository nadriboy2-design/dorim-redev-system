# 대동백화점 부지 분할 검토 (창원 성산구 상남동 44-1)

> ⛔ 도림 재개발 시스템과 **완전히 분리**된 별개 사업 자료입니다.
> backend/frontend, members.xlsx, RAG, 지도에 연결·import 하지 않습니다.

## 폴더
- 루트 `*.md`  리스크 검증·조합진행/허가조건/용적률/분필 검토·증빙 정리·현장조사 체크리스트·법령발췌
- `보고서/`    PPT·PDF (요약10장 / 보고용 큰글씨 / 통합보고서(PDF만) / 거절근거 v2)
- `작업도구/`  보고서 재생성 스크립트 (build_report4.py, make_summary10.py, apt_trade.py 등)
- `실거래/`    성산구 아파트 실거래 csv, 비교 xlsx, summary84.json
- `증빙/`      법령 캡처, 증빙 이미지(ev), 조합 공고, 별표28 hwp

이어서 작업: `이어하기_README.md` 참고 (미확인 9항목, 다음 할 일 포함).
스크립트 실행 시 환경변수 `DAEDONG_ROOT`를 이 폴더 경로로 지정하세요.

원본: Google Drive "대동백화점 부지 분할 검토" 폴더 (이어하기_README.md 참고)

## 집 PC와 동기화
집 PC: `git pull` → 작업 → `git add analysis/daedong` → commit/push.

## API 키
`DATA_GO_KR_KEY`(공공데이터포털)는 **파일/저장소에 적지 않습니다.**
`.env`(gitignore 대상) 또는 클라우드 환경 비밀값으로만 설정합니다. 예시는 `.env.example`.
