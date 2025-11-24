#!/usr/bin/env python3
"""CLI script for evaluating solutions."""

import sys
import argparse
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.evaluator import Evaluator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate SDK-Bench solutions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick evaluation (no build/tests)
  uv run evaluate samples/task1_init_001/expected

  # Full evaluation with build and tests
  uv run evaluate samples/task1_init_001/expected --build --tests

  # Save detailed report
  uv run evaluate samples/task1_init_001/expected --output results/ --detailed

  # Batch evaluate multiple samples
  uv run evaluate samples/*/expected --output results/ --batch
        """,
    )

    parser.add_argument(
        "solution_dir",
        type=Path,
        help="Path to solution directory (or pattern for batch mode)",
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory for results (optional)",
    )

    parser.add_argument(
        "-m", "--metadata",
        type=Path,
        help="Path to metadata.json (default: solution_dir/metadata.json)",
    )

    parser.add_argument(
        "-b", "--build",
        action="store_true",
        help="Run build (for F-CORR metric)",
    )

    parser.add_argument(
        "-t", "--tests",
        action="store_true",
        help="Run tests (for F-CORR metric)",
    )

    parser.add_argument(
        "-d", "--detailed",
        action="store_true",
        help="Generate detailed report",
    )

    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"],
        help="Specific metrics to run (default: all)",
    )

    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: evaluate multiple solutions",
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode: minimal output",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Batch mode
    if args.batch:
        run_batch_evaluation(args)
        return

    # Single evaluation
    run_single_evaluation(args)


def run_single_evaluation(args):
    """Run evaluation on a single solution.

    Args:
        args: Command line arguments
    """
    solution_dir = args.solution_dir

    if not solution_dir.exists():
        print(f"Error: Solution directory not found: {solution_dir}")
        sys.exit(1)

    try:
        # Create evaluator
        evaluator = Evaluator(solution_dir, metadata_path=args.metadata)

        if not args.quiet:
            print("=" * 60)
            print(f"Evaluating: {solution_dir}")
            print("=" * 60)

        # Run evaluation
        if args.build or args.tests:
            result = evaluator.evaluate(
                run_build=args.build,
                run_tests=args.tests,
                metrics=args.metrics,
            )
        else:
            result = evaluator.evaluate_quick()

        # Output results
        if args.json:
            output_json_results(result, args.detailed, evaluator)
        else:
            output_text_results(result, args.detailed, evaluator, args.quiet)

        # Save to file if output specified
        if args.output:
            save_results(result, args.output, evaluator, args.detailed)

    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_batch_evaluation(args):
    """Run evaluation on multiple solutions.

    Args:
        args: Command line arguments
    """
    # Find all matching directories
    pattern = str(args.solution_dir)
    base_dir = Path(".").resolve()

    # Use glob to find directories
    if "*" in pattern:
        sample_dirs = list(base_dir.glob(pattern))
        sample_dirs = [d for d in sample_dirs if d.is_dir()]
    else:
        sample_dirs = [args.solution_dir]

    if not sample_dirs:
        print(f"Error: No directories found matching: {pattern}")
        sys.exit(1)

    if not args.quiet:
        print(f"Found {len(sample_dirs)} samples to evaluate")
        print("=" * 60)

    results = []
    failed = []

    for i, sample_dir in enumerate(sample_dirs, 1):
        if not args.quiet:
            print(f"\n[{i}/{len(sample_dirs)}] Evaluating: {sample_dir}")

        try:
            evaluator = Evaluator(sample_dir)

            if args.build or args.tests:
                result = evaluator.evaluate(
                    run_build=args.build,
                    run_tests=args.tests,
                    metrics=args.metrics,
                )
            else:
                result = evaluator.evaluate_quick()

            results.append(result)

            if not args.quiet:
                print(f"   Overall Score: {result.overall_score:.1f}%")

            # Save individual result
            if args.output:
                save_results(result, args.output, evaluator, args.detailed)

        except Exception as e:
            failed.append((sample_dir, str(e)))
            if not args.quiet:
                print(f"   ❌ Failed: {e}")

    # Summary
    if not args.quiet:
        print("\n" + "=" * 60)
        print("Batch Evaluation Summary")
        print("=" * 60)
        print(f"Total samples: {len(sample_dirs)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(failed)}")

        if results:
            avg_score = sum(r.overall_score for r in results) / len(results)
            print(f"Average score: {avg_score:.1f}%")

        if failed:
            print("\nFailed samples:")
            for sample_dir, error in failed:
                print(f"  - {sample_dir}: {error}")


def output_text_results(result, detailed, evaluator, quiet):
    """Output results as formatted text.

    Args:
        result: EvaluationResult
        detailed: Whether to show detailed report
        evaluator: Evaluator instance
        quiet: Whether to minimize output
    """
    if quiet:
        print(f"{result.overall_score:.1f}")
        return

    print(f"\nSample ID: {result.sample_id}")
    print(f"Task Type: {result.task_type}")
    print(f"Overall Score: {result.overall_score:.1f}%")
    print()

    # Metric scores
    print("Metric Scores:")
    print("-" * 40)

    if result.i_acc:
        print(f"  I-ACC  (Initialization):     {result.i_acc.score:6.1f}%")
    if result.c_comp:
        print(f"  C-COMP (Configuration):      {result.c_comp.score:6.1f}%")
    if result.ipa:
        print(f"  IPA    (Integration):        {result.ipa.f1*100:6.1f}%")
    if result.f_corr:
        print(f"  F-CORR (Functionality):      {result.f_corr.score:6.1f}%")
    if result.cq:
        print(f"  CQ     (Code Quality):       {result.cq.score:6.1f}%")
    if result.sem_sim:
        print(f"  SEM-SIM (Similarity):        {result.sem_sim.score*100:6.1f}%")

    if detailed:
        print("\n" + "=" * 60)
        print("Detailed Report")
        print("=" * 60)

        report = evaluator.get_detailed_report()

        # I-ACC details
        if result.i_acc:
            print("\n[I-ACC] Initialization Correctness:")
            i_acc_details = report['metrics']['i_acc']['details']
            if 'file_location' in i_acc_details:
                print(f"  File location: {'✅' if i_acc_details['file_location']['correct'] else '❌'}")
            if 'imports' in i_acc_details:
                print(f"  Imports: {'✅' if i_acc_details['imports']['correct'] else '❌'}")
            if 'pattern' in i_acc_details:
                print(f"  Pattern: {'✅' if i_acc_details['pattern']['correct'] else '❌'}")
            if 'placement' in i_acc_details:
                print(f"  Placement: {'✅' if i_acc_details['placement']['correct'] else '❌'}")

        # IPA details
        if result.ipa:
            print("\n[IPA] Integration Point Accuracy:")
            ipa_details = report['metrics']['ipa']['details']
            print(f"  Precision: {ipa_details['precision']:.2%}")
            print(f"  Recall: {ipa_details['recall']:.2%}")
            print(f"  F1 Score: {ipa_details['f1_score']:.2%}")

        # CQ details
        if result.cq:
            print("\n[CQ] Code Quality:")
            cq_details = report['metrics']['cq']['details']
            print(f"  Total deductions: {cq_details['total_deductions']} points")
            print(f"  Issue count: {cq_details['deduction_count']}")


def output_json_results(result, detailed, evaluator):
    """Output results as JSON.

    Args:
        result: EvaluationResult
        detailed: Whether to include detailed report
        evaluator: Evaluator instance
    """
    if detailed:
        output = evaluator.get_detailed_report()
    else:
        output = result.model_dump()

    print(json.dumps(output, indent=2, default=str))


def save_results(result, output_dir, evaluator, detailed):
    """Save results to file.

    Args:
        result: EvaluationResult
        output_dir: Output directory
        evaluator: Evaluator instance
        detailed: Whether to save detailed report
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{result.sample_id}_result.json"

    if detailed:
        report = evaluator.get_detailed_report()
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    else:
        result.to_json_file(output_path)

    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    main()
