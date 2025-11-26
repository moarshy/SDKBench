"""Unit tests for test harness models."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.test_harness.models import (
    Language, TestFramework, RunnerDetectionResult, TestResult, TestFailure,
    DependencyInstallResult, FCorrResult
)


class TestLanguageEnum:
    """Tests for Language enum."""

    def test_python_value(self):
        """Should have correct Python value."""
        assert Language.PYTHON.value == "python"

    def test_typescript_value(self):
        """Should have correct TypeScript value."""
        assert Language.TYPESCRIPT.value == "typescript"


class TestTestFrameworkEnum:
    """Tests for TestFramework enum."""

    def test_pytest_value(self):
        """Should have correct pytest value."""
        assert TestFramework.PYTEST.value == "pytest"

    def test_jest_value(self):
        """Should have correct Jest value."""
        assert TestFramework.JEST.value == "jest"

    def test_vitest_value(self):
        """Should have correct Vitest value."""
        assert TestFramework.VITEST.value == "vitest"

    def test_mocha_value(self):
        """Should have correct Mocha value."""
        assert TestFramework.MOCHA.value == "mocha"


class TestRunnerDetectionResult:
    """Tests for RunnerDetectionResult model."""

    def test_default_values(self):
        """Should have correct default values."""
        result = RunnerDetectionResult(detected=False)

        assert result.detected is False
        assert result.confidence == 0.0
        assert result.markers_found == []
        assert result.language is None
        assert result.framework is None

    def test_with_all_fields(self):
        """Should accept all fields."""
        result = RunnerDetectionResult(
            detected=True,
            confidence=0.95,
            markers_found=["package.json", "jest in dependencies"],
            language=Language.TYPESCRIPT,
            framework=TestFramework.JEST,
        )

        assert result.detected is True
        assert result.confidence == 0.95
        assert len(result.markers_found) == 2
        assert result.language == Language.TYPESCRIPT
        assert result.framework == TestFramework.JEST


class TestTestFailure:
    """Tests for TestFailure model."""

    def test_required_fields(self):
        """Should require test_name and error_message."""
        failure = TestFailure(
            test_name="test_example",
            error_message="AssertionError"
        )

        assert failure.test_name == "test_example"
        assert failure.error_message == "AssertionError"

    def test_optional_fields(self):
        """Should accept optional fields."""
        failure = TestFailure(
            test_name="test_example",
            error_message="AssertionError",
            file_path="tests/test_app.py",
            line_number=42,
            stack_trace="Traceback...\n  at line 42"
        )

        assert failure.file_path == "tests/test_app.py"
        assert failure.line_number == 42
        assert failure.stack_trace == "Traceback...\n  at line 42"

    def test_default_optional_fields(self):
        """Should have None defaults for optional fields."""
        failure = TestFailure(
            test_name="test_x",
            error_message="Error"
        )

        assert failure.file_path is None
        assert failure.line_number is None
        assert failure.stack_trace is None


class TestTestResult:
    """Tests for TestResult model."""

    def test_with_required_success_field(self):
        """Should require success field."""
        result = TestResult(success=False)

        assert result.success is False
        assert result.total == 0
        assert result.passed == 0
        assert result.failed == 0
        assert result.skipped == 0
        assert result.duration == 0.0
        assert result.output == ""
        assert result.failures == []

    def test_pass_rate_calculation(self):
        """Should calculate pass rate correctly."""
        result = TestResult(success=True, total=10, passed=8, failed=2)

        assert result.pass_rate == 80.0

    def test_pass_rate_zero_total(self):
        """Should handle zero total tests."""
        result = TestResult(success=False, total=0, passed=0, failed=0)

        assert result.pass_rate == 0.0

    def test_with_failures(self):
        """Should store failure details."""
        failures = [
            TestFailure(test_name="test_one", error_message="Error 1"),
            TestFailure(test_name="test_two", error_message="Error 2"),
        ]
        result = TestResult(
            success=False,
            total=5,
            passed=3,
            failed=2,
            failures=failures
        )

        assert len(result.failures) == 2
        assert result.failures[0].test_name == "test_one"

    def test_successful_result(self):
        """Should represent successful test run."""
        result = TestResult(
            success=True,
            total=10,
            passed=10,
            failed=0,
            duration=5.5
        )

        assert result.success is True
        assert result.pass_rate == 100.0


class TestDependencyInstallResult:
    """Tests for DependencyInstallResult model."""

    def test_successful_install(self):
        """Should represent successful installation."""
        result = DependencyInstallResult(
            success=True,
            duration=5.5,
            output="Successfully installed pytest"
        )

        assert result.success is True
        assert result.duration == 5.5
        assert result.error is None

    def test_failed_install(self):
        """Should represent failed installation."""
        result = DependencyInstallResult(
            success=False,
            error="Package not found",
            duration=2.0
        )

        assert result.success is False
        assert result.error == "Package not found"


class TestFCorrResult:
    """Tests for FCorrResult model (test harness version)."""

    def test_with_required_score(self):
        """Should require score field."""
        result = FCorrResult(score=0.0)

        assert result.score == 0.0
        assert result.passed is False
        assert result.error is None

    def test_with_test_results(self):
        """Should store test results."""
        test_result = TestResult(
            success=True,
            total=5,
            passed=5,
            failed=0
        )
        result = FCorrResult(
            score=100.0,
            test_results=test_result,
            duration=10.5
        )

        assert result.score == 100.0
        assert result.passed is True
        assert result.test_results.total == 5
        assert result.duration == 10.5

    def test_with_error(self):
        """Should store error information."""
        result = FCorrResult(
            score=0.0,
            error="Test execution failed"
        )

        assert result.score == 0.0
        assert result.passed is False
        assert result.error == "Test execution failed"

    def test_passed_property(self):
        """Should compute passed based on score."""
        result_pass = FCorrResult(score=50.0)
        result_fail = FCorrResult(score=0.0)

        assert result_pass.passed is True
        assert result_fail.passed is False
