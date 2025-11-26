"""Unit tests for CQ (Code Quality) metric."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core.result import CQResult


class TestCQResult:
    """Tests for CQResult model."""

    def test_default_values(self):
        """Should have correct default values."""
        result = CQResult()

        assert result.score == 100.0  # Starts at 100, deductions reduce it
        assert result.type_errors == 0
        assert result.eslint_errors == 0
        assert result.security_issues == 0
        assert result.type_error_details == []
        assert result.eslint_error_details == []
        assert result.security_issue_details == []
        assert result.deductions == []

    def test_score_deduction_from_type_errors(self):
        """Should deduct 5 points per type error."""
        result = CQResult(
            type_errors=4,  # 4 * 5 = 20 points deducted
        )

        assert result.score == 80.0

    def test_score_deduction_from_eslint_errors(self):
        """Should deduct 2 points per ESLint error."""
        result = CQResult(
            eslint_errors=10,  # 10 * 2 = 20 points deducted
        )

        assert result.score == 80.0

    def test_score_deduction_from_security_issues(self):
        """Should deduct 20 points per security issue."""
        result = CQResult(
            security_issues=2,  # 2 * 20 = 40 points deducted
        )

        assert result.score == 60.0

    def test_combined_deductions(self):
        """Should combine all deductions."""
        result = CQResult(
            type_errors=2,      # 10 points
            eslint_errors=5,    # 10 points
            security_issues=1,  # 20 points
        )
        # Total: 40 points deducted = 60

        assert result.score == 60.0

    def test_score_minimum_zero(self):
        """Score should not go below 0."""
        result = CQResult(
            type_errors=50,  # 250 points would be deducted
        )

        assert result.score == 0.0

    def test_perfect_score(self):
        """Should return 100 for clean code."""
        result = CQResult(
            type_errors=0,
            eslint_errors=0,
            security_issues=0,
        )

        assert result.score == 100.0


class TestCQDeductions:
    """Tests for CQ deductions field."""

    def test_deductions_list(self):
        """Should store deductions list."""
        deductions = [
            {"reason": "Type error in app.py:10", "points": 5},
            {"reason": "ESLint: no-unused-vars", "points": 2},
            {"reason": "Security: SQL injection risk", "points": 20},
        ]
        result = CQResult(deductions=deductions)

        assert len(result.deductions) == 3
        assert result.total_deductions == 27

    def test_total_deductions_property(self):
        """Should calculate total deductions correctly."""
        deductions = [
            {"points": 5},
            {"points": 10},
            {"points": 15},
        ]
        result = CQResult(deductions=deductions)

        assert result.total_deductions == 30

    def test_score_from_deductions(self):
        """Should calculate score from deductions list."""
        deductions = [
            {"reason": "Error 1", "points": 10},
            {"reason": "Error 2", "points": 15},
        ]
        result = CQResult(deductions=deductions)

        # 100 - 25 = 75
        assert result.score == 75.0

    def test_empty_deductions(self):
        """Should handle empty deductions list."""
        result = CQResult(deductions=[])

        assert result.total_deductions == 0
        assert result.score == 100.0


class TestCQErrorDetails:
    """Tests for storing error details."""

    def test_type_error_details(self):
        """Should store type error details."""
        details = [
            "app.py:10 - Type 'string' not assignable to 'number'",
            "utils.py:25 - Missing return type annotation",
        ]
        result = CQResult(
            type_errors=2,
            type_error_details=details,
        )

        assert len(result.type_error_details) == 2
        assert "app.py:10" in result.type_error_details[0]

    def test_eslint_error_details(self):
        """Should store ESLint error details."""
        details = [
            "no-unused-vars: 'x' is defined but never used",
            "semi: Missing semicolon",
        ]
        result = CQResult(
            eslint_errors=2,
            eslint_error_details=details,
        )

        assert len(result.eslint_error_details) == 2

    def test_security_issue_details(self):
        """Should store security issue details."""
        details = [
            "Potential XSS vulnerability in user input handling",
        ]
        result = CQResult(
            security_issues=1,
            security_issue_details=details,
        )

        assert len(result.security_issue_details) == 1
        assert "XSS" in result.security_issue_details[0]
