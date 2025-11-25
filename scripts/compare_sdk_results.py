#!/usr/bin/env python3
"""
Compare evaluation results across different SDKs.
Generates comparison reports and visualizations.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import statistics


class SDKComparisonAnalyzer:
    """Analyze and compare results across SDKs."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.results_dir = self.base_dir / "results"

    def load_sdk_results(self, sdk: str) -> Dict:
        """Load all results for a specific SDK."""
        sdk_dir = self.results_dir / sdk
        if not sdk_dir.exists():
            return {}

        results = {}
        for summary_file in sdk_dir.glob("*_summary.json"):
            model = summary_file.stem.replace("_summary", "")
            with open(summary_file) as f:
                results[model] = json.load(f)

        return results

    def generate_comparison_report(self):
        """Generate comprehensive comparison report."""
        # Find all SDKs
        sdks = [d.name for d in self.results_dir.iterdir()
                if d.is_dir() and not d.name.startswith('.')]

        if len(sdks) < 2:
            print("⚠️  Need at least 2 SDKs for comparison")
            return

        print("\n" + "="*80)
        print("SDK COMPARISON REPORT")
        print("="*80)
        print(f"SDKs analyzed: {', '.join(sdks)}")
        print(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
        print()

        # Load all results
        all_results = {}
        for sdk in sdks:
            all_results[sdk] = self.load_sdk_results(sdk)

        # Find common models
        all_models = set()
        for sdk_results in all_results.values():
            all_models.update(sdk_results.keys())

        if not all_models:
            print("❌ No evaluation results found")
            return

        # Compare by model
        for model in sorted(all_models):
            print(f"\n{'='*60}")
            print(f"MODEL: {model}")
            print(f"{'='*60}")

            model_data = []
            for sdk in sdks:
                if model in all_results[sdk]:
                    data = all_results[sdk][model]
                    model_data.append((sdk, data))

            if not model_data:
                print("No data available")
                continue

            # Display results table
            self._display_comparison_table(model_data)

        # Generate overall statistics
        print(f"\n{'='*60}")
        print("OVERALL STATISTICS")
        print(f"{'='*60}")
        self._display_overall_stats(all_results)

        # Save JSON report
        self._save_json_report(all_results)

    def _display_comparison_table(self, model_data: List[tuple]):
        """Display comparison table for a model."""
        # Header
        print(f"\n{'SDK':<15} {'Samples':<10} {'Success':<10} {'I-ACC':<8} {'C-COMP':<8} {'IPA':<8} {'F-CORR':<8} {'CQ':<8} {'SEM-SIM':<8}")
        print("-" * 90)

        # Rows
        for sdk, data in model_data:
            total = data.get("total_samples", 0)
            eval_data = data.get("evaluation", {})
            success = eval_data.get("success", 0)

            # Get metrics
            metrics = data.get("average_metrics", {})
            i_acc = metrics.get("i_acc", 0)
            c_comp = metrics.get("c_comp", 0)
            ipa = metrics.get("ipa", 0)
            f_corr = metrics.get("f_corr", 0)
            cq = metrics.get("cq", 0)
            sem_sim = metrics.get("sem_sim", 0)

            print(f"{sdk:<15} {total:<10} {success:<10} "
                  f"{i_acc:<8.3f} {c_comp:<8.3f} {ipa:<8.3f} "
                  f"{f_corr:<8.3f} {cq:<8.3f} {sem_sim:<8.3f}")

        # Calculate differences if exactly 2 SDKs
        if len(model_data) == 2:
            sdk1, data1 = model_data[0]
            sdk2, data2 = model_data[1]
            metrics1 = data1.get("average_metrics", {})
            metrics2 = data2.get("average_metrics", {})

            if metrics1 and metrics2:
                print("\n📊 Difference (SDK2 - SDK1):")
                for metric in ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]:
                    diff = metrics2.get(metric, 0) - metrics1.get(metric, 0)
                    sign = "+" if diff > 0 else ""
                    print(f"  {metric}: {sign}{diff:.3f}")

    def _display_overall_stats(self, all_results: Dict):
        """Display overall statistics across SDKs."""
        for sdk, sdk_results in all_results.items():
            if not sdk_results:
                continue

            print(f"\n📦 {sdk.upper()}")

            # Aggregate metrics across all models
            all_metrics = []
            total_samples = 0
            total_success = 0

            for model_data in sdk_results.values():
                if "average_metrics" in model_data:
                    all_metrics.append(model_data["average_metrics"])
                total_samples += model_data.get("total_samples", 0)
                total_success += model_data.get("evaluation", {}).get("success", 0)

            if all_metrics:
                # Calculate mean of means
                aggregated = {}
                for metric in ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]:
                    values = [m.get(metric, 0) for m in all_metrics if metric in m]
                    if values:
                        aggregated[metric] = statistics.mean(values)

                print(f"  Total samples evaluated: {total_samples}")
                print(f"  Total successful: {total_success}")
                print(f"  Success rate: {total_success/total_samples*100:.1f}%" if total_samples > 0 else "N/A")
                print(f"  Average metrics across all models:")
                for metric, value in aggregated.items():
                    print(f"    {metric}: {value:.3f}")

    def _save_json_report(self, all_results: Dict):
        """Save comparison report as JSON."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "sdks": list(all_results.keys()),
            "comparison": all_results,
            "summary": {}
        }

        # Add summary statistics
        for sdk, sdk_results in all_results.items():
            if sdk_results:
                all_metrics = []
                for model_data in sdk_results.values():
                    if "average_metrics" in model_data:
                        all_metrics.append(model_data["average_metrics"])

                if all_metrics:
                    aggregated = {}
                    for metric in ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]:
                        values = [m.get(metric, 0) for m in all_metrics if metric in m]
                        if values:
                            aggregated[metric] = statistics.mean(values)
                    report["summary"][sdk] = aggregated

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"sdk_comparison_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Comparison report saved to: {output_file}")

    def generate_markdown_report(self):
        """Generate markdown comparison report."""
        # Find all SDKs
        sdks = [d.name for d in self.results_dir.iterdir()
                if d.is_dir() and not d.name.startswith('.')]

        if len(sdks) < 2:
            return

        # Load all results
        all_results = {}
        for sdk in sdks:
            all_results[sdk] = self.load_sdk_results(sdk)

        # Create markdown content
        content = []
        content.append("# SDK Comparison Report")
        content.append(f"\n**Generated:** {datetime.now():%Y-%m-%d %H:%M:%S}")
        content.append(f"\n**SDKs:** {', '.join(sdks)}")

        # Add comparison tables
        content.append("\n## Model Performance Comparison")

        # Find common models
        all_models = set()
        for sdk_results in all_results.values():
            all_models.update(sdk_results.keys())

        for model in sorted(all_models):
            content.append(f"\n### {model}")
            content.append("\n| SDK | Samples | Success | I-ACC | C-COMP | IPA | F-CORR | CQ | SEM-SIM |")
            content.append("|-----|---------|---------|-------|--------|-----|--------|----|---------:|")

            for sdk in sdks:
                if model in all_results[sdk]:
                    data = all_results[sdk][model]
                    total = data.get("total_samples", 0)
                    success = data.get("evaluation", {}).get("success", 0)
                    metrics = data.get("average_metrics", {})

                    row = f"| {sdk} | {total} | {success} |"
                    for metric in ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]:
                        value = metrics.get(metric, 0)
                        row += f" {value:.3f} |"
                    content.append(row)

        # Add summary
        content.append("\n## Overall Statistics by SDK")

        for sdk in sdks:
            content.append(f"\n### {sdk.upper()}")
            sdk_results = all_results[sdk]

            if sdk_results:
                all_metrics = []
                total_samples = 0
                total_success = 0

                for model_data in sdk_results.values():
                    if "average_metrics" in model_data:
                        all_metrics.append(model_data["average_metrics"])
                    total_samples += model_data.get("total_samples", 0)
                    total_success += model_data.get("evaluation", {}).get("success", 0)

                content.append(f"- **Total samples:** {total_samples}")
                content.append(f"- **Successful evaluations:** {total_success}")

                if all_metrics:
                    content.append("\n**Average metrics across all models:**")
                    for metric in ["i_acc", "c_comp", "ipa", "f_corr", "cq", "sem_sim"]:
                        values = [m.get(metric, 0) for m in all_metrics if metric in m]
                        if values:
                            avg = statistics.mean(values)
                            content.append(f"- {metric.upper()}: {avg:.3f}")

        # Save markdown
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"sdk_comparison_{timestamp}.md"

        with open(output_file, 'w') as f:
            f.write('\n'.join(content))

        print(f"📝 Markdown report saved to: {output_file}")


def main():
    """Main entry point."""
    analyzer = SDKComparisonAnalyzer()

    print("🔍 Analyzing SDK evaluation results...")
    analyzer.generate_comparison_report()
    analyzer.generate_markdown_report()


if __name__ == "__main__":
    main()