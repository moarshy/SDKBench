#!/usr/bin/env python3
"""
Run evaluation on LanceDB samples.
Adapted from run_evaluation_correct.py to work with LanceDB samples.
"""
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm


class LanceDBEvaluator:
    """Evaluator for LanceDB samples."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.samples_dir = self.base_dir / "samples" / "lancedb"  # LanceDB samples
        self.results_dir = self.base_dir / "results" / "lancedb"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_evaluator(self, sample_path: Path, output_path: Path) -> Dict:
        """Run evaluator on a single sample."""
        try:
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)

            # Use existing evaluator script
            cmd = [
                "python", str(self.base_dir / "scripts" / "evaluate_existing.py"),
                "--model", "test",  # Model name for evaluation
                "--limit", "1"  # Process just this sample
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Load evaluation results
            eval_file = output_path / "evaluation_results.json"
            if eval_file.exists():
                with open(eval_file) as f:
                    return json.load(f)
            else:
                return {
                    "error": "No evaluation results",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

        except subprocess.TimeoutExpired:
            return {"error": "Evaluation timeout"}
        except Exception as e:
            return {"error": str(e)}

    def process_sample(self, sample_path: Path, model: str) -> Dict:
        """Process a single sample."""
        sample_id = sample_path.name

        # For testing, we'll use the expected solution as the model output
        # In real evaluation, you'd generate code with the model
        expected_dir = sample_path / "expected"
        if not expected_dir.exists():
            return {
                "sample_id": sample_id,
                "error": "No expected solution found"
            }

        # Create temp output directory for this evaluation
        temp_output = self.results_dir / f"temp_{sample_id}_{model}"

        # Run evaluation
        result = self.run_evaluator(sample_path, temp_output)

        # Clean up temp directory
        if temp_output.exists():
            import shutil
            shutil.rmtree(temp_output)

        return {
            "sample_id": sample_id,
            "model": model,
            **result
        }

    def run_evaluation(self, model: str = "test", limit: int = None):
        """Run evaluation on all LanceDB samples."""
        # Get samples
        samples = sorted(self.samples_dir.glob("lancedb_task*"))
        if limit:
            samples = samples[:limit]

        print(f"\n{'='*60}")
        print(f"LanceDB Evaluation")
        print(f"{'='*60}")
        print(f"Model: {model}")
        print(f"Samples: {len(samples)}")
        print(f"SDK: LanceDB")

        results = []

        # Process samples
        with tqdm(total=len(samples), desc=f"Evaluating {model}") as pbar:
            for sample in samples:
                result = self.process_sample(sample, model)
                results.append(result)
                pbar.update(1)

        # Calculate metrics
        successful = [r for r in results if "error" not in r]

        if successful:
            # Average metrics across samples
            metrics = {}
            metric_keys = [
                "instruction_following",
                "code_completeness",
                "import_analysis",
                "function_correctness",
                "code_quality",
                "semantic_similarity"
            ]

            for key in metric_keys:
                values = [r.get(key, 0) for r in successful if key in r]
                if values:
                    metrics[key] = sum(values) / len(values)

            print(f"\n📊 Evaluation Metrics:")
            for key, value in metrics.items():
                print(f"  {key}: {value:.3f}")

        else:
            print("\n❌ No successful evaluations")

        # Save results
        output_file = self.results_dir / f"lancedb_evaluation_{model}_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "model": model,
                "sdk": "lancedb",
                "timestamp": datetime.now().isoformat(),
                "total_samples": len(samples),
                "successful": len(successful),
                "results": results,
                "metrics": metrics if successful else {}
            }, f, indent=2)

        print(f"\n✅ Results saved to: {output_file}")

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run evaluation on LanceDB samples"
    )
    parser.add_argument(
        "--model",
        default="test",
        help="Model name (for testing, uses expected solutions)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples to evaluate"
    )

    args = parser.parse_args()

    evaluator = LanceDBEvaluator()
    evaluator.run_evaluation(args.model, args.limit)


if __name__ == "__main__":
    main()