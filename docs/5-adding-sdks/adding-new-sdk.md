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

**Goal**: Integrate SDK into the evaluation framework and verify it works end-to-end.

**Time**: 4-8 hours (depending on whether new language support is needed)

### Prerequisites

- Phase 5 completed with all validations passing
- All 50 samples in `samples/{sdk_name}/` with correct structure
- Dataset manifest generated by `build_samples.py`
- API keys configured for evaluation models in `.env`

---

### Step 1: Verify Dataset Manifest

The dataset manifest should have been created by `build_samples.py`. Verify it exists and is correct:

```bash
# Check manifest exists
cat samples/{sdk_name}/{sdk}_dataset_manifest.json | jq '.total_samples, .by_task_type'
```

**Expected Output**:
```
50
{
  "1": 15,
  "2": 15,
  "3": 10,
  "4": 7,
  "5": 3
}
```

**Required Manifest Fields**:
```json
{
  "dataset_version": "1.0",
  "sdk": "{sdk_name}",
  "language": "python|typescript",
  "created_at": "2025-XX-XXTXX:XX:XX.XXXXXX",
  "total_samples": 50,
  "by_task_type": {
    "1": 15,
    "2": 15,
    "3": 10,
    "4": 7,
    "5": 3
  },
  "samples": [
    {
      "sample_id": "{sdk}_task1_init_001",
      "task_type": 1,
      "sdk": "{sdk_name}",
      "created_at": "..."
    }
    // ... 49 more samples
  ]
}
```

---

### Step 2: Update Evaluation Pipeline (if needed)

The evaluation pipeline (`scripts/run_evaluation_multi_sdk.py`) auto-discovers SDKs. Verify your SDK is detected:

```bash
# Check SDK discovery
python -c "
from pathlib import Path
samples = Path('samples')
for sdk_dir in sorted(samples.iterdir()):
    if sdk_dir.is_dir() and not sdk_dir.name.startswith('.'):
        count = len(list(sdk_dir.glob('*_task*')))
        print(f'{sdk_dir.name}: {count} samples')
"
```

**If your SDK is NOT detected**, check:
1. Directory name matches SDK name in manifest
2. Sample directories follow naming convention: `{sdk}_task{N}_{name}_{id}`
3. Samples contain `input/`, `expected/`, and `tests/` directories

---

### Step 3: Add Language Parser (if new language)

The evaluation framework uses parsers to extract patterns from code. Check if your language is supported:

**Currently Supported Languages**:
| Language | Parser | File Extensions |
|----------|--------|-----------------|
| TypeScript/JavaScript | `TypeScriptParser` | `.ts`, `.tsx`, `.js`, `.jsx` |
| Configuration | `ConfigParser` | `.json` |
| Environment | `EnvParser` | `.env`, `.env.example` |

**If adding a new language (e.g., Python, Rust)**:

1. **Create parser file**: `sdkbench/parsers/{language}_parser.py`

```python
# sdkbench/parsers/python_parser.py
"""Parser for extracting patterns from Python files."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Optional


class PythonParser:
    """Parse Python files to extract SDK patterns."""

    # File extensions this parser handles
    EXTENSIONS = {'.py'}

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.content = self._read_file()
        self.tree = self._parse_ast()

    def _read_file(self) -> str:
        """Read file content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def _parse_ast(self) -> Optional[ast.AST]:
        """Parse Python AST."""
        try:
            return ast.parse(self.content)
        except SyntaxError:
            return None

    def extract_imports(self) -> List[str]:
        """Extract all import statements."""
        imports = []
        if not self.tree:
            return imports

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = ", ".join(alias.name for alias in node.names)
                imports.append(f"from {module} import {names}")

        return imports

    def has_import(self, package: str) -> bool:
        """Check if a specific package is imported."""
        imports = self.extract_imports()
        return any(package in imp for imp in imports)

    def extract_function_calls(self, function_name: str) -> List[str]:
        """Extract calls to a specific function."""
        calls = []
        pattern = rf'{function_name}\s*\([^)]*\)'
        matches = re.finditer(pattern, self.content)
        for match in matches:
            calls.append(match.group(0))
        return calls

    def has_pattern(self, pattern: str) -> bool:
        """Check if a pattern exists in the file."""
        return pattern in self.content
```

2. **Register parser** in `sdkbench/parsers/__init__.py`:

```python
from sdkbench.parsers.python_parser import PythonParser

__all__ = [
    "TypeScriptParser",
    "EnvParser",
    "ConfigParser",
    "PythonParser",  # Add new parser
]
```

