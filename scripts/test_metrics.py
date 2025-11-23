#!/usr/bin/env python3
"""Quick test script to verify metrics work."""

from pathlib import Path
from sdkbench.core import Solution, GroundTruth
from sdkbench.metrics import IAccEvaluator, CCompEvaluator, IPAEvaluator


def test_i_acc():
    """Test I-ACC metric evaluator."""
    print("\n✓ Testing I-ACC metric...")

    sample_dir = Path("samples/task1_init_001/expected")
    metadata_path = sample_dir / "metadata.json"

    if not sample_dir.exists() or not metadata_path.exists():
        print(f"   ⚠️  Sample not found: {sample_dir}")
        print("   Run 'uv run build-samples' first")
        return False

    solution = Solution(sample_dir)
    ground_truth = GroundTruth(metadata_path)

    evaluator = IAccEvaluator(solution, ground_truth)
    result = evaluator.evaluate()

    print(f"   File location: {result.file_location_correct}")
    print(f"   Imports: {result.imports_correct}")
    print(f"   Pattern: {result.pattern_correct}")
    print(f"   Placement: {result.placement_correct}")
    print(f"   Overall Score: {result.score:.1f}%")

    # Get detailed breakdown
    details = evaluator.get_details()
    print(f"   Details available: {len(details)} components")

    return True


def test_c_comp():
    """Test C-COMP metric evaluator."""
    print("\n✓ Testing C-COMP metric...")

    sample_dir = Path("samples/task1_init_001/expected")
    metadata_path = sample_dir / "metadata.json"

    if not sample_dir.exists() or not metadata_path.exists():
        print(f"   ⚠️  Sample not found: {sample_dir}")
        return False

    solution = Solution(sample_dir)
    ground_truth = GroundTruth(metadata_path)

    evaluator = CCompEvaluator(solution, ground_truth)
    result = evaluator.evaluate()

    print(f"   Env vars: {result.env_vars_score}")
    print(f"   Provider props: {result.provider_props_score}")
    print(f"   Middleware config: {result.middleware_config_score}")
    print(f"   Overall Score: {result.score:.1f}%")

    # Get detailed breakdown
    details = evaluator.get_details()
    print(f"   Details available: {len(details)} components")

    return True


def test_ipa():
    """Test IPA metric evaluator."""
    print("\n✓ Testing IPA metric...")

    sample_dir = Path("samples/task1_init_001/expected")
    metadata_path = sample_dir / "metadata.json"

    if not sample_dir.exists() or not metadata_path.exists():
        print(f"   ⚠️  Sample not found: {sample_dir}")
        return False

    solution = Solution(sample_dir)
    ground_truth = GroundTruth(metadata_path)

    evaluator = IPAEvaluator(solution, ground_truth)
    result = evaluator.evaluate()

    print(f"   Precision: {result.precision:.2%}")
    print(f"   Recall: {result.recall:.2%}")
    print(f"   F1 Score: {result.f1:.2%}")
    print(f"   True Positives: {result.true_positives}")
    print(f"   False Positives: {result.false_positives}")
    print(f"   False Negatives: {result.false_negatives}")

    # Get detailed breakdown
    details = evaluator.get_details()
    print(f"   Expected integration points: {details['expected_count']}")
    print(f"   Solution integration points: {details['solution_count']}")

    return True


def main():
    """Run all metric tests."""
    print("=" * 60)
    print("SDK-Bench Metrics Test")
    print("=" * 60)

    tests = [
        ("I-ACC", test_i_acc),
        ("C-COMP", test_c_comp),
        ("IPA", test_ipa),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All metric tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please fix before continuing.")


if __name__ == "__main__":
    main()
