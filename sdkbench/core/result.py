"""Result classes for storing evaluation outcomes."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, computed_field


# ==================== Base Metric Result ====================

class MetricResult(BaseModel):
    """Base class for metric results."""
    # Use None as sentinel to distinguish "not set" from "calculated as 0"
    score: Optional[float] = None  # 0-100, None means auto-calculate
    details: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        """Ensure score has a default value if not calculated by subclass."""
        if self.score is None:
            self.score = 0.0


# ==================== Individual Metric Results ====================

class IAccResult(MetricResult):
    """I-ACC (Initialization Correctness) metric result."""
    file_location_correct: bool = False
    imports_correct: bool = False
    pattern_correct: bool = False
    placement_correct: bool = False

    def model_post_init(self, __context: Any) -> None:
        """Calculate score based on components."""
        if self.score is None:  # Only calculate if not explicitly set
            self.score = (
                (self.file_location_correct * 0.20) +
                (self.imports_correct * 0.20) +
                (self.pattern_correct * 0.30) +
                (self.placement_correct * 0.30)
            ) * 100


class CCompResult(MetricResult):
    """C-COMP (Configuration Completeness) metric result."""
    env_vars_score: float = 0.0  # 0-1
    provider_props_score: float = 0.0  # 0-1
    middleware_config_score: float = 0.0  # 0-1
    missing_env_vars: List[str] = Field(default_factory=list)
    missing_provider_props: List[str] = Field(default_factory=list)
    missing_middleware_config: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        """Calculate score based on components."""
        if self.score is None:  # Only calculate if not explicitly set
            self.score = (
                (self.env_vars_score * 0.5) +
                (self.provider_props_score * 0.3) +
                (self.middleware_config_score * 0.2)
            ) * 100


class IPAResult(MetricResult):
    """IPA (Integration Point Accuracy) metric result."""
    precision: float = 0.0  # 0-1 scale
    recall: float = 0.0  # 0-1 scale
    f1: float = 0.0  # 0-1 scale
    true_positives: List[str] = Field(default_factory=list)
    false_positives: List[str] = Field(default_factory=list)
    false_negatives: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        """Use F1 score as the main score (converted to 0-100 scale)."""
        if self.score is None:  # Only calculate if not explicitly set
            self.score = self.f1 * 100  # Convert from 0-1 to 0-100


class FCorrResult(MetricResult):
    """F-CORR (Functional Correctness) metric result."""
    tests_passed: int = 0
    tests_total: int = 0
    tests_skipped: int = 0
    pass_rate: float = 0.0  # 0-100
    failed_tests: List[str] = Field(default_factory=list)
    error_messages: List[str] = Field(default_factory=list)
    # Detailed failure information with stack traces
    failure_details: List[Dict[str, Any]] = Field(default_factory=list)
    # Each entry: {
    #   "test_name": "test_database_connection",
    #   "file_path": "tests/test_init.py",
    #   "line_number": 18,
    #   "error_message": "AssertionError: assert app.db is not None",
    #   "stack_trace": "Traceback (most recent call last):\n..."
    # }
    # Raw test output for debugging
    raw_output: Optional[str] = None
    # Build/install error details
    install_error: Optional[str] = None
    build_error: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        """Calculate pass rate and score."""
        # Always calculate pass_rate from test counts
        if self.tests_total > 0:
            self.pass_rate = (self.tests_passed / self.tests_total) * 100
        else:
            self.pass_rate = 0.0

        # Only calculate score if not explicitly set
        if self.score is None:
            self.score = self.pass_rate


class CQResult(MetricResult):
    """CQ (Code Quality) metric result."""
    type_errors: int = 0
    eslint_errors: int = 0
    security_issues: int = 0
    type_error_details: List[str] = Field(default_factory=list)
    eslint_error_details: List[str] = Field(default_factory=list)
    security_issue_details: List[str] = Field(default_factory=list)
    # Deductions list for detailed quality analysis
    deductions: List[Dict[str, Any]] = Field(default_factory=list)

    @property
    def total_deductions(self) -> int:
        """Calculate total deduction points."""
        return sum(d.get('points', 0) for d in self.deductions)

    def model_post_init(self, __context: Any) -> None:
        """Calculate score by deducting points."""
        if self.score is None:  # Only calculate if not explicitly set
            # If deductions provided, calculate from them
            if self.deductions:
                self.score = max(0, 100 - self.total_deductions)
            else:
                # Legacy calculation from individual counts
                score = 100
                score -= self.type_errors * 5
                score -= self.eslint_errors * 2
                score -= self.security_issues * 20
                self.score = max(0, score)


class SemSimResult(MetricResult):
    """SEM-SIM (Semantic Similarity) metric result."""
    similarity_score: float = 0.0  # 0-100
    pattern_match: bool = False
    approach_match: bool = False
    matched_patterns: List[str] = Field(default_factory=list)
    missing_patterns: List[str] = Field(default_factory=list)
    # Numeric component scores (0-100 scale) for detailed analysis
    structure_similarity: float = 0.0
    pattern_matching: float = 0.0
    approach_alignment: float = 0.0

    def model_post_init(self, __context: Any) -> None:
        """Use similarity score as main score."""
        if self.score is None:  # Only calculate if not explicitly set
            self.score = self.similarity_score


# ==================== Complete Evaluation Result ====================

class EvaluationResult(BaseModel):
    """Complete evaluation result for a solution."""

    # Metadata
    sample_id: str
    solution_dir: Path
    task_type: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    duration_seconds: float = 0.0

    # Metric results (optional, set by evaluator)
    i_acc: Optional[IAccResult] = None
    c_comp: Optional[CCompResult] = None
    ipa: Optional[IPAResult] = None
    f_corr: Optional[FCorrResult] = None
    cq: Optional[CQResult] = None
    sem_sim: Optional[SemSimResult] = None

    # Error tracking
    evaluation_error: Optional[str] = None

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    @computed_field
    @property
    def overall_score(self) -> float:
        """Calculate overall score as average of all metrics.

        Returns:
            Average score across all completed metrics (0-100)
        """
        scores = []
        if self.i_acc:
            scores.append(self.i_acc.score)
        if self.c_comp:
            scores.append(self.c_comp.score)
        if self.ipa:
            scores.append(self.ipa.score)
        if self.f_corr:
            scores.append(self.f_corr.score)
        if self.cq:
            scores.append(self.cq.score)
        if self.sem_sim:
            scores.append(self.sem_sim.score)

        return sum(scores) / len(scores) if scores else 0.0

    @property
    def has_errors(self) -> bool:
        """Check if evaluation encountered errors.

        Returns:
            True if evaluation_error is set
        """
        return self.evaluation_error is not None

    def get_metric_summary(self) -> Dict[str, float]:
        """Get summary of all metric scores.

        Returns:
            Dict mapping metric names to scores
        """
        return {
            "i_acc": self.i_acc.score if self.i_acc else 0.0,
            "c_comp": self.c_comp.score if self.c_comp else 0.0,
            "ipa": self.ipa.score if self.ipa else 0.0,
            "f_corr": self.f_corr.score if self.f_corr else 0.0,
            "cq": self.cq.score if self.cq else 0.0,
            "sem_sim": self.sem_sim.score if self.sem_sim else 0.0,
            "overall": self.overall_score
        }

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of results
        """
        return self.model_dump(mode='python')

    def to_json_file(self, path: Path) -> None:
        """Save results to JSON file.

        Args:
            path: Path to save JSON file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def from_dict(cls, data: Dict) -> 'EvaluationResult':
        """Load from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            EvaluationResult instance
        """
        return cls.model_validate(data)

    @classmethod
    def from_json_file(cls, path: Path) -> 'EvaluationResult':
        """Load from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            EvaluationResult instance
        """
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"EvaluationResult(sample={self.sample_id}, "
            f"overall={self.overall_score:.1f}%)"
        )

    def print_summary(self) -> None:
        """Print formatted summary to console."""
        print(f"\n📊 Evaluation Results: {self.sample_id}")
        print(f"   Task Type: {self.task_type}")
        print(f"   Duration: {self.duration_seconds:.2f}s")
        print()

        if self.evaluation_error:
            print(f"   ❌ Error: {self.evaluation_error}")
            return

        # Print metric scores
        if self.i_acc:
            print(f"   I-ACC:    {self.i_acc.score:5.1f}%  {'✓' if self.i_acc.score >= 70 else '✗'}")
        if self.c_comp:
            print(f"   C-COMP:   {self.c_comp.score:5.1f}%  {'✓' if self.c_comp.score >= 70 else '✗'}")
        if self.ipa:
            print(f"   IPA:      {self.ipa.score:5.1f}%  {'✓' if self.ipa.score >= 70 else '✗'} (F1)")
        if self.f_corr:
            print(f"   F-CORR:   {self.f_corr.score:5.1f}%  {'✓' if self.f_corr.score >= 70 else '✗'} ({self.f_corr.tests_passed}/{self.f_corr.tests_total} tests)")
        if self.cq:
            print(f"   CQ:       {self.cq.score:5.1f}%  {'✓' if self.cq.score >= 70 else '✗'}")
        if self.sem_sim:
            print(f"   SEM-SIM:  {self.sem_sim.score:5.1f}%  {'✓' if self.sem_sim.score >= 70 else '✗'}")

        print()
        print(f"   Overall:  {self.overall_score:5.1f}%  {'✓' if self.overall_score >= 70 else '✗'}")
