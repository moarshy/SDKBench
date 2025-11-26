#!/usr/bin/env python
"""Standalone F-CORR (Functional Correctness) evaluation runner.

Run functional correctness tests on samples or solutions.

Usage:
    # Run on a single sample's expected/ directory
    python scripts/run_fcorr.py --sample samples/lancedb/lancedb_task1_init_001

    # Run on all samples for an SDK
    python scripts/run_fcorr.py --sdk lancedb

    # Run on a generated solution
    python scripts/run_fcorr.py --solution solutions/clerk/claude-sonnet-4-5/task1_init_001

    # Run on any directory with tests
    python scripts/run_fcorr.py --directory /path/to/project

    # Verbose output
    python scripts/run_fcorr.py --sample samples/clerk/task1_init_001 --verbose

    # JSON output
    python scripts/run_fcorr.py --sdk lancedb --json
"""

import argparse
import json
import sys
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sdkbench.test_harness.registry import TestRunnerRegistry
from sdkbench.test_harness.models import FCorrResult


def run_fcorr_on_directory(
    project_dir: Path,
    test_dir: Optional[Path] = None,
    auto_install: bool = True,
    verbose: bool = False,
) -> FCorrResult:
    """Run F-CORR evaluation on a directory.

    Args:
        project_dir: Directory containing the project
        test_dir: Optional specific test directory
        auto_install: Whether to install dependencies
        verbose: Print detailed output

    Returns:
        FCorrResult with evaluation results
    """
    import time
    start_time = time.time()

    if verbose:
        print(f"Evaluating: {project_dir}")

    # Check if this is a prepared sample directory with tests/ subdirectory
    tests_subdir = project_dir / "tests"
    if tests_subdir.exists() and test_dir is None:
        test_dir = tests_subdir

    runner = TestRunnerRegistry.get_runner(project_dir)

    if runner is None:
        return FCorrResult(
            score=0.0,
            error="No compatible test runner found",
            duration=time.time() - start_time,
        )

    detection = runner.detect()
    if verbose:
        print(f"  Language: {detection.language.value if detection.language else 'unknown'}")
        print(f"  Framework: {detection.framework.value if detection.framework else 'unknown'}")
        print(f"  Markers: {detection.markers_found}")

    # Install dependencies
    if auto_install:
        if verbose:
            print("  Installing dependencies...")
        install_result = runner.install_dependencies()
        if not install_result.success:
            return FCorrResult(
                score=0.0,
                install_results=install_result,
                language=detection.language,
                framework=detection.framework,
                error=f"Install failed: {install_result.error}",
                duration=time.time() - start_time,
            )
        if verbose:
            print(f"  Install completed in {install_result.duration:.1f}s")

    # Run tests
    if verbose:
        print("  Running tests...")
    test_result = runner.run_tests(test_dir)

    # Calculate strict score
    if test_result.success and test_result.failed == 0:
        score = 100.0
    else:
        score = 0.0

    if verbose:
        print(f"  Results: {test_result.passed} passed, {test_result.failed} failed, {test_result.skipped} skipped")
        print(f"  Duration: {test_result.duration:.1f}s")
        print(f"  F-CORR Score: {score}%")

    return FCorrResult(
        score=score,
        test_results=test_result,
        language=detection.language,
        framework=detection.framework,
        error=None if score == 100.0 else f"{test_result.failed} tests failed",
        duration=time.time() - start_time,
    )


def prepare_sample_for_testing(sample_path: Path, verbose: bool = False) -> Optional[Path]:
    """Prepare a sample directory for testing.

    For SDKBench samples, the structure is:
    - sample/expected/  (contains the solution code)
    - sample/tests/     (contains tests that import from 'expected')

    We preserve this structure by creating:
    - temp/expected/  (copy of expected/)
    - temp/tests/     (copy of tests/)
    - temp/conftest.py (copy from SDK level if exists)

    Tests import like: `from expected import app`

    Args:
        sample_path: Path to sample directory
        verbose: Print detailed output

    Returns:
        Path to prepared test directory, or None if failed
    """
    expected_dir = sample_path / "expected"
    tests_dir = sample_path / "tests"

    if not expected_dir.exists():
        if verbose:
            print(f"  Error: No expected/ directory in {sample_path}")
        return None

    if not tests_dir.exists():
        if verbose:
            print(f"  Warning: No tests/ directory in {sample_path}")
        # Still try to run - maybe tests are in expected/
        return expected_dir

    # Create temp directory that mirrors the sample structure
    temp_dir = Path(tempfile.mkdtemp(prefix="fcorr_"))

    if verbose:
        print(f"  Preparing test directory: {temp_dir}")

    # Copy expected/ directory (preserving the 'expected' name for imports)
    expected_dest = temp_dir / "expected"
    shutil.copytree(expected_dir, expected_dest)

    # Create __init__.py in expected/ for Python imports (if not exists)
    init_file = expected_dest / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Auto-generated for F-CORR testing\n")

    # Copy tests/ directory
    tests_dest = temp_dir / "tests"
    shutil.copytree(tests_dir, tests_dest)

    # Copy conftest.py if it exists (for shared test utilities)
    # Look in sample's parent directory (SDK level) for conftest.py
    sdk_conftest = sample_path.parent / "conftest.py"
    if sdk_conftest.exists():
        shutil.copy2(sdk_conftest, temp_dir / "conftest.py")
        if verbose:
            print(f"  Copied conftest.py from {sdk_conftest}")

    # Copy requirements.txt if it exists in expected/
    req_file = expected_dir / "requirements.txt"
    if req_file.exists():
        shutil.copy2(req_file, temp_dir / "requirements.txt")

    # Copy package.json if it exists in expected/
    pkg_file = expected_dir / "package.json"
    if pkg_file.exists():
        shutil.copy2(pkg_file, temp_dir / "package.json")

    return temp_dir


