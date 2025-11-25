#!/usr/bin/env python3
"""
Interactive CLI for SDK-Bench evaluation.

Usage:
    python scripts/run.py                                         # Interactive
    python scripts/run.py --sdk clerk --model claude-sonnet-4-5   # Flag mode
    python scripts/run.py --sdk all --model gpt-4o --workers 10   # All SDKs
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

from sdkbench.llm import AnthropicProvider, OpenAIProvider, LLMConfig
from sdkbench.llm.prompt_builder import PromptBuilder
from sdkbench.llm.solution_generator import SolutionGenerator
from sdkbench.evaluator import Evaluator
from sdkbench.core import GroundTruth
from sdkbench.test_harness.registry import TestRunnerRegistry
from sdkbench.test_harness.models import FCorrResult

console = Console()

# =============================================================================
# Configuration
# =============================================================================

AVAILABLE_MODELS = {
    "claude-sonnet-4-5": {"provider": "anthropic", "model_id": "claude-sonnet-4-5-20250929", "description": "Claude Sonnet 4.5"},
    "claude-3-5-sonnet": {"provider": "anthropic", "model_id": "claude-3-5-sonnet-20241022", "description": "Claude 3.5 Sonnet"},
    "gpt-4o": {"provider": "openai", "model_id": "gpt-4o", "description": "GPT-4o"},
    "gpt-4o-mini": {"provider": "openai", "model_id": "gpt-4o-mini", "description": "GPT-4o Mini"},
}


# =============================================================================
# Evaluation Pipeline
# =============================================================================

class EvaluationPipeline:
    """Multi-SDK evaluation pipeline."""

    # Metric weights for overall score calculation
    WEIGHTS_WITHOUT_FCORR = {
        "i_acc": 0.20,
        "c_comp": 0.20,
        "ipa": 0.20,
        "cq": 0.20,
        "sem_sim": 0.20,
    }

    WEIGHTS_WITH_FCORR = {
        "i_acc": 0.15,
        "c_comp": 0.15,
        "ipa": 0.15,
        "f_corr": 0.25,
        "cq": 0.15,
        "sem_sim": 0.15,
    }

    # Grade thresholds
    GRADE_THRESHOLDS = [
        (90, "A"),
        (80, "B"),
        (70, "C"),
        (60, "D"),
        (0, "F"),
    ]

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.samples_dir = self.base_dir / "samples"
        self.results_dir = self.base_dir / "results"

        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.prompt_builder = PromptBuilder()
        self.solution_generator = SolutionGenerator()

    def _calculate_overall_score(self, metrics: Dict, include_fcorr: bool = False) -> float:
        """Calculate weighted overall score from individual metrics.

        Args:
            metrics: Dictionary of metric scores
            include_fcorr: Whether F-CORR is enabled for this run

        Returns:
            Weighted overall score (0-100)
        """
        if include_fcorr and "f_corr" in metrics:
            weights = self.WEIGHTS_WITH_FCORR
        else:
            weights = self.WEIGHTS_WITHOUT_FCORR

        score = 0.0
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric in metrics and metrics[metric] is not None:
                value = metrics[metric]
                # Normalize IPA if it's in 0-1 scale
                if metric == "ipa" and value <= 1.0:
                    value = value * 100
                score += value * weight
                total_weight += weight

        # Handle case where some metrics are missing
        if total_weight > 0 and total_weight < 1.0:
            score = score / total_weight

        return round(score, 2)

    def _calculate_grade(self, score: float) -> str:
        """Convert overall score to letter grade.

        Args:
            score: Overall score (0-100)

        Returns:
            Letter grade (A, B, C, D, or F)
        """
        for threshold, grade in self.GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"

    def _save_metric_details(self, metrics_dir: Path, metric_name: str, data: Dict):
        """Save detailed metric data to JSON file.

        Args:
            metrics_dir: Directory to save metrics
            metric_name: Name of the metric (e.g., 'i_acc')
            data: Metric data to save
        """
        metric_file = metrics_dir / f"{metric_name}.json"
        with open(metric_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def get_sdk_samples(self, sdk: str, limit: Optional[int] = None) -> List[Path]:
        """Get samples for a specific SDK."""
        sdk_dir = self.samples_dir / sdk
        if not sdk_dir.exists():
            return []

        if sdk == "clerk":
            samples = sorted(sdk_dir.glob("task*"))
        elif sdk == "lancedb":
            samples = sorted(sdk_dir.glob("lancedb_task*"))
        else:
            samples = sorted(sdk_dir.glob(f"{sdk}_task*"))
            if not samples:
                samples = sorted(sdk_dir.glob("task*"))

        # Filter to only directories with expected/metadata.json
        valid_samples = []
        for s in samples:
            if s.is_dir() and (s / "expected" / "metadata.json").exists():
                valid_samples.append(s)

        return valid_samples[:limit] if limit else valid_samples

    def get_all_sdks(self) -> List[str]:
        """Get list of all available SDKs."""
        sdks = []
        for sdk_dir in self.samples_dir.iterdir():
            if sdk_dir.is_dir() and not sdk_dir.name.startswith('.'):
                has_samples = any(p.is_dir() and 'task' in p.name for p in sdk_dir.iterdir())
                if has_samples:
                    sdks.append(sdk_dir.name)
        return sorted(sdks)

    def get_provider(self, model_name: str) -> tuple:
        """Get LLM provider for a model."""
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Unknown model: {model_name}")

        model_info = AVAILABLE_MODELS[model_name]
        config = LLMConfig(
            model=model_info["model_id"],
            max_tokens=4096,
            temperature=0.2,
        )

        if model_info["provider"] == "anthropic":
            return AnthropicProvider(config), model_info["provider"]
        elif model_info["provider"] == "openai":
            return OpenAIProvider(config), model_info["provider"]
        else:
            raise ValueError(f"Unknown provider: {model_info['provider']}")

    def generate_solution(self, sample_path: Path, model_name: str, output_dir: Path) -> Dict:
        """Generate solution for a sample using LLM."""
        try:
            # Load metadata
            metadata_path = sample_path / "expected" / "metadata.json"
            input_dir = sample_path / "input"

            if not metadata_path.exists():
                return {"success": False, "error": f"No metadata.json found in {sample_path}"}

            # Build prompt
            system_prompt, user_prompt = self.prompt_builder.build_from_metadata(
                metadata_path, input_dir
            )

            # Get provider and generate
            provider, provider_name = self.get_provider(model_name)
            response = provider.generate(user_prompt, system_prompt)

            # Save generated solution
            output_dir.mkdir(parents=True, exist_ok=True)

            # Extract and save files from response
            files = self.solution_generator._extract_files_from_response(response.content)

            if not files:
                # If no files extracted, save raw response
                with open(output_dir / "solution.txt", "w") as f:
                    f.write(response.content)
            else:
                for filepath, content in files.items():
                    file_path = output_dir / filepath
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, "w") as f:
                        f.write(content)

            # Save metadata
            with open(output_dir / "generation_metadata.json", "w") as f:
                json.dump({
                    "sample_id": sample_path.name,
                    "model": model_name,
                    "provider": provider_name,
                    "generated_at": datetime.now().isoformat(),
                    "tokens_used": response.tokens_used,
                    "cost": response.cost,
                    "files_generated": list(files.keys()) if files else ["solution.txt"],
                }, f, indent=2)

            # Save full prompt for debugging
            with open(output_dir / "prompt.md", "w") as f:
                f.write("# System Prompt\n\n")
                f.write(system_prompt)
                f.write("\n\n---\n\n# User Prompt\n\n")
                f.write(user_prompt)

            # Save raw LLM response for debugging
            with open(output_dir / "llm_response.md", "w") as f:
                f.write(response.content)

            return {"success": True, "files": len(files), "tokens": response.tokens_used}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def evaluate_solution(self, sample_path: Path, solution_path: Path, run_fcorr: bool = False) -> Dict:
        """Evaluate a generated solution.

        Args:
            sample_path: Path to sample directory
            solution_path: Path to generated solution
            run_fcorr: Whether to run F-CORR (functional correctness) tests
        """
        try:
            metadata_path = sample_path / "expected" / "metadata.json"

            if not metadata_path.exists():
                return {"success": False, "error": "No metadata found"}

            # Check if solution has any files
            solution_files = list(solution_path.glob("*"))
            if not solution_files or (len(solution_files) == 1 and solution_files[0].name == "generation_metadata.json"):
                return {"success": False, "error": "No solution files generated"}

            # Run evaluator
            evaluator = Evaluator(solution_path, metadata_path)
            result = evaluator.evaluate_quick()

            # IPA returns 0-1 scale, convert to 0-100 for consistency
            ipa_score = (result.ipa.f1 * 100) if result.ipa else 0

            eval_result = {
                "success": True,
                "metrics": {
                    "i_acc": result.i_acc.score if result.i_acc else 0,
                    "c_comp": result.c_comp.score if result.c_comp else 0,
                    "ipa": ipa_score,
                    "cq": result.cq.score if result.cq else 0,
                    "sem_sim": result.sem_sim.score if result.sem_sim else 0,
                },
            }

            # Run F-CORR if enabled
            if run_fcorr:
                fcorr_result = self._run_fcorr(sample_path, solution_path)
                eval_result["metrics"]["f_corr"] = fcorr_result.get("score", 0)
                eval_result["f_corr_details"] = fcorr_result

            # Calculate overall score with proper weighting
            overall_score = self._calculate_overall_score(eval_result["metrics"], include_fcorr=run_fcorr)
            grade = self._calculate_grade(overall_score)
            eval_result["overall_score"] = overall_score
            eval_result["grade"] = grade

            # Create metrics directory and save detailed breakdowns
            metrics_dir = solution_path / "metrics"
            metrics_dir.mkdir(exist_ok=True)

            # Save individual metric details
            if result.i_acc:
                self._save_metric_details(metrics_dir, "i_acc", {
                    "score": result.i_acc.score,
                    "file_location_correct": result.i_acc.file_location_correct,
                    "imports_correct": result.i_acc.imports_correct,
                    "pattern_correct": result.i_acc.pattern_correct,
                    "placement_correct": result.i_acc.placement_correct,
                    "details": result.i_acc.details if hasattr(result.i_acc, 'details') else {},
                })

            if result.c_comp:
                self._save_metric_details(metrics_dir, "c_comp", {
                    "score": result.c_comp.score,
                    "env_vars_score": result.c_comp.env_vars_score,
                    "provider_props_score": result.c_comp.provider_props_score,
                    "middleware_config_score": result.c_comp.middleware_config_score,
                    "details": {
                        "missing_env_vars": result.c_comp.missing_env_vars,
                        "missing_provider_props": result.c_comp.missing_provider_props,
                        "missing_middleware_config": result.c_comp.missing_middleware_config,
                    },
                })

            if result.ipa:
                self._save_metric_details(metrics_dir, "ipa", {
                    "score": ipa_score,
                    "precision": result.ipa.precision,
                    "recall": result.ipa.recall,
                    "f1": result.ipa.f1,
                    "details": {
                        "true_positives": result.ipa.true_positives,
                        "false_positives": result.ipa.false_positives,
                        "false_negatives": result.ipa.false_negatives,
                    },
                })

            if result.cq:
                self._save_metric_details(metrics_dir, "cq", {
                    "score": result.cq.score,
                    "type_errors": result.cq.type_errors,
                    "eslint_errors": result.cq.eslint_errors,
                    "security_issues": result.cq.security_issues,
                    "details": {
                        "type_error_list": result.cq.type_error_list if hasattr(result.cq, 'type_error_list') else [],
                        "eslint_error_list": result.cq.eslint_error_list if hasattr(result.cq, 'eslint_error_list') else [],
                        "security_issue_list": result.cq.security_issue_list if hasattr(result.cq, 'security_issue_list') else [],
                    },
                })

            if result.sem_sim:
                self._save_metric_details(metrics_dir, "sem_sim", {
                    "score": result.sem_sim.score,
                    "pattern_match": result.sem_sim.pattern_match,
                    "approach_match": result.sem_sim.approach_match,
                    "details": {
                        "matched_patterns": result.sem_sim.matched_patterns,
                        "missing_patterns": result.sem_sim.missing_patterns,
                    },
                })

            # Save F-CORR details if enabled
            if run_fcorr and "f_corr_details" in eval_result:
                fcorr = eval_result["f_corr_details"]
                self._save_metric_details(metrics_dir, "f_corr", {
                    "score": fcorr.get("score", 0),
                    "tests_passed": fcorr.get("passed", 0),
                    "tests_failed": fcorr.get("failed", 0),
                    "tests_total": fcorr.get("total", 0),
                    "tests_skipped": fcorr.get("skipped", 0),
                    "duration": fcorr.get("duration", 0),
                    "error": fcorr.get("error"),
                })

            # Save summary with overall score
            weights_used = self.WEIGHTS_WITH_FCORR if run_fcorr else self.WEIGHTS_WITHOUT_FCORR
            summary_data = {
                "sample_id": sample_path.name,
                "timestamp": datetime.now().isoformat(),
                "overall_score": overall_score,
                "grade": grade,
                "f_corr_enabled": run_fcorr,
                "metrics": eval_result["metrics"],
                "weights_used": weights_used,
            }
            with open(metrics_dir / "summary.json", "w") as f:
                json.dump(summary_data, f, indent=2)

            return eval_result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_fcorr(self, sample_path: Path, solution_path: Path) -> Dict:
        """Run F-CORR (functional correctness) evaluation.

        Args:
            sample_path: Path to sample directory containing tests/
            solution_path: Path to generated solution

        Returns:
            Dict with F-CORR results
        """
        import shutil
        import tempfile
        import time

        start_time = time.time()
        tests_dir = sample_path / "tests"

        # Check if tests exist
        if not tests_dir.exists():
            return {
                "score": 0,
                "error": "No tests/ directory found",
                "duration": time.time() - start_time,
            }

        # Create temp directory with solution as 'expected/' and tests/
        temp_dir = Path(tempfile.mkdtemp(prefix="fcorr_"))

        try:
            # Copy solution files to expected/ (tests import from expected)
            expected_dest = temp_dir / "expected"
            shutil.copytree(solution_path, expected_dest)

            # Copy tests
            tests_dest = temp_dir / "tests"
            shutil.copytree(tests_dir, tests_dest)

            # Copy requirements.txt if it exists in solution
            req_file = solution_path / "requirements.txt"
            if req_file.exists():
                shutil.copy2(req_file, temp_dir / "requirements.txt")

            # Also check sample's expected for requirements
            sample_req = sample_path / "expected" / "requirements.txt"
            if sample_req.exists() and not req_file.exists():
                shutil.copy2(sample_req, temp_dir / "requirements.txt")

            # Copy package.json if it exists
            pkg_file = solution_path / "package.json"
            if pkg_file.exists():
                shutil.copy2(pkg_file, temp_dir / "package.json")

            # Get runner and run tests
            runner = TestRunnerRegistry.get_runner(temp_dir)

            if runner is None:
                return {
                    "score": 0,
                    "error": "No compatible test runner found",
                    "duration": time.time() - start_time,
                }

            # Install dependencies
            install_result = runner.install_dependencies()
            if not install_result.success:
                return {
                    "score": 0,
                    "error": f"Dependency install failed: {install_result.error}",
                    "duration": time.time() - start_time,
                }

            # Run tests
            test_result = runner.run_tests()

            # Strict scoring: any failure = 0
            if test_result.success and test_result.failed == 0:
                score = 100.0
            else:
                score = 0.0

            return {
                "score": score,
                "passed": test_result.passed,
                "failed": test_result.failed,
                "total": test_result.total,
                "skipped": test_result.skipped,
                "duration": time.time() - start_time,
                "error": None if score == 100.0 else f"{test_result.failed} tests failed",
            }

        except Exception as e:
            return {
                "score": 0,
                "error": str(e),
                "duration": time.time() - start_time,
            }
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def process_sample(self, sample: Path, model: str, sdk: str,
                       skip_generation: bool, skip_evaluation: bool,
                       run_fcorr: bool = False) -> Dict:
        """Process a single sample."""
        sample_id = sample.name
        # Store solutions inside results directory
        solution_path = self.results_dir / sdk / model / "solutions" / sample_id

        result = {"sample": sample_id, "model": model, "sdk": sdk, "generation": {}, "evaluation": {}}

        # Generation phase
        if not skip_generation:
            result["generation"] = self.generate_solution(sample, model, solution_path)
        else:
            result["generation"] = {"success": True, "skipped": True}

        # Evaluation phase
        if not skip_evaluation and result["generation"].get("success"):
            result["evaluation"] = self.evaluate_solution(sample, solution_path, run_fcorr=run_fcorr)
        else:
            result["evaluation"] = {"skipped": True}

        return result

    def save_summary(self, sdk: str, model: str, results: List[Dict], run_fcorr: bool = False):
        """Save summary for a specific SDK-model combination."""
        successful_gen = sum(1 for r in results if r.get("generation", {}).get("success"))
        successful_eval = sum(1 for r in results if r.get("evaluation", {}).get("success"))

        # Check if any results have F-CORR enabled
        has_fcorr = any(
            "f_corr" in r.get("evaluation", {}).get("metrics", {})
            for r in results if r.get("evaluation", {}).get("success")
        )

        summary = {
            "sdk": sdk,
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "f_corr_enabled": has_fcorr,
            "total_samples": len(results),
            "generation": {"success": successful_gen, "failed": len(results) - successful_gen},
            "evaluation": {"success": successful_eval, "failed": len(results) - successful_eval},
        }

        # Calculate average metrics
        metrics_data = [r.get("evaluation", {}).get("metrics", {}) for r in results
                        if r.get("evaluation", {}).get("success")]
        if metrics_data:
            avg_metrics = {}
            for key in ["i_acc", "c_comp", "ipa", "cq", "sem_sim", "f_corr"]:
                values = [m.get(key, 0) for m in metrics_data if key in m]
                if values:
                    avg_metrics[key] = round(sum(values) / len(values), 2)

            # Calculate average overall score
            overall_scores = [r.get("evaluation", {}).get("overall_score", 0) for r in results
                             if r.get("evaluation", {}).get("success") and r.get("evaluation", {}).get("overall_score") is not None]
            if overall_scores:
                avg_metrics["overall"] = round(sum(overall_scores) / len(overall_scores), 2)

            summary["average_metrics"] = avg_metrics

        # Add per-sample results
        summary["samples"] = []
        for r in results:
            sample_result = {
                "sample_id": r.get("sample"),
                "generation": {
                    "success": r.get("generation", {}).get("success", False),
                    "error": r.get("generation", {}).get("error"),
                },
                "evaluation": {
                    "success": r.get("evaluation", {}).get("success", False),
                    "error": r.get("evaluation", {}).get("error"),
                }
            }
            # Add metrics and overall score if evaluation succeeded
            if r.get("evaluation", {}).get("success"):
                sample_result["metrics"] = r.get("evaluation", {}).get("metrics", {})
                sample_result["overall_score"] = r.get("evaluation", {}).get("overall_score", 0)
                sample_result["grade"] = r.get("evaluation", {}).get("grade", "F")
            summary["samples"].append(sample_result)

        output_file = self.results_dir / sdk / f"{model}_summary.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def run_evaluation(self, sdks: List[str], models: List[str], workers: int = 5,
                       limit: Optional[int] = None, skip_generation: bool = False,
                       skip_evaluation: bool = False, run_fcorr: bool = False) -> Dict:
        """Run the full evaluation pipeline.

        Args:
            sdks: List of SDK names to evaluate
            models: List of model names to use
            workers: Number of concurrent workers
            limit: Maximum samples per SDK
            skip_generation: Skip LLM generation phase
            skip_evaluation: Skip evaluation phase
            run_fcorr: Run F-CORR (functional correctness) tests
        """
        all_results = []
        start_time = time.time()

        for sdk in sdks:
            samples = self.get_sdk_samples(sdk, limit)
            if not samples:
                console.print(f"[yellow]No valid samples found for {sdk}[/yellow]")
                continue

            console.print(f"\n[bold cyan]SDK: {sdk.upper()}[/bold cyan] ({len(samples)} samples)")
            if run_fcorr:
                console.print("[dim]F-CORR enabled - will run functional tests[/dim]")

            for model in models:
                console.print(f"\n[green]Model:[/green] {model}")

                model_results = []

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console
                ) as progress:
                    task = progress.add_task(f"Processing {sdk}/{model}", total=len(samples))

                    with ThreadPoolExecutor(max_workers=workers) as executor:
                        futures = {
                            executor.submit(
                                self.process_sample, sample, model, sdk,
                                skip_generation, skip_evaluation, run_fcorr
                            ): sample for sample in samples
                        }

                        for future in as_completed(futures):
                            try:
                                result = future.result()
                                model_results.append(result)
                                all_results.append(result)

                                # Show inline status
                                gen_status = "ok" if result["generation"].get("success") else "fail"
                                eval_status = "ok" if result["evaluation"].get("success") else "skip"
                                progress.console.print(
                                    f"  [dim]{result['sample']}[/dim]: gen={gen_status}, eval={eval_status}",
                                    highlight=False
                                )
                            except Exception as e:
                                console.print(f"[red]Error: {e}[/red]")
                            progress.advance(task)

                summary = self.save_summary(sdk, model, model_results)
                self._print_summary(summary)

        elapsed = time.time() - start_time
        self._save_overall_report(all_results, elapsed, models, sdks, run_fcorr=run_fcorr)

        return {"results": all_results, "elapsed": elapsed}

    def _print_summary(self, summary: Dict):
        """Print a summary table."""
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        gen = summary.get("generation", {})
        table.add_row("Generation", f"{gen.get('success', 0)}/{summary['total_samples']}")

        eval_info = summary.get("evaluation", {})
        table.add_row("Evaluation", f"{eval_info.get('success', 0)}/{summary['total_samples']}")

        if "average_metrics" in summary:
            for key, value in summary["average_metrics"].items():
                table.add_row(key.upper(), f"{value:.3f}")

        console.print(table)

    def _save_overall_report(self, results: List[Dict], elapsed: float, models: List[str], sdks: List[str], run_fcorr: bool = False):
        """Save overall evaluation report with metrics."""

        def calc_avg_metrics(result_list: List[Dict]) -> Dict:
            """Calculate average metrics from results."""
            metrics_data = [r.get("evaluation", {}).get("metrics", {}) for r in result_list
                          if r.get("evaluation", {}).get("success")]
            if not metrics_data:
                return {}
            avg = {}
            for key in ["i_acc", "c_comp", "ipa", "cq", "sem_sim", "f_corr"]:
                values = [m.get(key, 0) for m in metrics_data if key in m]
                if values:
                    avg[key] = round(sum(values) / len(values), 2)

            # Calculate average overall score
            overall_scores = [r.get("evaluation", {}).get("overall_score", 0) for r in result_list
                             if r.get("evaluation", {}).get("success") and r.get("evaluation", {}).get("overall_score") is not None]
            if overall_scores:
                avg["overall"] = round(sum(overall_scores) / len(overall_scores), 2)

            return avg

        # Check if any results have F-CORR enabled
        has_fcorr = any(
            "f_corr" in r.get("evaluation", {}).get("metrics", {})
            for r in results if r.get("evaluation", {}).get("success")
        )

        report = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "f_corr_enabled": has_fcorr,
            "models": models,
            "sdks": sdks,
            "total_evaluations": len(results),
            "by_sdk": {},
            "by_model": {},
            "by_sdk_model": {}
        }

        # Aggregate by SDK
        for sdk in sdks:
            sdk_results = [r for r in results if r.get("sdk") == sdk]
            report["by_sdk"][sdk] = {
                "total": len(sdk_results),
                "gen_success": sum(1 for r in sdk_results if r.get("generation", {}).get("success")),
                "eval_success": sum(1 for r in sdk_results if r.get("evaluation", {}).get("success")),
                "average_metrics": calc_avg_metrics(sdk_results)
            }

        # Aggregate by Model
        for model in models:
            model_results = [r for r in results if r.get("model") == model]
            report["by_model"][model] = {
                "total": len(model_results),
                "gen_success": sum(1 for r in model_results if r.get("generation", {}).get("success")),
                "eval_success": sum(1 for r in model_results if r.get("evaluation", {}).get("success")),
                "average_metrics": calc_avg_metrics(model_results)
            }

        # Aggregate by SDK + Model combination
        for sdk in sdks:
            for model in models:
                combo_results = [r for r in results if r.get("sdk") == sdk and r.get("model") == model]
                if combo_results:
                    key = f"{sdk}/{model}"
                    report["by_sdk_model"][key] = {
                        "total": len(combo_results),
                        "gen_success": sum(1 for r in combo_results if r.get("generation", {}).get("success")),
                        "eval_success": sum(1 for r in combo_results if r.get("evaluation", {}).get("success")),
                        "average_metrics": calc_avg_metrics(combo_results)
                    }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"overall_report_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)


# =============================================================================
# Interactive Selection Functions
# =============================================================================

def display_header():
    """Display the CLI header."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SDK-BENCH EVALUATION[/bold cyan]\n"
        "[dim]Multi-SDK benchmark for LLM code generation[/dim]",
        border_style="cyan"
    ))
    console.print()