3. **Update Solution class** in `sdkbench/core/solution.py`:

Add Python extensions to the `_load_files` method:
```python
# In Solution._load_files()
extensions = {'.ts', '.tsx', '.js', '.jsx', '.json', '.env', '.py'}  # Add .py
```

Update import extraction patterns for Python:
```python
# In Solution.extract_imports()
# Add Python import patterns
python_patterns = [
    r"^import\s+(\S+)",                    # import X
    r"^from\s+(\S+)\s+import\s+(.+)",     # from X import Y
]
```

---

### Step 4: Configure SDK-Specific Evaluation

Some SDKs may need SDK-specific evaluation logic. Check `sdkbench/metrics/` for metric evaluators:

**Metric Evaluators**:
| Metric | File | What It Checks |
|--------|------|----------------|
| I-ACC | `i_acc.py` | Ingredient accuracy (imports, configs) |
| C-COMP | `c_comp.py` | Component completeness |
| IPA | `ipa.py` | Import precision/accuracy |
| F-CORR | `f_corr.py` | Functional correctness (build/tests) |
| CQ | `cq.py` | Code quality |
| SEM-SIM | `sem_sim.py` | Semantic similarity |

**If SDK needs custom evaluation**:

1. Check if ground truth metadata contains SDK-specific fields
2. Verify metric evaluators can read your `metadata.json` format
3. Update evaluators if needed for SDK-specific patterns

---

### Step 5: Run Test Evaluation (Dry Run)

Test the evaluation pipeline with a small subset:

```bash
# Dry run: Parse samples but don't call LLM
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --limit 3 \
    --skip-generation \
    --skip-evaluation

# Check output
ls -la solutions/{sdk_name}/
```

**Expected**: No errors, solution directories created

---

### Step 6: Run Sample Evaluation (5 samples)

Test with actual LLM generation on 5 samples:

```bash
# Run with Claude Sonnet on 5 samples
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --model claude-sonnet-4-5 \
    --limit 5 \
    --n-workers 3
```

**Monitor Output**:
```
================================================================================
MULTI-SDK BENCH EVALUATION
================================================================================
SDKs: {sdk_name}
Models: claude-sonnet-4-5
Workers: 3
Output: /path/to/solutions
================================================================================

============================================================
SDK: {SDK_NAME}
============================================================
Found 5 samples

==================================================
MODEL: claude-sonnet-4-5
Provider: anthropic
SDK: {sdk_name}
==================================================

{sdk_name}/claude-sonnet-4-5: 100%|████████| 5/5 [00:30<00:00]

📊 Saved {sdk_name}/claude-sonnet-4-5 summary to: results/{sdk_name}/claude-sonnet-4-5_summary.json
```

**Check Results**:
```bash
# View summary
cat results/{sdk_name}/claude-sonnet-4-5_summary.json | jq '.'

# Expected structure:
{
  "sdk": "{sdk_name}",
  "model": "claude-sonnet-4-5",
  "timestamp": "...",
  "total_samples": 5,
  "generation": {"success": 5, "failed": 0},
  "evaluation": {"success": 5, "failed": 0},
  "average_metrics": {
    "i_acc": 0.85,
    "c_comp": 0.90,
    "ipa": 0.88,
    "f_corr": 0.75,
    "cq": 0.82,
    "sem_sim": 0.91
  }
}
```

---

### Step 7: Run Full Evaluation (50 samples)

Once test evaluation passes, run on all 50 samples:

```bash
# Full evaluation with single model
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --model claude-sonnet-4-5 \
    --n-workers 5

# Or evaluate multiple models
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --models "claude-sonnet-4-5,gpt-4o,gemini-1.5-pro" \
    --n-workers 5
```

**Expected Time**: ~10-20 minutes for 50 samples with 5 workers

**Verify Results**:
```bash
# Check all samples evaluated
cat results/{sdk_name}/claude-sonnet-4-5_summary.json | jq '.total_samples'
# Should output: 50

# Check metrics
cat results/{sdk_name}/claude-sonnet-4-5_summary.json | jq '.average_metrics'
```

---

### Step 8: Compare with Existing SDKs

Generate comparison report:

```bash
# Run comparison analysis
uv run python scripts/compare_sdk_results.py
```

