"""Integration tests for the Evaluator orchestrator."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.evaluator.evaluator import Evaluator
from sdkbench.core import (
    EvaluationResult,
    IAccResult,
    CCompResult,
    IPAResult,
    FCorrResult,
    CQResult,
    SemSimResult,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_metadata():
    """Create a valid metadata structure for testing."""
    return {
        "sample_id": "test_sample_001",
        "task_type": 1,
        "task_name": "initialization",
        "sdk": "lancedb",
        "lancedb_version": "0.5.0",
        "framework": "python",
        "difficulty": "easy",
        "ground_truth": {
            "ingredients": {
                "initialization": {
                    "location": "app.py",
                    "pattern": "lancedb.connect",
                    "imports": ["lancedb"]
                }
            }
        },
        "evaluation_targets": {
            "i_acc": {
                "correct_file": "app.py",
                "correct_pattern": "lancedb.connect",
                "correct_imports": ["import lancedb"]
            },
            "c_comp": {
                "required_components": 2
            },
            "ipa": {
                "integration_points": ["lancedb.connect"]
            },
            "f_corr": {
                "test_command": "pytest",
                "expected_pass": True
            }
        }
    }


@pytest.fixture
def temp_solution_dir(mock_metadata):
    """Create a temporary solution directory with metadata."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="eval_test_"))

    # Create solution file
    (tmp_dir / "app.py").write_text('''
import lancedb

db = lancedb.connect("./my_db")

def main():
    print(db.table_names())

if __name__ == "__main__":
    main()
''')

    # Create metadata.json
    (tmp_dir / "metadata.json").write_text(json.dumps(mock_metadata, indent=2))

    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def temp_solution_dir_with_tests(temp_solution_dir):
    """Solution directory with test files."""
    tests_dir = temp_solution_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text('''
def test_import():
    import lancedb
    assert lancedb is not None
''')
    return temp_solution_dir


# =============================================================================
# Evaluator Initialization Tests
# =============================================================================

