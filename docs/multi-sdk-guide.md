# Multi-SDK Evaluation Guide

## Overview

SDKBench now supports evaluation of multiple SDKs using a unified pipeline. The framework maintains the same 6 evaluation metrics (I-ACC, C-COMP, IPA, F-CORR, CQ, SEM-SIM) across all SDKs, enabling direct comparison of LLM performance across different SDK integration tasks.

## Current SDKs

1. **Clerk** - Authentication and user management (TypeScript/JavaScript)
2. **LanceDB** - Vector database for AI applications (Python)

## Directory Structure

```
SDKBench/
├── samples/
│   ├── clerk/           # 50 Clerk samples
│   │   ├── task1_init_001/
│   │   └── clerk_dataset_manifest.json
│   └── lancedb/         # 50 LanceDB samples
│       ├── lancedb_task1_init_001/
│       └── lancedb_dataset_manifest.json
├── scripts/
│   ├── run_evaluation_multi_sdk.py  # Multi-SDK evaluator
│   ├── compare_sdk_results.py       # SDK comparison tool
│   └── test_multi_sdk.py           # Setup verification
└── results/
    ├── clerk/           # Clerk-specific results
    ├── lancedb/         # LanceDB-specific results
    └── sdk_comparison_*.json/md  # Comparison reports
```

## Usage

### 1. Verify Multi-SDK Setup

Check that all SDKs are properly configured:

```bash
uv run python scripts/test_multi_sdk.py
```

Expected output:
```
✅ Found SDKs:
  📦 CLERK
     Samples: 50
  📦 LANCEDB
     Samples: 50
✅ Multi-SDK setup is ready!
```

### 2. Run Multi-SDK Evaluation

#### Evaluate All SDKs
```bash
uv run python scripts/run_evaluation_multi_sdk.py \
  --sdk all \
  --model claude-sonnet-4-5 \
  --n-workers 10
```

#### Evaluate Specific SDK
```bash
uv run python scripts/run_evaluation_multi_sdk.py \
  --sdk lancedb \
  --model gpt-5.1-2025-11-13 \
  --limit 10
```

#### Evaluate Multiple Models
```bash
uv run python scripts/run_evaluation_multi_sdk.py \
  --sdk all \
  --models "claude-sonnet-4-5,gpt-5.1-2025-11-13,gemini-2-pro" \
  --n-workers 5
```

### 3. Compare SDK Results

Generate comparison reports after evaluation:

```bash
uv run python scripts/compare_sdk_results.py
```

This generates:
- JSON comparison report: `results/sdk_comparison_*.json`
- Markdown report: `results/sdk_comparison_*.md`

## Command-Line Options

### run_evaluation_multi_sdk.py

| Option | Description | Example |
|--------|-------------|---------|
| `--sdk` | SDK to evaluate (clerk, lancedb, all) | `--sdk all` |
| `--model` | Single model to evaluate | `--model claude-sonnet-4-5` |
| `--models` | Multiple models (comma-separated) | `--models "model1,model2"` |
| `--limit` | Limit samples per SDK | `--limit 10` |
| `--n-workers` | Concurrent workers | `--n-workers 10` |
| `--skip-generation` | Skip code generation | `--skip-generation` |
| `--skip-evaluation` | Skip evaluation phase | `--skip-evaluation` |

## Adding New SDKs

### 1. GitHub Mining Pipeline

Create mining scripts in `scripts/data_collection/{sdk_name}/`:
- `search_repos.py` - Find repositories using the SDK
- `mine_repos.py` - Clone and analyze repositories
- `extract_patterns.py` - Extract usage patterns
- `build_samples.py` - Generate evaluation samples

### 2. Sample Structure

Each sample must have:
```
samples/{sdk_name}/{sdk_name}_task{type}_{category}_{number}/
├── input/            # Starter code with TODOs
├── expected/         # Reference solution
├── tests/            # Test cases (optional)
└── metadata.json     # Sample metadata
```

### 3. Manifest File

Create `{sdk_name}_dataset_manifest.json`:
```json
{
  "dataset_version": "1.0",
  "sdk": "sdk_name",
  "total_samples": 50,
  "by_task_type": {
    "1": 15,  // Initialization
    "2": 15,  // Data operations
    "3": 10,  // Search/queries
    "4": 7,   // Complete pipelines
    "5": 3    // Migrations
  }
}
```

## Evaluation Metrics

All SDKs are evaluated using the same 6 metrics:

1. **I-ACC** (Instruction Accuracy) - Following TODO instructions
2. **C-COMP** (Code Completeness) - Completing all required parts
3. **IPA** (Import Presence Analysis) - Correct imports/dependencies
4. **F-CORR** (Function Correctness) - Correct function implementations
5. **CQ** (Code Quality) - Code organization and best practices
6. **SEM-SIM** (Semantic Similarity) - Similarity to expected solution

## Sample Distribution

Each SDK should have 50-60 samples distributed across 5 task types:

| Task Type | Count | Description | Clerk Example | LanceDB Example |
|-----------|-------|-------------|---------------|-----------------|
| 1 | 15 | Initialization | Auth setup | DB connection |
| 2 | 15 | Data Operations | Middleware | Table operations |
| 3 | 10 | Search/Query | Hooks | Vector search |
| 4 | 7 | Complete Pipeline | Full auth flow | RAG pipeline |
| 5 | 3 | Migration | Version upgrade | Schema migration |

## Best Practices

1. **Sample Generation**: Base samples on real-world usage patterns from GitHub
2. **Consistency**: Maintain identical structure across all SDKs
3. **Testing**: Test with small subsets before full evaluation
4. **Documentation**: Include clear TODOs in input files
5. **Language Support**: Adapt metrics for different languages (TypeScript vs Python)

## Troubleshooting

### Missing SDK Samples
```bash
# Check sample location
ls -la samples/{sdk_name}/

# Verify manifest
cat samples/{sdk_name}/{sdk_name}_dataset_manifest.json
```

### Evaluation Failures
```bash
# Test with limited samples
uv run python scripts/run_evaluation_multi_sdk.py \
  --sdk {sdk_name} \
  --limit 1 \
  --model test
```

### Results Not Found
```bash
# Check results directory
ls -la results/{sdk_name}/

# View latest comparison
ls -lt results/sdk_comparison_* | head -1
```

## Next Steps

1. **Run full evaluations** with production models
2. **Analyze patterns** in SDK-specific performance
3. **Add more SDKs** following the established process
4. **Optimize prompts** based on SDK characteristics
5. **Create SDK-specific metrics** if needed (as extensions)

## Resources

- [Multi-SDK Plan](./multi-sdk-plan.md)
- [Progress Summary](./progress-summary.md)
- [Repository Structure](./repository-structure.md)
- [LanceDB Patterns](../data/lancedb/patterns.md)