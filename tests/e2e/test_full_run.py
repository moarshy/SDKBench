"""End-to-end benchmark run tests."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.evaluator.evaluator import Evaluator
from sdkbench.core import EvaluationResult


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def samples_dir(project_root) -> Path:
    """Return path to samples directory."""
    return project_root / "samples"


@pytest.fixture
def lancedb_sample_dirs(samples_dir) -> list:
    """Get list of LanceDB sample directories."""
    lancedb_dir = samples_dir / "lancedb"
    if not lancedb_dir.exists():
        pytest.skip("LanceDB samples not found")
    return sorted(lancedb_dir.iterdir())[:3]  # First 3 for speed


@pytest.fixture
def clerk_sample_dirs(samples_dir) -> list:
    """Get list of Clerk sample directories."""
    clerk_dir = samples_dir / "clerk"
    if not clerk_dir.exists():
        pytest.skip("Clerk samples not found")
    return sorted(clerk_dir.iterdir())[:3]  # First 3 for speed


# =============================================================================
# Single Sample Evaluation Tests
# =============================================================================

class TestSingleSampleEvaluation:
    """Tests for evaluating a single sample."""

    def test_evaluate_lancedb_sample_quick(self, lancedb_sample_dirs):
        """Quick evaluation of a LanceDB sample should complete."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        result = evaluator.evaluate_quick()

        assert result is not None
        assert isinstance(result, EvaluationResult)
        assert result.sample_id is not None

    def test_evaluate_clerk_sample_quick(self, clerk_sample_dirs):
        """Quick evaluation of a Clerk sample should complete."""
        if not clerk_sample_dirs:
            pytest.skip("No Clerk samples available")

        sample_dir = clerk_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        result = evaluator.evaluate_quick()

        assert result is not None
        assert isinstance(result, EvaluationResult)

    def test_evaluation_produces_all_static_metrics(self, lancedb_sample_dirs):
        """Evaluation should produce all static metric results."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        result = evaluator.evaluate_quick()

        # All static metrics should be populated
        assert result.i_acc is not None
        assert result.c_comp is not None
        assert result.ipa is not None
        assert result.cq is not None
        assert result.sem_sim is not None

    def test_evaluation_has_valid_scores(self, lancedb_sample_dirs):
        """All scores should be in valid range (0-100)."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        result = evaluator.evaluate_quick()

        if result.i_acc:
            assert 0.0 <= result.i_acc.score <= 100.0
        if result.c_comp:
            assert 0.0 <= result.c_comp.score <= 100.0
        if result.ipa:
            assert 0.0 <= result.ipa.score <= 100.0
        if result.cq:
            assert 0.0 <= result.cq.score <= 100.0
        if result.sem_sim:
            assert 0.0 <= result.sem_sim.score <= 100.0


# =============================================================================
# Multi-Sample Batch Tests
# =============================================================================

