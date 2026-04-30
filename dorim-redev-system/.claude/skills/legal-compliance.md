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
