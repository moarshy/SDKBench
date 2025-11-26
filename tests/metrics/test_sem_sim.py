"""Unit tests for SEM-SIM (Semantic Similarity) metric."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core.result import SemSimResult


class TestSemSimResult:
    """Tests for SemSimResult model."""

    def test_default_values(self):
        """Should have correct default values."""
        result = SemSimResult()

        assert result.score == 0.0
        assert result.similarity_score == 0.0
        assert result.pattern_match is False
        assert result.approach_match is False
        assert result.matched_patterns == []
        assert result.missing_patterns == []
        assert result.structure_similarity == 0.0
        assert result.pattern_matching == 0.0
        assert result.approach_alignment == 0.0

    def test_score_from_similarity(self):
        """Should calculate score from similarity_score."""
        result = SemSimResult(
            similarity_score=85.5,
        )

        assert result.score == 85.5

    def test_perfect_score(self):
        """Should handle perfect similarity score."""
        result = SemSimResult(
            similarity_score=100.0,
            pattern_match=True,
            approach_match=True,
        )

        assert result.score == 100.0
        assert result.pattern_match is True
        assert result.approach_match is True

    def test_component_scores(self):
        """Should store component similarity scores."""
        result = SemSimResult(
            similarity_score=75.0,
            structure_similarity=80.0,
            pattern_matching=70.0,
            approach_alignment=75.0,
        )

        assert result.structure_similarity == 80.0
        assert result.pattern_matching == 70.0
        assert result.approach_alignment == 75.0

    def test_matched_patterns(self):
        """Should store matched and missing patterns."""
        result = SemSimResult(
            similarity_score=60.0,
            matched_patterns=["lancedb.connect", "db.create_table"],
            missing_patterns=["db.search", "table.add"],
        )

        assert len(result.matched_patterns) == 2
        assert len(result.missing_patterns) == 2
        assert "lancedb.connect" in result.matched_patterns
        assert "db.search" in result.missing_patterns


class TestSemSimScoreCalculation:
    """Tests for SemSim score calculations."""

    def test_weighted_average_calculation(self):
        """Should calculate weighted average correctly."""
        # Given component scores
        structure = 0.8  # 80%
        pattern = 0.7   # 70%
        approach = 0.9  # 90%

        # Weights: structure 30%, pattern 40%, approach 30%
        expected = (structure * 0.30 + pattern * 0.40 + approach * 0.30) * 100

        result = SemSimResult(
            similarity_score=expected,
            structure_similarity=structure * 100,
            pattern_matching=pattern * 100,
            approach_alignment=approach * 100,
        )

        assert abs(result.score - expected) < 0.01

    def test_pattern_match_threshold(self):
        """Should set pattern_match based on threshold."""
        # Pattern match is True when pattern_matching > 50
        result_high = SemSimResult(
            pattern_matching=60.0,
            pattern_match=True,
        )
        result_low = SemSimResult(
            pattern_matching=40.0,
            pattern_match=False,
        )

        assert result_high.pattern_match is True
        assert result_low.pattern_match is False

    def test_approach_match_threshold(self):
        """Should set approach_match based on threshold."""
        # Approach match is True when approach_alignment > 50
        result_high = SemSimResult(
            approach_alignment=60.0,
            approach_match=True,
        )
        result_low = SemSimResult(
            approach_alignment=40.0,
            approach_match=False,
        )

        assert result_high.approach_match is True
        assert result_low.approach_match is False


class TestSemSimEdgeCases:
    """Tests for edge cases in SemSim."""

    def test_zero_similarity(self):
        """Should handle zero similarity."""
        result = SemSimResult(
            similarity_score=0.0,
            pattern_match=False,
            approach_match=False,
        )

        assert result.score == 0.0

    def test_score_bounds(self):
        """Score should be within 0-100 range."""
        # Test that we don't exceed bounds
        result = SemSimResult(
            similarity_score=100.0,
            structure_similarity=100.0,
            pattern_matching=100.0,
            approach_alignment=100.0,
        )

        assert result.score <= 100.0
        assert result.score >= 0.0

    def test_empty_patterns(self):
        """Should handle empty pattern lists."""
        result = SemSimResult(
            similarity_score=50.0,
            matched_patterns=[],
            missing_patterns=[],
        )

        assert result.matched_patterns == []
        assert result.missing_patterns == []
