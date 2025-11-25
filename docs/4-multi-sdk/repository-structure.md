# SDKBench Repository Structure - Multi-SDK Organization

## Complete Directory Structure

```
SDKBench/
├── README.md                              # Main documentation
├── pyproject.toml                         # Project dependencies
├── requirements.txt                       # Python requirements
├── .env.example                          # Environment variables template
│
├── docs/                                  # Documentation
│   ├── multi-sdk-plan.md                # Multi-SDK extension plan
│   ├── repository-structure.md          # This file
│   ├── evaluation-metrics.md            # Metrics documentation
│   └── lancedb/
│       └── lancedb-plan.md             # LanceDB-specific planning
│
├── data/                                  # Mined data from GitHub
│   ├── clerk/                           # Clerk-specific data
│   │   ├── repositories.json           # Found Clerk repositories
│   │   ├── mined-repos.json           # Analyzed Clerk repos
│   │   ├── patterns.json              # Extracted Clerk patterns
│   │   ├── patterns.md                # Human-readable patterns
│   │   └── cloned-repos/              # Cloned Clerk repositories
│   │       ├── repo_001/
│   │       ├── repo_002/
│   │       └── ...
│   │
│   └── lancedb/                         # LanceDB-specific data
│       ├── repositories.json           # Found LanceDB repositories
│       ├── mined-repos.json           # Analyzed LanceDB repos
│       ├── patterns.json              # Extracted LanceDB patterns
│       ├── patterns.md                # Human-readable patterns
│       └── cloned-repos/              # Cloned LanceDB repositories
│           ├── repo_001/
│           ├── repo_002/
│           └── ...
│
├── samples/                              # Evaluation samples
│   ├── dataset_manifest.json           # Overall dataset metadata
│   │
│   ├── clerk/                          # Clerk samples (existing, unchanged)
│   │   ├── task1_init_001/
│   │   │   ├── input/
│   │   │   │   ├── package.json
│   │   │   │   ├── app/
│   │   │   │   └── ...
│   │   │   ├── expected/
│   │   │   │   ├── metadata.json      # Ground truth
│   │   │   │   ├── package.json
│   │   │   │   ├── app/
│   │   │   │   └── ...
│   │   │   └── tests/
│   │   │       └── init.test.ts
│   │   ├── task1_init_002/
│   │   ├── ...
│   │   ├── task2_middleware_016/
│   │   ├── ...
│   │   ├── task3_hooks_031/
│   │   ├── ...
│   │   ├── task4_complete_041/
│   │   ├── ...
│   │   └── task5_migration_048/
│   │
│   └── lancedb/                        # LanceDB samples (new)
│       ├── task1_init_001/
│       │   ├── input/
│       │   │   ├── requirements.txt
│       │   │   ├── app.py
│       │   │   └── ...
│       │   ├── expected/
│       │   │   ├── metadata.json      # Ground truth
│       │   │   ├── requirements.txt
│       │   │   ├── app.py
│       │   │   └── ...
│       │   └── tests/
│       │       └── test_init.py
│       ├── task1_init_002/
│       ├── ...
│       ├── task2_operations_016/
│       ├── ...
│       ├── task3_search_031/
│       ├── ...
│       ├── task4_pipeline_041/
│       ├── ...
│       └── task5_migration_048/
│
├── scripts/                              # All scripts
│   ├── data_collection/                # GitHub mining scripts
│   │   ├── clerk/                     # Clerk-specific scripts
│   │   │   ├── search_repos.py       # Search for Clerk repos
│   │   │   ├── mine_repos.py         # Mine Clerk repos
│   │   │   ├── extract_patterns.py   # Extract Clerk patterns
│   │   │   └── build_samples.py      # Build Clerk samples
│   │   │
│   │   └── lancedb/                   # LanceDB-specific scripts
│   │       ├── search_repos.py       # Search for LanceDB repos
│   │       ├── mine_repos.py         # Mine LanceDB repos
│   │       ├── extract_patterns.py   # Extract LanceDB patterns
│   │       └── build_samples.py      # Build LanceDB samples
│   │
│   ├── evaluation/                     # Evaluation scripts
│   │   ├── __init__.py
│   │   ├── evaluate.py                # Main evaluation script (SDK-agnostic)
│   │   └── llm_evaluate.py           # LLM evaluation script
│   │
│   └── analysis/                       # Analysis scripts
│       ├── compare_sdks.py           # Compare performance across SDKs
│       └── generate_report.py        # Generate evaluation reports
│
├── sdkbench/                            # Core package
│   ├── __init__.py
│   │
│   ├── core/                          # Core components
│   │   ├── __init__.py
│   │   ├── solution.py               # Solution handler
│   │   ├── ground_truth.py           # Ground truth handler (SDK-aware)
│   │   ├── result.py                 # Result models
│   │   │
│   │   └── sdk/                      # SDK abstraction layer
│   │       ├── __init__.py
│   │       ├── base_sdk.py          # Abstract base SDK class
│   │       ├── registry.py          # SDK registry
│   │       ├── clerk_sdk.py         # Clerk SDK implementation
│   │       ├── clerk_config.json    # Clerk configuration
│   │       ├── lancedb_sdk.py       # LanceDB SDK implementation
│   │       └── lancedb_config.json  # LanceDB configuration
│   │
│   ├── evaluator/                    # Evaluation engine
│   │   ├── __init__.py
│   │   └── evaluator.py             # Main evaluator (SDK-aware)
│   │
│   ├── metrics/                      # Evaluation metrics (unchanged)
│   │   ├── __init__.py
│   │   ├── i_acc.py                 # Initialization accuracy
│   │   ├── c_comp.py                # Configuration completeness
│   │   ├── ipa.py                   # Integration points
│   │   ├── f_corr.py                # Functional correctness
│   │   ├── cq.py                    # Code quality
│   │   └── sem_sim.py               # Semantic similarity
│   │
│   ├── parsers/                      # Language parsers
│   │   ├── __init__.py
│   │   ├── typescript_parser.py     # TypeScript/JavaScript parser
│   │   └── python_parser.py         # Python parser (new)
│   │
│   └── llm/                          # LLM providers
│       ├── __init__.py
│       ├── base.py                  # Base LLM class
│       ├── openai_provider.py       # OpenAI provider
│       ├── anthropic_provider.py    # Anthropic provider
│       ├── prompt_builder.py        # Prompt builder (SDK-aware)
│       └── solution_generator.py    # Solution generator
│
├── results/                             # Evaluation results
│   ├── clerk/                         # Clerk evaluation results
│   │   ├── gpt-5.1-2025-11-13/
│   │   ├── claude-sonnet-4-5/
│   │   └── ...
│   │
│   ├── lancedb/                       # LanceDB evaluation results
│   │   ├── gpt-5.1-2025-11-13/
│   │   ├── claude-sonnet-4-5/
│   │   └── ...
│   │
│   └── comparisons/                   # Cross-SDK comparisons
│       ├── sdk_comparison.md
│       └── model_performance.json
│
└── tests/                              # Unit tests
    ├── __init__.py
    ├── test_clerk_samples.py         # Test Clerk samples
    ├── test_lancedb_samples.py       # Test LanceDB samples
    ├── test_evaluator.py             # Test evaluator
    ├── test_metrics.py               # Test metrics
    └── test_sdk_registry.py          # Test SDK registry
```

