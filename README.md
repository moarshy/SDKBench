# SDK-Bench: Clerk POC

A benchmark for evaluating LLM capabilities in SDK instrumentation, starting with Clerk authentication SDK.

## Project Structure

```
SDKBench/
├── scripts/           # Data collection and mining scripts
├── data/             # Collected repositories and patterns
├── samples/          # Benchmark samples (50 total)
├── evaluator/        # Evaluation pipeline
├── results/          # Evaluation results
├── reports/          # Analysis and visualizations
├── docs/             # Documentation
└── LogBench/         # Original LogBench dataset
```

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Create virtual environment and install dependencies

```bash
# Create venv and install all dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env and add your tokens
```

## Week 1: Data Collection (Current Phase)

Goal: Mine 50-100 Clerk repositories and extract integration patterns.

### Usage

```bash
# 1. Search GitHub for Clerk repositories
python -m scripts.search_repos --max-repos 100

# 2. Clone and analyze repositories
python -m scripts.mine_repos

# 3. Extract Clerk patterns
python -m scripts.extract_patterns
```

Or use the installed commands:

```bash
search-repos --max-repos 100
mine-repos
extract-patterns
```

## Progress Checklist

### Week 1: Data Collection
- [ ] Set up GitHub API access
- [ ] Search and collect 50-100 Clerk repositories
- [ ] Clone repositories locally
- [ ] Extract Clerk integration patterns
- [ ] Create `data/repositories.json` catalog
- [ ] Document findings in `data/patterns.md`

### Week 2: Dataset Construction
- [ ] Create 15 Task Type 1 samples (Initialization)
- [ ] Create 15 Task Type 2 samples (Middleware)
- [ ] Create 10 Task Type 3 samples (Hooks)
- [ ] Create 7 Task Type 4 samples (Complete Integration)
- [ ] Create 3 Task Type 5 samples (Migration)

### Week 3: Evaluation Pipeline
- [ ] Implement I-ACC metric
- [ ] Implement C-COMP metric
- [ ] Implement IPA metric
- [ ] Implement F-CORR metric
- [ ] Implement CQ metric
- [ ] Implement SEM-SIM metric

### Week 4: Baseline Evaluation
- [ ] Test Claude 3.5 Sonnet
- [ ] Test GPT-4 Turbo
- [ ] Test GPT-4o
- [ ] Analyze results
- [ ] Generate final report

## Development

```bash
# Run tests
pytest

# Format code
black .

# Lint code
ruff check .

# Type check
mypy scripts/
```

## References

- [Clerk POC Plan](docs/clerk-poc-plan.md)
- [SDK-Bench Methodology](docs/plan.md)
- [Ingredients vs Tasks](docs/ingredients-vs-tasks.md)

## License

MIT
