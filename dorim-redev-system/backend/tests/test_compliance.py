# dorim-redev-system/backend/tests/test_compliance.py
import pytest
from fastapi import HTTPException
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from compliance import ComplianceChecker


@pytest.fixture
def checker():
    return ComplianceChecker(workflow_path="ai_harness/workflow.yaml")


class TestFARLimit:
    """하드락 A: 용적률 검증"""

    def test_far_limit_exact_700_passes(self, checker):
        """700% 정확히는 통과해야 한다"""
        checker.check_far(700.0)  # Should not raise

    def test_far_limit_over_700_raises(self, checker):
        """700% 초과는 HARD_LOCK_A 발생"""
        with pytest.raises(HTTPException) as exc_info:
            checker.check_far(700.1)
        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["code"] == "HARD_LOCK_A"

    def test_far_limit_well_below_passes(self, checker):
        """500% 같이 충분히 낮으면 통과"""
        checker.check_far(500.0)  # Should not raise


class TestContractorSelection:
    """하드락 B: 시공사 입찰공고 시기 검증"""

    def test_contractor_blocked_at_stage1(self, checker):
        """STAGE_1에서 시공사 입찰공고 생성 시도 → 차단"""
        with pytest.raises(HTTPException) as exc_info:
            checker.check_doc_generation(
                doc_type="시공사입찰공고",
                current_stage="STAGE_1_PRELIMINARY",
                has_cost_verification=False,
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "HARD_LOCK_B"

    def test_contractor_blocked_at_stage2(self, checker):
        """STAGE_2에서도 시공사 입찰공고 차단"""
        with pytest.raises(HTTPException) as exc_info:
            checker.check_doc_generation(
                doc_type="시공사입찰공고",
                current_stage="STAGE_2_COMMITTEE",
                has_cost_verification=False,
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "HARD_LOCK_B"

    def test_contractor_allowed_at_stage3(self, checker):
        """STAGE_3(조합설립) 이후 시공사 입찰공고 허용"""
        checker.check_doc_generation(
            doc_type="시공사입찰공고",
            current_stage="STAGE_3_ASSOCIATION",
            has_cost_verification=False,
        )  # Should not raise

    def test_contractor_allowed_at_stage4(self, checker):
        """STAGE_4에서 시공사 입찰공고 허용"""
        checker.check_doc_generation(
            doc_type="시공사입찰공고",
            current_stage="STAGE_4_CONTRACTOR",
            has_cost_verification=False,
        )  # Should not raise

    def test_contractor_allowed_at_stage5(self, checker):
        """STAGE_5에서 시공사 입찰공고 허용"""
        checker.check_doc_generation(
            doc_type="시공사입찰공고",
            current_stage="STAGE_5_DISPOSAL",
            has_cost_verification=False,
        )  # Should not raise


class TestSaleAnnouncement:
    """하드락 C: 분양공고 공사비 검증 의무"""

    def test_sale_blocked_without_cost_verification(self, checker):
        """공사비 검증 없이 분양공고 → HARD_LOCK_C"""
        with pytest.raises(HTTPException) as exc_info:
            checker.check_doc_generation(
                doc_type="분양공고",
                current_stage="STAGE_4_CONTRACTOR",
                has_cost_verification=False,
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "HARD_LOCK_C"

    def test_sale_allowed_with_cost_verification(self, checker):
        """공사비 검증 있으면 분양공고 허용"""
        checker.check_doc_generation(
            doc_type="분양공고",
            current_stage="STAGE_4_CONTRACTOR",
            has_cost_verification=True,
        )  # Should not raise

    def test_sale_blocked_stage2_even_with_verification(self, checker):
        """STAGE_2에서는 분양공고 차단 (공사비 검증 있어도)"""
        # Note: Based on workflow.yaml, STAGE_2 has sale_announcement: BLOCKED
        with pytest.raises(HTTPException) as exc_info:
            checker.check_doc_generation(
                doc_type="분양공고",
                current_stage="STAGE_2_COMMITTEE",
                has_cost_verification=True,
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "HARD_LOCK_C"

    def test_sale_allowed_stage3_with_verification(self, checker):
        """STAGE_3에서는 분양공고 차단 (공사비 검증 필요하지 않음)"""
        # Note: Based on workflow.yaml, STAGE_3 has sale_announcement: BLOCKED
        with pytest.raises(HTTPException) as exc_info:
            checker.check_doc_generation(
                doc_type="분양공고",
                current_stage="STAGE_3_ASSOCIATION",
                has_cost_verification=True,
            )
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "HARD_LOCK_C"


class TestOtherDocuments:
    """다른 문서는 하드락 미적용"""

    def test_other_doc_always_allowed(self, checker):
        """'보고서' 같은 다른 문서는 항상 허용"""
        checker.check_doc_generation(
            doc_type="보고서",
            current_stage="STAGE_1_PRELIMINARY",
            has_cost_verification=False,
        )  # Should not raise

    def test_preliminary_docs_allowed_at_stage1(self, checker):
        """STAGE_1 필수 문서는 허용"""
        checker.check_doc_generation(
            doc_type="정비계획 사전검토 신청서",
            current_stage="STAGE_1_PRELIMINARY",
            has_cost_verification=False,
        )  # Should not raise
