# CLAUDE.md - SDKBench Project Guide

## Objective

SDKBench is a benchmark framework for evaluating LLM capabilities in SDK instrumentation tasks. The goal is to measure how well LLMs can generate correct, working code that integrates various SDKs (authentication, databases, APIs, etc.) based on documentation and task descriptions.

**Core Evaluation Question**: Given an SDK's documentation and a task description, can an LLM generate code that correctly initializes, configures, and uses the SDK?

---

## Quick Commands

```bash
# Run evaluation
python scripts/run.py --sdk lancedb --model claude-sonnet-4-5 --run-fcorr

# Run F-CORR only on existing solutions
python scripts/run_fcorr.py --sdk lancedb --verbose

# Compare SDK results
python scripts/compare_sdk_results.py

# Verify multi-SDK setup
python scripts/test_multi_sdk.py
```

---

## Key Documentation

| Topic | Location |
|-------|----------|
| **Adding new SDKs** | `docs/5-adding-sdks/adding-new-sdk.md` |
| **Multi-SDK guide** | `docs/4-multi-sdk/multi-sdk-guide.md` |
| **Metrics system** | `docs/revised-metrics.md` |
| **Architecture** | `docs/6-sdk-details/sdkbench-architecture.md` |
| **Metric flows** | `docs/6-sdk-details/metric-sequence-diagrams.md` |
| **Metric deep dives** | `docs/3-metrics-deep-dive/` |

---

## Adding a New SDK

Follow the 7-phase process in `docs/5-adding-sdks/adding-new-sdk.md`:

1. **Phase 0**: SDK Research - understand the SDK deeply
2. **Phase 1**: GitHub Discovery - find 50-100 real repos using the SDK
3. **Phase 2**: Repository Mining - clone and analyze repos
4. **Phase 3**: Pattern Extraction - document common usage patterns
5. **Phase 4**: Sample Generation - build 50 benchmark samples
6. **Phase 5**: Validation - QA review with Claude Code
7. **Phase 6**: Integration - wire up evaluation pipeline

### Sample Distribution (Fixed)

Each SDK must have **50 samples** distributed as:
- Task 1: 15 samples (Initialization)
- Task 2: 15 samples (Primary SDK operation)
- Task 3: 10 samples (Advanced feature)
- Task 4: 7 samples (Complete integration)
- Task 5: 3 samples (Migration)

### Directory Structure

```
SDKBench/
├── samples/{sdk_name}/
│   ├── {sdk}_task1_init_001/
│   │   ├── input/           # Incomplete code with TODOs
│   │   ├── expected/        # Complete solution + metadata.json
│   │   └── tests/           # Validation tests
│   └── {sdk}_dataset_manifest.json
├── scripts/data_collection/{sdk_name}/
│   ├── search_repos.py
│   ├── mine_repos.py
│   ├── extract_patterns.py
│   └── build_samples.py
└── data/{sdk_name}/
    ├── repositories.json
    ├── mined-repos.json
    ├── patterns.json
    └── cloned-repos/
```

---

## Evaluation Metrics

| Metric | Description | Weight (with F-CORR) |
|--------|-------------|---------------------|
| **I-ACC** | Initialization accuracy | 15% |
| **C-COMP** | Configuration completeness | 15% |
| **IPA** | Integration point accuracy (F1) | 15% |
| **F-CORR** | Functional correctness (tests) | 25% |
| **CQ** | Code quality | 15% |
| **SEM-SIM** | Semantic similarity | 15% |

F-CORR is the only **dynamic metric** (runs actual tests). All others are static analysis.

---

## Test Infrastructure Best Practices

### Critical: Test Behavior, Not Structure

Tests must accept **multiple valid implementations**. Never couple tests to specific code patterns.

**Bad** (fails for valid alternative implementations):
```python
def test_database():
    from expected import app
    assert app.db is not None  # Fails if solution uses get_database()
```

**Good** (accepts multiple patterns):
```python
def test_database():
    from expected import app
    assert has_db_connection(app)
    db = get_db_connection(app)  # Helper accepts db, get_db(), etc.
    assert db is not None
```

### Shared Test Utilities

For Python SDKs, create `samples/{sdk}/conftest.py` with flexible helpers:

```python
"""Shared test utilities for {SDK} samples."""

def get_db_connection(module):
    """Get database connection using various patterns."""
    # Module-level variable
    if hasattr(module, 'db') and module.db is not None:
        return module.db

    # Factory functions
    for func_name in ['get_database', 'get_db', 'connect']:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                try:
                    return func()
                except Exception:
                    continue
    return None

def has_db_connection(module):
    """Check if module has any database connection method."""
    if hasattr(module, 'db'):
        return True
    return any(hasattr(module, name) and callable(getattr(module, name))
               for name in ['get_database', 'get_db', 'connect'])
```