## Key Organization Principles

### 1. SDK Separation
- Each SDK has its own subdirectory in `data/`, `samples/`, and `scripts/data_collection/`
- Keeps SDK-specific code isolated
- Makes it easy to add new SDKs

### 2. Shared Core Components
- `sdkbench/core/` contains shared functionality
- `sdkbench/metrics/` remains unchanged (SDK-agnostic)
- `sdkbench/evaluator/` handles all SDKs

### 3. Backward Compatibility
- Existing Clerk files remain in their current locations
- New SDK-aware code reads SDK from metadata
- Default behavior assumes Clerk if SDK not specified

### 4. File Naming Conventions

#### Samples
```
{sdk}/task{number}_{name}_{id}/
```
Examples:
- `clerk/task1_init_001/`
- `lancedb/task1_init_001/`

#### Data Files
```
{sdk}/{type}.json
```
Examples:
- `clerk/repositories.json`
- `lancedb/patterns.json`

#### Scripts
```
{sdk}/{action}_repos.py
```
Examples:
- `clerk/search_repos.py`
- `lancedb/mine_repos.py`

## Migration Path

### Phase 1: Add New Structure (No Breaking Changes)
1. Create `data/clerk/` and copy existing data files
2. Create `data/lancedb/` for new LanceDB data
3. Create `scripts/data_collection/clerk/` and copy existing scripts
4. Create `scripts/data_collection/lancedb/` with adapted scripts
5. Create `sdkbench/core/sdk/` with abstraction layer

### Phase 2: Update Core Components
1. Update `ground_truth.py` to read SDK from metadata
2. Update `evaluator.py` to be SDK-aware
3. Add `python_parser.py` for Python code parsing
4. Update `prompt_builder.py` for SDK-specific prompts

### Phase 3: Generate LanceDB Samples
1. Run LanceDB mining scripts
2. Generate 50 LanceDB samples
3. Place in `samples/lancedb/`

### Phase 4: Validate
1. Run existing Clerk samples - must pass
2. Run new LanceDB samples
3. Compare results across SDKs

## Benefits of This Structure

1. **Scalability**: Easy to add new SDKs
2. **Clarity**: Clear separation between SDKs
3. **Maintainability**: SDK-specific code is isolated
4. **Compatibility**: No breaking changes to existing code
5. **Flexibility**: Can run evaluations per-SDK or across SDKs

## Future SDK Additions

To add a new SDK (e.g., Pinecone):
1. Create `data/pinecone/` directory
2. Create `scripts/data_collection/pinecone/` with adapted scripts
3. Create `samples/pinecone/` for samples
4. Add `pinecone_sdk.py` to `sdkbench/core/sdk/`
5. Run mining → pattern extraction → sample generation
6. Evaluate with existing metrics