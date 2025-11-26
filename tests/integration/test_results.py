"""Integration tests for Result models."""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core.result import (
    EvaluationResult,
    IAccResult,
    CCompResult,
    IPAResult,
    FCorrResult,
    CQResult,
    SemSimResult,
)


# =============================================================================
# IAccResult Integration Tests
# =============================================================================

class TestIAccResultIntegration:
    """Integration tests for IAccResult scoring."""

    def test_iacc_score_from_all_true(self):
        """Score should be 100 when all components are correct."""
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
        )

        assert result.score == 100.0

    def test_iacc_score_from_all_false(self):
        """Score should be 0 when all components are incorrect."""
        result = IAccResult(
            file_location_correct=False,
            imports_correct=False,
            pattern_correct=False,
            placement_correct=False,
        )

        assert result.score == 0.0

    def test_iacc_weighted_scoring(self):
        """Score should use weighted components (20+20+30+30)."""
        # Only file and imports correct (20% + 20% = 40%)
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=False,
            placement_correct=False,
        )

        assert result.score == 40.0

    def test_iacc_serialization_roundtrip(self):
        """IAccResult should serialize and deserialize correctly."""
        original = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=False,
            details={"found_file": "app.py"}
        )

        # Serialize to dict
        data = original.model_dump()

        # Deserialize back
        restored = IAccResult(**data)

        assert restored.score == original.score
        assert restored.file_location_correct == original.file_location_correct
        assert restored.details == original.details


# =============================================================================
# CCompResult Integration Tests
# =============================================================================

class TestCCompResultIntegration:
    """Integration tests for CCompResult scoring."""

    def test_ccomp_perfect_score(self):
        """Score should be 100 when all components are perfect."""
        result = CCompResult(
            env_vars_score=1.0,
            provider_props_score=1.0,
            middleware_config_score=1.0,
        )

        assert result.score == 100.0

    def test_ccomp_zero_score(self):
        """Score should be 0 when all components are zero."""
        result = CCompResult(
            env_vars_score=0.0,
            provider_props_score=0.0,
            middleware_config_score=0.0,
        )

        assert result.score == 0.0

    def test_ccomp_weighted_formula(self):
        """Score should use weighted formula (50/30/20)."""
        # Only env_vars correct (weight 0.5) = 50
        result = CCompResult(
            env_vars_score=1.0,
            provider_props_score=0.0,
            middleware_config_score=0.0,
        )

        assert result.score == 50.0

    def test_ccomp_tracks_missing_items(self):
        """CCompResult should track missing configuration items."""
        result = CCompResult(
            env_vars_score=0.5,
            missing_env_vars=["API_KEY", "SECRET"],
            missing_provider_props=["afterSignInUrl"],
        )

        assert len(result.missing_env_vars) == 2
        assert "API_KEY" in result.missing_env_vars
        assert len(result.missing_provider_props) == 1

    def test_ccomp_serialization_roundtrip(self):
        """CCompResult should serialize and deserialize correctly."""
        original = CCompResult(
            env_vars_score=0.8,
            provider_props_score=1.0,
            middleware_config_score=0.5,
            missing_env_vars=["KEY1"]
        )

        data = original.model_dump()
        restored = CCompResult(**data)

        assert abs(restored.score - original.score) < 0.01
        assert restored.missing_env_vars == original.missing_env_vars


# =============================================================================
# IPAResult Integration Tests
# =============================================================================

