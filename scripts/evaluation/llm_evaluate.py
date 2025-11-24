#!/usr/bin/env python3
"""Run LLM evaluation on SDK-Bench samples."""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.llm import LLMConfig, AnthropicProvider, OpenAIProvider
from sdkbench.llm.prompt_builder import PromptBuilder
from sdkbench.llm.solution_generator import SolutionGenerator
from sdkbench.evaluator import Evaluator


def generate_solution(
    sample_path: Path,
    provider_name: str,
    model: str,
    output_dir: Path,
    api_key: Optional[str] = None
) -> Dict:
    """Generate solution for a single sample.

    Args:
        sample_path: Path to sample directory
        provider_name: Provider name (anthropic, openai)
        model: Model name
        output_dir: Output directory
        api_key: API key (optional, uses env var if not provided)

    Returns:
        Result dictionary
    """
    sample_id = sample_path.name
    print(f"Processing {sample_id}...")

    # Prepare paths
    metadata_path = sample_path / "expected" / "metadata.json"
    input_dir = sample_path / "input"

    if not metadata_path.exists():
        print(f"  ❌ Metadata not found: {metadata_path}")
        return {"sample_id": sample_id, "error": "Metadata not found"}

    # Build prompt
    builder = PromptBuilder()
    system_prompt, user_prompt = builder.build_from_metadata(metadata_path, input_dir)

    # Create provider
    config = LLMConfig(
        model=model,
        temperature=0.1,
        max_tokens=4000,
        api_key=api_key
    )

    if provider_name == "anthropic":
        provider = AnthropicProvider(config)
    elif provider_name == "openai":
        provider = OpenAIProvider(config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

    # Generate solution
    try:
        print(f"  Generating with {model}...")
        start_time = time.time()

        response = provider.generate(user_prompt, system_prompt)

        generation_time = time.time() - start_time
        print(f"  ✅ Generated in {generation_time:.1f}s")
        print(f"     Tokens: {response.tokens_used} (cost: ${response.cost:.4f})")

        # Generate solution files
        generator = SolutionGenerator()
        solution_dir = generator.generate_solution(
            response.content,
            output_dir,
            sample_id,
            model,
            copy_input=input_dir if input_dir.exists() else None
        )

        print(f"  📁 Solution saved to: {solution_dir}")

        return {
            "sample_id": sample_id,
            "model": model,
            "success": True,
            "solution_dir": str(solution_dir),
            "tokens_used": response.tokens_used,
            "cost": response.cost,
            "generation_time": generation_time
        }

    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        return {
            "sample_id": sample_id,
            "model": model,
            "success": False,
            "error": str(e)
        }


def evaluate_solution(solution_dir: Path, sample_path: Path) -> Dict:
    """Evaluate a generated solution.

    Args:
        solution_dir: Path to solution directory
        sample_path: Path to original sample

    Returns:
        Evaluation results
    """
    metadata_path = sample_path / "expected" / "metadata.json"

    try:
        evaluator = Evaluator(solution_dir, metadata_path=metadata_path)
        result = evaluator.evaluate_quick()  # Quick evaluation without build/test

        return {
            "success": True,
            "overall_score": result.overall_score,
            "i_acc": result.i_acc.score if result.i_acc else None,
            "c_comp": result.c_comp.score if result.c_comp else None,
            "ipa": result.ipa.f1 if result.ipa else None,
            "cq": result.cq.score if result.cq else None,
            "sem_sim": result.sem_sim.score if result.sem_sim else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run LLM evaluation on SDK-Bench")
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="LLM provider to use"
    )
    parser.add_argument(
        "--model",
        default="claude-3-haiku-20240307",
        help="Model to use (default: claude-3-haiku-20240307)"
    )
    parser.add_argument(
        "--samples",
        default="samples/task1_init_001",
        help="Sample(s) to process (glob pattern or single path)"
    )
    parser.add_argument(
        "--output",
        default="results/llm_solutions",
        help="Output directory for solutions"
    )
    parser.add_argument(
        "--api-key",
        help="API key (uses env var if not provided)"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate generated solutions"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of samples to process"
    )

    args = parser.parse_args()

    # Find samples
    if '*' in args.samples or '?' in args.samples:
        # Glob pattern
        sample_paths = list(Path().glob(args.samples))
    elif Path(args.samples).is_dir():
        # Single sample directory
        sample_paths = [Path(args.samples)]
    else:
        # Multiple samples in directory
        samples_dir = Path(args.samples)
        if samples_dir.exists():
            sample_paths = sorted([
                d for d in samples_dir.iterdir()
                if d.is_dir() and d.name.startswith('task')
            ])
        else:
            print(f"❌ Samples path not found: {args.samples}")
            return 1

    # Apply limit if specified
    if args.limit:
        sample_paths = sample_paths[:args.limit]

    print("=" * 60)
    print(f"SDK-Bench LLM Evaluation")
    print("=" * 60)
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model}")
    print(f"Samples: {len(sample_paths)}")
    print(f"Output: {args.output}")
    print()

    # Check API key
    api_key = args.api_key
    if not api_key:
        if args.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("❌ ANTHROPIC_API_KEY not set. Use --api-key or set environment variable.")
                return 1
        elif args.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OPENAI_API_KEY not set. Use --api-key or set environment variable.")
                return 1

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    total_cost = 0.0
    total_time = 0.0

    # Generate solutions
    for i, sample_path in enumerate(sample_paths, 1):
        print(f"\n[{i}/{len(sample_paths)}] {sample_path.name}")
        print("-" * 40)

        result = generate_solution(
            sample_path,
            args.provider,
            args.model,
            output_dir,
            api_key
        )

        results.append(result)

        if result.get("success"):
            total_cost += result.get("cost", 0)
            total_time += result.get("generation_time", 0)

            # Evaluate if requested
            if args.evaluate and result.get("solution_dir"):
                print("  Evaluating solution...")
                eval_result = evaluate_solution(
                    Path(result["solution_dir"]),
                    sample_path
                )

                if eval_result["success"]:
                    result["evaluation"] = eval_result
                    print(f"  📊 Overall Score: {eval_result['overall_score']:.1f}%")
                else:
                    print(f"  ❌ Evaluation failed: {eval_result.get('error')}")

        # Save intermediate results
        results_file = output_dir / "results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful

    print(f"Total samples: {len(results)}")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Avg time per sample: {total_time/len(results):.1f}s" if results else "N/A")

    if args.evaluate and successful > 0:
        # Calculate average scores
        scores = [
            r["evaluation"]["overall_score"]
            for r in results
            if r.get("evaluation", {}).get("success")
        ]
        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"\nAverage Overall Score: {avg_score:.1f}%")

            # Breakdown by metric
            metrics = ["i_acc", "c_comp", "ipa", "cq", "sem_sim"]
            for metric in metrics:
                metric_scores = [
                    r["evaluation"][metric]
                    for r in results
                    if r.get("evaluation", {}).get("success") and r["evaluation"].get(metric) is not None
                ]
                if metric_scores:
                    avg = sum(metric_scores) / len(metric_scores)
                    # IPA is 0-1, others are 0-100
                    if metric == "ipa":
                        print(f"  {metric.upper()}: {avg:.3f}")
                    else:
                        print(f"  {metric.upper()}: {avg:.1f}%")

    print(f"\nResults saved to: {results_file}")

    return 0 if successful > 0 else 1


if __name__ == "__main__":
    sys.exit(main())