# 대동백화점 부지 분할 검토 (창원 성산구 상남동 44-1)

> ⛔ 도림 재개발 시스템과 **완전히 분리**된 별개 사업 자료입니다.
> backend/frontend, members.xlsx, RAG, 지도에 연결·import 하지 않습니다.

## 폴더
- `문서/`   메모(.md), 보고서 PPT/PDF
- `작업도구/` 보고서 재생성·실거래 조회 스크립트 (build_report4.py, make_summary10.py, apt_trade.py)
- `실거래/`  성산구 아파트 실거래 csv, 요약 xlsx
- `증빙/`   법령 캡처, 증빙 이미지

원본: Google Drive "대동백화점 부지 분할 검토" 폴더 (이어하기_README.md 참고)

## 집 PC와 동기화
집 PC에서 `창원_대동백화점` 폴더 내용을 이 폴더로 복사 → `git add analysis/daedong` → commit/push.
(zip 대용량 파일은 git에 부적합하면 PDF·md·스크립트·csv만 올리세요.)

## API 키
`DATA_GO_KR_KEY`(공공데이터포털)는 **파일/저장소에 적지 않습니다.**
`.env`(gitignore 대상) 또는 클라우드 환경 비밀값으로만 설정합니다. 예시는 `.env.example`.
