#!/usr/bin/env python3
"""
Week 1, Day 5: Pattern Extraction Script

Analyzes mined repositories to extract common Clerk integration patterns.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Set
from collections import Counter, defaultdict
from dotenv import load_dotenv
import click

load_dotenv()


class PatternExtractor:
    """Extract Clerk integration patterns from mined repositories."""

    def __init__(self):
        """Initialize pattern extractor."""
        self.patterns = {
            "initialization": [],
            "configuration": [],
            "middleware": [],
            "hooks": [],
            "api_protection": [],
            "error_handling": [],
        }

    def extract_imports(self, file_path: Path) -> List[str]:
        """Extract Clerk imports from a file."""
        imports = []
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Match import statements
                import_patterns = [
                    r"import\s+{([^}]+)}\s+from\s+['\"](@clerk/[^'\"]+)['\"]",
                    r"import\s+(\w+)\s+from\s+['\"](@clerk/[^'\"]+)['\"]",
                    r"require\(['\"](@clerk/[^'\"]+)['\"]\)",
                ]

                for pattern in import_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        imports.append(match.group(0))

        except Exception as e:
            pass

        return imports

    def extract_provider_usage(self, file_path: Path) -> Dict:
        """Extract ClerkProvider usage patterns."""
        pattern_data = {}
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Check for ClerkProvider
                if "ClerkProvider" in content:
                    pattern_data["has_provider"] = True

                    # Extract props
                    props_match = re.search(
                        r"<ClerkProvider([^>]*)>", content, re.DOTALL
                    )
                    if props_match:
                        props_text = props_match.group(1)
                        pattern_data["props"] = props_text.strip()

                        # Common props
                        if "publishableKey" in props_text:
                            pattern_data["has_publishable_key"] = True
                        if "appearance" in props_text:
                            pattern_data["has_appearance"] = True
                        if "afterSignInUrl" in props_text or "afterSignUpUrl" in props_text:
                            pattern_data["has_redirect_urls"] = True

        except:
            pass

        return pattern_data

    def extract_middleware_patterns(self, file_path: Path) -> Dict:
        """Extract middleware patterns."""
        pattern_data = {}
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Check for authMiddleware
                if "authMiddleware" in content:
                    pattern_data["type"] = "authMiddleware"

                    # Extract publicRoutes
                    public_routes_match = re.search(
                        r"publicRoutes:\s*\[(.*?)\]", content, re.DOTALL
                    )
                    if public_routes_match:
                        routes_text = public_routes_match.group(1)
                        routes = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)
                        pattern_data["public_routes"] = routes

                    # Extract ignoredRoutes
                    ignored_routes_match = re.search(
                        r"ignoredRoutes:\s*\[(.*?)\]", content, re.DOTALL
                    )
                    if ignored_routes_match:
                        routes_text = ignored_routes_match.group(1)
                        routes = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)
                        pattern_data["ignored_routes"] = routes

                # Check for ClerkExpressWithAuth
                if "ClerkExpressWithAuth" in content:
                    pattern_data["type"] = "express_middleware"

        except:
            pass

        return pattern_data

    def extract_hook_usage(self, file_path: Path) -> Dict:
        """Extract Clerk hook usage patterns."""
        hooks = {
            "useAuth": False,
            "useUser": False,
            "useClerk": False,
            "useSignIn": False,
            "useSignUp": False,
        }

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                for hook in hooks.keys():
                    if hook in content:
                        hooks[hook] = True

        except:
            pass

        return {k: v for k, v in hooks.items() if v}

    def extract_api_protection_patterns(self, file_path: Path) -> Dict:
        """Extract API route protection patterns."""
        pattern_data = {}
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

                # Check for auth() usage
                if re.search(r"const\s*{[^}]*userId[^}]*}\s*=\s*auth\(\)", content):
                    pattern_data["uses_auth_helper"] = True

                # Check for currentUser()
                if "currentUser()" in content:
                    pattern_data["uses_current_user"] = True

                # Check for requireAuth
                if "requireAuth" in content:
                    pattern_data["uses_require_auth"] = True

                # Check for getAuth
                if "getAuth(" in content:
                    pattern_data["uses_get_auth"] = True  # Likely v4

        except:
            pass

        return pattern_data

    def extract_env_variables(self, file_path: Path) -> List[str]:
        """Extract Clerk environment variables."""
        env_vars = set()
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.startswith("CLERK_") or line.startswith(
                        "NEXT_PUBLIC_CLERK_"
                    ):
                        var_name = line.split("=")[0].strip()
                        env_vars.add(var_name)

        except:
            pass

        return list(env_vars)

    def analyze_repository(self, repo_data: Dict, clone_dir: Path) -> Dict:
        """
        Analyze a single repository for patterns.

        Args:
            repo_data: Repository metadata with analysis
            clone_dir: Directory containing cloned repositories

        Returns:
            Dictionary of extracted patterns
        """
        repo_name = repo_data["full_name"].replace("/", "_")
        repo_path = clone_dir / repo_name

        if not repo_path.exists():
            return {}

        patterns = {
            "repo_id": repo_data["id"],
            "repo_name": repo_data["full_name"],
            "framework": repo_data.get("analysis", {}).get("framework", "unknown"),
            "clerk_version": repo_data.get("analysis", {}).get("clerk_version"),
            "imports": [],
            "provider_patterns": [],
            "middleware_patterns": [],
            "hook_usage": [],
            "api_protection": [],
            "env_vars": set(),
        }

        clerk_files = repo_data.get("analysis", {}).get("clerk_files", {})

        # Extract from layout files
        for file_rel_path in clerk_files.get("layout_files", []):
            file_path = repo_path / file_rel_path
            if file_path.exists():
                patterns["imports"].extend(self.extract_imports(file_path))
                provider_pattern = self.extract_provider_usage(file_path)
                if provider_pattern:
                    patterns["provider_patterns"].append(provider_pattern)

        # Extract from middleware files
        for file_rel_path in clerk_files.get("middleware_files", []):
            file_path = repo_path / file_rel_path
            if file_path.exists():
                patterns["imports"].extend(self.extract_imports(file_path))
                middleware_pattern = self.extract_middleware_patterns(file_path)
                if middleware_pattern:
                    patterns["middleware_patterns"].append(middleware_pattern)

        # Extract from component files
        for file_rel_path in clerk_files.get("component_files", [])[:10]:  # Limit
            file_path = repo_path / file_rel_path
            if file_path.exists():
                patterns["imports"].extend(self.extract_imports(file_path))
                hook_usage = self.extract_hook_usage(file_path)
                if hook_usage:
                    patterns["hook_usage"].append(hook_usage)

        # Extract from API routes
        for file_rel_path in clerk_files.get("api_routes", [])[:10]:  # Limit
            file_path = repo_path / file_rel_path
            if file_path.exists():
                patterns["imports"].extend(self.extract_imports(file_path))
                api_pattern = self.extract_api_protection_patterns(file_path)
                if api_pattern:
                    patterns["api_protection"].append(api_pattern)

        # Extract env vars
        for file_rel_path in clerk_files.get("config_files", []):
            file_path = repo_path / file_rel_path
            if file_path.exists():
                env_vars = self.extract_env_variables(file_path)
                patterns["env_vars"].update(env_vars)

        # Convert set to list for JSON serialization
        patterns["env_vars"] = list(patterns["env_vars"])

        return patterns

    def aggregate_patterns(self, all_patterns: List[Dict]) -> Dict:
        """
        Aggregate patterns across all repositories.

        Args:
            all_patterns: List of pattern dictionaries

        Returns:
            Aggregated pattern statistics
        """
        aggregated = {
            "total_repos_analyzed": len(all_patterns),
            "by_framework": Counter(),
            "clerk_versions": Counter(),
            "common_imports": Counter(),
            "provider_usage": {
                "total": 0,
                "with_publishable_key": 0,
                "with_appearance": 0,
                "with_redirect_urls": 0,
            },
            "middleware_usage": {"authMiddleware": 0, "express_middleware": 0},
            "common_hooks": Counter(),
            "api_protection_methods": Counter(),
            "common_env_vars": Counter(),
            "task_suitability": {
                "task1_init": [],  # Repos good for initialization samples
                "task2_middleware": [],  # Repos good for middleware samples
                "task3_hooks": [],  # Repos good for hooks samples
                "task4_complete": [],  # Repos good for complete integration
                "task5_migration": [],  # Repos using v4 (migration candidates)
            },
        }

        for pattern in all_patterns:
            # Count frameworks
            fw = pattern["framework"]
            aggregated["by_framework"][fw] += 1

            # Count versions
            version = pattern.get("clerk_version")
            if version:
                aggregated["clerk_versions"][version] += 1

                # Migration candidates (v4)
                if "^4." in version or "@4." in version:
                    aggregated["task_suitability"]["task5_migration"].append(
                        pattern["repo_name"]
                    )

            # Count imports
            for imp in pattern["imports"]:
                aggregated["common_imports"][imp] += 1

            # Provider patterns
            for provider in pattern["provider_patterns"]:
                aggregated["provider_usage"]["total"] += 1
                if provider.get("has_publishable_key"):
                    aggregated["provider_usage"]["with_publishable_key"] += 1
                if provider.get("has_appearance"):
                    aggregated["provider_usage"]["with_appearance"] += 1
                if provider.get("has_redirect_urls"):
                    aggregated["provider_usage"]["with_redirect_urls"] += 1

                # Good for Task 1 (initialization)
                aggregated["task_suitability"]["task1_init"].append(
                    pattern["repo_name"]
                )

            # Middleware patterns
            for middleware in pattern["middleware_patterns"]:
                mw_type = middleware.get("type", "unknown")
                aggregated["middleware_usage"][mw_type] += 1

                # Good for Task 2 (middleware)
                aggregated["task_suitability"]["task2_middleware"].append(
                    pattern["repo_name"]
                )

            # Hook usage
            for hooks in pattern["hook_usage"]:
                for hook, used in hooks.items():
                    if used:
                        aggregated["common_hooks"][hook] += 1

                # Good for Task 3 (hooks)
                if hooks:
                    aggregated["task_suitability"]["task3_hooks"].append(
                        pattern["repo_name"]
                    )

            # API protection
            for api in pattern["api_protection"]:
                for method, used in api.items():
                    if used:
                        aggregated["api_protection_methods"][method] += 1

            # Env vars
            for var in pattern["env_vars"]:
                aggregated["common_env_vars"][var] += 1

            # Complete integration (has multiple patterns)
            has_provider = len(pattern["provider_patterns"]) > 0
            has_middleware = len(pattern["middleware_patterns"]) > 0
            has_hooks = len(pattern["hook_usage"]) > 0
            has_api = len(pattern["api_protection"]) > 0

            if sum([has_provider, has_middleware, has_hooks, has_api]) >= 3:
                aggregated["task_suitability"]["task4_complete"].append(
                    pattern["repo_name"]
                )

        # Convert Counters to dicts for JSON serialization
        aggregated["by_framework"] = dict(aggregated["by_framework"].most_common())
        aggregated["clerk_versions"] = dict(aggregated["clerk_versions"].most_common())
        aggregated["common_imports"] = dict(
            aggregated["common_imports"].most_common(20)
        )
        aggregated["common_hooks"] = dict(aggregated["common_hooks"].most_common())
        aggregated["api_protection_methods"] = dict(
            aggregated["api_protection_methods"].most_common()
        )
        aggregated["common_env_vars"] = dict(aggregated["common_env_vars"].most_common())

        return aggregated

    def generate_patterns_markdown(self, aggregated: Dict) -> str:
        """Generate patterns documentation in Markdown."""
        md = ["# Clerk Integration Patterns\n", "## Overview\n"]

        md.append(f"Total repositories analyzed: {aggregated['total_repos_analyzed']}\n")
        md.append(f"Analysis date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}\n")

        md.append("\n## Frameworks\n")
        for fw, count in aggregated["by_framework"].items():
            md.append(f"- **{fw}**: {count} repositories\n")

        md.append("\n## Clerk Versions\n")
        for version, count in list(aggregated["clerk_versions"].items())[:10]:
            md.append(f"- `{version}`: {count} repositories\n")

        md.append("\n## Ingredient 1: Initialization Patterns\n")
        md.append(f"\n### Provider Usage\n")
        md.append(f"- Total repos with ClerkProvider: {aggregated['provider_usage']['total']}\n")
        md.append(f"- With publishableKey: {aggregated['provider_usage']['with_publishable_key']}\n")
        md.append(f"- With appearance config: {aggregated['provider_usage']['with_appearance']}\n")
        md.append(f"- With redirect URLs: {aggregated['provider_usage']['with_redirect_urls']}\n")

        md.append("\n### Common Imports\n")
        for imp, count in list(aggregated["common_imports"].items())[:10]:
            md.append(f"- `{imp}`: {count} repos\n")

        md.append("\n## Ingredient 2: Configuration Patterns\n")
        md.append("\n### Environment Variables\n")
        for var, count in list(aggregated["common_env_vars"].items())[:10]:
            md.append(f"- `{var}`: {count} repos\n")

        md.append("\n## Ingredient 3: Integration Points\n")
        md.append("\n### Middleware Usage\n")
        for mw_type, count in aggregated["middleware_usage"].items():
            md.append(f"- {mw_type}: {count} repos\n")

        md.append("\n### Hook Usage\n")
        for hook, count in aggregated["common_hooks"].items():
            md.append(f"- `{hook}()`: {count} repos\n")

        md.append("\n### API Protection Methods\n")
        for method, count in aggregated["api_protection_methods"].items():
            md.append(f"- {method}: {count} repos\n")

        md.append("\n## Task Suitability\n")
        for task, repos in aggregated["task_suitability"].items():
            md.append(f"\n### {task}\n")
            md.append(f"Found {len(repos)} suitable repositories\n")
            for repo in repos[:5]:
                md.append(f"- {repo}\n")
            if len(repos) > 5:
                md.append(f"- ... and {len(repos) - 5} more\n")

        return "".join(md)


@click.command()
@click.option(
    "--input", default="data/mined-repos.json", help="Input mined repositories file"
)
@click.option(
    "--clone-dir", default="data/cloned-repos", help="Directory with cloned repos"
)
@click.option(
    "--output-json",
    default="data/patterns.json",
    help="Output patterns JSON file",
)
@click.option(
    "--output-md", default="data/patterns.md", help="Output patterns Markdown file"
)
def main(input: str, clone_dir: str, output_json: str, output_md: str):
    """Extract Clerk integration patterns from mined repositories."""

    input_path = Path(input)
    if not input_path.exists():
        print(f"❌ Error: {input} not found")
        print(f"   Run: python -m scripts.mine_repos first")
        return

    # Load mined repositories
    with open(input_path) as f:
        repos = json.load(f)

    if not repos:
        print("❌ No repositories found in input file")
        return

    print("🚀 SDK-Bench: Pattern Extraction")
    print(f"   Input: {input}")
    print(f"   Analyzing {len(repos)} repositories...")

    # Extract patterns
    extractor = PatternExtractor()
    all_patterns = []

    for repo in tqdm(repos, desc="Extracting patterns"):
        patterns = extractor.analyze_repository(repo, Path(clone_dir))
        if patterns:
            all_patterns.append(patterns)

    # Aggregate patterns
    print("\n📊 Aggregating patterns...")
    aggregated = extractor.aggregate_patterns(all_patterns)

    # Save JSON
    output_json_path = Path(output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_json_path, "w") as f:
        json.dump(
            {"individual_patterns": all_patterns, "aggregated": aggregated},
            f,
            indent=2,
        )

    print(f"✅ Saved patterns JSON to {output_json_path}")

    # Generate and save Markdown
    md_content = extractor.generate_patterns_markdown(aggregated)
    output_md_path = Path(output_md)

    with open(output_md_path, "w") as f:
        f.write(md_content)

    print(f"✅ Saved patterns Markdown to {output_md_path}")

    print(f"\n📊 Summary:")
    print(f"   Total repos analyzed: {aggregated['total_repos_analyzed']}")
    print(f"   Frameworks: {dict(aggregated['by_framework'])}")
    print(f"   Task 1 (Init) candidates: {len(aggregated['task_suitability']['task1_init'])}")
    print(f"   Task 2 (Middleware) candidates: {len(aggregated['task_suitability']['task2_middleware'])}")
    print(f"   Task 3 (Hooks) candidates: {len(aggregated['task_suitability']['task3_hooks'])}")
    print(f"   Task 4 (Complete) candidates: {len(aggregated['task_suitability']['task4_complete'])}")
    print(f"   Task 5 (Migration) candidates: {len(aggregated['task_suitability']['task5_migration'])}")

    print(f"\n✨ Week 1 complete! Ready for Week 2: Dataset Construction")


if __name__ == "__main__":
    main()