class TestIPAResultIntegration:
    """Integration tests for IPAResult scoring.

    Note: IPAResult stores precision/recall/f1 as 0-100 values,
    and the score is f1 * 100 (so also 0-100 scale).
    """

    def test_ipa_perfect_score(self):
        """Score should be 100 when f1 is 1.0 (stored as 100)."""
        result = IPAResult(
            precision=100.0,  # 0-100 scale
            recall=100.0,
            f1=1.0,  # 0-1 scale, will be converted to 0-100 for score
        )

        assert result.score == 100.0  # f1 * 100 = 100

    def test_ipa_zero_score(self):
        """Score should be 0 when f1 is 0."""
        result = IPAResult(
            precision=0.0,
            recall=100.0,
            f1=0.0,
        )

        assert result.score == 0.0

    def test_ipa_f1_stored_directly(self):
        """F1 value is stored directly (not auto-calculated from P/R)."""
        # The IPAResult doesn't auto-calculate F1 from P/R
        # It expects f1 to be passed in
        result = IPAResult(
            precision=80.0,
            recall=60.0,
            f1=0.6857,  # Pre-calculated F1 on 0-1 scale
        )

        assert abs(result.f1 - 0.6857) < 0.001
        # Score is f1 * 100
        assert abs(result.score - 68.57) < 0.01

    def test_ipa_tracks_integration_points(self):
        """IPAResult should track found and missing points."""
        result = IPAResult(
            precision=50.0,
            recall=50.0,
            f1=0.5,
            true_positives=["app.py", "middleware.py"],
            false_positives=["wrong.py"],
            false_negatives=["missing.py"],
        )

        assert len(result.true_positives) == 2
        assert len(result.false_positives) == 1
        assert len(result.false_negatives) == 1

    def test_ipa_serialization_roundtrip(self):
        """IPAResult should serialize and deserialize correctly."""
        original = IPAResult(
            precision=75.0,
            recall=80.0,
            f1=0.77,
            true_positives=["a.py", "b.py"],
        )

        data = original.model_dump()
        restored = IPAResult(**data)

        assert abs(restored.f1 - original.f1) < 0.001
        assert restored.true_positives == original.true_positives


# =============================================================================
# FCorrResult Integration Tests
# =============================================================================

class TestFCorrResultIntegration:
    """Integration tests for FCorrResult scoring."""

    def test_fcorr_perfect_score(self):
        """Score should be 100 when all tests pass."""
        result = FCorrResult(
            tests_passed=10,
            tests_total=10,
        )

        assert result.score == 100.0

    def test_fcorr_zero_score(self):
        """Score should be 0 when no tests pass."""
        result = FCorrResult(
            tests_passed=0,
            tests_total=10,
        )

        assert result.score == 0.0

    def test_fcorr_partial_score(self):
        """Score should be pass rate percentage."""
        result = FCorrResult(
            tests_passed=7,
            tests_total=10,
        )

        assert result.score == 70.0

    def test_fcorr_handles_zero_total(self):
        """Score should handle zero total tests."""
        result = FCorrResult(
            tests_passed=0,
            tests_total=0,
        )

        # Implementation specific - check it doesn't crash
        assert result.score >= 0.0

    def test_fcorr_tracks_failed_tests(self):
        """FCorrResult should track failed test names."""
        result = FCorrResult(
            tests_passed=2,
            tests_total=3,
            failed_tests=["test_login"],
            error_messages=["AssertionError: expected True"],
        )

        assert len(result.failed_tests) == 1
        assert "test_login" in result.failed_tests
        assert len(result.error_messages) == 1

    def test_fcorr_tracks_failure_details(self):
        """FCorrResult should track detailed failure info."""
        result = FCorrResult(
            tests_passed=1,
            tests_total=2,
            failure_details=[{
                "test_name": "test_auth",
                "file_path": "tests/test_auth.py",
                "line_number": 15,
                "error_message": "AssertionError",
                "stack_trace": "..."
            }],
        )

        assert len(result.failure_details) == 1
        assert result.failure_details[0]["test_name"] == "test_auth"

    def test_fcorr_serialization_roundtrip(self):
        """FCorrResult should serialize and deserialize correctly."""
        original = FCorrResult(
            tests_passed=8,
            tests_total=10,
            failed_tests=["test_a", "test_b"],
        )

        data = original.model_dump()
        restored = FCorrResult(**data)

        assert restored.score == original.score
        assert restored.failed_tests == original.failed_tests
        assert restored.tests_passed == original.tests_passed


# =============================================================================
# CQResult Integration Tests
# =============================================================================

