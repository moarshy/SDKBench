"""Unit tests for IPA (Integration Point Accuracy) metric."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core.result import IPAResult


class TestIPAResult:
    """Tests for IPAResult model."""

    def test_default_values(self):
        """Should have correct default values."""
        result = IPAResult()

        assert result.score == 0.0
        assert result.precision == 0.0
        assert result.recall == 0.0
        assert result.f1 == 0.0
        assert result.true_positives == []
        assert result.false_positives == []
        assert result.false_negatives == []

    def test_f1_score_sets_score(self):
        """Setting F1 should set overall score."""
        result = IPAResult(f1=0.75)

        # score is f1 * 100
        assert result.score == 75.0

    def test_perfect_score(self):
        """Should handle perfect F1 score."""
        result = IPAResult(
            precision=100.0,
            recall=100.0,
            f1=1.0,
        )

        assert result.f1 == 1.0
        assert result.score == 100.0

    def test_zero_f1(self):
        """Should handle zero F1."""
        result = IPAResult(
            precision=0.0,
            recall=0.0,
            f1=0.0,
        )

        assert result.f1 == 0.0
        assert result.score == 0.0


class TestIPAConfusionMatrix:
    """Tests for confusion matrix components."""

    def test_true_positives_list(self):
        """Should store true positives as list."""
        result = IPAResult(
            true_positives=["pattern1", "pattern2", "pattern3"],
        )

        assert len(result.true_positives) == 3
        assert "pattern1" in result.true_positives

    def test_false_positives_list(self):
        """Should store false positives as list."""
        result = IPAResult(
            false_positives=["wrong_pattern1", "wrong_pattern2"],
        )

        assert len(result.false_positives) == 2
        assert "wrong_pattern1" in result.false_positives

    def test_false_negatives_list(self):
        """Should store false negatives as list."""
        result = IPAResult(
            false_negatives=["missed_pattern1", "missed_pattern2", "missed_pattern3"],
        )

        assert len(result.false_negatives) == 3
        assert "missed_pattern1" in result.false_negatives

    def test_precision_calculation_from_lists(self):
        """Should verify precision can be calculated from list lengths."""
        tp_list = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        fp_list = ["fp1", "fp2"]

        # Precision = TP / (TP + FP) = 8 / 10 = 0.8
        precision = len(tp_list) / (len(tp_list) + len(fp_list))

        result = IPAResult(
            precision=precision * 100,  # Store as percentage
            true_positives=tp_list,
            false_positives=fp_list,
        )

        assert result.precision == 80.0

    def test_recall_calculation_from_lists(self):
        """Should verify recall can be calculated from list lengths."""
        tp_list = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
        fn_list = ["fn1", "fn2"]

        # Recall = TP / (TP + FN) = 8 / 10 = 0.8
        recall = len(tp_list) / (len(tp_list) + len(fn_list))

        result = IPAResult(
            recall=recall * 100,  # Store as percentage
            true_positives=tp_list,
            false_negatives=fn_list,
        )

        assert result.recall == 80.0


class TestIPAEdgeCases:
    """Tests for edge cases in IPA metric."""

    def test_no_predictions(self):
        """Should handle case with no predictions."""
        result = IPAResult(
            true_positives=[],
            false_positives=[],
            false_negatives=["expected1", "expected2"],
            precision=0.0,
            recall=0.0,
            f1=0.0,
        )

        assert result.f1 == 0.0
        assert result.score == 0.0
        assert len(result.false_negatives) == 2

    def test_all_false_positives(self):
        """Should handle case with all false positives."""
        result = IPAResult(
            true_positives=[],
            false_positives=["fp1", "fp2", "fp3"],
            false_negatives=["fn1", "fn2"],
            precision=0.0,
            recall=0.0,
            f1=0.0,
        )

        assert result.precision == 0.0
        assert result.f1 == 0.0
        assert len(result.false_positives) == 3

    def test_high_precision_low_recall(self):
        """Should handle high precision with low recall."""
        result = IPAResult(
            precision=95.0,
            recall=20.0,
            f1=0.33,  # Approximate F1 for these values
        )

        # F1 should be much lower than precision (as percentage)
        assert result.f1 * 100 < result.precision

    def test_low_precision_high_recall(self):
        """Should handle low precision with high recall."""
        result = IPAResult(
            precision=20.0,
            recall=95.0,
            f1=0.33,  # Approximate F1 for these values
        )

        # F1 should be much lower than recall (as percentage)
        assert result.f1 * 100 < result.recall

    def test_empty_lists_default(self):
        """Should default to empty lists."""
        result = IPAResult()

        assert result.true_positives == []
        assert result.false_positives == []
        assert result.false_negatives == []
