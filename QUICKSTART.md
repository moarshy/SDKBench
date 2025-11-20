# SDK-Bench Quick Start Guide

## Setup (5 minutes)

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Configure API keys (IMPORTANT - Do this first!)

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your GitHub token
# Get one at: https://github.com/settings/tokens
# Required scope: public_repo (for public repos)
```

## Week 1: Data Collection

### Step 1: Search for Clerk repositories (Day 1-2)

```bash
# Use 'uv run' - it auto-creates venv and installs dependencies!
uv run python -m scripts.search_repos --max-repos 100
```

This will:
- Search GitHub for repositories using `@clerk/nextjs`, `@clerk/clerk-react`, etc.
- Filter by stars (>10), recent activity (<6 months)
- Classify by framework (Next.js, Express, React)
- Save results to `data/repositories.json`

**Output:** `data/repositories.json` with ~100 Clerk repositories

### Step 2: Clone and mine repositories (Day 3-4)

```bash
# Mine first 20 repos (for testing)
uv run python -m scripts.mine_repos --limit 20

# Or mine all
uv run python -m scripts.mine_repos
```

This will:
- Clone repositories to `data/cloned-repos/`
- Find all Clerk-related files
- Detect framework and Clerk version
- Save analysis to `data/mined-repos.json`

**Warning:** This can take 10-30 minutes and use ~2-5 GB disk space

### Step 3: Extract patterns (Day 5)

```bash
uv run python -m scripts.extract_patterns
```

This will:
- Analyze all cloned repositories
- Extract initialization, middleware, hooks, and API protection patterns
- Identify suitable repositories for each task type
- Generate `data/patterns.json` and `data/patterns.md`

## Expected Results

After completing Week 1, you should have:

```
data/
├── repositories.json       # ~100 Clerk repos metadata
├── mined-repos.json        # Detailed analysis of repos
├── patterns.json           # Extracted patterns (JSON)
├── patterns.md             # Patterns documentation
└── cloned-repos/           # ~2-5 GB of cloned repos
    ├── user_repo1/
    ├── user_repo2/
    └── ...
```

### Sample Output from patterns.md

```markdown
# Clerk Integration Patterns

## Overview
Total repositories analyzed: 87
Analysis date: 2025-01-20

## Frameworks
- **nextjs**: 52 repositories
- **react**: 23 repositories
- **express**: 8 repositories
- **other**: 4 repositories

## Task Suitability
### task1_init
Found 48 suitable repositories
- vercel/next.js-clerk-example
- ...

### task2_middleware
Found 35 suitable repositories
...
```

## Troubleshooting

### "GITHUB_TOKEN not found"
- Create a token at https://github.com/settings/tokens
- Add it to `.env`: `GITHUB_TOKEN=your_token_here`

### "Rate limit exceeded"
- GitHub API has rate limits (5,000 requests/hour for authenticated)
- Wait an hour or use `--limit` flag to process fewer repos

### "Failed to clone" errors
- Some repos may be private or deleted
- This is normal, script will continue with successful ones

### Disk space issues
- Use `--limit` flag to clone fewer repos
- Delete `data/cloned-repos/` after pattern extraction if needed

## Next Steps

After Week 1, proceed to:
- **Week 2:** Dataset Construction (create 50 benchmark samples)
- **Week 3:** Evaluation Pipeline (implement 6 metrics)
- **Week 4:** Baseline Evaluation (test LLMs)

See [docs/clerk-poc-plan.md](docs/clerk-poc-plan.md) for full plan.

## Development

```bash
# Run tests
pytest

# Format code
black scripts/

# Lint
ruff check scripts/

# Type check
mypy scripts/
```
