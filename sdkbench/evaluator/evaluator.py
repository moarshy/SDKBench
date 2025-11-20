"""Main evaluator that orchestrates all metrics."""

from pathlib import Path
from typing import Dict, Optional
import json

from sdkbench.core import Solution, GroundTruth, EvaluationResult
from sdkbench.metrics import (
    IAccEvaluator,
    CCompEvaluator,
    IPAEvaluator,
    FCorrEvaluator,
    CQEvaluator,
    SemSimEvaluator,
)


class Evaluator:
    """Main evaluator that runs all metrics and generates results.

    Orchestrates the evaluation of a solution against ground truth,
    running all 6 metrics and producing a comprehensive evaluation result.
    """

    def __init__(
        self,
        solution_dir: Path,
        metadata_path: Optional[Path] = None,
    ):
        """Initialize evaluator.

        Args:
            solution_dir: Path to solution directory
            metadata_path: Optional path to metadata.json (defaults to solution_dir/metadata.json)
        """
        self.solution_dir = Path(solution_dir)

        # Default metadata path
        if metadata_path is None:
            metadata_path = self.solution_dir / "metadata.json"

        self.metadata_path = Path(metadata_path)

        # Load solution and ground truth
        self.solution = Solution(self.solution_dir)
        self.ground_truth = GroundTruth(self.metadata_path)

        # Initialize metric evaluators
        self.i_acc_evaluator = IAccEvaluator(self.solution, self.ground_truth)
        self.c_comp_evaluator = CCompEvaluator(self.solution, self.ground_truth)
        self.ipa_evaluator = IPAEvaluator(self.solution, self.ground_truth)
        self.f_corr_evaluator = FCorrEvaluator(self.solution, self.ground_truth)
        self.cq_evaluator = CQEvaluator(self.solution, self.ground_truth)
        self.sem_sim_evaluator = SemSimEvaluator(self.solution, self.ground_truth)

    def evaluate(
        self,
        run_build: bool = True,
        run_tests: bool = True,
        metrics: Optional[list] = None,
    ) -> EvaluationResult:
        """Run evaluation with all metrics.

        Args:
            run_build: Whether to run build (for F-CORR)
            run_tests: Whether to run tests (for F-CORR)
            metrics: Optional list of metric names to run (default: all)

        Returns:
            EvaluationResult with all metric scores
        """
        # Determine which metrics to run
        all_metrics = ['i_acc', 'c_comp', 'ipa', 'f_corr', 'cq', 'sem_sim']
        metrics_to_run = metrics if metrics else all_metrics

        # Run metrics
        i_acc = None
        c_comp = None
        ipa = None
        f_corr = None
        cq = None
        sem_sim = None

        if 'i_acc' in metrics_to_run:
            i_acc = self.i_acc_evaluator.evaluate()

        if 'c_comp' in metrics_to_run:
            c_comp = self.c_comp_evaluator.evaluate()

        if 'ipa' in metrics_to_run:
            ipa = self.ipa_evaluator.evaluate()

        if 'f_corr' in metrics_to_run:
            f_corr = self.f_corr_evaluator.evaluate(
                run_build=run_build,
                run_tests=run_tests,
            )

        if 'cq' in metrics_to_run:
            cq = self.cq_evaluator.evaluate()

        if 'sem_sim' in metrics_to_run:
            sem_sim = self.sem_sim_evaluator.evaluate()

        # Create evaluation result
        result = EvaluationResult(
            sample_id=self.ground_truth.sample_id,
            solution_dir=self.solution_dir,
            task_type=self.ground_truth.task_type,
            i_acc=i_acc,
            c_comp=c_comp,
            ipa=ipa,
            f_corr=f_corr,
            cq=cq,
            sem_sim=sem_sim,
        )

        return result

    def evaluate_quick(self) -> EvaluationResult:
        """Quick evaluation without running build/tests.

        Uses static analysis only for F-CORR.

        Returns:
            EvaluationResult with quick evaluation
        """
        i_acc = self.i_acc_evaluator.evaluate()
        c_comp = self.c_comp_evaluator.evaluate()
        ipa = self.ipa_evaluator.evaluate()
        f_corr = self.f_corr_evaluator.evaluate_without_execution()
        cq = self.cq_evaluator.evaluate()
        sem_sim = self.sem_sim_evaluator.evaluate()

        result = EvaluationResult(
            sample_id=self.ground_truth.sample_id,
            solution_dir=self.solution_dir,
            task_type=self.ground_truth.task_type,
            i_acc=i_acc,
            c_comp=c_comp,
            ipa=ipa,
            f_corr=f_corr,
            cq=cq,
            sem_sim=sem_sim,
        )

        return result

    def get_detailed_report(self) -> Dict:
        """Get detailed evaluation report with all metric details.

        Returns:
            Dict with comprehensive evaluation details
        """
        # Run quick evaluation
        result = self.evaluate_quick()

        # Get detailed breakdowns from each metric
        report = {
            "sample_id": self.ground_truth.sample_id,
            "task_type": self.ground_truth.task_type,
            "framework": self.ground_truth.framework,
            "overall_score": result.overall_score,
            "metrics": {
                "i_acc": {
                    "score": result.i_acc.score if result.i_acc else None,
                    "details": self.i_acc_evaluator.get_details(),
                },
                "c_comp": {
                    "score": result.c_comp.score if result.c_comp else None,
                    "details": self.c_comp_evaluator.get_details(),
                },
                "ipa": {
                    "score": result.ipa.f1_score if result.ipa else None,
                    "details": self.ipa_evaluator.get_details(),
                },
                "f_corr": {
                    "score": result.f_corr.score if result.f_corr else None,
                    "details": self.f_corr_evaluator.quick_check(),
                },
                "cq": {
                    "score": result.cq.score if result.cq else None,
                    "details": self.cq_evaluator.get_details(),
                },
                "sem_sim": {
                    "score": result.sem_sim.score if result.sem_sim else None,
                    "details": self.sem_sim_evaluator.get_details(),
                },
            },
        }

        return report

    def get_summary(self) -> Dict:
        """Get high-level evaluation summary.

        Returns:
            Dict with summary statistics
        """
        result = self.evaluate_quick()

        return {
            "sample_id": self.ground_truth.sample_id,
            "task_type": self.ground_truth.task_type,
            "overall_score": result.overall_score,
            "scores": {
                "i_acc": result.i_acc.score if result.i_acc else None,
                "c_comp": result.c_comp.score if result.c_comp else None,
                "ipa": result.ipa.f1_score if result.ipa else None,
                "f_corr": result.f_corr.score if result.f_corr else None,
                "cq": result.cq.score if result.cq else None,
                "sem_sim": result.sem_sim.score if result.sem_sim else None,
            },
            "grade": self._calculate_grade(result.overall_score),
        }

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score.

        Args:
            score: Overall score 0-100

        Returns:
            Letter grade A-F
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def save_results(self, output_path: Path, detailed: bool = False) -> None:
        """Save evaluation results to file.

        Args:
            output_path: Path to save results
            detailed: Whether to save detailed report (default: summary only)
        """
        if detailed:
            report = self.get_detailed_report()
        else:
            result = self.evaluate_quick()
            report = result.model_dump()

        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

    @staticmethod
    def evaluate_directory(
        solution_dir: Path,
        output_dir: Optional[Path] = None,
        run_build: bool = False,
        run_tests: bool = False,
    ) -> EvaluationResult:
        """Convenience method to evaluate a directory.

        Args:
            solution_dir: Path to solution directory
            output_dir: Optional path to save results
            run_build: Whether to run build
            run_tests: Whether to run tests

        Returns:
            EvaluationResult
        """
        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate(run_build=run_build, run_tests=run_tests)

        if output_dir:
            output_path = Path(output_dir) / f"{result.sample_id}_result.json"
            result.to_json_file(output_path)

        return result

    @staticmethod
    def batch_evaluate(
        sample_dirs: list[Path],
        output_dir: Path,
        run_build: bool = False,
        run_tests: bool = False,
    ) -> list[EvaluationResult]:
        """Evaluate multiple samples.

        Args:
            sample_dirs: List of sample directories
            output_dir: Directory to save results
            run_build: Whether to run builds
            run_tests: Whether to run tests

        Returns:
            List of EvaluationResults
        """
        results = []

        for sample_dir in sample_dirs:
            try:
                result = Evaluator.evaluate_directory(
                    sample_dir,
                    output_dir=output_dir,
                    run_build=run_build,
                    run_tests=run_tests,
                )
                results.append(result)
            except Exception as e:
                print(f"Failed to evaluate {sample_dir}: {e}")

        return results
