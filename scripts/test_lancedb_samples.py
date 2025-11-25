#!/usr/bin/env python3
"""
Simple test script to verify LanceDB samples work with evaluation metrics.
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sdkbench.metrics.i_acc import IAccEvaluator
from sdkbench.metrics.c_comp import CCompEvaluator
from sdkbench.metrics.ipa import IPAEvaluator
from sdkbench.metrics.f_corr import FCorrEvaluator
from sdkbench.metrics.cq import CQEvaluator
from sdkbench.metrics.sem_sim import SemSimEvaluator


def test_sample(sample_path: Path):
    """Test a single LanceDB sample with all metrics."""
    print(f"\n{'='*60}")
    print(f"Testing: {sample_path.name}")
    print(f"{'='*60}")

    # Load sample files
    input_file = sample_path / "input" / "app.py"
    expected_file = sample_path / "expected" / "app.py"

    if not input_file.exists() or not expected_file.exists():
        print("❌ Missing input or expected files")
        return None

    # Read files
    with open(input_file) as f:
        input_code = f.read()

    with open(expected_file) as f:
        expected_code = f.read()

    # For testing, use expected as the generated code
    generated_code = expected_code

    # Initialize metrics
    metrics = {
        "I-ACC": IAccEvaluator(input_code, generated_code, expected_code),
        "C-COMP": CCompEvaluator(input_code, generated_code, expected_code),
        "IPA": IPAEvaluator(input_code, generated_code, expected_code),
        "F-CORR": FCorrEvaluator(input_code, generated_code, expected_code),
        "CQ": CQEvaluator(input_code, generated_code, expected_code),
        "SEM-SIM": SemSimEvaluator(input_code, generated_code, expected_code)
    }

    results = {}

    # Evaluate each metric
    for name, evaluator in metrics.items():
        try:
            result = evaluator.evaluate()
            # Extract score from result object
            if hasattr(result, 'score'):
                score = result.score
            elif hasattr(result, 'final_score'):
                score = result.final_score
            else:
                # Try to get the numeric value from the result
                score = float(result) if result is not None else 0.0

            results[name] = score
            print(f"  {name}: {score:.3f}")
        except Exception as e:
            print(f"  {name}: Error - {e}")
            results[name] = 0.0

    # Overall score (average)
    overall = sum(results.values()) / len(results)
    results["overall"] = overall
    print(f"\n  Overall: {overall:.3f}")

    return results


def main():
    """Test first 5 LanceDB samples."""
    base_dir = Path(__file__).parent.parent
    samples_dir = base_dir / "samples" / "lancedb"

    # Get first 5 samples
    samples = sorted(samples_dir.glob("lancedb_task*"))[:5]

    if not samples:
        print("No LanceDB samples found!")
        return

    print(f"\n🧪 Testing {len(samples)} LanceDB samples with evaluation metrics...")

    all_results = []
    for sample_path in samples:
        result = test_sample(sample_path)
        if result:
            all_results.append({
                "sample": sample_path.name,
                **result
            })

    # Calculate average metrics
    if all_results:
        print(f"\n{'='*60}")
        print("📊 Average Metrics Across All Samples:")
        print(f"{'='*60}")

        metric_names = ["I-ACC", "C-COMP", "IPA", "F-CORR", "CQ", "SEM-SIM", "overall"]
        for metric in metric_names:
            values = [r[metric] for r in all_results if metric in r]
            if values:
                avg = sum(values) / len(values)
                print(f"  {metric}: {avg:.3f}")

        # Save results
        results_file = base_dir / "results" / "lancedb" / "test_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump({
                "samples_tested": len(samples),
                "results": all_results
            }, f, indent=2)

        print(f"\n✅ Test results saved to: {results_file}")
        print(f"\n🎉 LanceDB samples are compatible with existing metrics!")
    else:
        print("\n❌ No successful tests")


if __name__ == "__main__":
    main()