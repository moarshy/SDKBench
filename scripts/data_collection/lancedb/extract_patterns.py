#!/usr/bin/env python3
"""
Pattern Extraction Script for LanceDB

Analyzes mined repositories to extract common LanceDB integration patterns.
Adapted from Clerk pattern extraction to follow the same POC process.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from collections import Counter, defaultdict
from dotenv import load_dotenv
from tqdm import tqdm
import click

load_dotenv()


class LanceDBPatternExtractor:
    """Extract LanceDB integration patterns from mined repositories."""

    def __init__(self):
        """Initialize pattern extractor."""
        self.patterns = {
            "imports": [],
            "connection": [],
            "table_operations": [],
            "embeddings": [],
            "search_operations": [],
            "schema_definitions": [],
            "error_handling": [],
            "configurations": [],
        }

    def extract_imports(self, file_path: Path) -> List[str]:
        """Extract LanceDB imports from a file."""
        imports = []
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Match import statements
                import_patterns = [
                    r"import\s+lancedb",
                    r"from\s+lancedb\s+import\s+[\w, ]+",
                    r"from\s+lancedb\.[\w\.]+\s+import\s+[\w, ]+",
                    r"import\s+lancedb\.[\w\.]+",
                ]

                for pattern in import_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        imports.append(match.group(0).strip())

        except Exception:
            pass

        return imports

    def extract_connection_patterns(self, file_path: Path) -> Dict:
        """Extract LanceDB connection patterns."""
        pattern_data = {}
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Connection patterns
                connection_patterns = [
                    (r"lancedb\.connect\s*\(\s*['\"]([^'\"]+)['\"]", "local_path"),
                    (r"lancedb\.connect\s*\(\s*([^)]+)\)", "connection_string"),
                    (r"db\s*=\s*lancedb\.connect", "assignment"),
                ]

                for pattern, pattern_type in connection_patterns:
                    matches = re.finditer(pattern, content, re.DOTALL)
                    for match in matches:
                        if pattern_type not in pattern_data:
                            pattern_data[pattern_type] = []
                        pattern_data[pattern_type].append(match.group(0).strip())

                # Check for environment variables
                if re.search(r"os\.(?:getenv|environ)", content) and "lancedb" in content.lower():
                    pattern_data["uses_env_vars"] = True

        except:
            pass

        return pattern_data

    def extract_table_operations(self, file_path: Path) -> Dict:
        """Extract table operation patterns."""
        pattern_data = {
            "create_table": [],
            "open_table": [],
            "add_operations": [],
            "schema_definitions": [],
        }

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Create table patterns
                create_patterns = re.finditer(
                    r"(create_table|createTable)\s*\([^)]+\)",
                    content,
                    re.DOTALL
                )
                for match in create_patterns:
                    pattern_data["create_table"].append(match.group(0)[:200])  # First 200 chars

                # Open table patterns
                open_patterns = re.finditer(
                    r"(open_table|openTable)\s*\([^)]+\)",
                    content,
                    re.DOTALL
                )
                for match in open_patterns:
                    pattern_data["open_table"].append(match.group(0)[:200])

                # Add/insert patterns
                add_patterns = re.finditer(
                    r"\.(add|insert|append)\s*\([^)]+\)",
                    content,
                    re.DOTALL
                )
                for match in add_patterns:
                    pattern_data["add_operations"].append(match.group(0)[:200])

                # Schema definitions (Pydantic models)
                if "LanceModel" in content or "class.*Vector" in content:
                    schema_patterns = re.finditer(
                        r"class\s+\w+.*(?:LanceModel|BaseModel).*?(?=class|\Z)",
                        content,
                        re.DOTALL
                    )
                    for match in schema_patterns:
                        pattern_data["schema_definitions"].append(match.group(0)[:300])

        except:
            pass

        return pattern_data

    def extract_embedding_patterns(self, file_path: Path) -> Dict:
        """Extract embedding-related patterns."""
        pattern_data = {
            "embedding_models": [],
            "embedding_functions": [],
            "vector_dimensions": [],
        }

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Common embedding models
                model_patterns = [
                    r"SentenceTransformer\s*\(\s*['\"]([^'\"]+)['\"]",
                    r"OpenAIEmbeddings\s*\(",
                    r"HuggingFaceEmbeddings\s*\(",
                    r"all-MiniLM-L6-v2",
                    r"text-embedding-ada-002",
                ]

                for pattern in model_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        pattern_data["embedding_models"].append(match.group(0))

                # Embedding function patterns
                embed_patterns = re.finditer(
                    r"(encode|embed|get_embedding|compute_embeddings?)\s*\([^)]+\)",
                    content
                )
                for match in embed_patterns:
                    pattern_data["embedding_functions"].append(match.group(0)[:100])

                # Vector dimensions
                dim_patterns = re.finditer(
                    r"(Vector|dimension|dim)\s*[=:]\s*(\d+)",
                    content,
                    re.IGNORECASE
                )
                for match in dim_patterns:
                    pattern_data["vector_dimensions"].append(int(match.group(2)))

        except:
            pass

        return pattern_data

    def extract_search_patterns(self, file_path: Path) -> Dict:
        """Extract search operation patterns."""
        pattern_data = {
            "search_methods": [],
            "limit_patterns": [],
            "filter_patterns": [],
            "metric_types": [],
        }

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Search method patterns
                search_patterns = re.finditer(
                    r"\.(search|query|vector_search|similarity_search)\s*\([^)]+\)",
                    content,
                    re.DOTALL
                )
                for match in search_patterns:
                    pattern_data["search_methods"].append(match.group(0)[:150])

                # Limit patterns
                limit_patterns = re.finditer(
                    r"\.(limit|top_k|k)\s*\(\s*(\d+)\s*\)",
                    content
                )
                for match in limit_patterns:
                    pattern_data["limit_patterns"].append(match.group(0))

                # Filter patterns
                filter_patterns = re.finditer(
                    r"\.(filter|where)\s*\([^)]+\)",
                    content
                )
                for match in filter_patterns:
                    pattern_data["filter_patterns"].append(match.group(0)[:100])

                # Distance metrics
                metrics = ["cosine", "euclidean", "l2", "dot", "manhattan"]
                for metric in metrics:
                    if metric in content.lower():
                        pattern_data["metric_types"].append(metric)

        except:
            pass

        return pattern_data

    def extract_error_handling(self, file_path: Path) -> Dict:
        """Extract error handling patterns."""
        pattern_data = {
            "has_try_except": False,
            "error_types": [],
            "retry_patterns": False,
        }

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Check for try-except blocks
                if re.search(r"try:\s*\n.*?except", content, re.DOTALL):
                    pattern_data["has_try_except"] = True

                # Common error types
                error_patterns = [
                    "TableNotFoundError",
                    "ConnectionError",
                    "ValueError",
                    "Exception",
                ]
                for error in error_patterns:
                    if error in content:
                        pattern_data["error_types"].append(error)

                # Retry patterns
                if "retry" in content.lower() or "attempt" in content.lower():
                    pattern_data["retry_patterns"] = True

        except:
            pass

        return pattern_data

    def analyze_repository(self, repo_path: Path) -> Dict:
        """Analyze all Python files in a repository."""
        repo_patterns = {
            "imports": Counter(),
            "connection_methods": [],
            "table_operations": defaultdict(list),
            "embedding_models": Counter(),
            "search_patterns": [],
            "error_handling": defaultdict(int),
        }

        # Find all Python files
        python_files = list(repo_path.rglob("*.py"))

        for file_path in python_files:
            if ".venv" in str(file_path) or "site-packages" in str(file_path):
                continue

            # Extract imports
            imports = self.extract_imports(file_path)
            for imp in imports:
                repo_patterns["imports"][imp] += 1

            # Extract connection patterns
            conn_patterns = self.extract_connection_patterns(file_path)
            if conn_patterns:
                repo_patterns["connection_methods"].append(conn_patterns)

            # Extract table operations
            table_ops = self.extract_table_operations(file_path)
            for op_type, ops in table_ops.items():
                if ops:
                    repo_patterns["table_operations"][op_type].extend(ops[:3])  # Keep top 3

            # Extract embeddings
            embed_patterns = self.extract_embedding_patterns(file_path)
            for model in embed_patterns.get("embedding_models", []):
                repo_patterns["embedding_models"][model] += 1

            # Extract search patterns
            search_patterns = self.extract_search_patterns(file_path)
            if search_patterns.get("search_methods"):
                repo_patterns["search_patterns"].extend(search_patterns["search_methods"][:3])

            # Extract error handling
            error_patterns = self.extract_error_handling(file_path)
            if error_patterns["has_try_except"]:
                repo_patterns["error_handling"]["try_except"] += 1

        return repo_patterns

    def analyze_all_repositories(self, clone_dir: Path, mined_repos_file: Path) -> Dict:
        """Analyze all cloned repositories."""
        # Load mined repos data
        with open(mined_repos_file) as f:
            mined_data = json.load(f)

        all_patterns = {
            "total_repos": len(mined_data["repositories"]),
            "import_patterns": Counter(),
            "connection_patterns": [],
            "table_patterns": defaultdict(list),
            "embedding_models": Counter(),
            "search_methods": [],
            "common_patterns": defaultdict(int),
            "task_suitability": defaultdict(list),
        }

        print(f"\n📊 Analyzing {len(mined_data['repositories'])} repositories...")

        for repo in tqdm(mined_data["repositories"], desc="Analyzing repos"):
            repo_name = repo["full_name"].replace("/", "_")
            repo_path = clone_dir / repo_name

            if not repo_path.exists():
                continue

            # Analyze repository
            repo_patterns = self.analyze_repository(repo_path)

            # Aggregate patterns
            all_patterns["import_patterns"].update(repo_patterns["imports"])
            all_patterns["connection_patterns"].extend(repo_patterns["connection_methods"][:2])

            for op_type, ops in repo_patterns["table_operations"].items():
                all_patterns["table_patterns"][op_type].extend(ops[:2])

            all_patterns["embedding_models"].update(repo_patterns["embedding_models"])
            all_patterns["search_methods"].extend(repo_patterns["search_patterns"][:2])

            # Determine task suitability
            if repo_patterns["connection_methods"]:
                all_patterns["task_suitability"]["initialization"].append(repo["name"])

            if repo_patterns["table_operations"]["create_table"] or repo_patterns["table_operations"]["add_operations"]:
                all_patterns["task_suitability"]["data_operations"].append(repo["name"])

            if repo_patterns["embedding_models"]:
                all_patterns["task_suitability"]["embeddings"].append(repo["name"])

            if repo_patterns["search_patterns"]:
                all_patterns["task_suitability"]["vector_search"].append(repo["name"])

            # Check for RAG patterns
            if (repo_patterns["embedding_models"] and
                repo_patterns["search_patterns"] and
                ("rag" in repo["name"].lower() or "retrieval" in str(repo_path).lower())):
                all_patterns["task_suitability"]["rag_pipeline"].append(repo["name"])

        return all_patterns

    def save_patterns(self, patterns: Dict, output_file: Path):
        """Save extracted patterns to JSON."""
        # Convert Counter objects to dict for JSON serialization
        patterns_json = {
            "total_repos": patterns["total_repos"],
            "import_patterns": dict(patterns["import_patterns"].most_common(20)),
            "connection_patterns": patterns["connection_patterns"][:10],
            "table_patterns": {k: v[:10] for k, v in patterns["table_patterns"].items()},
            "embedding_models": dict(patterns["embedding_models"].most_common(10)),
            "search_methods": patterns["search_methods"][:10],
            "task_suitability": dict(patterns["task_suitability"]),
        }

        with open(output_file, "w") as f:
            json.dump(patterns_json, f, indent=2)

        print(f"\n💾 Saved patterns to {output_file}")

    def generate_markdown_report(self, patterns: Dict, output_file: Path):
        """Generate a markdown report of patterns."""
        report = []
        report.append("# LanceDB Pattern Analysis Report\n")
        report.append(f"**Total Repositories Analyzed:** {patterns['total_repos']}\n")

        # Import patterns
        report.append("\n## Import Patterns\n")
        for imp, count in patterns["import_patterns"].most_common(10):
            report.append(f"- `{imp}` ({count} repos)\n")

        # Connection patterns
        report.append("\n## Connection Patterns\n")
        unique_connections = set()
        for conn in patterns["connection_patterns"]:
            if conn:
                for key, values in conn.items():
                    if isinstance(values, list):
                        for v in values[:2]:
                            unique_connections.add(v)
        for conn in list(unique_connections)[:5]:
            report.append(f"```python\n{conn}\n```\n")

        # Embedding models
        report.append("\n## Embedding Models\n")
        for model, count in patterns["embedding_models"].most_common(5):
            report.append(f"- `{model}` ({count} instances)\n")

        # Search methods
        report.append("\n## Search Methods\n")
        for method in patterns["search_methods"][:5]:
            report.append(f"```python\n{method}\n```\n")

        # Task suitability
        report.append("\n## Task Suitability\n")
        for task, repos in patterns["task_suitability"].items():
            report.append(f"\n### {task.replace('_', ' ').title()} ({len(repos)} repos)\n")
            for repo in repos[:3]:
                report.append(f"- {repo}\n")

        with open(output_file, "w") as f:
            f.write("".join(report))

        print(f"📝 Generated markdown report: {output_file}")


@click.command()
@click.option(
    "--mined-repos",
    default="data/lancedb/mined-repos.json",
    help="Path to mined repositories JSON",
)
@click.option(
    "--clone-dir",
    default="data/lancedb/cloned-repos",
    help="Directory with cloned repositories",
)
@click.option(
    "--output-json",
    default="data/lancedb/patterns.json",
    help="Output JSON file for patterns",
)
@click.option(
    "--output-md",
    default="data/lancedb/patterns.md",
    help="Output markdown report",
)
def main(mined_repos: str, clone_dir: str, output_json: str, output_md: str):
    """Extract LanceDB patterns from mined repositories."""
    print(f"🚀 LanceDB Pattern Extraction")
    print(f"{'='*60}")

    extractor = LanceDBPatternExtractor()

    # Analyze repositories
    patterns = extractor.analyze_all_repositories(
        Path(clone_dir),
        Path(mined_repos)
    )

    # Save patterns
    extractor.save_patterns(patterns, Path(output_json))

    # Generate report
    extractor.generate_markdown_report(patterns, Path(output_md))

    # Print summary
    print(f"\n{'='*60}")
    print("📊 Extraction Summary")
    print(f"{'='*60}")
    print(f"Import patterns found: {len(patterns['import_patterns'])}")
    print(f"Connection patterns: {len(patterns['connection_patterns'])}")
    print(f"Embedding models: {len(patterns['embedding_models'])}")
    print(f"Search methods: {len(patterns['search_methods'])}")

    print("\n✅ Pattern extraction complete!")


if __name__ == "__main__":
    main()