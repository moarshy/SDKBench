"""Unit tests for I-ACC (Initialization Correctness) metric."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core.result import IAccResult


class TestIAccResult:
    """Tests for IAccResult model."""

    def test_default_values(self):
        """Should have correct default values."""
        result = IAccResult()

        assert result.score == 0.0
        assert result.file_location_correct is False
        assert result.imports_correct is False
        assert result.pattern_correct is False
        assert result.placement_correct is False

    def test_score_auto_calculation(self):
        """Should auto-calculate score from components."""
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
        )

        # Score should be calculated: (0.20 + 0.20 + 0.30 + 0.30) * 100 = 100
        assert result.score == 100.0


class TestIAccScoring:
    """Tests for I-ACC score calculation."""

    def test_perfect_score(self):
        """Should return 100 for perfect match."""
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
        )

        assert result.score == 100.0

    def test_partial_score_file_and_imports(self):
        """Should calculate partial scores for file and imports only."""
        result = IAccResult(
            file_location_correct=True,  # 20%
            imports_correct=True,  # 20%
            pattern_correct=False,  # 0%
            placement_correct=False,  # 0%
        )

        # (0.20 + 0.20 + 0 + 0) * 100 = 40
        assert result.score == 40.0

    def test_partial_score_pattern_only(self):
        """Should calculate partial score for pattern only."""
        result = IAccResult(
            file_location_correct=False,  # 0%
            imports_correct=False,  # 0%
            pattern_correct=True,  # 30%
            placement_correct=False,  # 0%
        )

        # (0 + 0 + 0.30 + 0) * 100 = 30
        assert result.score == 30.0

    def test_partial_score_placement_only(self):
        """Should calculate partial score for placement only."""
        result = IAccResult(
            file_location_correct=False,  # 0%
            imports_correct=False,  # 0%
            pattern_correct=False,  # 0%
            placement_correct=True,  # 30%
        )

        # (0 + 0 + 0 + 0.30) * 100 = 30
        assert result.score == 30.0

    def test_zero_score(self):
        """Should return 0 for complete mismatch."""
        result = IAccResult(
            file_location_correct=False,
            imports_correct=False,
            pattern_correct=False,
            placement_correct=False,
        )

        assert result.score == 0.0

    def test_pattern_and_placement_weight_more(self):
        """Pattern and placement should have more weight than file/imports."""
        # File + imports (40%) vs pattern + placement (60%)
        result_low = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=False,
            placement_correct=False,
        )

        result_high = IAccResult(
            file_location_correct=False,
            imports_correct=False,
            pattern_correct=True,
            placement_correct=True,
        )

        assert result_high.score > result_low.score
        assert result_low.score == 40.0
        assert result_high.score == 60.0


class TestIAccResultWeights:
    """Tests for IAccResult component weights."""

    def test_file_location_weight(self):
        """File location should be worth 20%."""
        result = IAccResult(
            file_location_correct=True,
            imports_correct=False,
            pattern_correct=False,
            placement_correct=False,
        )

        assert result.score == 20.0

    def test_imports_weight(self):
        """Imports should be worth 20%."""
        result = IAccResult(
            file_location_correct=False,
            imports_correct=True,
            pattern_correct=False,
            placement_correct=False,
        )

        assert result.score == 20.0

    def test_pattern_weight(self):
        """Pattern should be worth 30%."""
        result = IAccResult(
            file_location_correct=False,
            imports_correct=False,
            pattern_correct=True,
            placement_correct=False,
        )

        assert result.score == 30.0

    def test_placement_weight(self):
        """Placement should be worth 30%."""
        result = IAccResult(
            file_location_correct=False,
            imports_correct=False,
            pattern_correct=False,
            placement_correct=True,
        )

        assert result.score == 30.0

    def test_weights_sum_to_100(self):
        """All weights should sum to 100%."""
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
        )

        assert result.score == 100.0


class TestIAccResultDetails:
    """Tests for IAccResult details field."""

    def test_default_details_empty(self):
        """Should have empty details by default."""
        result = IAccResult()

        assert result.details == {}

    def test_can_store_details(self):
        """Should be able to store additional details."""
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
            details={
                "found_file": "app/layout.tsx",
                "expected_file": "app/layout.tsx",
                "imports_found": ["@clerk/nextjs"],
            }
        )

        assert "found_file" in result.details
        assert result.details["imports_found"] == ["@clerk/nextjs"]


class TestIAccResultBooleanCombinations:
    """Tests for various boolean combinations."""

    def test_all_true(self):
        """All true should be 100."""
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
        )
        assert result.score == 100.0

    def test_all_false(self):
        """All false should be 0."""
        result = IAccResult(
            file_location_correct=False,
            imports_correct=False,
            pattern_correct=False,
            placement_correct=False,
        )
        assert result.score == 0.0

    def test_three_true_one_false(self):
        """Three true, one false."""
        # Missing file location (20%)
        result = IAccResult(
            file_location_correct=False,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
        )
        assert result.score == 80.0

        # Missing imports (20%)
        result = IAccResult(
            file_location_correct=True,
            imports_correct=False,
            pattern_correct=True,
            placement_correct=True,
        )
        assert result.score == 80.0

        # Missing pattern (30%)
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=False,
            placement_correct=True,
        )
        assert result.score == 70.0

        # Missing placement (30%)
        result = IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=False,
        )
        assert result.score == 70.0
