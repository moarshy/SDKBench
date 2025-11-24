#!/usr/bin/env python3
"""
SDK Bench Evaluation Pipeline Orchestrator

This script orchestrates the complete SDK Bench evaluation pipeline:
1. Data Collection - Search, mine, and extract patterns from GitHub repos
2. Sample Generation - Build test cases from extracted patterns
3. Evaluation - Generate LLM solutions and evaluate them

Usage:
    # Run complete pipeline
    python scripts/run_pipeline.py --full

    # Run specific phase
    python scripts/run_pipeline.py --phase data_collection
    python scripts/run_pipeline.py --phase sample_generation
    python scripts/run_pipeline.py --phase evaluation

    # Skip data collection (use existing data)
    python scripts/run_pipeline.py --skip-collection
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import time
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class SDKBenchPipeline:
    """Orchestrate the SDK Bench evaluation pipeline."""

    def __init__(self, base_dir: Path, config: Optional[Dict] = None):
        """Initialize pipeline with base directory and configuration."""
        self.base_dir = Path(base_dir)
        self.scripts_dir = self.base_dir / "scripts"
        self.data_dir = self.base_dir / "data"
        self.samples_dir = self.base_dir / "samples"
        self.results_dir = self.base_dir / "results"

        # Create necessary directories
        for dir_path in [self.data_dir, self.samples_dir, self.results_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Load or use default configuration
        self.config = config or self._default_config()

    def _default_config(self) -> Dict:
        """Return default pipeline configuration."""
        return {
            "data_collection": {
                "max_repos": 100,
                "min_stars": 10,
                "languages": ["TypeScript", "JavaScript"],
                "search_query": "clerk nextjs auth"
            },
            "sample_generation": {
                "task_counts": {
                    "initialization": 15,
                    "middleware": 15,
                    "hooks": 10,
                    "complete": 7,
                    "migration": 3
                }
            },
            "evaluation": {
                "models": [
                    {"provider": "anthropic", "name": "claude-3-haiku-20240307"},
                    {"provider": "anthropic", "name": "claude-haiku-4-5-20251001"}
                ]
            }
        }

    def run_command(self, command: List[str], description: str) -> bool:
        """Run a command and return success status."""
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(command)}")
        print('='*60)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )

            if result.returncode != 0:
                print(f"❌ Error: {result.stderr}")
                return False

            print(f"✅ Success: {description}")
            if result.stdout:
                print(f"Output:\n{result.stdout[:500]}...")  # Show first 500 chars
            return True

        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

    def phase1_data_collection(self) -> bool:
        """Execute Phase 1: Data Collection."""
        print("\n" + "="*80)
        print("PHASE 1: DATA COLLECTION")
        print("="*80)

        config = self.config["data_collection"]

        # Step 1: Search repositories
        search_output = self.data_dir / "searched_repos.json"
        if not self.run_command([
            "python", "scripts/data_collection/search_repos.py",
            "--query", config["search_query"],
            "--max-repos", str(config["max_repos"]),
            "--min-stars", str(config["min_stars"]),
            "--output", str(search_output)
        ], "Searching GitHub repositories"):
            return False

        # Step 2: Mine repositories
        mined_output = self.data_dir / "mined_repos.json"
        if not self.run_command([
            "python", "scripts/data_collection/mine_repos.py",
            "--input", str(search_output),
            "--output", str(mined_output),
            "--clone-dir", str(self.data_dir / "cloned_repos")
        ], "Mining repositories"):
            return False

        # Step 3: Extract patterns
        patterns_output = self.data_dir / "patterns.json"
        if not self.run_command([
            "python", "scripts/data_collection/extract_patterns.py",
            "--input", str(mined_output),
            "--output", str(patterns_output)
        ], "Extracting patterns"):
            return False

        print("\n✅ Phase 1 complete: Data collection finished")
        return True

    def phase2_sample_generation(self) -> bool:
        """Execute Phase 2: Sample Generation."""
        print("\n" + "="*80)
        print("PHASE 2: SAMPLE GENERATION")
        print("="*80)

        patterns_file = self.data_dir / "patterns.json"
        repos_file = self.data_dir / "mined_repos.json"

        # Check if required files exist
        if not patterns_file.exists() or not repos_file.exists():
            print("❌ Error: Required data files not found. Run data collection first.")
            return False

        # Build samples
        if not self.run_command([
            "python", "scripts/sample_generation/build_samples.py",
            "--patterns", str(patterns_file),
            "--repos", str(repos_file),
            "--output", str(self.samples_dir)
        ], "Building SDK-Bench samples"):
            return False

        print("\n✅ Phase 2 complete: Sample generation finished")
        return True

    def phase3_evaluation(self) -> bool:
        """Execute Phase 3: Evaluation."""
        print("\n" + "="*80)
        print("PHASE 3: EVALUATION")
        print("="*80)

        models = self.config["evaluation"]["models"]

        # Check if samples exist
        sample_dirs = list(self.samples_dir.glob("task*"))
        if not sample_dirs:
            print("❌ Error: No samples found. Run sample generation first.")
            return False

        print(f"Found {len(sample_dirs)} samples to evaluate")

        # Generate solutions for each model
        for model_config in models:
            provider = model_config["provider"]
            model_name = model_config["name"]

            print(f"\n📊 Evaluating with {provider}/{model_name}")

            # Generate LLM solutions
            solutions_dir = self.results_dir / "llm_solutions"
            if not self.run_command([
                "python", "scripts/evaluation/llm_evaluate.py",
                "--provider", provider,
                "--model", model_name,
                "--samples", str(self.samples_dir),
                "--output", str(solutions_dir)
            ], f"Generating solutions with {model_name}"):
                print(f"⚠️  Warning: Failed to generate solutions for {model_name}")
                continue

            # Evaluate solutions
            for sample_dir in sample_dirs:
                sample_name = sample_dir.name
                solution_dir = solutions_dir / sample_name / model_name.replace(".", "-")

                if solution_dir.exists():
                    self.run_command([
                        "python", "scripts/evaluation/evaluate.py",
                        str(solution_dir),
                        "--metadata", str(sample_dir / "expected" / "metadata.json"),
                        "--output", str(self.results_dir),
                        "--detailed"
                    ], f"Evaluating {sample_name}/{model_name}")

        print("\n✅ Phase 3 complete: Evaluation finished")
        return True

    def generate_report(self) -> bool:
        """Generate final evaluation report."""
        print("\n" + "="*80)
        print("GENERATING FINAL REPORT")
        print("="*80)

        results_file = self.results_dir / "results.json"
        if not results_file.exists():
            # Aggregate all individual results
            all_results = []
            for result_file in self.results_dir.glob("*/evaluation_*.json"):
                with open(result_file) as f:
                    all_results.append(json.load(f))

            # Save aggregated results
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2)

        # Generate markdown report
        report_path = self.results_dir / "pipeline_report.md"
        self._create_markdown_report(report_path)

        print(f"\n📄 Report generated: {report_path}")
        return True

    def _create_markdown_report(self, output_path: Path):
        """Create markdown report of pipeline execution."""
        report = [
            "# SDK Bench Pipeline Execution Report",
            f"\nGenerated: {datetime.now().isoformat()}",
            "\n## Pipeline Configuration",
            f"```json\n{json.dumps(self.config, indent=2)}\n```",
            "\n## Execution Summary",
        ]

        # Add phase results
        phases = [
            ("Data Collection", self.data_dir),
            ("Sample Generation", self.samples_dir),
            ("Evaluation", self.results_dir)
        ]

        for phase_name, phase_dir in phases:
            if phase_dir.exists():
                file_count = len(list(phase_dir.glob("**/*")))
                report.append(f"\n### {phase_name}")
                report.append(f"- Output directory: `{phase_dir}`")
                report.append(f"- Files generated: {file_count}")

        # Add results summary if available
        results_file = self.results_dir / "results.json"
        if results_file.exists():
            with open(results_file) as f:
                results = json.load(f)

            report.append("\n## Evaluation Results Summary")
            report.append(f"- Total evaluations: {len(results)}")

            # Calculate average scores
            if results:
                avg_scores = {}
                for result in results:
                    if "scores" in result:
                        for metric, score in result["scores"].items():
                            if metric not in avg_scores:
                                avg_scores[metric] = []
                            if score is not None:
                                avg_scores[metric].append(score)

                report.append("\n### Average Scores by Metric")
                for metric, scores in avg_scores.items():
                    if scores:
                        avg = sum(scores) / len(scores)
                        report.append(f"- {metric}: {avg:.2f}%")

        # Write report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))

    def run_full_pipeline(self) -> bool:
        """Run the complete evaluation pipeline."""
        print("\n" + "🚀 " * 20)
        print("SDK BENCH FULL PIPELINE EXECUTION")
        print("🚀 " * 20)

        start_time = time.time()

        # Execute all phases
        success = (
            self.phase1_data_collection() and
            self.phase2_sample_generation() and
            self.phase3_evaluation() and
            self.generate_report()
        )

        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        print("\n" + "="*80)
        if success:
            print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        else:
            print("⚠️  PIPELINE COMPLETED WITH WARNINGS")
        print(f"Total time: {hours}h {minutes}m {seconds}s")
        print("="*80)

        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SDK Bench Evaluation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run complete pipeline (all phases)"
    )

    parser.add_argument(
        "--phase",
        choices=["data_collection", "sample_generation", "evaluation"],
        help="Run specific phase only"
    )

    parser.add_argument(
        "--skip-collection",
        action="store_true",
        help="Skip data collection (use existing data)"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file (JSON or YAML)"
    )

    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Base directory for SDK Bench"
    )

    args = parser.parse_args()

    # Load configuration if provided
    config = None
    if args.config and args.config.exists():
        with open(args.config) as f:
            if args.config.suffix == '.yaml':
                import yaml
                config = yaml.safe_load(f)
            else:
                config = json.load(f)

    # Initialize pipeline
    pipeline = SDKBenchPipeline(args.base_dir, config)

    # Execute based on arguments
    if args.full:
        pipeline.run_full_pipeline()
    elif args.phase == "data_collection":
        pipeline.phase1_data_collection()
    elif args.phase == "sample_generation":
        pipeline.phase2_sample_generation()
    elif args.phase == "evaluation":
        pipeline.phase3_evaluation()
    elif args.skip_collection:
        pipeline.phase2_sample_generation()
        pipeline.phase3_evaluation()
        pipeline.generate_report()
    else:
        print("Please specify --full, --phase, or --skip-collection")
        parser.print_help()


if __name__ == "__main__":
    main()