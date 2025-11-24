#!/usr/bin/env python3
"""
Week 1, Day 1-2: GitHub Repository Search Script

Searches GitHub for repositories using Clerk SDK and filters by quality criteria.
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


class ClerkRepoSearcher:
    """Search GitHub for Clerk repositories."""

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
        min_stars: int = 10,
        max_age_months: int = 12,
        language: str = None,
    ) -> List[Dict]:
        """
        Search GitHub repositories matching criteria.

        Args:
            query: Search query string
            min_stars: Minimum star count
            max_age_months: Maximum months since last commit (set to 0 to disable)
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
            # Use proper date: get current year first
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

            # Convert to list for parallel processing
            # If unlimited mode (max_repos >= 10000), get all results from this query
            # Otherwise, get up to 100 per query to avoid rate limits
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
                "id": f"repo_{index + 1:03d}",
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
            # Check common test directories/files
            test_indicators = [
                "test",
                "tests",
                "__tests__",
                "spec",
                "specs",
                ".test.",
                ".spec.",
                "jest.config",
                "vitest.config",
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
        """Run all Clerk search queries."""

        searches = [
            # Next.js queries (relaxed - Clerk is relatively new)
            {"query": '"@clerk/nextjs"', "language": "TypeScript", "min_stars": 5, "max_age_months": 0},
            {"query": '"@clerk/nextjs"', "language": "JavaScript", "min_stars": 3, "max_age_months": 0},
            # React queries
            {
                "query": '"@clerk/clerk-react"',
                "language": "TypeScript",
                "min_stars": 3,
                "max_age_months": 0,
            },
            {
                "query": '"@clerk/clerk-react"',
                "language": "JavaScript",
                "min_stars": 2,
                "max_age_months": 0,
            },
            # Express queries
            {
                "query": '"@clerk/express" OR "@clerk/clerk-sdk-node"',
                "language": "TypeScript",
                "min_stars": 2,
                "max_age_months": 0,
            },
            # Try without quotes for broader search
            {"query": "clerk nextjs", "language": "TypeScript", "min_stars": 10, "max_age_months": 0},
            # Try package.json search
            {"query": '"@clerk/nextjs" in:file filename:package.json', "language": None, "min_stars": 5, "max_age_months": 0},
        ]

        all_results = []
        seen_repos = set()

        target_text = f"{self.max_repos}" if self.max_repos < 10000 else "unlimited"
        print(f"\n📊 Target: {target_text} unique repositories")

        for i, search_config in enumerate(searches, 1):
            print(f"\n[Query {i}/{len(searches)}] Running search...")
            results = self.search_repositories(**search_config)

            # Deduplicate and add to results
            new_repos = 0
            for result in results:
                if result["full_name"] not in seen_repos:
                    seen_repos.add(result["full_name"])
                    all_results.append(result)
                    new_repos += 1

                    # Stop if we've reached the target (if limited)
                    if self.max_repos < 10000 and len(all_results) >= self.max_repos:
                        break

            if self.max_repos < 10000:
                print(f"   Added {new_repos} new repos (total: {len(all_results)}/{self.max_repos})")
            else:
                print(f"   Added {new_repos} new repos (total: {len(all_results)})")

            # Stop searching if we've reached the target (if limited)
            if self.max_repos < 10000 and len(all_results) >= self.max_repos:
                print(f"\n✅ Reached target of {self.max_repos} repositories!")
                break

        print(f"\n📦 Collected {len(all_results)} unique repositories")
        return all_results

    def classify_repositories(self, repos: List[Dict]) -> Dict:
        """Classify repositories by framework and suitability."""

        classification = {
            "nextjs": [],
            "express": [],
            "react_spa": [],
            "other": [],
            "v4_migration_candidates": [],
        }

        for repo in repos:
            # Detect framework from name, topics, or language
            name_lower = repo["name"].lower()
            description = (repo.get("description") or "").lower()
            topics = [t.lower() for t in repo.get("topics", [])]

            # Classification logic
            if (
                "nextjs" in topics
                or "next.js" in description
                or "next-" in name_lower
            ):
                classification["nextjs"].append(repo)
            elif "express" in topics or "express" in description:
                classification["express"].append(repo)
            elif "react" in topics and "next" not in topics:
                classification["react_spa"].append(repo)
            else:
                classification["other"].append(repo)

            # Check for v4 (migration candidates)
            if "@clerk/nextjs@4" in repo.get("search_query", ""):
                classification["v4_migration_candidates"].append(repo)

        return classification

    def save_results(self, repos: List[Dict], output_path: Path):
        """Save repository catalog to JSON."""

        # Classify repositories
        classified = self.classify_repositories(repos)

        # Create summary
        summary = {
            "total_repositories": len(repos),
            "by_framework": {
                "nextjs": len(classified["nextjs"]),
                "express": len(classified["express"]),
                "react_spa": len(classified["react_spa"]),
                "other": len(classified["other"]),
            },
            "v4_migration_candidates": len(classified["v4_migration_candidates"]),
            "collection_date": datetime.now().isoformat(),
            "avg_stars": sum(r["stars"] for r in repos) / len(repos) if repos else 0,
            "avg_contributors": (
                sum(r.get("contributors", 0) for r in repos) / len(repos)
                if repos
                else 0
            ),
            "with_tests": sum(1 for r in repos if r.get("has_tests")),
        }

        output_data = {
            "summary": summary,
            "repositories": repos,
            "classified": classified,
        }

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to JSON
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n✅ Saved {len(repos)} repositories to {output_path}")
        print(f"\n📊 Summary:")
        print(f"   Next.js: {summary['by_framework']['nextjs']}")
        print(f"   Express: {summary['by_framework']['express']}")
        print(f"   React SPA: {summary['by_framework']['react_spa']}")
        print(f"   Other: {summary['by_framework']['other']}")
        print(f"   v4 Migration: {summary['v4_migration_candidates']}")
        print(f"   With Tests: {summary['with_tests']}")
        print(f"   Avg Stars: {summary['avg_stars']:.1f}")


@click.command()
@click.option("--max-repos", default=None, type=int, help="Maximum repositories to collect (default: unlimited)")
@click.option("--output", default="data/repositories.json", help="Output file path")
@click.option("--workers", default=10, help="Number of concurrent workers for processing")
def main(max_repos: int, output: str, workers: int):
    """Search GitHub for Clerk repositories."""

    # Check for GitHub token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Error: GITHUB_TOKEN not found in environment")
        print("   Create a token at: https://github.com/settings/tokens")
        print("   Add it to .env file: GITHUB_TOKEN=your_token_here")
        return

    print("🚀 SDK-Bench: Clerk Repository Search")
    print(f"   Max repos: {max_repos if max_repos else 'unlimited'}")
    print(f"   Workers: {workers}")
    print(f"   Output: {output}")

    # Initialize searcher (use very high number if unlimited)
    actual_max = max_repos if max_repos else 10000
    searcher = ClerkRepoSearcher(token=token, max_repos=actual_max, n_workers=workers)

    # Run searches
    repos = searcher.run_all_searches()

    if not repos:
        print("❌ No repositories found")
        return

    # Save results
    output_path = Path(output)
    searcher.save_results(repos, output_path)

    print(f"\n✨ Done! Next step: python -m scripts.mine_repos")


if __name__ == "__main__":
    main()
