#!/usr/bin/env python3
"""Quick test script to verify core infrastructure works."""

from pathlib import Path
from sdkbench.core import Solution, GroundTruth, EvaluationResult, IAccResult

def test_solution():
    """Test Solution class."""
    print("\n✓ Testing Solution class...")

    # Test with task1_init_001 expected directory
    sample_dir = Path("samples/task1_init_001/expected")

    if not sample_dir.exists():
        print(f"   ⚠️  Sample not found: {sample_dir}")
        print("   Run 'uv run build-samples' first")
        return False

    solution = Solution(sample_dir)
    print(f"   Loaded {len(solution.files)} files")

    # Test basic operations
    has_layout = solution.has_file("app/layout.tsx")
    print(f"   Has app/layout.tsx: {has_layout}")

    imports = solution.extract_imports()
    print(f"   Found {len(imports)} imports")

    clerk_imports = [imp for imp in imports if "@clerk" in imp]
    print(f"   Clerk imports: {len(clerk_imports)}")

    return True

def test_ground_truth():
    """Test GroundTruth class."""
    print("\n✓ Testing GroundTruth class...")

    metadata_path = Path("samples/task1_init_001/expected/metadata.json")

    if not metadata_path.exists():
        print(f"   ⚠️  Metadata not found: {metadata_path}")
        return False

    ground_truth = GroundTruth(metadata_path)
    print(f"   Sample ID: {ground_truth.sample_id}")
    print(f"   Task Type: {ground_truth.task_type}")
    print(f"   Framework: {ground_truth.framework}")

    expected_files = ground_truth.get_expected_files()
    print(f"   Expected files: {expected_files}")

    expected_imports = ground_truth.get_expected_imports()
    print(f"   Expected imports: {expected_imports}")

    return True

def test_result():
    """Test Result classes."""
    print("\n✓ Testing Result classes...")

    # Create a sample I-ACC result
    i_acc = IAccResult(
        file_location_correct=True,
        imports_correct=True,
        pattern_correct=True,
        placement_correct=False,
    )
    print(f"   I-ACC Score: {i_acc.score:.1f}%")

    # Create evaluation result
    result = EvaluationResult(
        sample_id="task1_init_001",
        solution_dir=Path("samples/task1_init_001/expected"),
        task_type=1,
        i_acc=i_acc
    )

    print(f"   Evaluation Result: {result}")
    print(f"   Overall Score: {result.overall_score:.1f}%")

    # Test serialization
    data = result.to_dict()
    print(f"   Serialized to dict: {len(data)} keys")

    # Test deserialization
    result2 = EvaluationResult.from_dict(data)
    print(f"   Deserialized: {result2}")

    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("SDK-Bench Core Infrastructure Test")
    print("=" * 60)

    tests = [
        ("Solution", test_solution),
        ("GroundTruth", test_ground_truth),
        ("Result", test_result),
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
        print("\n🎉 All core infrastructure tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please fix before continuing.")

if __name__ == "__main__":
    main()