def run_on_sample(sample_path: Path, verbose: bool = False, cleanup: bool = True) -> FCorrResult:
    """Run F-CORR on a sample's expected/ directory with its tests/.

    Args:
        sample_path: Path to sample directory
        verbose: Print detailed output
        cleanup: Whether to cleanup temp directory after

    Returns:
        FCorrResult with evaluation results
    """
    import time
    start_time = time.time()

    if verbose:
        print(f"\nSample: {sample_path.name}")

    # Prepare the sample for testing
    test_dir = prepare_sample_for_testing(sample_path, verbose=verbose)

    if test_dir is None:
        return FCorrResult(
            score=0.0,
            error=f"Could not prepare sample: {sample_path}",
            duration=time.time() - start_time,
        )

    try:
        result = run_fcorr_on_directory(test_dir, verbose=verbose)
    finally:
        # Cleanup temp directory if we created one
        if cleanup and test_dir != sample_path / "expected":
            if verbose:
                print(f"  Cleaning up: {test_dir}")
            shutil.rmtree(test_dir, ignore_errors=True)

    return result


def run_on_sdk(
    sdk_name: str,
    samples_dir: Path,
    verbose: bool = False,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Run F-CORR on all samples for an SDK.

    Args:
        sdk_name: Name of SDK (e.g., 'lancedb', 'clerk')
        samples_dir: Base samples directory
        verbose: Print detailed output
        limit: Maximum number of samples to run

    Returns:
        List of result dictionaries
    """
    sdk_dir = samples_dir / sdk_name

    if not sdk_dir.exists():
        print(f"SDK directory not found: {sdk_dir}")
        return []

    results = []
    sample_dirs = sorted([d for d in sdk_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])

    if limit:
        sample_dirs = sample_dirs[:limit]

    for sample_dir in sample_dirs:
        # Skip manifest files
        if sample_dir.name.endswith("_dataset_manifest.json"):
            continue

        print(f"\n{'='*60}")
        print(f"Sample: {sample_dir.name}")
        print(f"{'='*60}")

        result = run_on_sample(sample_dir, verbose=verbose)
        results.append({
            "sample_id": sample_dir.name,
            "score": result.score,
            "passed": result.passed,
            "error": result.error,
            "duration": result.duration,
            "language": result.language.value if result.language else None,
            "framework": result.framework.value if result.framework else None,
            "tests_passed": result.test_results.passed if result.test_results else 0,
            "tests_failed": result.test_results.failed if result.test_results else 0,
            "tests_total": result.test_results.total if result.test_results else 0,
        })

    return results


def print_summary(results: List[Dict[str, Any]]) -> None:
    """Print summary of F-CORR results."""
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    total = len(results)
    passed = sum(1 for r in results if r["score"] == 100.0)
    failed = total - passed

    print(f"Total Samples: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if total > 0:
        print(f"Pass Rate: {passed/total*100:.1f}%")

        # Group by language
        by_language = {}
        for r in results:
            lang = r.get("language", "unknown") or "unknown"
            if lang not in by_language:
                by_language[lang] = {"total": 0, "passed": 0}
            by_language[lang]["total"] += 1
            if r["score"] == 100.0:
                by_language[lang]["passed"] += 1

        print("\nBy Language:")
        for lang, stats in by_language.items():
            rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"  {lang}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")

    # Show failures
    failures = [r for r in results if r["score"] != 100.0]
    if failures:
        print("\nFailed Samples:")
        for f in failures[:10]:  # Show first 10 failures
            error = f.get("error", "Unknown error")
            print(f"  - {f['sample_id']}: {error}")
        if len(failures) > 10:
            print(f"  ... and {len(failures) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description="Run F-CORR (Functional Correctness) evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sample",
        type=Path,
        help="Path to a single sample directory",
    )
    group.add_argument(
        "--sdk",
        type=str,
        help="SDK name to evaluate all samples (e.g., 'lancedb', 'clerk')",
    )
    group.add_argument(
        "--solution",
        type=Path,
        help="Path to a generated solution directory",
    )
    group.add_argument(
        "--directory",
        type=Path,
        help="Path to any project directory with tests",
    )

    parser.add_argument(
        "--samples-dir",
        type=Path,
        default=PROJECT_ROOT / "samples",
        help="Base samples directory (default: ./samples)",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Skip dependency installation",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples to evaluate (for --sdk)",
    )

    args = parser.parse_args()

    if args.sample:
        result = run_on_sample(args.sample, verbose=args.verbose)
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(f"\nF-CORR Score: {result.score}%")
            if result.error:
                print(f"Error: {result.error}")
            if result.test_results:
                print(f"Tests: {result.test_results.passed}/{result.test_results.total} passed")

    elif args.sdk:
        results = run_on_sdk(
            args.sdk,
            args.samples_dir,
            verbose=args.verbose,
            limit=args.limit,
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_summary(results)

    elif args.solution:
        result = run_fcorr_on_directory(
            args.solution,
            auto_install=not args.no_install,
            verbose=args.verbose,
        )
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(f"\nF-CORR Score: {result.score}%")
            if result.error:
                print(f"Error: {result.error}")

    elif args.directory:
        result = run_fcorr_on_directory(
            args.directory,
            auto_install=not args.no_install,
            verbose=args.verbose,
        )
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(f"\nF-CORR Score: {result.score}%")
            if result.error:
                print(f"Error: {result.error}")


if __name__ == "__main__":
    main()
