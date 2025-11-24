#!/usr/bin/env python3
"""
Week 1, Day 3-4: Repository Mining Script

Clones repositories and extracts Clerk SDK usage patterns.
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
import git
from tqdm import tqdm
import click

load_dotenv()


class RepoMiner:
    """Clone and analyze Clerk repositories."""

    def __init__(self, clone_dir: Path):
        """Initialize repository miner."""
        self.clone_dir = Path(clone_dir)
        self.clone_dir.mkdir(parents=True, exist_ok=True)

    def clone_repository(self, repo_data: Dict) -> Optional[Path]:
        """
        Clone a single repository.

        Args:
            repo_data: Repository metadata dictionary

        Returns:
            Path to cloned repository or None if failed
        """
        repo_name = repo_data["full_name"].replace("/", "_")
        repo_path = self.clone_dir / repo_name

        # Skip if already cloned
        if repo_path.exists():
            print(f"  ⏭️  Already cloned: {repo_name}")
            return repo_path

        try:
            print(f"  📥 Cloning: {repo_data['full_name']}...")
            git.Repo.clone_from(
                repo_data["clone_url"], repo_path, depth=1  # Shallow clone
            )
            return repo_path
        except Exception as e:
            print(f"  ❌ Failed to clone {repo_data['full_name']}: {e}")
            return None

    def find_clerk_files(self, repo_path: Path) -> Dict[str, List[Path]]:
        """
        Find files that use Clerk SDK.

        Args:
            repo_path: Path to cloned repository

        Returns:
            Dictionary of file types and their paths
        """
        clerk_files = {
            "package_json": [],
            "layout_files": [],
            "middleware_files": [],
            "component_files": [],
            "api_routes": [],
            "config_files": [],
        }

        # Find package.json files
        for pkg in repo_path.rglob("package.json"):
            if "node_modules" in str(pkg):
                continue
            try:
                with open(pkg) as f:
                    content = f.read()
                    if "@clerk/" in content:
                        clerk_files["package_json"].append(pkg)
            except:
                pass

        # Find TypeScript/JavaScript files with Clerk imports
        for ext in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            for file in repo_path.rglob(ext):
                if "node_modules" in str(file) or ".next" in str(file):
                    continue

                try:
                    with open(file, encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                        if "@clerk/" not in content:
                            continue

                        # Classify file type
                        filename = file.name.lower()
                        if "layout" in filename:
                            clerk_files["layout_files"].append(file)
                        elif "middleware" in filename:
                            clerk_files["middleware_files"].append(file)
                        elif (
                            "api" in str(file)
                            or "route" in filename
                            or "handler" in filename
                        ):
                            clerk_files["api_routes"].append(file)
                        else:
                            clerk_files["component_files"].append(file)

                except:
                    pass

        # Find .env files
        for env_file in repo_path.rglob(".env*"):
            if env_file.name != ".env":  # Exclude actual .env files
                try:
                    with open(env_file, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "CLERK" in content:
                            clerk_files["config_files"].append(env_file)
                except:
                    pass

        return clerk_files

    def extract_repo_metadata(self, repo_data: Dict, repo_path: Path) -> Dict:
        """
        Extract detailed metadata from repository.

        Args:
            repo_data: Original repository data
            repo_path: Path to cloned repository

        Returns:
            Enhanced metadata dictionary
        """
        clerk_files = self.find_clerk_files(repo_path)

        # Detect Clerk version from package.json
        clerk_version = None
        for pkg_path in clerk_files["package_json"]:
            try:
                with open(pkg_path) as f:
                    pkg_data = json.load(f)
                    deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}

                    for key in deps:
                        if "@clerk/" in key:
                            clerk_version = deps[key]
                            break

                    if clerk_version:
                        break
            except:
                pass

        # Detect framework
        framework = "unknown"
        if any("next.config" in str(f) for f in repo_path.rglob("*")):
            framework = "nextjs"
        elif any("express" in str(f).lower() for f in clerk_files["api_routes"]):
            framework = "express"
        elif clerk_files["component_files"]:
            framework = "react"

        metadata = {
            **repo_data,
            "analysis": {
                "clerk_version": clerk_version,
                "framework": framework,
                "file_counts": {k: len(v) for k, v in clerk_files.items()},
                "clerk_files": {
                    k: [str(f.relative_to(repo_path)) for f in v]
                    for k, v in clerk_files.items()
                },
                "analyzed_at": __import__("datetime").datetime.now().isoformat(),
            },
        }

        return metadata

    def mine_repositories(self, repositories: List[Dict], limit: Optional[int] = None) -> List[Dict]:
        """
        Clone and analyze all repositories.

        Args:
            repositories: List of repository metadata
            limit: Maximum number to process

        Returns:
            List of enhanced repository metadata
        """
        if limit:
            repositories = repositories[:limit]

        results = []

        print(f"\n⛏️  Mining {len(repositories)} repositories...")

        for repo_data in tqdm(repositories, desc="Mining repos"):
            # Clone repository
            repo_path = self.clone_repository(repo_data)

            if repo_path is None:
                results.append(
                    {**repo_data, "analysis": {"error": "Failed to clone"}}
                )
                continue

            # Extract metadata
            metadata = self.extract_repo_metadata(repo_data, repo_path)
            results.append(metadata)

        return results

    def save_results(self, results: List[Dict], output_path: Path):
        """Save mining results to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Saved mining results to {output_path}")

        # Print summary
        successful = [r for r in results if "error" not in r.get("analysis", {})]
        print(f"\n📊 Mining Summary:")
        print(f"   Total processed: {len(results)}")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(results) - len(successful)}")

        if successful:
            frameworks = {}
            for r in successful:
                fw = r["analysis"]["framework"]
                frameworks[fw] = frameworks.get(fw, 0) + 1

            print(f"\n   By Framework:")
            for fw, count in sorted(frameworks.items(), key=lambda x: -x[1]):
                print(f"     {fw}: {count}")


@click.command()
@click.option(
    "--input",
    default="data/repositories.json",
    help="Input repositories JSON file",
)
@click.option(
    "--output", default="data/mined-repos.json", help="Output mined data file"
)
@click.option("--limit", default=None, type=int, help="Limit number of repos to mine")
@click.option(
    "--clone-dir", default="data/cloned-repos", help="Directory to clone repos into"
)
def main(input: str, output: str, limit: Optional[int], clone_dir: str):
    """Mine Clerk repositories for integration patterns."""

    input_path = Path(input)
    if not input_path.exists():
        print(f"❌ Error: {input} not found")
        print(f"   Run: python -m scripts.search_repos first")
        return

    # Load repositories
    with open(input_path) as f:
        data = json.load(f)
        repositories = data.get("repositories", [])

    if not repositories:
        print("❌ No repositories found in input file")
        return

    print(f"🚀 SDK-Bench: Repository Mining")
    print(f"   Input: {input}")
    print(f"   Output: {output}")
    print(f"   Clone dir: {clone_dir}")
    print(f"   Limit: {limit or 'None (all)'}")

    # Mine repositories
    miner = RepoMiner(clone_dir=Path(clone_dir))
    results = miner.mine_repositories(repositories, limit=limit)

    # Save results
    output_path = Path(output)
    miner.save_results(results, output_path)

    print(f"\n✨ Done! Next step: python -m scripts.extract_patterns")


if __name__ == "__main__":
    main()