**Expected Output**:
```
================================================================================
SDK COMPARISON REPORT
================================================================================
SDKs analyzed: clerk, lancedb, {sdk_name}
Generated: 2025-XX-XX XX:XX:XX

============================================================
MODEL: claude-sonnet-4-5
============================================================

SDK             Samples    Success    I-ACC    C-COMP   IPA      F-CORR   CQ       SEM-SIM
------------------------------------------------------------------------------------------
clerk           50         48         0.850    0.920    0.880    0.750    0.820    0.910
lancedb         50         49         0.870    0.900    0.860    0.780    0.840    0.920
{sdk_name}      50         47         0.XXX    0.XXX    0.XXX    0.XXX    0.XXX    0.XXX

📝 Markdown report saved to: results/sdk_comparison_YYYYMMDD_HHMMSS.md
💾 Comparison report saved to: results/sdk_comparison_YYYYMMDD_HHMMSS.json
```

**Review Comparison Report**:
```bash
# View markdown report
cat results/sdk_comparison_*.md | head -50
```

---

### Step 9: Debug Failed Evaluations (if any)

If some samples fail evaluation:

```bash
# Find failed samples
cat results/{sdk_name}/claude-sonnet-4-5_summary.json | jq '.evaluation.failed'

# Check individual solution
ls -la solutions/{sdk_name}/claude-sonnet-4-5/{sdk}_task1_init_001/

# Review generated code
cat solutions/{sdk_name}/claude-sonnet-4-5/{sdk}_task1_init_001/*.{py,ts}
```

**Common Issues**:
| Issue | Symptom | Fix |
|-------|---------|-----|
| Parser error | `No files loaded` | Add file extension to parser |
| Missing import | `i_acc: 0` | Check ground truth `ingredients` field |
| Build failure | `f_corr: 0` | Verify `tests/` are correct |
| Low similarity | `sem_sim < 0.5` | Review expected vs generated code |

---

### Step 10: Create Results Summary

Document the evaluation results:

```bash
# Generate final summary
python -c "
import json
from pathlib import Path

sdk = '{sdk_name}'
results_dir = Path('results') / sdk

print(f'# {sdk.upper()} Evaluation Results')
print()

for summary_file in sorted(results_dir.glob('*_summary.json')):
    model = summary_file.stem.replace('_summary', '')
    with open(summary_file) as f:
        data = json.load(f)

    print(f'## {model}')
    print(f'- Total samples: {data.get(\"total_samples\", \"N/A\")}')
    print(f'- Generation success: {data.get(\"generation\", {}).get(\"success\", \"N/A\")}')
    print(f'- Evaluation success: {data.get(\"evaluation\", {}).get(\"success\", \"N/A\")}')

    metrics = data.get('average_metrics', {})
    if metrics:
        print('- Average metrics:')
        for k, v in metrics.items():
            print(f'  - {k.upper()}: {v:.3f}')
    print()
"
```

---

### Integration Checklist

Before considering integration complete:

- [ ] Dataset manifest exists and is valid
- [ ] SDK is auto-discovered by evaluation pipeline
- [ ] Parser supports SDK's language (add new parser if needed)
- [ ] Dry run completes without errors
- [ ] 5-sample evaluation runs successfully
- [ ] All 50 samples evaluated
- [ ] Results saved to `results/{sdk_name}/`
- [ ] Comparison with existing SDKs generated
- [ ] Average metrics are reasonable (> 0.5 for most metrics)
- [ ] Failed samples investigated and documented

---

### Expected Directory Structure After Integration

```
SDKBench/
├── samples/
│   └── {sdk_name}/
│       ├── {sdk}_dataset_manifest.json
│       ├── {sdk}_task1_init_001/
│       ├── {sdk}_task1_init_002/
│       │   ... (50 sample directories)
│       └── {sdk}_task5_migration_050/
├── solutions/
│   └── {sdk_name}/
│       ├── claude-sonnet-4-5/
│       │   ├── {sdk}_task1_init_001/
│       │   │   ... (LLM-generated solutions)
│       │   └── {sdk}_task5_migration_050/
│       └── gpt-4o/
│           └── ...
├── results/
│   ├── {sdk_name}/
│   │   ├── claude-sonnet-4-5_summary.json
│   │   └── gpt-4o_summary.json
│   ├── overall_report_YYYYMMDD_HHMMSS.json
│   ├── sdk_comparison_YYYYMMDD_HHMMSS.json
│   └── sdk_comparison_YYYYMMDD_HHMMSS.md
└── sdkbench/
    └── parsers/
        ├── __init__.py
        ├── typescript_parser.py
        ├── python_parser.py  # If added
        └── ...
```

---

### Troubleshooting Guide

#### Problem: SDK not found by pipeline

```bash
# Check directory structure
ls -la samples/{sdk_name}/

# Verify sample naming
ls samples/{sdk_name}/ | head -5
# Should show: {sdk}_task1_init_001, {sdk}_task1_init_002, ...
```