### Test Runner Configuration

The test harness auto-detects language and framework:

| Language | Framework | Detection |
|----------|-----------|-----------|
| Python | pytest | `requirements.txt`, `test_*.py` |
| TypeScript | Jest/Vitest/Mocha | `package.json`, `*.test.ts` |

Key files:
- `sdkbench/test_harness/registry.py` - auto-detection
- `sdkbench/test_harness/python_runner.py` - pytest execution
- `sdkbench/test_harness/typescript_runner.py` - JS/TS execution

### Excluded Directories

Test detection excludes these directories (defined in runners):
```python
EXCLUDED_DIRS = {"venv", ".venv", "node_modules", "__pycache__",
                 ".git", "dist", "build", ".pytest_cache"}
```

---

## Code Architecture

### Core Package (`sdkbench/`)

```
sdkbench/
├── core/           # Solution, GroundTruth, Result models
├── parsers/        # Python, TypeScript, Env, Config parsers
├── metrics/        # I-ACC, C-COMP, IPA, CQ, SEM-SIM, F-CORR evaluators
├── test_harness/   # Multi-language test runner (F-CORR only)
├── llm/            # Anthropic/OpenAI providers, prompt builder
└── evaluator/      # Main Evaluator orchestrating all metrics
```

### Key Classes

| Class | Location | Purpose |
|-------|----------|---------|
| `Solution` | `core/solution.py` | LLM-generated code to evaluate |
| `GroundTruth` | `core/ground_truth.py` | Expected patterns from metadata.json |
| `Evaluator` | `evaluator/evaluator.py` | Orchestrates all 6 metrics |
| `FCorrEvaluator` | `metrics/f_corr.py` | Runs tests via TestRunnerRegistry |
| `SolutionGenerator` | `llm/solution_generator.py` | LLM code generation |
| `PromptBuilder` | `llm/prompt_builder.py` | SDK-specific prompts |

---

## Common Bugs to Avoid

| Bug | Symptom | Prevention |
|-----|---------|------------|
| Module-level variable coupling | Tests fail for function-based implementations | Use flexible helper functions |
| venv in test detection | Thousands of test files detected | Filter EXCLUDED_DIRS |
| Missing model fields | AttributeError in evaluators | Audit Pydantic models vs usage |
| No stack traces in F-CORR | "1 test failed" with no details | Capture full failure_details |

---

## Environment Setup

```bash
# Required environment variables
ANTHROPIC_API_KEY=sk-ant-...     # For Claude models
OPENAI_API_KEY=sk-...            # For GPT models
GITHUB_TOKEN=ghp_...             # For repository mining
```

---

## Debugging Tips

```bash
# Test single sample
python scripts/run.py --sdk lancedb --model claude-sonnet-4-5 --limit 1

# Run F-CORR standalone with verbose output
python scripts/run_fcorr.py --sample samples/lancedb/lancedb_task1_init_001 --verbose

# Check test runner detection
python -c "
from sdkbench.test_harness.registry import TestRunnerRegistry
from pathlib import Path
runner = TestRunnerRegistry.get_runner(Path('samples/lancedb/lancedb_task1_init_001/expected'))
print(runner.detect())
"
```

---

## Reference Implementations

When adding new SDKs, study these existing implementations:

| SDK | Language | Key Files |
|-----|----------|-----------|
| **Clerk** | TypeScript | `scripts/data_collection/clerk/`, `samples/clerk/` |
| **LanceDB** | Python | `scripts/data_collection/lancedb/`, `samples/lancedb/` |

---

## Checklist for New SDK Integration

- [ ] Research complete (`docs/sdk-research/{sdk}.md`)
- [ ] 50+ repositories mined (`data/{sdk}/repositories.json`)
- [ ] Patterns documented (`data/{sdk}/patterns.md`)
- [ ] 50 samples generated (`samples/{sdk}/`)
- [ ] Dataset manifest created (`samples/{sdk}/{sdk}_dataset_manifest.json`)
- [ ] Shared test utilities (`samples/{sdk}/conftest.py` for Python)
- [ ] Tests are behavioral (not structural)
- [ ] Prompt context added (`sdkbench/llm/prompt_builder.py`)
- [ ] Dry run passes (`python scripts/run.py --sdk {sdk} --limit 1`)
- [ ] Full evaluation completes with reasonable metrics

---

## Notes

- F-CORR scoring is **strict**: any test failure = 0 score
- Static metrics (I-ACC, C-COMP, IPA, CQ, SEM-SIM) use pattern matching
- Results are saved per-sample in `metrics/` folders for detailed debugging
- The test harness supports Python (pytest) and TypeScript (Jest/Vitest/Mocha)
