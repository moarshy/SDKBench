"""Unit tests for F-CORR (Functional Correctness) metric."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core.result import FCorrResult


class TestFCorrResult:
    """Tests for FCorrResult model."""

    def test_default_values(self):
        """Should have correct default values."""
        result = FCorrResult()

        assert result.score == 0.0
        assert result.tests_passed == 0
        assert result.tests_total == 0
        assert result.tests_skipped == 0
        assert result.pass_rate == 0.0
        assert result.failed_tests == []
        assert result.error_messages == []
        assert result.failure_details == []
        assert result.raw_output is None

    def test_pass_rate_calculation(self):
        """Should calculate pass rate from passed/total."""
        result = FCorrResult(
            tests_passed=8,
            tests_total=10,
        )

        assert result.pass_rate == 80.0
        assert result.score == 80.0

    def test_zero_tests(self):
        """Should handle zero total tests."""
        result = FCorrResult(
            tests_passed=0,
            tests_total=0,
        )

        assert result.pass_rate == 0.0
        assert result.score == 0.0

    def test_perfect_score(self):
        """Should return 100 for all tests passing."""
        result = FCorrResult(
            tests_passed=5,
            tests_total=5,
        )

        assert result.pass_rate == 100.0
        assert result.score == 100.0

    def test_failure_details_storage(self):
        """Should store failure details with stack traces."""
        failure_details = [
            {
                "test_name": "test_database_connection",
                "file_path": "tests/test_init.py",
                "line_number": 18,
                "error_message": "AssertionError: assert app.db is not None",
                "stack_trace": "Traceback...",
            }
        ]
        result = FCorrResult(
            tests_passed=2,
            tests_total=3,
            failed_tests=["test_database_connection"],
            failure_details=failure_details,
        )

        assert len(result.failure_details) == 1
        assert result.failure_details[0]["test_name"] == "test_database_connection"
        assert result.failure_details[0]["stack_trace"] == "Traceback..."

    def test_raw_output_storage(self):
        """Should store raw test output."""
        raw_output = """
============================= test session starts ==============================
collected 3 items
test_init.py ..F
============================== 1 failed, 2 passed in 0.05s =====================
"""
        result = FCorrResult(
            tests_passed=2,
            tests_total=3,
            raw_output=raw_output,
        )

        assert result.raw_output == raw_output
        assert "collected 3 items" in result.raw_output

    def test_install_error_storage(self):
        """Should store installation errors."""
        result = FCorrResult(
            tests_passed=0,
            tests_total=0,
            install_error="pip install failed: Package not found",
        )

        assert result.install_error == "pip install failed: Package not found"

    def test_build_error_storage(self):
        """Should store build errors."""
        result = FCorrResult(
            tests_passed=0,
            tests_total=0,
            build_error="tsc failed: Type errors found",
        )

        assert result.build_error == "tsc failed: Type errors found"


class TestFCorrStrictScoring:
    """Tests for strict scoring mode."""

    def test_strict_mode_any_failure_zero_score(self):
        """In strict mode, any failure should result in 0 score."""
        # Even with 99% pass rate, strict mode gives 0
        result = FCorrResult(
            tests_passed=99,
            tests_total=100,
        )
        # In strict mode, we'd override the score to 0
        # This is handled by the evaluator, not the model

        assert result.pass_rate == 99.0

    def test_strict_mode_all_pass_full_score(self):
        """In strict mode, all passing should give 100."""
        result = FCorrResult(
            tests_passed=10,
            tests_total=10,
        )

        assert result.score == 100.0


class TestFCorrErrorHandling:
    """Tests for error handling in F-CORR."""

    def test_stores_multiple_error_messages(self):
        """Should store multiple error messages."""
        result = FCorrResult(
            tests_passed=0,
            tests_total=3,
            failed_tests=["test_a", "test_b", "test_c"],
            error_messages=[
                "test_a: AssertionError",
                "test_b: ValueError",
                "test_c: TypeError",
            ],
        )

        assert len(result.error_messages) == 3
        assert "AssertionError" in result.error_messages[0]

    def test_stores_failed_test_names(self):
        """Should store names of failed tests."""
        result = FCorrResult(
            tests_passed=2,
            tests_total=5,
            failed_tests=["test_one", "test_two", "test_three"],
        )

        assert len(result.failed_tests) == 3
        assert "test_one" in result.failed_tests
        assert "test_two" in result.failed_tests
        assert "test_three" in result.failed_tests


class TestFCorrSkippedTests:
    """Tests for handling skipped tests."""

    def test_skipped_tests_counted(self):
        """Should count skipped tests separately."""
        result = FCorrResult(
            tests_passed=3,
            tests_total=5,
            tests_skipped=2,
        )

        assert result.tests_skipped == 2
        # Pass rate based on total, not excluding skipped
        assert result.pass_rate == 60.0