#### Problem: Parser errors

```bash
# Test parser manually
python -c "
from sdkbench.parsers import TypeScriptParser  # or PythonParser
from pathlib import Path

sample = Path('samples/{sdk_name}/{sdk}_task1_init_001/expected/app.py')
parser = PythonParser(sample)
print('Imports:', parser.extract_imports())
print('Has {sdk}:', parser.has_import('{sdk_package}'))
"
```

#### Problem: Low metrics

```bash
# Compare expected vs generated
diff -u samples/{sdk_name}/{sdk}_task1_init_001/expected/app.py \
        solutions/{sdk_name}/claude-sonnet-4-5/{sdk}_task1_init_001/app.py

# Check ground truth metadata
cat samples/{sdk_name}/{sdk}_task1_init_001/expected/metadata.json | jq '.ground_truth'
```

#### Problem: Generation failures

```bash
# Check API key
echo $ANTHROPIC_API_KEY | head -c 20

# Test API manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-5", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'
```

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

---

## Appendix: Lessons Learned & Best Practices

This section documents critical lessons learned from implementing Clerk (TypeScript) and LanceDB (Python) SDKs. **Following these practices will prevent common bugs and ensure accurate benchmark evaluation.**

### Test Design Best Practices

#### 1. Test Behavior, Not Implementation Structure

**Problem**: Tests that check specific implementation patterns (like `module.db is not None`) fail when correct code uses different patterns (like `module.get_database()`).

**Bad Pattern** ❌:
```python
def test_database_connection():
    from expected import app
    assert app.db is not None  # Fails if solution uses get_database()
```

**Good Pattern** ✅:
```python
def test_database_connection():
    from expected import app
    # Accept multiple valid implementation patterns
    assert has_db_connection(app), "No database connection method found"
    db = get_db_connection(app)
    assert db is not None
    assert hasattr(db, "table_names")
```

#### 2. Create Shared Test Utilities

For Python SDKs, create a `conftest.py` at `samples/{sdk}/conftest.py` with helper functions that accept multiple valid patterns:

```python
"""Shared test utilities for {SDK} samples."""

def get_db_connection(module):
    """Get database connection from module using various patterns.

    Supports:
    - module.db (module-level variable)
    - module.get_database() (factory function)
    - module.get_db() (short factory)
    - module.connect() (direct connect)
    """
    # Module-level variable
    if hasattr(module, 'db') and module.db is not None:
        return module.db

    # Factory functions
    for func_name in ['get_database', 'get_db', 'get_connection', 'connect']:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                try:
                    return func()
                except Exception:
                    continue

    return None

def has_db_connection(module):
    """Check if module has any way to get a database connection."""
    if hasattr(module, 'db'):
        return True
    connection_funcs = ['get_database', 'get_db', 'get_connection', 'connect']
    return any(hasattr(module, name) and callable(getattr(module, name))
               for name in connection_funcs)
```

#### 3. Update Test Templates in build_samples.py

When creating `build_samples.py`, ensure test templates:
1. Import shared utilities from conftest.py
2. Use flexible assertion patterns
3. Test behavior (e.g., "can create table") not structure (e.g., "has db variable")

```python
def _create_test_template(self, tests_dir: Path, scenario: Dict):
    test_content = '''"""Tests for {task}."""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import shared test utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from conftest import get_db_connection, has_db_connection

def test_database_connection():
    """Test database is connected."""
    from expected import app
    assert has_db_connection(app), "No database connection method found"
    db = get_db_connection(app)
    assert db is not None

def test_main_runs():
    """Test main function runs without errors."""
    from expected import app
    app.main()  # Should not raise
'''
```

### Test Runner Best Practices

#### 4. Exclude Virtual Environments from Test Detection

**Problem**: `rglob("test_*.py")` matches files inside `venv/`, `node_modules/`, causing false positives.

**Solution**: Filter excluded directories when detecting test files:

```python
EXCLUDED_DIRS = {"venv", ".venv", "node_modules", "__pycache__",
                 ".git", "dist", "build", ".pytest_cache"}

def _filter_excluded_dirs(self, files: List[Path]) -> List[Path]:
    return [f for f in files if not any(
        excluded in f.parts for excluded in self.EXCLUDED_DIRS
    )]

# Usage
test_files = self._filter_excluded_dirs(list(working_dir.rglob("test_*.py")))
```

### F-CORR (Functional Correctness) Best Practices

#### 5. Capture Full Error Tracebacks

