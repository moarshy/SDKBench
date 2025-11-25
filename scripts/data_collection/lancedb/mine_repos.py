#!/usr/bin/env python3
"""
Repository Mining Script for LanceDB

Clones repositories and extracts LanceDB usage patterns.
Adapted from Clerk mining script to follow the same POC process.
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


class LanceDBRepoMiner:
    """Clone and analyze LanceDB repositories."""

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

    def find_lancedb_files(self, repo_path: Path) -> Dict[str, List[Path]]:
        """
        Find files that use LanceDB.

        Args:
            repo_path: Path to cloned repository

        Returns:
            Dictionary of file types and their paths
        """
        lancedb_files = {
            "requirements_files": [],
            "connection_files": [],
            "table_files": [],
            "embedding_files": [],
            "search_files": [],
            "config_files": [],
            "notebook_files": [],
        }

        # Find requirements.txt and pyproject.toml
        for req_file in ["requirements.txt", "requirements*.txt", "pyproject.toml", "setup.py"]:
            for file in repo_path.rglob(req_file):
                if ".venv" in str(file) or "site-packages" in str(file):
                    continue
                try:
                    with open(file, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "lancedb" in content.lower():
                            lancedb_files["requirements_files"].append(file)
                except:
                    pass

        # Find Python files with LanceDB imports
        for file in repo_path.rglob("*.py"):
            if ".venv" in str(file) or "site-packages" in str(file):
                continue

            try:
                with open(file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    if "lancedb" not in content.lower():
                        continue

                    # Classify file type based on content
                    if "lancedb.connect" in content or "connect(" in content:
                        lancedb_files["connection_files"].append(file)

                    if "create_table" in content or "open_table" in content:
                        lancedb_files["table_files"].append(file)

                    if any(term in content.lower() for term in ["embedding", "encode", "transformer"]):
                        lancedb_files["embedding_files"].append(file)

                    if any(term in content for term in ["search", "query", "similarity"]):
                        lancedb_files["search_files"].append(file)

            except:
                pass

        # Find Jupyter notebooks
        for notebook in repo_path.rglob("*.ipynb"):
            if ".ipynb_checkpoints" in str(notebook):
                continue
            try:
                with open(notebook, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "lancedb" in content.lower():
                        lancedb_files["notebook_files"].append(notebook)
            except:
                pass

        # Find config files (.env, config.py, settings.py)
        for config_pattern in [".env*", "config*.py", "settings*.py", "*.yaml", "*.yml"]:
            for config_file in repo_path.rglob(config_pattern):
                if config_file.name == ".env":  # Skip actual .env files
                    continue
                try:
                    with open(config_file, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if any(term in content.lower() for term in ["lancedb", "vector", "embedding"]):
                            lancedb_files["config_files"].append(config_file)
                except:
                    pass

        return lancedb_files

    def extract_repo_metadata(self, repo_data: Dict, repo_path: Path) -> Dict:
        """
        Extract detailed metadata from repository.

        Args:
            repo_data: Original repository data
            repo_path: Path to cloned repository

        Returns:
            Enhanced metadata dictionary
        """
        lancedb_files = self.find_lancedb_files(repo_path)

        # Detect LanceDB version from requirements
        lancedb_version = None
        for req_path in lancedb_files["requirements_files"]:
            try:
                with open(req_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Look for lancedb version patterns
                    if "lancedb==" in content:
                        import re
                        match = re.search(r'lancedb==([0-9\.]+)', content)
                        if match:
                            lancedb_version = match.group(1)
                            break
            except:
                pass

        # Detect framework (e.g., FastAPI, Flask, Streamlit)
        framework = self._detect_framework(repo_path)

        # Count file types
        file_counts = {
            key: len(files) for key, files in lancedb_files.items()
        }

        # Extract use case patterns
        use_cases = []
        if lancedb_files["embedding_files"]:
            use_cases.append("embeddings")
        if lancedb_files["search_files"]:
            use_cases.append("vector_search")
        if any("rag" in str(f).lower() for f in lancedb_files["search_files"]):
            use_cases.append("rag")
        if lancedb_files["notebook_files"]:
            use_cases.append("notebooks")

        return {
            **repo_data,
            "lancedb_version": lancedb_version,
            "framework": framework,
            "file_counts": file_counts,
            "total_files": sum(file_counts.values()),
            "use_cases": use_cases,
            "has_embeddings": len(lancedb_files["embedding_files"]) > 0,
            "has_search": len(lancedb_files["search_files"]) > 0,
            "has_notebooks": len(lancedb_files["notebook_files"]) > 0,
        }

    def _detect_framework(self, repo_path: Path) -> Optional[str]:
        """Detect the framework used in the repository."""
        # Check for common Python frameworks
        indicators = {
            "fastapi": ["fastapi", "FastAPI"],
            "flask": ["flask", "Flask"],
            "streamlit": ["streamlit", "st."],
            "django": ["django", "Django"],
            "langchain": ["langchain", "LangChain"],
            "llamaindex": ["llama_index", "llama-index"],
        }

        for file in repo_path.rglob("*.py"):
            if ".venv" in str(file) or "site-packages" in str(file):
                continue

            try:
                with open(file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()[:5000]  # Check first 5000 chars

                    for framework, patterns in indicators.items():
                        if any(pattern in content for pattern in patterns):
                            return framework
            except:
                pass

        return None

    def mine_repositories(self, repos_file: Path, max_repos: int = 20) -> List[Dict]:
        """
        Mine multiple repositories.

        Args:
            repos_file: Path to repositories.json
            max_repos: Maximum number of repositories to mine

        Returns:
            List of enhanced repository metadata
        """
        # Load repositories
        with open(repos_file) as f:
            data = json.load(f)
            repos = data["repositories"][:max_repos]

        print(f"\n📊 Mining {len(repos)} repositories...")
        mined_data = []

        for repo in tqdm(repos, desc="Mining repositories"):
            repo_path = self.clone_repository(repo)
            if repo_path:
                metadata = self.extract_repo_metadata(repo, repo_path)
                mined_data.append(metadata)

        return mined_data

    def save_results(self, mined_data: List[Dict], output_file: Path):
        """Save mined repository data."""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(
                {
                    "total": len(mined_data),
                    "sdk": "lancedb",
                    "repositories": mined_data,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Saved mining results to {output_file}")

    def print_summary(self, mined_data: List[Dict]):
        """Print mining summary statistics."""
        print(f"\n{'='*60}")
        print("📊 Mining Summary")
        print(f"{'='*60}")
        print(f"Total repositories mined: {len(mined_data)}")

        # Framework distribution
        frameworks = {}
        for repo in mined_data:
            fw = repo.get("framework", "unknown")
            frameworks[fw] = frameworks.get(fw, 0) + 1

        print("\nFramework distribution:")
        for fw, count in sorted(frameworks.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {fw}: {count}")

        # Use case distribution
        use_case_counts = {}
        for repo in mined_data:
            for use_case in repo.get("use_cases", []):
                use_case_counts[use_case] = use_case_counts.get(use_case, 0) + 1

        print("\nUse case distribution:")
        for use_case, count in sorted(use_case_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {use_case}: {count}")

        # File statistics
        total_files = sum(repo.get("total_files", 0) for repo in mined_data)
        print(f"\nTotal LanceDB files found: {total_files}")

        # Top repositories by file count
        top_repos = sorted(mined_data, key=lambda x: x.get("total_files", 0), reverse=True)[:5]
        print("\nTop repositories by LanceDB file count:")
        for repo in top_repos:
            print(f"  - {repo['full_name']}: {repo.get('total_files', 0)} files")


@click.command()
@click.option(
    "--repos-file",
    default="data/lancedb/repositories.json",
    help="Path to repositories.json file",
)
@click.option(
    "--output-file",
    default="data/lancedb/mined-repos.json",
    help="Output file for mined data",
)
@click.option(
    "--clone-dir",
    default="data/lancedb/cloned-repos",
    help="Directory to clone repositories",
)
@click.option(
    "--max-repos",
    default=20,
    help="Maximum number of repositories to mine",
)
def main(repos_file: str, output_file: str, clone_dir: str, max_repos: int):
    """Mine LanceDB repositories for usage patterns."""
    print(f"🚀 LanceDB Repository Mining")
    print(f"{'='*60}")
    print(f"Repositories file: {repos_file}")
    print(f"Output file: {output_file}")
    print(f"Clone directory: {clone_dir}")
    print(f"Max repositories: {max_repos}")

    # Create miner and run mining
    miner = LanceDBRepoMiner(Path(clone_dir))
    mined_data = miner.mine_repositories(Path(repos_file), max_repos)

    # Save results
    miner.save_results(mined_data, Path(output_file))

    # Print summary
    miner.print_summary(mined_data)

    print(f"\n✅ Mining complete!")


if __name__ == "__main__":
    main()