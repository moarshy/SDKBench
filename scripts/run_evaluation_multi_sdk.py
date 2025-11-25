#!/usr/bin/env python3
"""
Multi-SDK evaluation pipeline for SDK Bench.
Supports evaluating Clerk, LanceDB, and future SDKs.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from tqdm import tqdm


class MultiSDKEvaluationPipeline:
    """Evaluation pipeline that supports multiple SDKs."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.samples_dir = self.base_dir / "samples"
        self.solutions_dir = self.base_dir / "solutions"
        self.results_dir = self.base_dir / "results"

        # Create necessary directories
        self.solutions_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def get_sdk_samples(self, sdk: str, limit: Optional[int] = None) -> List[Path]:
        """Get samples for a specific SDK."""
        sdk_dir = self.samples_dir / sdk

        if not sdk_dir.exists():
            print(f"❌ SDK directory not found: {sdk_dir}")
            return []

        # Different pattern matching for different SDKs
        if sdk == "clerk":
            samples = sorted(sdk_dir.glob("task*"))
        elif sdk == "lancedb":
            samples = sorted(sdk_dir.glob("lancedb_task*"))
        else:
            # Generic pattern for future SDKs
            samples = sorted(sdk_dir.glob(f"{sdk}_task*"))
            if not samples:
                # Fallback to task* pattern
                samples = sorted(sdk_dir.glob("task*"))

        if limit:
            samples = samples[:limit]

        return samples

    def get_all_sdks(self) -> List[str]:
        """Get list of all available SDKs."""
        sdks = []
        for sdk_dir in self.samples_dir.iterdir():
            if sdk_dir.is_dir() and not sdk_dir.name.startswith('.'):
                # Check if it contains sample directories
                has_samples = any(
                    p.is_dir() and ('task' in p.name)
                    for p in sdk_dir.iterdir()
                )
                if has_samples:
                    sdks.append(sdk_dir.name)
        return sorted(sdks)

    def get_provider_for_model(self, model: str) -> str:
        """Determine the provider for a model."""
        if "claude" in model.lower():
            return "anthropic"
        elif "gpt" in model.lower() or "o1" in model.lower():
            return "openai"
        elif "gemini" in model.lower():
            return "google"
        elif "deepseek" in model.lower():
            return "deepseek"
        else:
            return "openai"  # Default

    def run_code_generator(
        self,
        sample_path: Path,
        output_path: Path,
        model: str,
        provider: str,
        sdk: str
    ) -> Dict:
        """Run code generator for a sample."""
        try:
            # Create command
            cmd = [
                "python", str(self.base_dir / "sdkbench" / "generate_solution.py"),
                "--model", model,
                "--provider", provider,
                "--samples", str(sample_path),
                "--output", str(output_path)
            ]

            # Run generator
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr or "Generation failed"
                }

            return {"success": True}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Generation timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_evaluator(self, sample_path: Path, solution_path: Path, sdk: str) -> Dict:
        """Run evaluator on generated solution."""
        try:
            # Create temporary output directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_output = Path(temp_dir) / "eval_output"
                temp_output.mkdir()

                cmd = [
                    "python", str(self.base_dir / "sdkbench" / "evaluate.py"),
                    "--samples", str(sample_path),
                    "--generated", str(solution_path),
                    "--output", str(temp_output),
                    "--sdk", sdk  # Pass SDK for context
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                # Load evaluation results
                eval_file = temp_output / "evaluation_results.json"
                if eval_file.exists():
                    with open(eval_file) as f:
                        eval_results = json.load(f)
                    return {
                        "success": True,
                        "metrics": eval_results.get("metrics", {}),
                        "details": eval_results.get("details", {})
                    }
                else:
                    return {
                        "success": False,
                        "error": "No evaluation results"
                    }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Evaluation timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_sample(
        self,
        sample: Path,
        model: str,
        provider: str,
        sdk: str,
        skip_generation: bool,
        skip_evaluation: bool,
        pbar
    ) -> Dict:
        """Process a single sample."""
        sample_id = sample.name

        # Create output paths
        solution_path = self.solutions_dir / sdk / model / sample_id
        solution_path.mkdir(parents=True, exist_ok=True)

        result = {
            "sample": sample_id,
            "model": model,
            "sdk": sdk,
            "generation": {},
            "evaluation": {}
        }

        # Generation phase
        if not skip_generation:
            gen_result = self.run_code_generator(
                sample, solution_path, model, provider, sdk
            )
            result["generation"] = gen_result
        else:
            result["generation"] = {"success": True, "skipped": True}

        # Evaluation phase
        if not skip_evaluation and result["generation"].get("success"):
            eval_result = self.run_evaluator(sample, solution_path, sdk)
            result["evaluation"] = eval_result
        else:
            result["evaluation"] = {"skipped": True}

        # Update progress bar
        pbar.update(1)

        return result

    def run_evaluation(
        self,
        models: List[str],
        sdk: Optional[str] = None,
        limit: Optional[int] = None,
        skip_generation: bool = False,
        skip_evaluation: bool = False,
        n_workers: int = 1
    ):
        """Run the evaluation pipeline."""
        # Determine which SDKs to evaluate
        if sdk:
            if sdk == "all":
                sdks_to_eval = self.get_all_sdks()
            else:
                sdks_to_eval = [sdk]
        else:
            # Default to all SDKs
            sdks_to_eval = self.get_all_sdks()

        print(f"\n{'='*80}")
        print(f"MULTI-SDK BENCH EVALUATION")
        print(f"{'='*80}")
        print(f"SDKs: {', '.join(sdks_to_eval)}")
        print(f"Models: {', '.join(models)}")
        print(f"Workers: {n_workers}")
        print(f"Output: {self.solutions_dir}")
        print(f"{'='*80}\n")

        all_results = []
        start_time = time.time()

        for current_sdk in sdks_to_eval:
            print(f"\n{'='*60}")
            print(f"SDK: {current_sdk.upper()}")
            print(f"{'='*60}")

            # Get samples for this SDK
            samples = self.get_sdk_samples(current_sdk, limit)

            if not samples:
                print(f"⚠️  No samples found for {current_sdk}")
                continue

            print(f"Found {len(samples)} samples")

            # Create SDK results directory
            sdk_results_dir = self.results_dir / current_sdk
            sdk_results_dir.mkdir(parents=True, exist_ok=True)

            for model in models:
                provider = self.get_provider_for_model(model)

                print(f"\n{'='*50}")
                print(f"MODEL: {model}")
                print(f"Provider: {provider}")
                print(f"SDK: {current_sdk}")
                print(f"{'='*50}\n")

                model_results = []

                # Process samples concurrently
                with ThreadPoolExecutor(max_workers=n_workers) as executor:
                    with tqdm(total=len(samples), desc=f"{current_sdk}/{model}") as pbar:
                        # Submit all tasks
                        future_to_sample = {
                            executor.submit(
                                self.process_sample,
                                sample,
                                model,
                                provider,
                                current_sdk,
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
                                    "sdk": current_sdk,
                                    "error": str(e)
                                })

                # Save SDK-model specific summary
                self._save_sdk_model_summary(current_sdk, model, model_results)

        # Generate overall report
        elapsed = time.time() - start_time
        self._generate_overall_report(all_results, elapsed, models, sdks_to_eval)

        print(f"\n{'='*80}")
        print(f"EVALUATION COMPLETE")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Solutions: {self.solutions_dir}")
        print(f"Results: {self.results_dir}")
        print(f"{'='*80}\n")

    def _save_sdk_model_summary(self, sdk: str, model: str, results: List[Dict]):
        """Save summary for a specific SDK-model combination."""
        summary = {
            "sdk": sdk,
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

        # Calculate average metrics if available
        metrics_data = [
            r.get("evaluation", {}).get("metrics", {})
            for r in results
            if r.get("evaluation", {}).get("success")
        ]

        if metrics_data:
            avg_metrics = {}
            metric_keys = ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]
            for key in metric_keys:
                values = [m.get(key, 0) for m in metrics_data if key in m]
                if values:
                    avg_metrics[key] = sum(values) / len(values)
            summary["average_metrics"] = avg_metrics

        # Save to SDK-specific directory
        output_file = self.results_dir / sdk / f"{model}_summary.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"📊 Saved {sdk}/{model} summary to: {output_file}")

    def _generate_overall_report(
        self,
        results: List[Dict],
        elapsed: float,
        models: List[str],
        sdks: List[str]
    ):
        """Generate overall evaluation report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "models": models,
            "sdks": sdks,
            "total_evaluations": len(results),
            "by_sdk": {},
            "by_model": {},
            "combined_metrics": {}
        }

        # Group results by SDK
        for sdk in sdks:
            sdk_results = [r for r in results if r.get("sdk") == sdk]
            report["by_sdk"][sdk] = {
                "total": len(sdk_results),
                "success": sum(1 for r in sdk_results if r.get("evaluation", {}).get("success"))
            }

        # Group results by model
        for model in models:
            model_results = [r for r in results if r.get("model") == model]
            report["by_model"][model] = {
                "total": len(model_results),
                "success": sum(1 for r in model_results if r.get("evaluation", {}).get("success"))
            }

        # Calculate combined average metrics
        metrics_data = [
            r.get("evaluation", {}).get("metrics", {})
            for r in results
            if r.get("evaluation", {}).get("success")
        ]

        if metrics_data:
            metric_keys = ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]
            for key in metric_keys:
                values = [m.get(key, 0) for m in metrics_data if key in m]
                if values:
                    report["combined_metrics"][key] = sum(values) / len(values)

        # Save overall report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"overall_report_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Overall report saved to: {output_file}")

        # Print summary
        if report["combined_metrics"]:
            print("\n🎯 Combined Average Metrics:")
            for key, value in report["combined_metrics"].items():
                print(f"  {key}: {value:.3f}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Multi-SDK evaluation pipeline for SDK Bench"
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
        "--sdk",
        type=str,
        default="all",
        help="SDK to evaluate (clerk, lancedb, all)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples per SDK"
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

    # Determine models to evaluate
    if args.model:
        models = [args.model]
    elif args.models:
        models = [m.strip() for m in args.models.split(',')]
    else:
        # Default test models
        models = ["claude-sonnet-4-5", "gpt-5.1-2025-11-13"]

    # Run evaluation
    pipeline = MultiSDKEvaluationPipeline()
    pipeline.run_evaluation(
        models=models,
        sdk=args.sdk,
        limit=args.limit,
        skip_generation=args.skip_generation,
        skip_evaluation=args.skip_evaluation,
        n_workers=args.n_workers
    )


if __name__ == "__main__":
    main()