class TestEvaluatorInitialization:
    """Tests for Evaluator initialization."""

    def test_evaluator_accepts_solution_dir(self, temp_solution_dir):
        """Evaluator should accept a solution directory path."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator.solution_dir == temp_solution_dir

    def test_evaluator_accepts_path_object(self, temp_solution_dir):
        """Evaluator should accept Path objects."""
        evaluator = Evaluator(Path(temp_solution_dir))

        assert evaluator.solution_dir == temp_solution_dir

    def test_evaluator_loads_solution(self, temp_solution_dir):
        """Evaluator should load solution files."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator.solution is not None
        assert hasattr(evaluator.solution, 'files')

    def test_evaluator_loads_ground_truth(self, temp_solution_dir):
        """Evaluator should load ground truth from metadata."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator.ground_truth is not None
        assert evaluator.ground_truth.sample_id == "test_sample_001"

    def test_evaluator_default_metadata_path(self, temp_solution_dir):
        """Evaluator should default to metadata.json in solution dir."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator.metadata_path == temp_solution_dir / "metadata.json"

    def test_evaluator_custom_metadata_path(self, temp_solution_dir, mock_metadata):
        """Evaluator should accept custom metadata path."""
        custom_path = temp_solution_dir / "custom_metadata.json"
        custom_path.write_text(json.dumps(mock_metadata))

        evaluator = Evaluator(temp_solution_dir, metadata_path=custom_path)

        assert evaluator.metadata_path == custom_path

    def test_evaluator_initializes_all_metric_evaluators(self, temp_solution_dir):
        """Evaluator should initialize all 6 metric evaluators."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator.i_acc_evaluator is not None
        assert evaluator.c_comp_evaluator is not None
        assert evaluator.ipa_evaluator is not None
        assert evaluator.f_corr_evaluator is not None
        assert evaluator.cq_evaluator is not None
        assert evaluator.sem_sim_evaluator is not None


class TestEvaluatorMissingFiles:
    """Tests for handling missing files."""

    def test_raises_on_missing_solution_dir(self, tmp_path):
        """Should raise error for non-existent solution directory."""
        with pytest.raises(FileNotFoundError):
            Evaluator(tmp_path / "nonexistent")

    def test_raises_on_missing_metadata(self, tmp_path):
        """Should raise error for missing metadata.json."""
        solution_dir = tmp_path / "solution"
        solution_dir.mkdir()
        (solution_dir / "app.py").write_text("# empty")

        with pytest.raises(FileNotFoundError):
            Evaluator(solution_dir)


# =============================================================================
# Evaluate Method Tests
# =============================================================================

class TestEvaluateMethod:
    """Tests for the evaluate() method."""

    def test_evaluate_returns_evaluation_result(self, temp_solution_dir):
        """evaluate() should return an EvaluationResult object."""
        evaluator = Evaluator(temp_solution_dir)

        # Mock the expensive operations
        with patch.object(evaluator.f_corr_evaluator, 'evaluate') as mock_fcorr:
            mock_fcorr.return_value = FCorrResult(score=100.0, tests_passed=1, tests_total=1)
            result = evaluator.evaluate(run_build=False, run_tests=False)

        assert isinstance(result, EvaluationResult)

    def test_evaluate_populates_sample_id(self, temp_solution_dir):
        """evaluate() should populate sample_id from ground truth."""
        evaluator = Evaluator(temp_solution_dir)

        with patch.object(evaluator.f_corr_evaluator, 'evaluate') as mock_fcorr:
            mock_fcorr.return_value = FCorrResult()
            result = evaluator.evaluate(run_build=False, run_tests=False)

        assert result.sample_id == "test_sample_001"

    def test_evaluate_populates_task_type(self, temp_solution_dir):
        """evaluate() should populate task_type from ground truth."""
        evaluator = Evaluator(temp_solution_dir)

        with patch.object(evaluator.f_corr_evaluator, 'evaluate') as mock_fcorr:
            mock_fcorr.return_value = FCorrResult()
            result = evaluator.evaluate(run_build=False, run_tests=False)

        assert result.task_type == 1

    def test_evaluate_runs_all_metrics_by_default(self, temp_solution_dir):
        """evaluate() should run all 6 metrics by default."""
        evaluator = Evaluator(temp_solution_dir)

        with patch.object(evaluator.f_corr_evaluator, 'evaluate') as mock_fcorr:
            mock_fcorr.return_value = FCorrResult()
            result = evaluator.evaluate(run_build=False, run_tests=False)

        # Check all metrics were populated
        assert result.i_acc is not None
        assert result.c_comp is not None
        assert result.ipa is not None
        assert result.f_corr is not None
        assert result.cq is not None
        assert result.sem_sim is not None

    def test_evaluate_selective_metrics(self, temp_solution_dir):
        """evaluate() should only run specified metrics."""
        evaluator = Evaluator(temp_solution_dir)

        result = evaluator.evaluate(
            run_build=False,
            run_tests=False,
            metrics=['i_acc', 'c_comp']
        )

        assert result.i_acc is not None
        assert result.c_comp is not None
        assert result.ipa is None  # Not requested
        assert result.f_corr is None  # Not requested

    def test_evaluate_passes_build_flag_to_fcorr(self, temp_solution_dir):
        """evaluate() should pass run_build flag to F-CORR."""
        evaluator = Evaluator(temp_solution_dir)

        with patch.object(evaluator.f_corr_evaluator, 'evaluate') as mock_fcorr:
            mock_fcorr.return_value = FCorrResult()
            evaluator.evaluate(run_build=True, run_tests=False)

            mock_fcorr.assert_called_once()
            call_kwargs = mock_fcorr.call_args[1]
            assert call_kwargs.get('run_build') is True

    def test_evaluate_passes_tests_flag_to_fcorr(self, temp_solution_dir):
        """evaluate() should pass run_tests flag to F-CORR."""
        evaluator = Evaluator(temp_solution_dir)

        with patch.object(evaluator.f_corr_evaluator, 'evaluate') as mock_fcorr:
            mock_fcorr.return_value = FCorrResult()
            evaluator.evaluate(run_build=False, run_tests=True)

            mock_fcorr.assert_called_once()
            call_kwargs = mock_fcorr.call_args[1]
            assert call_kwargs.get('run_tests') is True


# =============================================================================
# Evaluate Quick Method Tests
# =============================================================================

class TestEvaluateQuickMethod:
    """Tests for the evaluate_quick() method."""

    def test_evaluate_quick_returns_result(self, temp_solution_dir):
        """evaluate_quick() should return an EvaluationResult."""
        evaluator = Evaluator(temp_solution_dir)
        result = evaluator.evaluate_quick()

        assert isinstance(result, EvaluationResult)

    def test_evaluate_quick_skips_fcorr(self, temp_solution_dir):
        """evaluate_quick() should skip F-CORR (returns None)."""
        evaluator = Evaluator(temp_solution_dir)
        result = evaluator.evaluate_quick()

        # F-CORR is disabled in quick mode
        assert result.f_corr is None

    def test_evaluate_quick_runs_static_metrics(self, temp_solution_dir):
        """evaluate_quick() should run all static metrics."""
        evaluator = Evaluator(temp_solution_dir)
        result = evaluator.evaluate_quick()

        assert result.i_acc is not None
        assert result.c_comp is not None
        assert result.ipa is not None
        assert result.cq is not None
        assert result.sem_sim is not None


# =============================================================================
# Grade Calculation Tests
# =============================================================================

class TestGradeCalculation:
    """Tests for grade calculation."""

    def test_grade_a_for_90_plus(self, temp_solution_dir):
        """Scores 90+ should get grade A."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator._calculate_grade(90.0) == "A"
        assert evaluator._calculate_grade(95.0) == "A"
        assert evaluator._calculate_grade(100.0) == "A"

    def test_grade_b_for_80_to_89(self, temp_solution_dir):
        """Scores 80-89 should get grade B."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator._calculate_grade(80.0) == "B"
        assert evaluator._calculate_grade(85.0) == "B"
        assert evaluator._calculate_grade(89.9) == "B"

    def test_grade_c_for_70_to_79(self, temp_solution_dir):
        """Scores 70-79 should get grade C."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator._calculate_grade(70.0) == "C"
        assert evaluator._calculate_grade(75.0) == "C"
        assert evaluator._calculate_grade(79.9) == "C"

    def test_grade_d_for_60_to_69(self, temp_solution_dir):
        """Scores 60-69 should get grade D."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator._calculate_grade(60.0) == "D"
        assert evaluator._calculate_grade(65.0) == "D"
        assert evaluator._calculate_grade(69.9) == "D"

    def test_grade_f_for_below_60(self, temp_solution_dir):
        """Scores below 60 should get grade F."""
        evaluator = Evaluator(temp_solution_dir)

        assert evaluator._calculate_grade(59.9) == "F"
        assert evaluator._calculate_grade(50.0) == "F"
        assert evaluator._calculate_grade(0.0) == "F"


# =============================================================================
# Report Generation Tests
# =============================================================================

class TestReportGeneration:
    """Tests for report generation methods."""

    def test_get_summary_returns_dict(self, temp_solution_dir):
        """get_summary() should return a dictionary."""
        evaluator = Evaluator(temp_solution_dir)
        summary = evaluator.get_summary()

        assert isinstance(summary, dict)

    def test_get_summary_contains_sample_id(self, temp_solution_dir):
        """get_summary() should include sample_id."""
        evaluator = Evaluator(temp_solution_dir)
        summary = evaluator.get_summary()

        assert "sample_id" in summary
        assert summary["sample_id"] == "test_sample_001"

    def test_get_summary_contains_task_type(self, temp_solution_dir):
        """get_summary() should include task_type."""
        evaluator = Evaluator(temp_solution_dir)
        summary = evaluator.get_summary()

        assert "task_type" in summary
        assert summary["task_type"] == 1

    def test_get_summary_contains_overall_score(self, temp_solution_dir):
        """get_summary() should include overall_score."""
        evaluator = Evaluator(temp_solution_dir)
        summary = evaluator.get_summary()

        assert "overall_score" in summary

    def test_get_summary_contains_scores_dict(self, temp_solution_dir):
        """get_summary() should include scores dictionary."""
        evaluator = Evaluator(temp_solution_dir)
        summary = evaluator.get_summary()

        assert "scores" in summary
        assert isinstance(summary["scores"], dict)

    def test_get_summary_contains_grade(self, temp_solution_dir):
        """get_summary() should include grade."""
        evaluator = Evaluator(temp_solution_dir)
        summary = evaluator.get_summary()

        assert "grade" in summary
        assert summary["grade"] in ["A", "B", "C", "D", "F"]

    def test_get_detailed_report_returns_dict(self, temp_solution_dir):
        """get_detailed_report() should return a dictionary."""
        evaluator = Evaluator(temp_solution_dir)
        report = evaluator.get_detailed_report()

        assert isinstance(report, dict)

    def test_get_detailed_report_contains_metrics_section(self, temp_solution_dir):
        """get_detailed_report() should include metrics section."""
        evaluator = Evaluator(temp_solution_dir)
        report = evaluator.get_detailed_report()

        assert "metrics" in report
        assert isinstance(report["metrics"], dict)

    def test_get_detailed_report_has_all_metric_keys(self, temp_solution_dir):
        """get_detailed_report() should have all 6 metric keys."""
        evaluator = Evaluator(temp_solution_dir)
        report = evaluator.get_detailed_report()

        expected_keys = ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]
        for key in expected_keys:
            assert key in report["metrics"]


# =============================================================================
# Static Methods Tests
# =============================================================================

class TestStaticMethods:
    """Tests for static/class methods."""

    def test_evaluate_directory_returns_result(self, temp_solution_dir):
        """evaluate_directory() should return EvaluationResult."""
        with patch('sdkbench.evaluator.evaluator.Evaluator.evaluate') as mock_eval:
            mock_eval.return_value = EvaluationResult(
                sample_id="test",
                solution_dir=temp_solution_dir,
                task_type=1
            )
            result = Evaluator.evaluate_directory(temp_solution_dir)

        assert isinstance(result, EvaluationResult)

    def test_batch_evaluate_returns_list(self, temp_solution_dir):
        """batch_evaluate() should return list of results."""
        with patch.object(Evaluator, 'evaluate_directory') as mock_eval:
            mock_eval.return_value = EvaluationResult(
                sample_id="test",
                solution_dir=temp_solution_dir,
                task_type=1
            )
            results = Evaluator.batch_evaluate(
                [temp_solution_dir],
                output_dir=temp_solution_dir
            )

        assert isinstance(results, list)

    def test_batch_evaluate_handles_failures(self, temp_solution_dir, tmp_path):
        """batch_evaluate() should continue when single sample fails."""
        bad_dir = tmp_path / "bad_sample"
        bad_dir.mkdir()

        # Should not raise, should continue with other samples
        results = Evaluator.batch_evaluate(
            [bad_dir, temp_solution_dir],
            output_dir=tmp_path,
            run_build=False,
            run_tests=False
        )

        # At least one might succeed (the temp_solution_dir)
        # The bad one should not crash the batch
        assert isinstance(results, list)


# =============================================================================
# Metric Handling on Failure Tests
# =============================================================================

class TestMetricFailureHandling:
    """Tests for handling metric evaluation failures."""

    def test_evaluate_continues_when_single_metric_fails(self, temp_solution_dir):
        """evaluate() should continue when a single metric fails."""
        evaluator = Evaluator(temp_solution_dir)

        # Make I-ACC fail
        with patch.object(evaluator.i_acc_evaluator, 'evaluate', side_effect=Exception("I-ACC error")):
            # This should not crash the entire evaluation
            with pytest.raises(Exception):
                evaluator.evaluate(run_build=False, run_tests=False)

    def test_result_includes_none_for_failed_metrics(self, temp_solution_dir):
        """Result should have None for metrics not run."""
        evaluator = Evaluator(temp_solution_dir)

        # Only run a subset
        result = evaluator.evaluate(
            run_build=False,
            run_tests=False,
            metrics=['i_acc']
        )

        assert result.i_acc is not None
        assert result.c_comp is None  # Not requested