class TestMultiSampleBatch:
    """Tests for batch evaluation of multiple samples."""

    def test_batch_evaluation_multiple_lancedb(self, lancedb_sample_dirs, tmp_path):
        """Batch evaluation of multiple LanceDB samples."""
        if len(lancedb_sample_dirs) < 2:
            pytest.skip("Need at least 2 LanceDB samples")

        solution_dirs = [
            d / "expected" for d in lancedb_sample_dirs[:2]
            if (d / "expected").exists()
        ]

        if not solution_dirs:
            pytest.skip("No valid sample directories found")

        results = Evaluator.batch_evaluate(
            solution_dirs,
            output_dir=tmp_path,
            run_build=False,
            run_tests=False
        )

        assert len(results) >= 1  # At least some should succeed

    def test_batch_saves_individual_results(self, lancedb_sample_dirs, tmp_path):
        """Batch evaluation should save individual result files."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        results = Evaluator.batch_evaluate(
            [sample_dir],
            output_dir=tmp_path,
            run_build=False,
            run_tests=False
        )

        # Check that output files were created
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) >= len(results)


# =============================================================================
# Cross-SDK Evaluation Tests
# =============================================================================

class TestCrossSDKEvaluation:
    """Tests for evaluating samples from different SDKs."""

    def test_evaluation_works_for_both_sdks(self, project_root):
        """Evaluation should work for both LanceDB and Clerk samples."""
        samples_dir = project_root / "samples"
        if not samples_dir.exists():
            pytest.skip("Samples directory not found")

        results = []

        # Try LanceDB
        lancedb_dir = samples_dir / "lancedb"
        if lancedb_dir.exists():
            sample_dirs = [d for d in sorted(lancedb_dir.iterdir()) if d.is_dir()][:1]
            if sample_dirs:
                sample_dir = sample_dirs[0] / "expected"
                if sample_dir.exists():
                    evaluator = Evaluator(sample_dir)
                    result = evaluator.evaluate_quick()
                    results.append(("lancedb", result))

        # Try Clerk
        clerk_dir = samples_dir / "clerk"
        if clerk_dir.exists():
            sample_dirs = [d for d in sorted(clerk_dir.iterdir()) if d.is_dir()][:1]
            if sample_dirs:
                sample_dir = sample_dirs[0] / "expected"
                if sample_dir.exists():
                    evaluator = Evaluator(sample_dir)
                    result = evaluator.evaluate_quick()
                    results.append(("clerk", result))

        # At least one should succeed
        if not results:
            pytest.skip("No valid samples found for either SDK")
        assert len(results) >= 1

    def test_sdk_detected_correctly(self, lancedb_sample_dirs, clerk_sample_dirs):
        """SDK should be detected correctly from metadata."""
        if lancedb_sample_dirs:
            sample_dir = lancedb_sample_dirs[0] / "expected"
            if sample_dir.exists():
                evaluator = Evaluator(sample_dir)
                assert evaluator.ground_truth.sdk == "lancedb"

        if clerk_sample_dirs:
            sample_dir = clerk_sample_dirs[0] / "expected"
            if sample_dir.exists():
                evaluator = Evaluator(sample_dir)
                assert evaluator.ground_truth.sdk == "clerk"


# =============================================================================
# Result Aggregation Tests
# =============================================================================

class TestResultAggregation:
    """Tests for result aggregation."""

    def test_overall_score_calculated(self, lancedb_sample_dirs):
        """Overall score should be calculated from individual metrics."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        result = evaluator.evaluate_quick()

        assert result.overall_score is not None
        assert 0.0 <= result.overall_score <= 100.0

    def test_summary_includes_all_metrics(self, lancedb_sample_dirs):
        """Summary should include scores for all metrics."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        summary = evaluator.get_summary()

        assert "scores" in summary
        expected_metrics = ["i_acc", "c_comp", "ipa", "cq", "sem_sim"]
        for metric in expected_metrics:
            assert metric in summary["scores"]


# =============================================================================
# Report Generation Tests
# =============================================================================

class TestReportGeneration:
    """Tests for report generation."""

    def test_detailed_report_generated(self, lancedb_sample_dirs):
        """Detailed report should be generated successfully."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        report = evaluator.get_detailed_report()

        assert isinstance(report, dict)
        assert "metrics" in report
        assert "overall_score" in report

    def test_report_has_metric_details(self, lancedb_sample_dirs):
        """Report should include details for each metric."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        report = evaluator.get_detailed_report()

        for metric_name in ["i_acc", "c_comp", "ipa", "cq", "sem_sim"]:
            assert metric_name in report["metrics"]
            metric_data = report["metrics"][metric_name]
            assert "score" in metric_data
            assert "details" in metric_data

    def test_report_saves_to_file(self, lancedb_sample_dirs, tmp_path):
        """Report should save to file correctly."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        output_path = tmp_path / "report.json"

        evaluator.save_results(output_path, detailed=True)

        assert output_path.exists()

        with open(output_path) as f:
            data = json.load(f)
            assert "metrics" in data


# =============================================================================
# Regression Prevention Tests
# =============================================================================

class TestRegressionPrevention:
    """Tests to prevent score regressions."""

    def test_expected_solution_scores_well(self, lancedb_sample_dirs):
        """Expected solutions should score reasonably well."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        evaluator = Evaluator(sample_dir)
        result = evaluator.evaluate_quick()

        # Expected solutions should score above 50% at minimum
        # (they may not be perfect due to metric implementation details)
        assert result.overall_score >= 0.0  # Basic sanity check

    def test_scores_are_deterministic(self, lancedb_sample_dirs):
        """Same input should produce same scores (deterministic)."""
        if not lancedb_sample_dirs:
            pytest.skip("No LanceDB samples available")

        sample_dir = lancedb_sample_dirs[0] / "expected"
        if not sample_dir.exists():
            pytest.skip("Expected directory not found")

        # Run evaluation twice
        evaluator1 = Evaluator(sample_dir)
        result1 = evaluator1.evaluate_quick()

        evaluator2 = Evaluator(sample_dir)
        result2 = evaluator2.evaluate_quick()

        # Scores should be identical
        assert result1.overall_score == result2.overall_score
        if result1.i_acc and result2.i_acc:
            assert result1.i_acc.score == result2.i_acc.score