class TestCQResultIntegration:
    """Integration tests for CQResult scoring.

    Note: CQResult uses 'eslint_errors' not 'lint_errors' field.
    Deductions: type_errors * 5, eslint_errors * 2, security_issues * 20
    """

    def test_cq_perfect_score(self):
        """Score should be 100 with no issues."""
        result = CQResult(
            type_errors=0,
            eslint_errors=0,
            security_issues=0,
        )

        assert result.score == 100.0

    def test_cq_deduction_for_type_errors(self):
        """Type errors should deduct from score (-5 each)."""
        result = CQResult(
            type_errors=2,  # -5 each = -10
            eslint_errors=0,
            security_issues=0,
        )

        assert result.score == 90.0

    def test_cq_deduction_for_eslint_errors(self):
        """ESLint errors should deduct from score (-2 each)."""
        result = CQResult(
            type_errors=0,
            eslint_errors=5,  # -2 each = -10
            security_issues=0,
        )

        assert result.score == 90.0

    def test_cq_deduction_for_security_issues(self):
        """Security issues should deduct heavily from score (-20 each)."""
        result = CQResult(
            type_errors=0,
            eslint_errors=0,
            security_issues=1,  # -20 each
        )

        assert result.score == 80.0

    def test_cq_score_floor_at_zero(self):
        """Score should not go below 0."""
        result = CQResult(
            type_errors=100,
            eslint_errors=100,
            security_issues=100,
        )

        assert result.score >= 0.0

    def test_cq_serialization_roundtrip(self):
        """CQResult should serialize and deserialize correctly."""
        original = CQResult(
            type_errors=3,
            eslint_errors=5,
            security_issues=1,
        )

        data = original.model_dump()
        restored = CQResult(**data)

        assert restored.score == original.score
        assert restored.type_errors == original.type_errors


# =============================================================================
# SemSimResult Integration Tests
# =============================================================================

class TestSemSimResultIntegration:
    """Integration tests for SemSimResult scoring."""

    def test_semsim_uses_similarity_score(self):
        """Score should use similarity_score field."""
        result = SemSimResult(
            similarity_score=85.0,
        )

        assert result.score == 85.0

    def test_semsim_pattern_match_tracking(self):
        """SemSimResult should track pattern matching."""
        result = SemSimResult(
            similarity_score=90.0,
            pattern_match=True,
            approach_match=True,
        )

        assert result.pattern_match is True
        assert result.approach_match is True

    def test_semsim_serialization_roundtrip(self):
        """SemSimResult should serialize and deserialize correctly."""
        original = SemSimResult(
            similarity_score=75.5,
            pattern_match=True,
            approach_match=False,
        )

        data = original.model_dump()
        restored = SemSimResult(**data)

        assert restored.score == original.score
        assert restored.pattern_match == original.pattern_match
        assert restored.approach_match == original.approach_match


# =============================================================================
# EvaluationResult Integration Tests
# =============================================================================

