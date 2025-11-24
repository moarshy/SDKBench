#!/usr/bin/env python3
"""
Evaluate existing LLM solutions that have already been generated.

This script is useful when generation succeeded but evaluation failed.
"""

import os
import sys
import json
from pathlib import Path
from tqdm import tqdm
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def evaluate_solution(solution_dir: Path, sample_path: Path, results_dir: Path) -> dict:
    """Evaluate a single solution."""
    sample_name = sample_path.name
    model_name = solution_dir.name
    metadata_path = sample_path / "expected" / "metadata.json"

    result = {
        "sample": sample_name,
        "model": model_name,
        "solution_dir": str(solution_dir)
    }

    if not solution_dir.exists() or not any(solution_dir.iterdir()):
        result["status"] = "no_solution"
        return result

    if not metadata_path.exists():
        result["status"] = "no_metadata"
        return result

    # Run evaluate.py
    cmd = [
        "python",
        "scripts/evaluation/evaluate.py",
        str(solution_dir),
        "--metadata", str(metadata_path),
        "--output", str(results_dir)
    ]

    try:
        process_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if process_result.returncode != 0:
            result["status"] = "failed"
            result["error"] = process_result.stderr[:500]
        else:
            result["status"] = "success"

            # Try to parse scores from output
            if "Overall Score:" in process_result.stdout:
                for line in process_result.stdout.split("\n"):
                    if "Overall Score:" in line:
                        result["overall_score"] = line.split(":")[-1].strip()
                        break

            # Parse individual metrics if available
            metrics = {}
            for line in process_result.stdout.split("\n"):
                if "I-ACC:" in line:
                    metrics["I-ACC"] = line.split(":")[-1].strip()
                elif "C-COMP:" in line:
                    metrics["C-COMP"] = line.split(":")[-1].strip()
                elif "IPA:" in line:
                    metrics["IPA"] = line.split(":")[-1].strip()
                elif "F-CORR:" in line:
                    metrics["F-CORR"] = line.split(":")[-1].strip()
                elif "CQ:" in line:
                    metrics["CQ"] = line.split(":")[-1].strip()
                elif "SEM-SIM:" in line:
                    metrics["SEM-SIM"] = line.split(":")[-1].strip()

            if metrics:
                result["metrics"] = metrics

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate existing LLM solutions"
    )

    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name to evaluate (must match directory name)"
    )

    parser.add_argument(
        "--n-workers",
        type=int,
        default=5,
        help="Number of concurrent workers"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples to evaluate"
    )

    args = parser.parse_args()

    # Setup paths
    base_dir = Path(__file__).parent.parent
    samples_dir = base_dir / "samples"
    solutions_dir = base_dir / "results" / "llm_solutions"
    results_dir = base_dir / "results"

    # Find all samples
    sample_paths = sorted(samples_dir.glob("task*"))
    if args.limit:
        sample_paths = sample_paths[:args.limit]

    print(f"\n{'='*60}")
    print(f"EVALUATING EXISTING SOLUTIONS")
    print(f"{'='*60}")
    print(f"Model: {args.model}")
    print(f"Samples: {len(sample_paths)}")
    print(f"Workers: {args.n_workers}")
    print(f"{'='*60}\n")

    # Collect all solution directories to evaluate
    tasks = []
    for sample_path in sample_paths:
        solution_dir = solutions_dir / sample_path.name / args.model
        if solution_dir.exists():
            tasks.append((solution_dir, sample_path))

    if not tasks:
        print(f"❌ No solutions found for model: {args.model}")
        return

    print(f"Found {len(tasks)} solutions to evaluate\n")

    # Run evaluations concurrently
    results = []
    with ThreadPoolExecutor(max_workers=args.n_workers) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(evaluate_solution, solution_dir, sample_path, results_dir): (solution_dir, sample_path)
            for solution_dir, sample_path in tasks
        }

        # Process results as they complete
        with tqdm(total=len(tasks), desc="Evaluating") as pbar:
            for future in as_completed(future_to_task):
                solution_dir, sample_path = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)

                    # Update progress bar with status
                    if result["status"] == "success":
                        pbar.set_postfix({"last": f"✅ {result['sample']}"})
                    else:
                        pbar.set_postfix({"last": f"❌ {result['sample']}: {result['status']}"})

                except Exception as e:
                    print(f"\n❌ Error evaluating {sample_path.name}: {e}")
                    results.append({
                        "sample": sample_path.name,
                        "model": args.model,
                        "status": "exception",
                        "error": str(e)
                    })

                pbar.update(1)

    # Summary
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count

    print(f"\n{'='*60}")
    print(f"EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}/{len(results)}")
    print(f"❌ Failed: {failed_count}/{len(results)}")

    # Save results
    output_file = results_dir / f"evaluation_results_{args.model}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

    # Print summary of scores
    if success_count > 0:
        print(f"\n{'='*60}")
        print("SCORE SUMMARY")
        print(f"{'='*60}")

        scores = []
        for r in results:
            if r["status"] == "success" and "overall_score" in r:
                try:
                    score_str = r["overall_score"].replace("%", "").strip()
                    score = float(score_str.split("/")[0]) if "/" in score_str else float(score_str)
                    scores.append(score)
                except:
                    pass

        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)

            print(f"Average Score: {avg_score:.2f}%")
            print(f"Min Score: {min_score:.2f}%")
            print(f"Max Score: {max_score:.2f}%")
            print(f"Scored Samples: {len(scores)}/{success_count}")


if __name__ == "__main__":
    main()