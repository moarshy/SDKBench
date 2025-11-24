# SDK Bench Scripts Documentation

## Overview

This directory contains the complete evaluation pipeline for SDK Bench, organized into logical phases that reflect the data flow from repository collection to evaluation.

## Directory Structure

```
scripts/
├── data_collection/       # Phase 1: Data gathering from GitHub
│   ├── search_repos.py    # Find repositories using Clerk SDK
│   ├── mine_repos.py      # Clone and analyze repositories
│   └── extract_patterns.py # Extract integration patterns
│
├── sample_generation/     # Phase 2: Test case creation
│   └── build_samples.py   # Generate SDK-Bench samples
│
├── evaluation/            # Phase 3: Solution evaluation
│   ├── llm_evaluate.py    # Generate LLM solutions
│   └── evaluate.py        # Score generated solutions
│
├── utils/                 # Helper utilities (if needed)
│
└── run_pipeline.py        # Main orchestrator script
```

## Pipeline Workflow

### Phase 1: Data Collection (Week 1)

The data collection phase mines real-world repositories to understand how developers use the Clerk SDK:

1. **search_repos.py** - Search GitHub for repositories
   - Filters by stars, language, recent activity
   - Outputs: `data/searched_repos.json`

2. **mine_repos.py** - Clone and analyze repositories
   - Clones repositories locally
   - Extracts file structure and patterns
   - Outputs: `data/mined_repos.json`

3. **extract_patterns.py** - Pattern extraction
   - Analyzes code for common patterns
   - Identifies integration approaches
   - Outputs: `data/patterns.json`

### Phase 2: Sample Generation (Week 2)

Creates structured test cases from mined patterns:

1. **build_samples.py** - Construct benchmark samples
   - Creates 50 samples across 5 task types
   - Generates input/expected directories
   - Outputs: `samples/` directory structure

**Task Types:**
- Task 1: Initialization (15 samples)
- Task 2: Middleware Configuration (15 samples)
- Task 3: Hooks Integration (10 samples)
- Task 4: Complete Implementation (7 samples)
- Task 5: Migration (3 samples)

### Phase 3: Evaluation

Evaluates LLM-generated solutions against expected patterns:

1. **llm_evaluate.py** - Generate solutions
   - Runs LLMs on samples
   - Supports multiple providers (Anthropic, OpenAI)
   - Outputs: `results/llm_solutions/`

2. **evaluate.py** - Score solutions
   - Applies 6 evaluation metrics
   - Generates detailed reports
   - Outputs: `results/evaluation_report.json`

## Quick Start

### Running the Complete Pipeline

```bash
# Run entire pipeline
python scripts/run_pipeline.py --full

# Run specific phases
python scripts/run_pipeline.py --phase data_collection
python scripts/run_pipeline.py --phase sample_generation
python scripts/run_pipeline.py --phase evaluation
```

### Individual Script Usage

#### Data Collection
```bash
# Search for repositories
python scripts/data_collection/search_repos.py \
    --query "clerk nextjs" \
    --max-repos 100 \
    --min-stars 10

# Clone and mine repositories
python scripts/data_collection/mine_repos.py \
    --input data/searched_repos.json \
    --output data/mined_repos.json

# Extract patterns
python scripts/data_collection/extract_patterns.py \
    --input data/mined_repos.json \
    --output data/patterns.json
```

#### Sample Generation
```bash
# Build all samples
python scripts/sample_generation/build_samples.py \
    --patterns data/patterns.json \
    --repos data/mined_repos.json \
    --output samples/
```

#### Evaluation
```bash
# Generate LLM solutions
python scripts/evaluation/llm_evaluate.py \
    --provider anthropic \
    --model claude-3-haiku-20240307 \
    --samples samples/ \
    --output results/llm_solutions/

# Evaluate solutions
python scripts/evaluation/evaluate.py \
    samples/task1_init_001/expected \
    --output results/ \
    --detailed
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
GITHUB_TOKEN=your_github_token
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Optional settings
MAX_REPOS=100
MIN_STARS=10
CLONE_DIR=data/cloned_repos
```

### Pipeline Configuration

Edit `scripts/config.yaml` for pipeline settings:

```yaml
data_collection:
  max_repos: 100
  min_stars: 10
  languages: ["TypeScript", "JavaScript"]

sample_generation:
  task_counts:
    initialization: 15
    middleware: 15
    hooks: 10
    complete: 7
    migration: 3

evaluation:
  models:
    - provider: anthropic
      name: claude-3-haiku-20240307
    - provider: openai
      name: gpt-4-turbo
  metrics:
    - I-ACC
    - C-COMP
    - IPA
    - F-CORR
    - CQ
    - SEM-SIM
```

## Evaluation Metrics

The evaluation phase uses 6 metrics to score solutions:

| Metric | Full Name | Score Type | Description |
|--------|-----------|------------|-------------|
| **I-ACC** | Initialization Accuracy | 0-100% | Validates SDK initialization patterns |
| **C-COMP** | Configuration Completeness | 0-100% | Checks env vars, deps, middleware |
| **IPA** | Integration Point Accuracy | P/R/F1 | Measures API endpoint coverage |
| **F-CORR** | Functional Correctness | 0-100% | Tests build/runtime behavior |
| **CQ** | Code Quality | 0-100 | Deducts for quality issues |
| **SEM-SIM** | Semantic Similarity | 0-100% | Compares to expected patterns |

## Output Structure

```
SDKBench/
├── data/                    # Raw data from collection
│   ├── searched_repos.json
│   ├── mined_repos.json
│   └── patterns.json
│
├── samples/                 # Generated test cases
│   ├── task1_init_001/
│   │   ├── input/
│   │   └── expected/
│   └── ...
│
└── results/                 # Evaluation results
    ├── llm_solutions/
    │   ├── task1_init_001/
    │   │   ├── claude-3-haiku/
    │   │   └── gpt-4-turbo/
    │   └── ...
    ├── evaluation_report.json
    └── results-analysis.md
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the project root when running scripts
   - Use `uv run` or activate the virtual environment

2. **API Rate Limits**
   - GitHub: Use authentication token
   - LLM APIs: Implement retry logic with backoff

3. **Memory Issues**
   - Use `--batch-size` flag for large datasets
   - Process repositories in chunks

### Debug Mode

Enable verbose logging:
```bash
python scripts/run_pipeline.py --debug --verbose
```

## Development

### Adding New Metrics

1. Create metric class in `sdkbench/metrics/`
2. Implement `evaluate()` method
3. Add to evaluator configuration

### Adding New LLM Providers

1. Create provider class in `sdkbench/llm/`
2. Implement `generate()` method
3. Register in `llm_evaluate.py`

## Performance Considerations

- **Parallel Processing**: Scripts use ThreadPoolExecutor for concurrent operations
- **Caching**: Repository clones are cached to avoid re-downloading
- **Batching**: Large datasets are processed in batches to manage memory

## Related Documentation

- [SDK Bench Overview](../README.md)
- [Metrics Documentation](../docs/metrics.md)
- [Sample Structure](../docs/samples.md)
- [Evaluation Results](../results-analysis.md)