def select_sdks_interactive(available_sdks: Dict[str, int]) -> List[str]:
    """Interactive SDK selection."""
    table = Table(title="Available SDKs", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("SDK", style="cyan")
    table.add_column("Samples", justify="right")

    sdk_list = list(available_sdks.keys())
    for i, sdk_name in enumerate(sdk_list, 1):
        table.add_row(str(i), sdk_name, str(available_sdks[sdk_name]))

    console.print(table)
    console.print()
    console.print("[dim]Enter numbers separated by commas (e.g., 1,2) or 'all'[/dim]")

    while True:
        selection = Prompt.ask("Select SDKs", default="all")
        if selection.lower() == "all":
            return sdk_list
        try:
            indices = [int(x.strip()) for x in selection.split(",")]
            selected = [sdk_list[i - 1] for i in indices if 1 <= i <= len(sdk_list)]
            if selected:
                return selected
        except (ValueError, IndexError):
            pass
        console.print("[red]Invalid selection[/red]")


def select_models_interactive() -> List[str]:
    """Interactive model selection."""
    table = Table(title="Available Models", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Model", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Description", style="dim")

    model_list = list(AVAILABLE_MODELS.keys())
    for i, model_name in enumerate(model_list, 1):
        info = AVAILABLE_MODELS[model_name]
        table.add_row(str(i), model_name, info["provider"], info["description"])

    console.print(table)
    console.print()
    console.print("[dim]Enter numbers separated by commas (e.g., 1,3)[/dim]")

    while True:
        selection = Prompt.ask("Select models", default="1")
        try:
            indices = [int(x.strip()) for x in selection.split(",")]
            selected = [model_list[i - 1] for i in indices if 1 <= i <= len(model_list)]
            if selected:
                return selected
        except (ValueError, IndexError):
            pass
        console.print("[red]Invalid selection[/red]")


def show_config_summary(sdks: List[str], models: List[str], workers: int,
                        limit: Optional[int], options: dict) -> bool:
    """Display configuration summary and confirm."""
    console.print()

    lines = [
        f"[cyan]SDKs:[/cyan] {', '.join(sdks)}",
        f"[cyan]Models:[/cyan] {', '.join(models)}",
        f"[cyan]Workers:[/cyan] {workers}",
        f"[cyan]Sample limit:[/cyan] {limit or 'None (all)'}",
    ]

    if options.get("skip_generation"):
        lines.append("[yellow]Skip generation:[/yellow] Yes")
    if options.get("skip_evaluation"):
        lines.append("[yellow]Skip evaluation:[/yellow] Yes")
    if options.get("run_fcorr"):
        lines.append("[green]F-CORR enabled:[/green] Yes (will run functional tests)")

    console.print(Panel("\n".join(lines), title="[bold]Configuration[/bold]", border_style="green"))
    console.print()

    return Confirm.ask("[bold]Proceed?[/bold]", default=True)


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SDK-Bench Evaluation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run.py                                         # Interactive
  python scripts/run.py --sdk clerk --model claude-sonnet-4-5   # Flag mode
  python scripts/run.py --sdk all --model gpt-4o --workers 10   # All SDKs
        """
    )

    parser.add_argument("--sdk", help="Comma-separated SDKs or 'all'")
    parser.add_argument("--model", help="Comma-separated models")
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers (default: 5)")
    parser.add_argument("--limit", type=int, help="Limit samples per SDK")
    parser.add_argument("--skip-generation", action="store_true", help="Only evaluate existing")
    parser.add_argument("--skip-evaluation", action="store_true", help="Only generate")
    parser.add_argument("--run-fcorr", action="store_true",
                        help="Run F-CORR (functional correctness) tests on solutions")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    display_header()

    pipeline = EvaluationPipeline()

    # Get available SDKs
    available_sdks = {sdk: len(pipeline.get_sdk_samples(sdk)) for sdk in pipeline.get_all_sdks()}
    if not available_sdks:
        console.print("[red]No SDKs found![/red]")
        sys.exit(1)

    # Determine SDKs
    if args.sdk:
        sdks = list(available_sdks.keys()) if args.sdk.lower() == "all" else [s.strip() for s in args.sdk.split(",")]
    else:
        sdks = select_sdks_interactive(available_sdks)

    # Determine models
    if args.model:
        models = [m.strip() for m in args.model.split(",")]
    else:
        models = select_models_interactive()

    # Validate models
    for m in models:
        if m not in AVAILABLE_MODELS:
            console.print(f"[red]Unknown model: {m}[/red]")
            console.print(f"[dim]Available: {', '.join(AVAILABLE_MODELS.keys())}[/dim]")
            sys.exit(1)

    # Get workers
    workers = args.workers

    # Get limit
    if args.limit is None and not (args.sdk and args.model):
        if Confirm.ask("Limit samples per SDK?", default=False):
            args.limit = IntPrompt.ask("Max samples", default=10)

    # Options
    options = {
        "skip_generation": args.skip_generation,
        "skip_evaluation": args.skip_evaluation,
        "run_fcorr": args.run_fcorr,
    }

    # Confirm
    if not args.no_confirm:
        if not show_config_summary(sdks, models, workers, args.limit, options):
            console.print("[yellow]Cancelled.[/yellow]")
            sys.exit(0)

    # Run
    console.print("\n[bold]Starting evaluation...[/bold]\n")

    result = pipeline.run_evaluation(
        sdks=sdks,
        models=models,
        workers=workers,
        limit=args.limit,
        skip_generation=options["skip_generation"],
        skip_evaluation=options["skip_evaluation"],
        run_fcorr=options["run_fcorr"]
    )

    # Done
    console.print()
    console.print(Panel.fit(
        f"[bold green]Complete![/bold green]\n"
        f"[dim]Time: {result['elapsed']:.1f}s | Results: {pipeline.results_dir}[/dim]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
