#!/usr/bin/env python3
"""
Run SDK Bench evaluation on all samples with specified models.

This script runs the complete evaluation pipeline:
1. Generate LLM solutions for all samples
2. Evaluate the generated solutions
3. Create a comprehensive results report

Usage:
    # Run with Claude models
    python scripts/run_all_samples.py --provider anthropic --model claude-3-5-sonnet-20241022

    # Run with OpenAI models
    python scripts/run_all_samples.py --provider openai --model gpt-4-turbo-preview

    # Run multiple models
    python scripts/run_all_samples.py --models claude-3-5-sonnet-20241022,gpt-4-turbo

    # Quick test with 5 samples
    python scripts/run_all_samples.py --model claude-3-haiku-20240307 --limit 5
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class AllSamplesEvaluator:
    """Run evaluation on all SDK Bench samples."""

    def __init__(self, base_dir: Path):
        """Initialize evaluator with base directory."""
        self.base_dir = Path(base_dir)
        self.samples_dir = self.base_dir / "samples"
        self.results_dir = self.base_dir / "results"
        self.scripts_dir = self.base_dir / "scripts"

        # Create results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Track execution stats
        self.stats = {
            "total_samples": 0,
            "processed_samples": 0,
            "failed_samples": 0,
            "total_time": 0,
            "total_cost": 0,
            "models_evaluated": []
        }

    def get_provider_for_model(self, model: str) -> str:
        """Determine provider based on model name."""
        if "claude" in model.lower():
            return "anthropic"
        elif "gpt" in model.lower():
            return "openai"
        else:
            # Default to anthropic for unknown models
            return "anthropic"

    def get_all_samples(self, limit: Optional[int] = None) -> List[Path]:
        """Get all sample directories."""
        samples = sorted(self.samples_dir.glob("task*"))

        if limit:
            samples = samples[:limit]

        return samples

    def run_llm_generation(
        self,
        sample_path: Path,
        provider: str,
        model: str,
        output_dir: Path
    ) -> Tuple[bool, Optional[Dict]]:
        """Generate LLM solution for a single sample."""
        sample_name = sample_path.name
        model_safe = model.replace(".", "-").replace("/", "-")
        solution_dir = output_dir / sample_name / model_safe

        # Check if solution already exists
        if solution_dir.exists() and any(solution_dir.iterdir()):
            # Silently skip existing solutions
            return True, None

        # Run llm_evaluate.py
        cmd = [
            "python",
            str(self.scripts_dir / "evaluation" / "llm_evaluate.py"),
            "--provider", provider,
            "--model", model,
            "--samples", str(sample_path),
            "--output", str(output_dir)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                timeout=60  # 60 second timeout per sample
            )

            if result.returncode != 0:
                # Return failure without printing (will be handled by progress bar)
                return False, {"error": result.stderr[:200]}

            # Parse cost if available
            cost_info = None
            if "Cost:" in result.stdout:
                try:
                    # Extract cost from output
                    for line in result.stdout.split("\n"):
                        if "Cost:" in line or "cost" in line.lower():
                            cost_info = {"raw": line}
                            break
                except:
                    pass

            return True, cost_info

        except subprocess.TimeoutExpired:
            return False, {"error": "Timeout"}
        except Exception as e:
            return False, {"error": str(e)}

    def run_evaluation(
        self,
        solution_dir: Path,
        metadata_path: Path,
        output_dir: Path
    ) -> Tuple[bool, Optional[Dict]]:
        """Evaluate a generated solution."""
        if not solution_dir.exists():
            return False, None

        # Run evaluate.py
        cmd = [
            "python",
            str(self.scripts_dir / "evaluation" / "evaluate.py"),
            str(solution_dir),
            "--metadata", str(metadata_path),
            "--output", str(output_dir)
            # Don't add --build flag, it's off by default
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                timeout=30  # 30 second timeout
            )

            if result.returncode != 0:
                return False, {"error": result.stderr[:200]}

            # Parse scores from output
            scores = None
            if "Overall Score:" in result.stdout:
                try:
                    for line in result.stdout.split("\n"):
                        if "Overall Score:" in line:
                            score_str = line.split(":")[-1].strip()
                            scores = {"overall": score_str}
                            break
                except:
                    pass

            return True, scores

        except subprocess.TimeoutExpired:
            return False, {"error": "Timeout"}
        except Exception as e:
            return False, {"error": str(e)}

    def process_single_sample(
        self,
        sample_path: Path,
        model: str,
        provider: str,
        skip_generation: bool,
        skip_evaluation: bool,
        progress_bar: Optional[tqdm] = None
    ) -> Dict:
        """Process a single sample."""
        sample_name = sample_path.name

        result = {
            "sample": sample_name,
            "model": model,
            "provider": provider,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Generate LLM solution
            if not skip_generation:
                solutions_dir = self.results_dir / "llm_solutions"
                success, cost_info = self.run_llm_generation(
                    sample_path, provider, model, solutions_dir
                )

                result["generation"] = {
                    "success": success,
                    "cost": cost_info
                }

                if success:
                    self.stats["processed_samples"] += 1
                else:
                    self.stats["failed_samples"] += 1

            # Evaluate solution
            if not skip_evaluation:
                model_safe = model.replace(".", "-").replace("/", "-")
                solution_dir = self.results_dir / "llm_solutions" / sample_name / model_safe
                metadata_path = sample_path / "expected" / "metadata.json"

                success, scores = self.run_evaluation(
                    solution_dir, metadata_path, self.results_dir
                )

                result["evaluation"] = {
                    "success": success,
                    "scores": scores
                }

        except Exception as e:
            result["error"] = str(e)
            self.stats["failed_samples"] += 1

        if progress_bar:
            progress_bar.update(1)

        return result

    def process_all_samples(
        self,
        models: List[str],
        providers: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        skip_generation: bool = False,
        skip_evaluation: bool = False,
        n_workers: int = 1
    ):
        """Process all samples with specified models."""
        samples = self.get_all_samples(limit)
        self.stats["total_samples"] = len(samples)

        print(f"\n{'='*80}")
        print(f"SDK BENCH FULL EVALUATION")
        print(f"{'='*80}")
        print(f"Samples: {len(samples)}")
        print(f"Models: {', '.join(models)}")
        print(f"Workers: {n_workers}")
        print(f"Output: {self.results_dir}")
        print(f"{'='*80}\n")

        start_time = time.time()
        all_results = []

        # Thread-safe counter for stats
        stats_lock = threading.Lock()

        # Process each model
        for model in models:
            provider = providers.get(model) if providers else self.get_provider_for_model(model)

            print(f"\n{'='*60}")
            print(f"MODEL: {model} (Provider: {provider})")
            print(f"Workers: {n_workers}")
            print(f"{'='*60}\n")

            self.stats["models_evaluated"].append(model)
            model_results = []

            # Create progress bar
            progress_bar = tqdm(total=len(samples), desc=f"Processing {model}")

            # Process samples concurrently
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                # Submit all tasks
                future_to_sample = {
                    executor.submit(
                        self.process_single_sample,
                        sample_path,
                        model,
                        provider,
                        skip_generation,
                        skip_evaluation,
                        progress_bar
                    ): sample_path
                    for sample_path in samples
                }

                # Collect results as they complete
                for future in as_completed(future_to_sample):
                    sample_path = future_to_sample[future]
                    try:
                        result = future.result()
                        model_results.append(result)
                        all_results.append(result)
                    except Exception as e:
                        print(f"\n❌ Error processing {sample_path.name}: {e}")
                        model_results.append({
                            "sample": sample_path.name,
                            "model": model,
                            "provider": provider,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })

            progress_bar.close()

            # Save intermediate results for this model
            model_safe = model.replace(".", "-").replace("/", "-")
            model_results_file = self.results_dir / f"results_{model_safe}.json"
            with open(model_results_file, 'w') as f:
                json.dump(model_results, f, indent=2)
            print(f"\nSaved results to: {model_results_file}")

        # Calculate total time
        self.stats["total_time"] = time.time() - start_time

        # Save all results
        all_results_file = self.results_dir / f"all_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(all_results_file, 'w') as f:
            json.dump({
                "stats": self.stats,
                "results": all_results
            }, f, indent=2)

        print(f"\n{'='*80}")
        print(f"EVALUATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total samples: {self.stats['total_samples']}")
        print(f"Processed: {self.stats['processed_samples']}")
        print(f"Failed: {self.stats['failed_samples']}")
        print(f"Time: {self.stats['total_time']:.2f} seconds")
        print(f"Results saved to: {all_results_file}")
        print(f"{'='*80}\n")

        return all_results

    def generate_summary_report(self, results_file: Path):
        """Generate a summary report from results."""
        with open(results_file) as f:
            data = json.load(f)

        stats = data.get("stats", {})
        results = data.get("results", [])

        # Calculate aggregated metrics
        by_model = {}
        by_task = {}

        for result in results:
            model = result["model"]
            sample = result["sample"]
            task_type = sample.split("_")[0] + "_" + sample.split("_")[1]

            # Aggregate by model
            if model not in by_model:
                by_model[model] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "scores": []
                }

            by_model[model]["total"] += 1

            if result.get("generation", {}).get("success"):
                by_model[model]["successful"] += 1
            else:
                by_model[model]["failed"] += 1

            if result.get("evaluation", {}).get("scores"):
                by_model[model]["scores"].append(result["evaluation"]["scores"])

            # Aggregate by task type
            if task_type not in by_task:
                by_task[task_type] = {
                    "total": 0,
                    "models": {}
                }

            by_task[task_type]["total"] += 1

            if model not in by_task[task_type]["models"]:
                by_task[task_type]["models"][model] = {
                    "successful": 0,
                    "failed": 0
                }

            if result.get("generation", {}).get("success"):
                by_task[task_type]["models"][model]["successful"] += 1
            else:
                by_task[task_type]["models"][model]["failed"] += 1

        # Generate markdown report
        report_path = self.results_dir / f"evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_path, 'w') as f:
            f.write("# SDK Bench Evaluation Summary\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")

            f.write("## Overall Statistics\n\n")
            f.write(f"- **Total Samples:** {stats.get('total_samples', 0)}\n")
            f.write(f"- **Models Evaluated:** {', '.join(stats.get('models_evaluated', []))}\n")
            f.write(f"- **Total Time:** {stats.get('total_time', 0):.2f} seconds\n")
            f.write(f"- **Average Time per Sample:** {stats.get('total_time', 0) / max(stats.get('total_samples', 1), 1):.2f} seconds\n\n")

            f.write("## Results by Model\n\n")
            f.write("| Model | Total | Successful | Failed | Success Rate |\n")
            f.write("|-------|-------|------------|--------|-------------|\n")

            for model, model_stats in by_model.items():
                success_rate = (model_stats["successful"] / model_stats["total"] * 100) if model_stats["total"] > 0 else 0
                f.write(f"| {model} | {model_stats['total']} | {model_stats['successful']} | {model_stats['failed']} | {success_rate:.1f}% |\n")

            f.write("\n## Results by Task Type\n\n")

            for task_type, task_stats in sorted(by_task.items()):
                f.write(f"### {task_type.replace('_', ' ').title()}\n\n")
                f.write(f"**Total Samples:** {task_stats['total'] // len(stats.get('models_evaluated', [1]))}\n\n")

                if task_stats["models"]:
                    f.write("| Model | Successful | Failed |\n")
                    f.write("|-------|------------|--------|\n")

                    for model, model_task_stats in task_stats["models"].items():
                        f.write(f"| {model} | {model_task_stats['successful']} | {model_task_stats['failed']} |\n")

                    f.write("\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review individual evaluation results in `results/llm_solutions/`\n")
            f.write("2. Analyze specific failures to identify patterns\n")
            f.write("3. Compare model performance across different task types\n")
            f.write("4. Run functional correctness tests on successful solutions\n")

        print(f"\nSummary report saved to: {report_path}")
        return report_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run SDK Bench evaluation on all samples",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Single model to evaluate"
    )

    parser.add_argument(
        "--models",
        type=str,
        help="Comma-separated list of models to evaluate"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["anthropic", "openai"],
        help="LLM provider (auto-detected if not specified)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples to process (for testing)"
    )

    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip LLM generation (use existing solutions)"
    )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip evaluation scoring (only generate)"
    )

    parser.add_argument(
        "--n-workers",
        type=int,
        default=5,
        help="Number of concurrent workers for LLM generation (default: 1)"
    )

    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Base directory for SDK Bench"
    )

    parser.add_argument(
        "--summary-only",
        type=str,
        help="Generate summary from existing results file"
    )

    args = parser.parse_args()

    # Initialize evaluator
    evaluator = AllSamplesEvaluator(args.base_dir)

    # Handle summary-only mode
    if args.summary_only:
        results_file = Path(args.summary_only)
        if not results_file.exists():
            print(f"Error: Results file not found: {results_file}")
            sys.exit(1)
        evaluator.generate_summary_report(results_file)
        return

    # Determine models to evaluate
    models = []
    if args.model:
        models = [args.model]
    elif args.models:
        models = [m.strip() for m in args.models.split(",")]
    else:
        # Default models
        models = ["claude-3-haiku-20240307", "claude-haiku-4-5-20251001"]

    # Run evaluation
    results = evaluator.process_all_samples(
        models=models,
        limit=args.limit,
        skip_generation=args.skip_generation,
        skip_evaluation=args.skip_evaluation,
        n_workers=args.n_workers
    )

    # Generate summary if we have results
    if results:
        # Find the latest results file
        latest_results = max(evaluator.results_dir.glob("all_results_*.json"))
        evaluator.generate_summary_report(latest_results)


if __name__ == "__main__":
    main()