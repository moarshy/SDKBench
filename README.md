# SDK-Bench

A benchmark for evaluating LLM capabilities in SDK instrumentation tasks across multiple SDKs.

## Supported SDKs

| SDK | Samples | Description |
|-----|---------|-------------|
| **Clerk** | 50 | Authentication & user management for web apps |
| **LanceDB** | 50 | Serverless vector database for AI applications |

## Quick Start

### Setup

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Configure API keys
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY and/or OPENAI_API_KEY
```

### Run Evaluation

```bash
# Interactive mode - prompts for SDK, model, and options
python scripts/run.py

# Flag mode - for scripting/CI
python scripts/run.py --sdk clerk,lancedb --model claude-sonnet-4-5 --workers 5

# Run specific SDK with sample limit
python scripts/run.py --sdk lancedb --model gpt-4o --limit 10

# Run with F-CORR (functional correctness testing)
python scripts/run.py --sdk lancedb --model claude-sonnet-4-5 --run-fcorr

# Quick evaluation without F-CORR (faster, static analysis only)
python scripts/run.py --sdk clerk --model claude-sonnet-4-5
```

### Available Models

| Model | Provider | ID |
|-------|----------|-----|
| `claude-sonnet-4-5` | Anthropic | Claude Sonnet 4.5 |
| `claude-3-5-sonnet` | Anthropic | Claude 3.5 Sonnet |
| `gpt-4o` | OpenAI | GPT-4o |
| `gpt-4o-mini` | OpenAI | GPT-4o Mini |

### CLI Options

```
--sdk           Comma-separated SDKs (clerk, lancedb, or 'all')
--model         Comma-separated models to evaluate
--workers       Number of parallel workers (default: 5)
--limit         Limit samples per SDK (for testing)
--skip-generation  Skip generation, evaluate existing solutions
--skip-evaluation  Skip evaluation, generate only
--run-fcorr     Run F-CORR functional correctness tests
--no-confirm    Skip confirmation prompt (for CI/scripting)
```

### F-CORR (Functional Correctness) Testing

F-CORR runs actual tests against generated solutions to verify functional correctness:

```bash
# Run evaluation with F-CORR enabled
python scripts/run.py --sdk lancedb --model claude-sonnet-4-5 --run-fcorr

# Run standalone F-CORR on a sample's expected solution
python scripts/run_fcorr.py --sample samples/lancedb/lancedb_task1_init_001

# Run F-CORR on all samples for an SDK
python scripts/run_fcorr.py --sdk lancedb --verbose
```

F-CORR supports multiple languages via auto-detection:
- **Python**: pytest (requires `requirements.txt` or `pyproject.toml`)
- **TypeScript/JavaScript**: Jest, Vitest, Mocha (via `package.json`)

Scoring is strict: any test failure results in F-CORR = 0%.

## Project Structure

```
SDKBench/
├── scripts/
│   ├── run.py              # Main CLI for running evaluations
│   ├── run_fcorr.py        # Standalone F-CORR evaluation
│   ├── compare_sdk_results.py  # Cross-SDK comparison reports
│   └── run_pipeline.py     # Data collection pipeline
├── samples/
│   ├── clerk/              # 50 Clerk SDK samples
│   └── lancedb/            # 50 LanceDB samples
├── sdkbench/
│   ├── llm/                # LLM providers (Anthropic, OpenAI)
│   ├── evaluator/          # Evaluation metrics
│   ├── test_harness/       # Multi-language test runner framework
│   │   ├── python_runner.py    # pytest support
│   │   ├── typescript_runner.py # Jest/Vitest/Mocha support
│   │   └── registry.py     # Auto-detection registry
│   └── core/               # Core utilities
├── results/                # Evaluation outputs
│   ├── {sdk}/{model}/
│   │   ├── solutions/      # Generated solutions with metrics/
│   │   └── *_summary.json  # Metrics summary
│   └── overall_report_*.json
└── docs/
    └── revised-metrics.md  # Detailed metrics documentation
```

## Evaluation Metrics

| Metric | Description | Weight |
|--------|-------------|--------|
| **I-ACC** | Instrumentation Accuracy - correct SDK usage patterns | 20% (15% with F-CORR) |
| **C-COMP** | Configuration Completeness - required config present | 20% (15% with F-CORR) |
| **IPA** | Integration Point Accuracy - correct integration points | 20% (15% with F-CORR) |
| **F-CORR** | Functional Correctness - code executes correctly | 25% (when enabled) |
| **CQ** | Code Quality - follows best practices | 20% (15% with F-CORR) |
| **SEM-SIM** | Semantic Similarity - matches expected output | 20% (15% with F-CORR) |
| **OVERALL** | Weighted average of all metrics | 100% |

### Overall Score & Grading

The overall score is a weighted average of individual metrics. When F-CORR is enabled, it receives 25% weight (emphasizing functional correctness), with other metrics at 15% each.

| Grade | Score Range |
|-------|-------------|
| A | >= 90 |
| B | >= 80 |
| C | >= 70 |
| D | >= 60 |
| F | < 60 |

### Per-Sample Metrics

Each evaluated solution includes a `metrics/` folder with detailed breakdowns:

```
results/{sdk}/{model}/solutions/{sample_id}/
├── app.py                    # Generated solution
├── generation_metadata.json
└── metrics/
    ├── i_acc.json            # Initialization accuracy details
    ├── c_comp.json           # Configuration completeness details
    ├── ipa.json              # Integration point accuracy (precision/recall/F1)
    ├── cq.json               # Code quality metrics
    ├── sem_sim.json          # Semantic similarity details
    ├── f_corr.json           # F-CORR results (if --run-fcorr)
    └── summary.json          # Overall score, grade, weights used
```

See [docs/revised-metrics.md](docs/revised-metrics.md) for detailed metric schemas.

## Task Types

Each SDK has 5 task types with varying complexity:

| Type | Clerk | LanceDB | Count |
|------|-------|---------|-------|
| 1 | Initialization | Initialization | 15 |
| 2 | Middleware Config | Data Operations | 15 |
| 3 | Hooks Integration | Search | 10 |
| 4 | Complete Integration | Pipeline Integration | 7 |
| 5 | Migration | Migration | 3 |

## Example Results

```
SDK: CLERK (50 samples)
Model: claude-sonnet-4-5
 Generation     50/50
 Evaluation     50/50
 I_ACC       100.000
 C_COMP       85.000
 IPA          95.000
 CQ          100.000
 SEM_SIM      72.500
 OVERALL      90.500   # Grade: A

SDK: LANCEDB (50 samples) [with --run-fcorr]
Model: claude-sonnet-4-5
 Generation     50/50
 Evaluation     50/50
 I_ACC       100.000
 C_COMP      100.000
 IPA         100.000
 CQ          100.000
 SEM_SIM      87.000
 F_CORR       80.000
 OVERALL      92.050   # Grade: A
```

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

## Adding New SDKs

1. Create samples in `samples/{sdk_name}/`
2. Add SDK context to `sdkbench/llm/prompt_builder.py`
3. Add version field mapping to `sdkbench/core/ground_truth.py`
4. Run evaluation: `python scripts/run.py --sdk {sdk_name}`

## License

MIT
