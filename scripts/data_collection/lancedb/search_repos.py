#!/usr/bin/env python3
"""
GitHub Repository Search Script for LanceDB

Searches GitHub for repositories using LanceDB vector database and filters by quality criteria.
Adapted from Clerk search script to follow the same POC process.
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from github import Github, GithubException
from tqdm import tqdm
import click

# Load environment variables
load_dotenv()


class LanceDBRepoSearcher:
    """Search GitHub for LanceDB repositories."""

    def __init__(self, token: str, max_repos: int = 100, n_workers: int = 10):
        """Initialize GitHub API client."""
        from github import Auth
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.max_repos = max_repos
        self.n_workers = n_workers
        self.results = []

    def search_repositories(
        self,
        query: str,
        min_stars: int = 2,
        max_age_months: int = 0,
        language: str = None,
    ) -> List[Dict]:
        """
        Search GitHub repositories matching criteria.

        Args:
            query: Search query string
            min_stars: Minimum star count
            max_age_months: Maximum months since last commit (0 to disable)
            language: Programming language filter

        Returns:
            List of repository metadata dictionaries
        """
        # Build search query
        search_parts = [query, f"stars:>={min_stars}"]

        if language:
            search_parts.append(f"language:{language}")

        # Filter by recent activity (optional - disable if max_age_months is 0)
        if max_age_months > 0:
            from datetime import date
            today = date.today()
            cutoff_date = today - timedelta(days=max_age_months * 30)
            search_parts.append(f"pushed:>={cutoff_date.strftime('%Y-%m-%d')}")

        search_query = " ".join(search_parts)

        print(f"\n🔍 Searching: {search_query}")

        try:
            repos = self.github.search_repositories(
                query=search_query, sort="stars", order="desc"
            )

            total = min(repos.totalCount, self.max_repos)
            print(f"Found {repos.totalCount} repositories (processing {total})")

            # Handle empty results
            if repos.totalCount == 0:
                print(f"⚠️  No repositories found for this query")
                return []

            # Get repositories based on limit
            if self.max_repos >= 10000:
                # Unlimited mode: get all repos from this query
                per_query_limit = repos.totalCount
            else:
                # Limited mode: get up to 100 per query
                per_query_limit = min(100, repos.totalCount)

            repo_list = list(repos[:per_query_limit])
            print(f"Processing {len(repo_list)} repos from this query...")

            # Process repositories in parallel
            results = []
            with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
                # Submit all tasks
                future_to_repo = {
                    executor.submit(
                        self._process_repository,
                        repo,
                        len(self.results) + i,
                        query
                    ): repo
                    for i, repo in enumerate(repo_list)
                }

                # Collect results with progress bar
                for future in tqdm(
                    as_completed(future_to_repo),
                    total=len(future_to_repo),
                    desc="Processing repos"
                ):
                    repo = future_to_repo[future]
                    try:
                        metadata = future.result()
                        if metadata:
                            results.append(metadata)
                    except Exception as e:
                        print(f"⚠️  Error processing {repo.full_name}: {e}")

            return results

        except GithubException as e:
            print(f"❌ Search failed: {e}")
            return []

    def _process_repository(self, repo, index: int, query: str) -> Optional[Dict]:
        """
        Process a single repository to extract metadata.

        Args:
            repo: GitHub repository object
            index: Repository index for ID generation
            query: Search query used to find this repo

        Returns:
            Repository metadata dictionary or None if processing failed
        """
        try:
            metadata = {
                "id": f"lancedb_repo_{index + 1:03d}",  # LanceDB prefix
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "description": repo.description,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "pushed_at": (
                    repo.pushed_at.isoformat() if repo.pushed_at else None
                ),
                "size_kb": repo.size,
                "default_branch": repo.default_branch,
                "topics": repo.get_topics(),
                "has_issues": repo.has_issues,
                "has_wiki": repo.has_wiki,
                "has_tests": self._check_has_tests(repo),
                "search_query": query,
                "collected_at": datetime.now().isoformat(),
                "sdk": "lancedb",  # Mark as LanceDB repository
            }

            # Try to get additional stats
            try:
                contributors = repo.get_contributors()
                metadata["contributors"] = contributors.totalCount
            except:
                metadata["contributors"] = 0

            return metadata

        except GithubException as e:
            print(f"⚠️  Error processing {repo.full_name}: {e}")
            return None

    def _check_has_tests(self, repo) -> bool:
        """Check if repository likely has tests."""
        try:
            # Check common Python test directories/files
            test_indicators = [
                "test",
                "tests",
                "test_",
                "_test.py",
                "pytest",
                "unittest",
                "conftest.py",
                "tox.ini",
                ".pytest",
            ]

            contents = repo.get_contents("")
            for content in contents:
                if any(
                    indicator in content.name.lower() for indicator in test_indicators
                ):
                    return True

            return False
        except:
            return False

    def run_all_searches(self) -> List[Dict]:
        """Run all LanceDB search queries."""

        searches = [
            # Direct package searches
            {"query": '"lancedb"', "language": "Python", "min_stars": 2, "max_age_months": 0},
            {"query": '"import lancedb"', "language": "Python", "min_stars": 1, "max_age_months": 0},
            {"query": '"from lancedb"', "language": "Python", "min_stars": 1, "max_age_months": 0},

            # Connection patterns
            {"query": '"lancedb.connect"', "language": "Python", "min_stars": 1, "max_age_months": 0},

            # Table operations
            {"query": '"create_table" lancedb', "language": "Python", "min_stars": 1, "max_age_months": 0},

            # Vector/embedding searches
            {"query": 'lancedb vector embeddings', "language": "Python", "min_stars": 2, "max_age_months": 0},
            {"query": 'lancedb RAG', "language": "Python", "min_stars": 2, "max_age_months": 0},

            # Requirements.txt search
            {"query": '"lancedb" in:file filename:requirements.txt', "language": None, "min_stars": 1, "max_age_months": 0},

            # Pyproject.toml search
            {"query": '"lancedb" in:file filename:pyproject.toml', "language": None, "min_stars": 1, "max_age_months": 0},

            # Broader searches for more results
            {"query": "lancedb", "language": "Python", "min_stars": 5, "max_age_months": 0},
        ]

        all_results = []
        seen_repos = set()

        target_text = f"{self.max_repos}" if self.max_repos < 10000 else "unlimited"
        print(f"\n📊 Target: {target_text} unique repositories")

        for i, search in enumerate(searches, 1):
            print(f"\n{'='*60}")
            print(f"Search {i}/{len(searches)}")
            print(f"{'='*60}")

            results = self.search_repositories(
                query=search["query"],
                min_stars=search["min_stars"],
                max_age_months=search["max_age_months"],
                language=search.get("language"),
            )

            # Deduplicate
            new_results = []
            for repo in results:
                if repo["full_name"] not in seen_repos:
                    seen_repos.add(repo["full_name"])
                    all_results.append(repo)
                    new_results.append(repo)

            print(f"✅ Added {len(new_results)} new unique repositories")
            print(f"📊 Total unique so far: {len(all_results)}")

            # Check if we've reached the target
            if self.max_repos < 10000 and len(all_results) >= self.max_repos:
                print(f"\n🎯 Reached target of {self.max_repos} repositories")
                break

            # Rate limiting between searches
            if i < len(searches):
                time.sleep(2)

        # Trim to max_repos if needed
        if self.max_repos < 10000 and len(all_results) > self.max_repos:
            all_results = all_results[:self.max_repos]

        self.results = all_results
        return all_results

    def save_results(self, output_dir: Path):
        """Save search results to JSON file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "repositories.json"

        with open(output_file, "w") as f:
            json.dump(
                {
                    "total": len(self.results),
                    "collected_at": datetime.now().isoformat(),
                    "sdk": "lancedb",
                    "repositories": self.results,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Saved {len(self.results)} repositories to {output_file}")

    def print_summary(self):
        """Print summary statistics."""
        if not self.results:
            print("\n⚠️  No repositories collected")
            return

        print(f"\n{'='*60}")
        print("📊 Summary Statistics")
        print(f"{'='*60}")
        print(f"Total repositories: {len(self.results)}")

        # Language distribution
        languages = {}
        for repo in self.results:
            lang = repo.get("language", "Unknown")
            languages[lang] = languages.get(lang, 0) + 1

        print("\nLanguage distribution:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {lang}: {count}")

        # Star distribution
        star_ranges = {"0-10": 0, "10-50": 0, "50-100": 0, "100+": 0}
        for repo in self.results:
            stars = repo.get("stars", 0)
            if stars < 10:
                star_ranges["0-10"] += 1
            elif stars < 50:
                star_ranges["10-50"] += 1
            elif stars < 100:
                star_ranges["50-100"] += 1
            else:
                star_ranges["100+"] += 1

        print("\nStar distribution:")
        for range_name, count in star_ranges.items():
            print(f"  - {range_name}: {count}")

        # Top 5 by stars
        top_repos = sorted(self.results, key=lambda x: x.get("stars", 0), reverse=True)[:5]
        print("\nTop 5 repositories by stars:")
        for repo in top_repos:
            print(f"  - {repo['full_name']}: {repo.get('stars', 0)} ⭐")


@click.command()
@click.option(
    "--max-repos",
    default=100,
    help="Maximum number of repositories to collect",
)
@click.option(
    "--output-dir",
    default="data/lancedb",
    help="Output directory for results",
)
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    help="GitHub API token (or set GITHUB_TOKEN env var)",
)
def main(max_repos: int, output_dir: str, token: str):
    """Search GitHub for LanceDB repositories."""
    if not token:
        print("❌ Error: GitHub token required")
        print("Set GITHUB_TOKEN environment variable or use --token option")
        return

    print(f"🚀 LanceDB Repository Search")
    print(f"{'='*60}")
    print(f"Max repositories: {max_repos}")
    print(f"Output directory: {output_dir}")

    # Create searcher and run searches
    searcher = LanceDBRepoSearcher(token, max_repos=max_repos)
    searcher.run_all_searches()

    # Save results
    searcher.save_results(Path(output_dir))

    # Print summary
    searcher.print_summary()

    print(f"\n✅ Search complete!")


if __name__ == "__main__":
    main()