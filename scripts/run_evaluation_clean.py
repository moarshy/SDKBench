#!/usr/bin/env python3
"""
Clean evaluation pipeline for SDK Bench.

This script organizes results properly:
- Each sample gets its own results directory
- LLM solutions are saved within each sample
- Only aggregated results are saved in the main results folder

Directory structure:
    samples/
    ├── task1_init_001/
    │   ├── input/           # Original input files
    │   ├── expected/        # Expected solution & metadata
    │   └── results/         # NEW: All results for this sample
    │       ├── claude-sonnet-4-5/
    │       │   ├── generated_files/  # LLM generated code
    │       │   ├── generation.json   # Generation metadata
    │       │   └── evaluation.json   # Evaluation scores
    │       └── gpt-4-turbo/
    │           ├── generated_files/
    │           ├── generation.json
    │           └── evaluation.json
    └── results/             # Only aggregated results
        ├── summary_claude-sonnet-4-5.json
        └── overall_report.md
"""

import os
import sys
import json
import shutil
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


class CleanEvaluator:
    """Clean evaluation pipeline with proper directory structure."""

    def __init__(self, base_dir: Path):
        """Initialize evaluator."""
        self.base_dir = Path(base_dir)
        self.samples_dir = self.base_dir / "samples"
        self.results_dir = self.base_dir / "results"
        self.scripts_dir = self.base_dir / "scripts"

        # Create results directory
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def get_provider_for_model(self, model: str) -> str:
        """Determine provider based on model name."""
        if "claude" in model.lower():
            return "anthropic"
        elif "gpt" in model.lower():
            return "openai"
        else:
            return "anthropic"  # Default

    def generate_solution(
        self,
        sample_path: Path,
        model: str,
        provider: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Generate LLM solution for a sample, saving in sample directory."""
        sample_name = sample_path.name

        # Create results directory within the sample
        sample_results_dir = sample_path / "results" / model
        sample_results_dir.mkdir(parents=True, exist_ok=True)

        # Check if solution already exists
        generated_files_dir = sample_results_dir / "generated_files"
        generation_meta = sample_results_dir / "generation.json"

        if generated_files_dir.exists() and any(generated_files_dir.iterdir()):
            return True, {"status": "already_exists"}

        # Create temporary output directory for llm_evaluate.py
        temp_output = self.base_dir / "temp_llm_output"
        temp_output.mkdir(exist_ok=True)

        # Run llm_evaluate.py
        cmd = [
            "python",
            str(self.scripts_dir / "evaluation" / "llm_evaluate.py"),
            "--provider", provider,
            "--model", model,
            "--samples", str(sample_path),
            "--output", str(temp_output)
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

            # Move generated files to proper location
            temp_solution_dir = temp_output / sample_name / model
            if temp_solution_dir.exists():
                # Move all generated files
                generated_files_dir.mkdir(exist_ok=True)
                for file in temp_solution_dir.iterdir():
                    if file.name != "llm_response.txt":  # Skip raw response
                        shutil.move(str(file), str(generated_files_dir / file.name))

                # Save generation metadata
                generation_data = {
                    "model": model,
                    "provider": provider,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "files_generated": [f.name for f in generated_files_dir.iterdir()]
                }

                # Extract cost/token info if available
                if "cost" in result.stdout.lower():
                    generation_data["cost_info"] = result.stdout

                with open(generation_meta, 'w') as f:
                    json.dump(generation_data, f, indent=2)

                return True, generation_data

            return False, {"error": "No files generated"}

        except subprocess.TimeoutExpired:
            return False, {"error": "Generation timeout"}
        except Exception as e:
            return False, {"error": str(e)}
        finally:
            # Clean up temp directory
            if temp_output.exists():
                shutil.rmtree(temp_output, ignore_errors=True)

    def evaluate_solution(
        self,
        sample_path: Path,
        model: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Evaluate a generated solution."""
        sample_results_dir = sample_path / "results" / model
        generated_files_dir = sample_results_dir / "generated_files"
        evaluation_meta = sample_results_dir / "evaluation.json"
        metadata_path = sample_path / "expected" / "metadata.json"

        if not generated_files_dir.exists():
            return False, {"error": "No solution to evaluate"}

        if not metadata_path.exists():
            return False, {"error": "No metadata for evaluation"}

        # Run evaluate.py
        cmd = [
            "python",
            str(self.scripts_dir / "evaluation" / "evaluate.py"),
            str(generated_files_dir),
            "--metadata", str(metadata_path),
            "--output", str(sample_results_dir)
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

                # Try to find detailed results file
                for file in sample_results_dir.glob("*_result.json"):
                    with open(file) as f:
                        detailed = json.load(f)
                        evaluation_data["metrics"] = detailed.get("scores", {})
                    break

            else:
                evaluation_data["error"] = result.stderr[:500] if result.stderr else "Evaluation failed"

            # Save evaluation metadata
            with open(evaluation_meta, 'w') as f:
                json.dump(evaluation_data, f, indent=2)

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
        skip_evaluation: bool
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

        return result

    def run_evaluation(
        self,
        models: List[str],
        limit: Optional[int] = None,
        skip_generation: bool = False,
        skip_evaluation: bool = False,
        n_workers: int = 1
    ):
        """Run the clean evaluation pipeline."""
        # Get samples
        samples = sorted(self.samples_dir.glob("task*"))
        if limit:
            samples = samples[:limit]

        print(f"\n{'='*80}")
        print(f"CLEAN SDK BENCH EVALUATION")
        print(f"{'='*80}")
        print(f"Samples: {len(samples)}")
        print(f"Models: {', '.join(models)}")
        print(f"Workers: {n_workers}")
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
                            skip_evaluation
                        ): sample
                        for sample in samples
                    }

                    # Collect results as they complete
                    for future in as_completed(future_to_sample):
                        sample = future_to_sample[future]
                        try:
                            result = future.result()
                            model_results.append(result)
                            all_results.append(result)

                            # Update progress bar
                            gen_ok = result.get("generation", {}).get("success", False)
                            eval_ok = result.get("evaluation", {}).get("success", False)

                            if gen_ok and eval_ok:
                                status = "✅"
                            elif gen_ok:
                                status = "⚠️"
                            else:
                                status = "❌"

                            pbar.set_postfix({"last": f"{status} {sample.name}"})

                        except Exception as e:
                            print(f"\n❌ Error processing {sample.name}: {e}")
                            model_results.append({
                                "sample": sample.name,
                                "model": model,
                                "error": str(e)
                            })

                        pbar.update(1)

            # Save model summary
            self._save_model_summary(model, model_results)

        # Generate overall report
        elapsed = time.time() - start_time
        self._generate_overall_report(all_results, elapsed)

        print(f"\n{'='*80}")
        print(f"EVALUATION COMPLETE")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Results saved in: samples/*/results/")
        print(f"Summary in: {self.results_dir}")
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
            },
            "results": results
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

        print(f"Model summary saved: {summary_path}")

    def _generate_overall_report(self, all_results: List[Dict], elapsed_time: float):
        """Generate markdown report for all models."""
        report_path = self.results_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        # Group results by model
        by_model = {}
        for result in all_results:
            model = result["model"]
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(result)

        with open(report_path, 'w') as f:
            f.write("# SDK Bench Clean Evaluation Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Total Time:** {elapsed_time:.2f} seconds\n\n")

            f.write("## Directory Structure\n\n")
            f.write("```\n")
            f.write("samples/\n")
            f.write("├── task1_init_001/\n")
            f.write("│   ├── input/\n")
            f.write("│   ├── expected/\n")
            f.write("│   └── results/\n")
            f.write("│       └── [model-name]/\n")
            f.write("│           ├── generated_files/\n")
            f.write("│           ├── generation.json\n")
            f.write("│           └── evaluation.json\n")
            f.write("└── ...\n")
            f.write("```\n\n")

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

            f.write("## Next Steps\n\n")
            f.write("1. Review individual results in `samples/*/results/[model]/`\n")
            f.write("2. Check `generation.json` and `evaluation.json` for details\n")
            f.write("3. Examine generated code in `generated_files/` directories\n")
            f.write("4. Compare model performance across different task types\n")

        print(f"Overall report saved: {report_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean SDK Bench evaluation pipeline"
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
    evaluator = CleanEvaluator(Path(__file__).parent.parent)
    evaluator.run_evaluation(
        models=models,
        limit=args.limit,
        skip_generation=args.skip_generation,
        skip_evaluation=args.skip_evaluation,
        n_workers=args.n_workers
    )


if __name__ == "__main__":
    main()