**Problem**: When tests fail, `f_corr.json` only shows "1 tests failed" without details, making debugging impossible.

**Solution**: Store full failure details including stack traces:

```python
# In FCorrResult model
class FCorrResult(MetricResult):
    tests_passed: int = 0
    tests_total: int = 0
    failed_tests: List[str] = Field(default_factory=list)
    error_messages: List[str] = Field(default_factory=list)
    # Add detailed failure info
    failure_details: List[Dict[str, Any]] = Field(default_factory=list)
    # Each entry: {
    #   "test_name": "test_database_connection",
    #   "file_path": "tests/test_init.py",
    #   "line_number": 18,
    #   "error_message": "AssertionError: assert app.db is not None",
    #   "stack_trace": "Traceback (most recent call last):\n..."
    # }
    raw_output: Optional[str] = None
```

#### 6. Parse Stack Traces from Test Output

Extract full tracebacks from pytest/jest output:

```python
def _extract_pytest_stack_traces(self, output: str) -> dict:
    """Extract stack traces from pytest output."""
    stack_traces = {}

    # pytest formats failures between "= FAILURES =" and summary
    failures_pattern = r'={3,}\s*FAILURES\s*={3,}(.*?)(?:={3,}\s*(?:short test summary)|\Z)'
    failures_match = re.search(failures_pattern, output, re.DOTALL)

    if failures_match:
        # Split by test headers and extract tracebacks
        test_pattern = r'_{3,}\s*([^\s_]+(?:::[^\s_]+)?)\s*_{3,}'
        parts = re.split(test_pattern, failures_match.group(1))
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                stack_traces[parts[i].strip()] = parts[i + 1].strip()

    return stack_traces
```

### Metric Model Best Practices

#### 7. Ensure Model Fields Match Usage

**Problem**: Code uses `result.deductions` but `CQResult` doesn't have that field, causing AttributeError.

**Solution**: Audit all metric result classes to ensure:
1. All fields used in evaluators exist in models
2. All fields used in formatters/summaries exist in models

```python
# In result.py - ensure model has all expected fields
class CQResult(MetricResult):
    type_errors: int = 0
    eslint_errors: int = 0
    security_issues: int = 0
    # Add missing field that evaluator uses
    deductions: List[Dict[str, Any]] = Field(default_factory=list)

    @property
    def total_deductions(self) -> int:
        return sum(d.get('points', 0) for d in self.deductions)
```

### SDK-Specific Considerations

#### 8. TypeScript/JavaScript SDKs (like Clerk)

- Tests check **file contents** using string matching (e.g., `expect(layout).toContain('ClerkProvider')`)
- Less prone to implementation pattern coupling
- Focus on ensuring expected files exist and contain required patterns

#### 9. Python SDKs (like LanceDB)

- Tests **import modules** and check attributes/behavior
- High risk of implementation pattern coupling
- Always use flexible helpers that accept multiple valid patterns
- Create `conftest.py` with shared utilities

### Checklist for New SDKs

Before finalizing samples for a new SDK:

- [ ] **Test utilities created**: `samples/{sdk}/conftest.py` with flexible helpers
- [ ] **Tests are behavioral**: Check what code does, not how it's structured
- [ ] **Multiple patterns accepted**: Tests pass for different valid implementations
- [ ] **Excluded dirs filtered**: venv/node_modules excluded from test detection
- [ ] **Error details captured**: Stack traces stored in f_corr.json
- [ ] **Model fields match**: All fields used in code exist in Pydantic models
- [ ] **Templates updated**: build_samples.py generates correct test templates

### Common Bugs to Avoid

| Bug | Symptom | Prevention |
|-----|---------|------------|
| Module-level variable coupling | Tests fail for function-based implementations | Use flexible helper functions |
| Missing model fields | AttributeError in evaluators | Audit model vs. usage |
| venv in test detection | Thousands of test files detected | Filter excluded directories |
| No stack traces | "1 tests failed" with no details | Capture full failure details |
| Template not updated | New samples have old bug | Update build_samples.py templates |

### Reference Files

Study these files for reference implementations:

| File | Purpose |
|------|---------|
| `samples/lancedb/conftest.py` | Shared test utilities for Python SDK |
| `sdkbench/test_harness/python_runner.py` | Test runner with excluded dir filtering |
| `sdkbench/core/result.py` | Metric result models with all required fields |
| `sdkbench/metrics/f_corr.py` | F-CORR evaluator with detailed failure capture |
| `scripts/data_collection/lancedb/build_samples.py` | Sample builder with correct test templates |
