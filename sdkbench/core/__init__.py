"""Core data structures for SDK-Bench evaluation."""

from sdkbench.core.solution import Solution
from sdkbench.core.ground_truth import GroundTruth
from sdkbench.core.result import (
    EvaluationResult,
    IAccResult,
    CCompResult,
    IPAResult,
    FCorrResult,
    CQResult,
    SemSimResult,
)

__all__ = [
    "Solution",
    "GroundTruth",
    "EvaluationResult",
    "IAccResult",
    "CCompResult",
    "IPAResult",
    "FCorrResult",
    "CQResult",
    "SemSimResult",
]
