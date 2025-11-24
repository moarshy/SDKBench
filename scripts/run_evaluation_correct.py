#!/usr/bin/env python3
"""
Correct evaluation pipeline for SDK Bench.

IMPORTANT: Samples folder remains UNTOUCHED!
All results go in the results folder with proper organization.

Directory structure:
    samples/                    # UNTOUCHED - No results here!
    ├── task1_init_001/
    │   ├── input/
    │   ├── expected/
    │   └── tests/
    │
    results/                    # ALL results go here
    ├── llm_solutions/
    │   ├── task1_init_001/
    │   │   └── claude-sonnet-4-5/
    │   │       ├── middleware.ts        # Generated files
    │   │       ├── app/
    │   │       ├── package.json
    │   │       └── evaluation.json      # Evaluation results HERE
    │   └── task1_init_002/
    │       └── claude-sonnet-4-5/
    │           ├── [generated files]
    │           └── evaluation.json
    └── overall_summary.json
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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class CorrectEvaluator:
    """Evaluation pipeline that keeps samples folder clean."""

    def __init__(self, base_dir: Path):
        """Initialize evaluator."""
        self.base_dir = Path(base_dir)
        self.samples_dir = self.base_dir / "samples"
        self.results_dir = self.base_dir / "results"
        self.solutions_dir = self.results_dir / "llm_solutions"
        self.scripts_dir = self.base_dir / "scripts"

        # Create results directories
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.solutions_dir.mkdir(parents=True, exist_ok=True)

    def get_provider_for_model(self, model: str) -> str:
        """Determine provider based on model name."""
        if "claude" in model.lower():
            return "anthropic"
        elif "gpt" in model.lower():
            return "openai"
        else:
            return "anthropic"

    def generate_solution(
        self,
        sample_path: Path,
        model: str,
        provider: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Generate LLM solution and save in results/llm_solutions."""
        sample_name = sample_path.name
        solution_dir = self.solutions_dir / sample_name / model

        # Check if solution already exists
        if solution_dir.exists() and any(solution_dir.glob("*.ts")) or any(solution_dir.glob("*.tsx")):
            return True, {"status": "already_exists"}

        # Run llm_evaluate.py
        cmd = [
            "python",
            str(self.scripts_dir / "evaluation" / "llm_evaluate.py"),
            "--provider", provider,
            "--model", model,
            "--samples", str(sample_path),
            "--output", str(self.solutions_dir)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                timeout=60
            )

            if result.returncode != 0:
                error_msg = result.stderr[:500] if result.stderr else "Unknown error"
                return False, {"error": error_msg}

            # Check if files were generated
            if solution_dir.exists():
                files_generated = list(solution_dir.glob("*"))
                return True, {
                    "status": "success",
                    "files_count": len(files_generated)
                }

            return False, {"error": "No files generated"}

        except subprocess.TimeoutExpired:
            return False, {"error": "Generation timeout"}
        except Exception as e:
            return False, {"error": str(e)}

    def evaluate_solution(
        self,
        sample_path: Path,
        model: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Evaluate solution and save results in the same directory."""
        sample_name = sample_path.name
        solution_dir = self.solutions_dir / sample_name / model
        evaluation_file = solution_dir / "evaluation.json"
        metadata_path = sample_path / "expected" / "metadata.json"

        if not solution_dir.exists():
            return False, {"error": "No solution to evaluate"}

        if not metadata_path.exists():
            return False, {"error": "No metadata for evaluation"}

        # Run evaluate.py with output to temp location
        temp_output = self.results_dir / "temp_eval"
        temp_output.mkdir(exist_ok=True)

        cmd = [
            "python",
            str(self.scripts_dir / "evaluation" / "evaluate.py"),
            str(solution_dir),
            "--metadata", str(metadata_path),
            "--output", str(temp_output)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                timeout=30
            )

            evaluation_data = {
                "model": model,
                "sample": sample_name,
                "timestamp": datetime.now().isoformat(),
                "success": result.returncode == 0
            }

            if result.returncode == 0:
                # Parse scores from output
                if "Overall Score:" in result.stdout:
                    for line in result.stdout.split("\n"):
                        if "Overall Score:" in line:
                            evaluation_data["overall_score"] = line.split(":")[-1].strip()
                            break

                # Look for detailed results file in temp output
                for file in temp_output.glob("*_result.json"):
                    with open(file) as f:
                        detailed = json.load(f)
                        evaluation_data["metrics"] = detailed.get("scores", {})
                    # Clean up the temp file
                    file.unlink()
                    break

            else:
                evaluation_data["error"] = result.stderr[:500] if result.stderr else "Evaluation failed"

            # Save evaluation results IN THE SOLUTION DIRECTORY
            with open(evaluation_file, 'w') as f:
                json.dump(evaluation_data, f, indent=2)

            # Clean up temp directory
            temp_output.rmdir()

            return evaluation_data["success"], evaluation_data

        except subprocess.TimeoutExpired:
            return False, {"error": "Evaluation timeout"}
        except Exception as e:
            return False, {"error": str(e)}

    def process_sample(
        self,
        sample_path: Path,
        model: str,
        provider: str,
        skip_generation: bool,
        skip_evaluation: bool,
        progress_bar: tqdm
    ) -> Dict:
        """Process a single sample."""
        result = {
            "sample": sample_path.name,
            "model": model,
            "provider": provider
        }

        # Generate solution
        if not skip_generation:
            success, gen_data = self.generate_solution(sample_path, model, provider)
            result["generation"] = {
                "success": success,
                "data": gen_data
            }
        else:
            result["generation"] = {"skipped": True}

        # Evaluate solution
        if not skip_evaluation:
            success, eval_data = self.evaluate_solution(sample_path, model)
            result["evaluation"] = {
                "success": success,
                "data": eval_data
            }
        else:
            result["evaluation"] = {"skipped": True}

        # Update progress bar
        gen_ok = result.get("generation", {}).get("success", False)
        eval_ok = result.get("evaluation", {}).get("success", False)

        if gen_ok and eval_ok:
            status = "✅"
        elif gen_ok:
            status = "⚠️"
        else:
            status = "❌"

        progress_bar.set_postfix({"last": f"{status} {sample_path.name}"})
        progress_bar.update(1)

        return result

    def run_evaluation(
        self,
        models: List[str],
        limit: Optional[int] = None,
        skip_generation: bool = False,
        skip_evaluation: bool = False,
        n_workers: int = 1
    ):
        """Run the evaluation pipeline."""
        # Get samples
        samples = sorted(self.samples_dir.glob("task*"))
        if limit:
            samples = samples[:limit]

        print(f"\n{'='*80}")
        print(f"SDK BENCH EVALUATION")
        print(f"{'='*80}")
        print(f"Samples: {len(samples)}")
        print(f"Models: {', '.join(models)}")
        print(f"Workers: {n_workers}")
        print(f"Output: {self.solutions_dir}")
        print(f"{'='*80}\n")

        all_results = []
        start_time = time.time()

        for model in models:
            provider = self.get_provider_for_model(model)

            print(f"\n{'='*60}")
            print(f"MODEL: {model}")
            print(f"Provider: {provider}")
            print(f"{'='*60}\n")

            model_results = []

            # Process samples concurrently
            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                # Create progress bar
                with tqdm(total=len(samples), desc=f"Processing {model}") as pbar:
                    # Submit all tasks
                    future_to_sample = {
                        executor.submit(
                            self.process_sample,
                            sample,
                            model,
                            provider,
                            skip_generation,
                            skip_evaluation,
                            pbar
                        ): sample
                        for sample in samples
                    }

                    # Collect results
                    for future in as_completed(future_to_sample):
                        sample = future_to_sample[future]
                        try:
                            result = future.result()
                            model_results.append(result)
                            all_results.append(result)
                        except Exception as e:
                            print(f"\n❌ Error processing {sample.name}: {e}")
                            model_results.append({
                                "sample": sample.name,
                                "model": model,
                                "error": str(e)
                            })

            # Save model summary
            self._save_model_summary(model, model_results)

        # Generate overall report
        elapsed = time.time() - start_time
        self._generate_overall_report(all_results, elapsed)

        print(f"\n{'='*80}")
        print(f"EVALUATION COMPLETE")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Solutions: {self.solutions_dir}")
        print(f"Summary: {self.results_dir}/overall_summary.json")
        print(f"{'='*80}\n")

    def _save_model_summary(self, model: str, results: List[Dict]):
        """Save summary for a specific model."""
        summary = {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(results),
            "generation": {
                "success": sum(1 for r in results if r.get("generation", {}).get("success")),
                "failed": sum(1 for r in results if not r.get("generation", {}).get("success"))
            },
            "evaluation": {
                "success": sum(1 for r in results if r.get("evaluation", {}).get("success")),
                "failed": sum(1 for r in results if not r.get("evaluation", {}).get("success"))
            }
        }

        # Calculate average scores
        scores = []
        for r in results:
            if r.get("evaluation", {}).get("data", {}).get("overall_score"):
                try:
                    score_str = r["evaluation"]["data"]["overall_score"]
                    score = float(score_str.replace("%", "").split("/")[0])
                    scores.append(score)
                except:
                    pass

        if scores:
            summary["scores"] = {
                "average": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "count": len(scores)
            }

        # Save summary
        summary_path = self.results_dir / f"summary_{model}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nModel summary saved: {summary_path}")

    def _generate_overall_report(self, all_results: List[Dict], elapsed_time: float):
        """Generate overall summary."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_time_seconds": elapsed_time,
            "results": all_results
        }

        # Save overall summary
        summary_path = self.results_dir / "overall_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate markdown report
        md_path = self.results_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(md_path, 'w') as f:
            f.write("# SDK Bench Evaluation Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Total Time:** {elapsed_time:.2f} seconds\n\n")

            f.write("## Directory Structure\n\n")
            f.write("```\n")
            f.write("results/\n")
            f.write("└── llm_solutions/\n")
            f.write("    ├── task1_init_001/\n")
            f.write("    │   └── claude-sonnet-4-5/\n")
            f.write("    │       ├── middleware.ts      # Generated code\n")
            f.write("    │       ├── package.json       # Generated code\n")
            f.write("    │       ├── app/               # Generated code\n")
            f.write("    │       └── evaluation.json    # Evaluation results\n")
            f.write("    └── ...\n")
            f.write("```\n\n")

            f.write("## Key Points\n\n")
            f.write("- **Samples folder**: UNTOUCHED - remains clean\n")
            f.write("- **Solutions**: All in `results/llm_solutions/`\n")
            f.write("- **Evaluations**: Each in its solution directory as `evaluation.json`\n")
            f.write("- **Summaries**: Only in main results folder\n\n")

            # Group by model
            by_model = {}
            for result in all_results:
                model = result.get("model")
                if model not in by_model:
                    by_model[model] = []
                by_model[model].append(result)

            f.write("## Results by Model\n\n")
            for model, results in by_model.items():
                gen_success = sum(1 for r in results if r.get("generation", {}).get("success"))
                eval_success = sum(1 for r in results if r.get("evaluation", {}).get("success"))

                f.write(f"### {model}\n\n")
                f.write(f"- **Generation:** {gen_success}/{len(results)} successful\n")
                f.write(f"- **Evaluation:** {eval_success}/{len(results)} successful\n")

                # Calculate average score
                scores = []
                for r in results:
                    if r.get("evaluation", {}).get("data", {}).get("overall_score"):
                        try:
                            score_str = r["evaluation"]["data"]["overall_score"]
                            score = float(score_str.replace("%", "").split("/")[0])
                            scores.append(score)
                        except:
                            pass

                if scores:
                    f.write(f"- **Average Score:** {sum(scores)/len(scores):.2f}%\n")
                    f.write(f"- **Score Range:** {min(scores):.2f}% - {max(scores):.2f}%\n")

                f.write("\n")

        print(f"Markdown report saved: {md_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SDK Bench evaluation - keeps samples folder clean"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Single model to evaluate"
    )

    parser.add_argument(
        "--models",
        type=str,
        help="Comma-separated list of models"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples"
    )

    parser.add_argument(
        "--n-workers",
        type=int,
        default=5,
        help="Number of concurrent workers"
    )

    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip generation, only evaluate"
    )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip evaluation, only generate"
    )

    args = parser.parse_args()

    # Determine models
    models = []
    if args.model:
        models = [args.model]
    elif args.models:
        models = [m.strip() for m in args.models.split(",")]
    else:
        print("Please specify --model or --models")
        return

    # Run evaluation
    evaluator = CorrectEvaluator(Path(__file__).parent.parent)
    evaluator.run_evaluation(
        models=models,
        limit=args.limit,
        skip_generation=args.skip_generation,
        skip_evaluation=args.skip_evaluation,
        n_workers=args.n_workers
    )


if __name__ == "__main__":
    main()