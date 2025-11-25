# Adding New SDKs to SDKBench

This guide documents the complete 7-phase process for integrating a new SDK into the SDKBench multi-SDK benchmark framework.

## Table of Contents

1. [Overview](#overview)
2. [Phase 0: SDK Research & Understanding](#phase-0-sdk-research--understanding)
3. [Phase 1: GitHub Repository Discovery](#phase-1-github-repository-discovery)
4. [Phase 2: Repository Mining & Cloning](#phase-2-repository-mining--cloning)
5. [Phase 3: Pattern Extraction & Analysis](#phase-3-pattern-extraction--analysis)
6. [Phase 4: Sample Generation](#phase-4-sample-generation)
7. [Phase 5: Sample Validation & QA](#phase-5-sample-validation--qa)
8. [Phase 6: Integration & Testing](#phase-6-integration--testing)
9. [Quick Reference](#quick-reference)

---

## Overview

SDKBench evaluates LLM capabilities in SDK instrumentation tasks. Each SDK in the benchmark:
- Has **50 samples** across **5 task types**
- Includes real-world patterns mined from GitHub repositories
- Is evaluated using **6 metrics** (I-ACC, C-COMP, IPA, F-CORR, CQ, SEM-SIM)

### Sample Distribution

Each SDK has **50 samples** distributed across **5 task types**. The count is fixed, but **task names are SDK-specific**:

| Task | Count | Description |
|------|-------|-------------|
| 1 | 15 | Initialization / Basic setup |
| 2 | 15 | Primary SDK operation (SDK-specific) |
| 3 | 10 | Advanced feature (SDK-specific) |
| 4 | 7 | Complete integration / Full pipeline |
| 5 | 3 | Migration (version upgrade) |

**Examples of SDK-specific task names:**

| SDK | Task 1 | Task 2 | Task 3 | Task 4 | Task 5 |
|-----|--------|--------|--------|--------|--------|
| **Clerk** (Auth) | init | middleware | hooks | complete | migration |
| **LanceDB** (Database) | init | data_ops | search | pipeline | migration |
| **Stripe** (Payments) | init | charges | webhooks | complete | migration |
| **OpenAI** (AI) | init | completions | streaming | pipeline | migration |

### Directory Structure After Completion

```
SDKBench/
├── data/{sdk_name}/
│   ├── repositories.json      # Phase 1: Found repos
│   ├── mined-repos.json       # Phase 2: Analyzed repos
│   ├── patterns.json          # Phase 3: Extracted patterns
│   ├── patterns.md            # Phase 3: Pattern documentation
│   └── cloned-repos/          # Phase 2: Cloned source code
├── samples/{sdk_name}/
│   ├── {sdk}_task1_init_001/
│   │   ├── input/             # Incomplete code with TODOs
│   │   ├── expected/          # Complete solution + metadata.json
│   │   └── tests/             # Validation tests
│   ├── ... (50 samples total)
│   └── {sdk}_dataset_manifest.json
├── scripts/data_collection/{sdk_name}/
│   ├── search_repos.py        # Phase 1 script
│   ├── mine_repos.py          # Phase 2 script
│   ├── extract_patterns.py    # Phase 3 script
│   └── build_samples.py       # Phase 4 script
└── docs/sdk-research/
    └── {sdk_name}.md          # Phase 0 research output
```

---

## Phase 0: SDK Research & Understanding

**Goal**: Gain deep understanding of the SDK before mining repositories.

**Time**: 2-4 hours

### Prerequisites

- Access to official SDK documentation
- Understanding of the SDK's primary use case
- Web search capability for research

### Steps

1. **Research the SDK** using web search and official docs
2. **Fill out the research template** (see `templates/sdk-research-template.md`)
3. **Define 5 task types** appropriate for the SDK
4. **Create search queries** for GitHub repository discovery

### Research Checklist

```markdown
### Basic Information
- [ ] Official documentation URL
- [ ] GitHub repository URL
- [ ] Package manager (npm, pip, cargo, etc.)
- [ ] Package name(s) for import
- [ ] Current stable version
- [ ] Supported languages/frameworks

### Core Concepts
- [ ] Primary use case (auth, database, AI, etc.)
- [ ] Key APIs/functions
- [ ] Initialization pattern
- [ ] Configuration requirements (env vars, config files)

### Integration Patterns
- [ ] Framework-specific integrations (Next.js, FastAPI, etc.)
- [ ] Common wrapper/provider patterns
- [ ] Middleware patterns (if applicable)
- [ ] Hook/utility patterns

### Version History
- [ ] Major version changes
- [ ] Breaking changes between versions
- [ ] Migration guides available
```

### Task Type Design by SDK Category

Task types should reflect the SDK's core functionality. Here are examples:

| SDK Category | Task 1 | Task 2 | Task 3 | Task 4 | Task 5 |
|--------------|--------|--------|--------|--------|--------|
| **Auth** (Clerk) | init | middleware | hooks | complete | migration |
| **Database** (LanceDB) | init | data_ops | search | pipeline | migration |
| **API Client** (Stripe) | init | charges | webhooks | complete | migration |
| **AI/ML** (OpenAI) | init | completions | streaming | pipeline | migration |
| **ORM** (Prisma) | init | queries | relations | complete | migration |
| **Storage** (Supabase) | init | crud | realtime | complete | migration |

**Guidelines for choosing task names:**
- **Task 1**: Always `init` - basic SDK setup
- **Task 2**: The most common SDK operation (e.g., `data_ops`, `middleware`, `charges`)
- **Task 3**: A secondary/advanced feature (e.g., `search`, `hooks`, `webhooks`)
- **Task 4**: Full integration combining Task 1-3 (e.g., `complete`, `pipeline`)
- **Task 5**: Always `migration` - version upgrade scenarios

### Output

Create `docs/sdk-research/{sdk_name}.md` with your research findings.

**Claude Code Prompt**: Use `prompts/phase0-research.prompt.md` for guided research.

---

## Phase 1: GitHub Repository Discovery

**Goal**: Find 50-100 real-world repositories using the SDK.

**Time**: 1-2 hours

### Prerequisites

- GitHub Personal Access Token (set as `GITHUB_TOKEN` env var)
- Phase 0 research completed with search queries

### Steps

1. **Create the search script** at `scripts/data_collection/{sdk_name}/search_repos.py`
2. **Adapt search queries** from the templates below
3. **Run the search** to collect repositories
4. **Review results** for quality and diversity

### Search Query Templates

**Python SDKs:**
```python
searches = [
    {"query": '"{package}"', "language": "Python", "min_stars": 2},
    {"query": '"import {package}"', "language": "Python", "min_stars": 1},
    {"query": '"from {package}"', "language": "Python", "min_stars": 1},
    {"query": '"{package}" in:file filename:requirements.txt', "min_stars": 1},
    {"query": '"{package}" in:file filename:pyproject.toml', "min_stars": 1},
]
```

**TypeScript/JavaScript SDKs:**
```python
searches = [
    {"query": '"@{org}/{package}"', "language": "TypeScript", "min_stars": 5},
    {"query": '"@{org}/{package}"', "language": "JavaScript", "min_stars": 3},
    {"query": '"@{org}/{package}" in:file filename:package.json', "min_stars": 3},
]
```

### Quality Filters

```python
QUALITY_FILTERS = {
    "min_stars": 2,          # Minimum quality threshold
    "max_age_months": 0,     # 0 = no limit, 12 = active repos only
    "has_tests": True,       # Prefer repos with tests
    "exclude_forks": True,   # Original repos only
}
```

### Run Command

```bash
cd SDKBench
uv run python scripts/data_collection/{sdk}/search_repos.py --max-repos 100
```

### Output

`data/{sdk_name}/repositories.json`:
```json
{
  "total": 100,
  "collected_at": "2025-01-20T...",
  "sdk": "{sdk_name}",
  "repositories": [
    {
      "id": "{sdk}_repo_001",
      "full_name": "owner/repo",
      "clone_url": "https://github.com/...",
      "stars": 50,
      "language": "Python",
      "topics": ["vector-db", "rag"],
      "sdk": "{sdk_name}"
    }
  ]
}
```

---

## Phase 2: Repository Mining & Cloning

**Goal**: Clone repositories and identify SDK usage patterns.

**Time**: 2-4 hours (depends on number of repos)

### Prerequisites

- Phase 1 completed with `repositories.json`
- Sufficient disk space for clones (~100MB-1GB per 20 repos)

### Steps

1. **Create the mining script** at `scripts/data_collection/{sdk_name}/mine_repos.py`
2. **Define file classification rules** for the SDK
3. **Run the mining script** to clone and analyze
4. **Review output** for pattern coverage

### File Classification Rules

Define how to identify and classify SDK-related files:

```python
FILE_CLASSIFICATION = {
    "init_files": {
        "patterns": ["Provider", "connect", "initialize", "setup"],
        "filenames": ["layout", "index", "main", "app", "__init__"],
    },
    "middleware_files": {
        "patterns": ["middleware", "Middleware"],
        "filenames": ["middleware"],
    },
    "integration_files": {
        "patterns": ["{sdk_function}", "{hook_pattern}"],
        "filenames": [],  # Any file with SDK usage
    },
    "config_files": {
        "patterns": ["{ENV_VAR_PREFIX}"],
        "filenames": [".env", "config"],
    },
}
```

### Run Command

```bash
uv run python scripts/data_collection/{sdk}/mine_repos.py --limit 20
```

### Output

`data/{sdk_name}/mined-repos.json`:
```json
[
  {
    "id": "{sdk}_repo_001",
    "full_name": "owner/repo",
    "analysis": {
      "{sdk}_version": "^1.0.0",
      "framework": "fastapi",
      "file_counts": {
        "init_files": 1,
        "integration_files": 5,
        "config_files": 1
      },
      "{sdk}_files": {
        "init_files": ["app/main.py"],
        "integration_files": ["app/services/db.py"]
      }
    }
  }
]
```

---

## Phase 3: Pattern Extraction & Analysis

**Goal**: Extract and document common SDK usage patterns.

**Time**: 4-8 hours (includes Claude Code analysis)

### Prerequisites

- Phase 2 completed with cloned repositories
- Access to Claude Code for pattern analysis

### Steps

1. **Create the extraction script** at `scripts/data_collection/{sdk_name}/extract_patterns.py`
2. **Run automated extraction** for basic patterns
3. **Use Claude Code** to analyze cloned repos for deeper insights
4. **Document patterns** in `patterns.md`

### Claude Code Analysis Session

Open the SDKBench project in Claude Code and use the prompt from `prompts/phase3-patterns.prompt.md`:

```
Analyze the cloned repositories in data/{sdk_name}/cloned-repos/ to:

1. **Initialization Patterns** - How is the SDK initialized?
2. **Configuration Patterns** - What env vars and config files are used?
3. **Core Operation Patterns** - What are the most common function calls?
4. **Advanced Feature Patterns** - Middleware, hooks, custom configs
5. **Framework-Specific Patterns** - Differences between frameworks

Output structured patterns.md with code examples and frequencies.
```

### Run Command

```bash
uv run python scripts/data_collection/{sdk}/extract_patterns.py
```

### Output

`data/{sdk_name}/patterns.md`:
```markdown
# {SDK_NAME} Integration Patterns

## Overview
Total repositories analyzed: 20
Analysis date: 2025-01-20

## Frameworks
- **fastapi**: 10 repositories
- **flask**: 5 repositories
- **streamlit**: 5 repositories

## {SDK} Versions
- `^1.0.0`: 15 repositories
- `^0.9.0`: 5 repositories

## Ingredient 1: Initialization Patterns

### Basic Connection
```python
import {sdk}
db = {sdk}.connect("./data")
```
Usage: 18 repositories

## Task Suitability

### task1_init
Found 20 suitable repositories
- repo1, repo2, ...
```

---

## Phase 4: Sample Generation

**Goal**: Build 50 benchmark samples across 5 task types.

**Time**: 8-16 hours

### Prerequisites

- Phase 3 completed with `patterns.json` and `patterns.md`
- Clear understanding of task type definitions

### Steps

1. **Create the build script** at `scripts/data_collection/{sdk_name}/build_samples.py`
2. **Implement sample generators** for each task type
3. **Run the builder** to generate all 50 samples
4. **Verify sample structure** manually

### Sample Structure

Each sample must have this structure:

```
{sdk}_task{N}_{name}_{id}/
├── input/
│   ├── {main_file}           # Incomplete code with TODOs
│   ├── {manifest}            # dependencies without SDK
│   └── .env.example          # Empty or minimal
├── expected/
│   ├── {main_file}           # Complete implementation
│   ├── {manifest}            # With SDK dependency
│   ├── .env.example          # With required variables
│   └── metadata.json         # Ground truth
└── tests/
    └── test_{task}.{ext}     # Validation tests
```

### Metadata Schema

See `templates/metadata-schema.json` for the complete schema. Key fields:

```json
{
  "sample_id": "{sdk}_task1_init_001",
  "task_type": 1,
  "task_name": "initialization",
  "sdk": "{sdk_name}",
  "{sdk}_version": "1.0.0",
  "framework": "{framework}",
  "difficulty": "easy|medium|hard",
  "ground_truth": {
    "ingredients": {
      "initialization": {...},
      "configuration": {...},
      "integration_points": [...]
    }
  },
  "evaluation_targets": {
    "i_acc": {...},
    "c_comp": {...},
    "f_corr": {...}
  }
}
```

### Variation Strategy

Vary samples within each task type:

| Task | Vary By | Examples |
|------|---------|----------|
| 1 (Init) | Framework, complexity | minimal, standard, full config |
| 2 (Core) | Operation type | create, read, update, delete |
| 3 (Advanced) | Feature type | search, filter, batch |
| 4 (Complete) | Use case | RAG pipeline, API backend |
| 5 (Migration) | Breaking change type | API change, config change |

### Run Command

```bash
uv run python scripts/data_collection/{sdk}/build_samples.py
```

### Output

```
samples/{sdk_name}/
├── {sdk}_task1_init_001/
├── {sdk}_task1_init_002/
├── ... (50 samples)
└── {sdk}_dataset_manifest.json
```

---

## Phase 5: Sample Validation & QA

**Goal**: Ensure all samples are correct, complete, and consistent.

**Time**: 4-8 hours

### Prerequisites

- Phase 4 completed with all 50 samples generated
- Access to Claude Code for QA review

### Steps

1. **Run automated validation** script
2. **Use Claude Code** for comprehensive QA review
3. **Fix identified issues**
4. **Re-validate** until all checks pass

### Automated Validation

Create/run validation script:

```python
def validate_sample(sample_dir: Path) -> List[str]:
    errors = []

    # Structure checks
    for d in ["input", "expected", "tests"]:
        if not (sample_dir / d).exists():
            errors.append(f"Missing directory: {d}")

    # Metadata checks
    metadata_path = sample_dir / "expected" / "metadata.json"
    if metadata_path.exists():
        metadata = json.load(open(metadata_path))
        required = ["sample_id", "task_type", "sdk", "ground_truth"]
        for field in required:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")

    return errors
```

### Claude Code QA Session

Use the prompt from `prompts/phase5-validation.prompt.md`:

```
Review all samples in samples/{sdk_name}/ to verify:

1. **Correctness** - Does expected/ contain valid, working code?
2. **Completeness** - Are all required files present?
3. **Consistency** - Do similar tasks follow same patterns?
4. **Test Coverage** - Do tests validate key requirements?

Report issues in format:
Sample: {sample_id}
Issue: [description]
Fix: [suggestion]
```

### Validation Checklist

See `checklists/validation-checklist.md` for complete checklist.

Key checks:
- [ ] All 50 samples have correct structure
- [ ] All metadata.json files have required fields
- [ ] Input files have TODO comments
- [ ] Expected files have complete SDK integration
- [ ] Tests reference expected/ files correctly
- [ ] Naming follows convention: `{sdk}_task{N}_{name}_{id}`

---

## Phase 6: Integration & Testing

**Goal**: Integrate SDK into the evaluation framework and verify it works.

**Time**: 2-4 hours

### Prerequisites

- Phase 5 completed with all validations passing
- Evaluation framework set up

### Steps

1. **Update dataset manifest** if not already created
2. **Add parser** (if new language)
3. **Run test evaluation** on a few samples
4. **Run full evaluation**
5. **Compare with existing SDKs**

### Dataset Manifest

Verify `samples/{sdk_name}/{sdk}_dataset_manifest.json` exists:

```json
{
  "dataset_version": "1.0",
  "sdk": "{sdk_name}",
  "language": "{language}",
  "created_at": "2025-01-20T...",
  "total_samples": 50,
  "by_task_type": {
    "1": 15, "2": 15, "3": 10, "4": 7, "5": 3
  },
  "samples": [...]
}
```

### Test Commands

```bash
# Test with a few samples
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --model claude-sonnet-4-5 \
    --samples 5 \
    --dry-run

# Full evaluation
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --model claude-sonnet-4-5

# Compare with existing SDKs
uv run python scripts/compare_sdk_results.py \
    --sdks clerk,lancedb,{sdk_name}
```

### Expected Results

After successful integration:
- Evaluation runs without errors on all 50 samples
- Results are saved to `results/{sdk_name}/`
- Comparison report shows metrics comparable to existing SDKs

---

## Quick Reference

### Commands Summary

```bash
# Phase 1: Search repositories
uv run python scripts/data_collection/{sdk}/search_repos.py --max-repos 100

# Phase 2: Mine repositories
uv run python scripts/data_collection/{sdk}/mine_repos.py --limit 20

# Phase 3: Extract patterns
uv run python scripts/data_collection/{sdk}/extract_patterns.py

# Phase 4: Build samples
uv run python scripts/data_collection/{sdk}/build_samples.py

# Phase 5: Validate (use Claude Code with prompts/)

# Phase 6: Run evaluation
uv run python scripts/run_evaluation_multi_sdk.py --sdk {sdk}
```

### Naming Conventions

- **Sample IDs**: `{sdk}_task{type}_{name}_{sequential_id}`
  - Example: `lancedb_task1_init_001`, `clerk_task3_hooks_031`
- **Repository IDs**: `{sdk}_repo_{sequential_id}`
  - Example: `lancedb_repo_001`

### File Locations

| Artifact | Location |
|----------|----------|
| Research notes | `docs/sdk-research/{sdk}.md` |
| Search script | `scripts/data_collection/{sdk}/search_repos.py` |
| Mine script | `scripts/data_collection/{sdk}/mine_repos.py` |
| Extract script | `scripts/data_collection/{sdk}/extract_patterns.py` |
| Build script | `scripts/data_collection/{sdk}/build_samples.py` |
| Repositories | `data/{sdk}/repositories.json` |
| Mined data | `data/{sdk}/mined-repos.json` |
| Patterns | `data/{sdk}/patterns.json`, `patterns.md` |
| Samples | `samples/{sdk}/` |
| Manifest | `samples/{sdk}/{sdk}_dataset_manifest.json` |

### Reference Implementations

Study these existing SDKs:
- **TypeScript/Next.js**: `scripts/data_collection/clerk/`
- **Python**: `scripts/data_collection/lancedb/`

---

## Appendix: Language-Specific Notes

### Python SDKs

- Use `requirements.txt` or `pyproject.toml` for dependencies
- Use pytest for tests
- Common frameworks: FastAPI, Flask, Streamlit, Django

### TypeScript/JavaScript SDKs

- Use `package.json` for dependencies
- Use Jest or Vitest for tests
- Common frameworks: Next.js, React, Express, Remix

### Rust SDKs

- Use `Cargo.toml` for dependencies
- Use built-in test framework (`#[cfg(test)]`)
- Consider async runtime (tokio, async-std)

### Go SDKs

- Use `go.mod` for dependencies
- Use built-in testing package
- Consider module path conventions
