# dorim-redev-system/backend/compliance.py
"""
Hard-lock compliance middleware for 도림사거리 역세권 재개발
Enforces immutable regulatory constraints per CLAUDE.md 규칙 2
"""

from pathlib import Path
import yaml
from fastapi import HTTPException


CONTRACTOR_ALLOWED_STAGES = {
    "STAGE_3_ASSOCIATION",
    "STAGE_4_CONTRACTOR",
    "STAGE_5_DISPOSAL",
}

SALE_BLOCKED_STAGES = {
    "STAGE_1_PRELIMINARY",
    "STAGE_2_COMMITTEE",
    "STAGE_3_ASSOCIATION",
}


class ComplianceChecker:
    """
    하드락 미들웨어: 3가지 규제 제약 자동 차단
    - HARD_LOCK_A: 용적률 700% 상한
    - HARD_LOCK_B: 시공사 선정 시기 잠금
    - HARD_LOCK_C: 공사비 검증 없는 분양공고 차단
    """

    def __init__(self, workflow_path: str = "ai_harness/workflow.yaml"):
        # Try to resolve path relative to project root
        self.workflow_path = Path(workflow_path)
        if not self.workflow_path.is_absolute():
            # If relative, try to find it from backend directory
            candidate = Path(__file__).parent.parent / workflow_path
            if candidate.exists():
                self.workflow_path = candidate

    def _load_workflow(self) -> dict:
        """workflow.yaml 로드"""
        with open(self.workflow_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def check_far(self, far_pct: float) -> None:
        """
        하드락 A: 용적률 상한 초과 차단
        - 이 사업(도림2동)의 법적상한용적률: 377.86% (가중평균)
        - 서울시 역세권 운영기준 절대 상한: 700% (1차 역세권 준주거)

        Args:
            far_pct: 용적률 (%)

        Raises:
            HTTPException: 상한 초과 시 422 Unprocessable Entity
        """
        wf = self._load_workflow()
        abs_limit = wf["compliance"]["far_limit_pct"]          # 700 (절대 상한)
        project_limit = wf["compliance"].get("project_far_limit_pct", 377.86)  # 이 사업 상한

        if far_pct > abs_limit:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "HARD_LOCK_A",
                    "message": (
                        f"1차 역세권 법적 절대 상한 {abs_limit}% 초과. "
                        "서울시 역세권 장기전세주택 건립 운영기준(2026.3.6.) 위반."
                    ),
                },
            )
        if far_pct > project_limit:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "HARD_LOCK_A_PROJECT",
                    "message": (
                        f"도림2동 역세권 사업 법적상한용적률 {project_limit}% 초과. "
                        f"계획 용적률: {project_limit}% (1차 역세권 준주거 500%+준공업 300% 가중평균). "
                        "정비계획 수립(안) 2023.6 기준 초과."
                    ),
                },
            )

    def check_doc_generation(
        self,
        doc_type: str,
        current_stage: str,
        has_cost_verification: bool,
    ) -> None:
        """
        하드락 B·C: 문서 생성 시기 및 조건 검증

        Args:
            doc_type: 문서 유형 (e.g., "시공사입찰공고", "분양공고")
            current_stage: 현재 사업 단계 (STAGE_1_PRELIMINARY ~ STAGE_5_DISPOSAL)
            has_cost_verification: 공사비 검증 결과서 첨부 여부

        Raises:
            HTTPException: 규칙 위반 시 403 Forbidden
        """
        wf = self._load_workflow()

        # 하드락 B: 시공사 입찰공고는 조합설립 이후만
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

        # 하드락 C: 분양공고는 단계별 조건 확인
        if doc_type == "분양공고":
            # 먼저 현 단계에서 분양공고가 차단되어 있는지 확인
            stage_config = wf["stages"].get(current_stage, {})
            hard_locks = stage_config.get("hard_locks", {})
            sale_lock = hard_locks.get("sale_announcement", "BLOCKED")

            # sale_announcement이 BLOCKED면 차단
            if sale_lock == "BLOCKED":
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "HARD_LOCK_C",
                        "message": (
                            "현 단계에서는 분양공고 생성이 허용되지 않습니다. "
                            "해당 단계에서의 하드락 설정을 확인하세요."
                        ),
                    },
                )

            # sale_announcement이 REQUIRES_COST_VERIFICATION면 공사비 검증 필수
            if sale_lock == "REQUIRES_COST_VERIFICATION" and not has_cost_verification:
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