class TestEvaluationResultIntegration:
    """Integration tests for EvaluationResult aggregation."""

    def test_overall_score_calculation(self):
        """Overall score should be average of all metric scores."""
        result = EvaluationResult(
            sample_id="test",
            solution_dir=Path("/tmp/test"),
            task_type=1,
            i_acc=IAccResult(
                file_location_correct=True,
                imports_correct=True,
                pattern_correct=True,
                placement_correct=True,
            ),  # 100
            c_comp=CCompResult(
                env_vars_score=1.0,
                provider_props_score=1.0,
                middleware_config_score=1.0,
            ),  # 100
            ipa=IPAResult(precision=100.0, recall=100.0, f1=1.0),  # score = f1 * 100 = 100
            f_corr=FCorrResult(tests_passed=10, tests_total=10),  # 100
            cq=CQResult(type_errors=0, eslint_errors=0, security_issues=0),  # 100
            sem_sim=SemSimResult(similarity_score=100.0),  # 100
        )

        # All 100s should average to 100
        assert result.overall_score == 100.0

    def test_overall_score_with_none_metrics(self):
        """Overall score should handle None metrics."""
        result = EvaluationResult(
            sample_id="test",
            solution_dir=Path("/tmp/test"),
            task_type=1,
            i_acc=IAccResult(
                file_location_correct=True,
                imports_correct=True,
                pattern_correct=True,
                placement_correct=True,
            ),
            c_comp=None,  # Not evaluated
            ipa=None,
            f_corr=None,
            cq=None,
            sem_sim=None,
        )

        # Should not crash, should calculate from available metrics
        assert result.overall_score >= 0.0

    def test_evaluation_result_serialization(self):
        """EvaluationResult should serialize to JSON."""
        result = EvaluationResult(
            sample_id="test_001",
            solution_dir=Path("/tmp/test"),
            task_type=1,
            i_acc=IAccResult(
                file_location_correct=True,
                imports_correct=True,
                pattern_correct=True,
                placement_correct=True,
            ),
        )

        data = result.model_dump()

        assert data["sample_id"] == "test_001"
        assert data["task_type"] == 1
        assert "i_acc" in data

    def test_evaluation_result_to_json_file(self, tmp_path):
        """EvaluationResult should save to JSON file."""
        result = EvaluationResult(
            sample_id="test_001",
            solution_dir=Path("/tmp/test"),
            task_type=1,
            i_acc=IAccResult(
                file_location_correct=True,
                imports_correct=True,
                pattern_correct=True,
                placement_correct=True,
            ),
        )

        output_path = tmp_path / "result.json"
        result.to_json_file(output_path)

        assert output_path.exists()

        # Verify content
        with open(output_path) as f:
            data = json.load(f)
            assert data["sample_id"] == "test_001"

    def test_get_metric_summary(self):
        """get_metric_summary() should return formatted summary."""
        result = EvaluationResult(
            sample_id="test",
            solution_dir=Path("/tmp/test"),
            task_type=1,
            i_acc=IAccResult(
                file_location_correct=True,
                imports_correct=True,
                pattern_correct=True,
                placement_correct=True,
            ),
            c_comp=CCompResult(
                env_vars_score=0.8,
                provider_props_score=1.0,
                middleware_config_score=0.5,
            ),
        )

        summary = result.get_metric_summary()

        assert isinstance(summary, dict)
        assert "i_acc" in summary
        assert "c_comp" in summary


# =============================================================================
# Cross-Metric Consistency Tests
# =============================================================================

class TestCrossMetricConsistency:
    """Tests for consistency across metrics."""

    def test_all_results_have_score_property(self):
        """All result types should have a score property."""
        results = [
            IAccResult(),
            CCompResult(),
            IPAResult(),
            FCorrResult(),
            CQResult(),
            SemSimResult(),
        ]

        for result in results:
            assert hasattr(result, 'score')
            assert isinstance(result.score, (int, float))

    def test_all_results_serializable(self):
        """All result types should be JSON serializable."""
        results = [
            IAccResult(file_location_correct=True, imports_correct=True,
                      pattern_correct=True, placement_correct=True),
            CCompResult(env_vars_score=1.0, provider_props_score=1.0,
                       middleware_config_score=1.0),
            IPAResult(precision=100.0, recall=100.0, f1=1.0),
            FCorrResult(tests_passed=10, tests_total=10),
            CQResult(type_errors=0, eslint_errors=0, security_issues=0),
            SemSimResult(similarity_score=100.0),
        ]

        for result in results:
            data = result.model_dump()
            json_str = json.dumps(data)
            assert json_str is not None

    def test_scores_in_valid_range(self):
        """All scores should be in 0-100 range."""
        results = [
            IAccResult(file_location_correct=True, imports_correct=True,
                      pattern_correct=True, placement_correct=True),
            CCompResult(env_vars_score=1.0, provider_props_score=1.0,
                       middleware_config_score=1.0),
            IPAResult(precision=100.0, recall=100.0, f1=1.0),
            FCorrResult(tests_passed=10, tests_total=10),
            CQResult(type_errors=0, eslint_errors=0, security_issues=0),
            SemSimResult(similarity_score=100.0),
        ]

        for result in results:
            assert 0.0 <= result.score <= 100.0, f"{type(result).__name__} score out of range"
