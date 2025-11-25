# Phase 3: Pattern Extraction Prompt

Copy and paste this prompt into Claude Code to analyze cloned repositories and extract SDK usage patterns.

---

## Prompt

```
Analyze the cloned repositories in `data/{sdk_name}/cloned-repos/` to extract common {SDK_NAME} integration patterns for SDKBench.

## Context

I've cloned {N} repositories that use {SDK_NAME}. I need to understand the real-world usage patterns to create realistic benchmark samples.

## Analysis Tasks

### 1. Initialization Patterns

Search for how the SDK is initialized across repositories:

```bash
# Find import statements
grep -r "import.*{package}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"
grep -r "from {package}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"

# Find initialization calls
grep -r "{init_function}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"
```

**What to capture:**
- Most common import patterns (exact strings)
- Provider/wrapper initialization patterns
- Configuration object structures
- Framework-specific differences

### 2. Configuration Patterns

Find environment variables and config files:

```bash
# Search .env files
grep -r "{SDK_PREFIX}" data/{sdk_name}/cloned-repos/ --include=".env*"
grep -r "{SDK_PREFIX}" data/{sdk_name}/cloned-repos/ --include="*.example"

# Search for config objects
grep -r "{config_pattern}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"
```

**What to capture:**
- Required environment variables (frequency of each)
- Optional environment variables
- Config file structures
- Framework-specific configuration

### 3. Core Operation Patterns

Identify the primary SDK operations:

```bash
# Search for common function calls
grep -r "{function_1}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"
grep -r "{function_2}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"
```

**What to capture:**
- Top 10 most used functions/methods
- Common parameter combinations
- Return value handling patterns
- Error handling approaches

### 4. Advanced Feature Patterns

Look for more complex integrations:

```bash
# Middleware patterns
grep -r "middleware" data/{sdk_name}/cloned-repos/ --include="*.{ext}"

# Hook patterns (if applicable)
grep -r "use{SDK}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"

# Custom configurations
grep -r "{advanced_pattern}" data/{sdk_name}/cloned-repos/ --include="*.{ext}"
```

**What to capture:**
- Middleware implementations
- Hook usage patterns
- Custom configuration patterns
- Integration with other libraries

### 5. Framework-Specific Patterns

Group findings by framework:

**For {Framework 1}:**
- Initialization location (e.g., `app/layout.tsx`, `main.py`)
- Framework-specific imports
- Integration patterns

**For {Framework 2}:**
- Initialization location
- Framework-specific imports
- Integration patterns

### 6. Version Analysis

```bash
# Find version specifications
grep -r '"{package}"' data/{sdk_name}/cloned-repos/ --include="package.json" -A1
grep -r '{package}' data/{sdk_name}/cloned-repos/ --include="requirements.txt"
grep -r '{package}' data/{sdk_name}/cloned-repos/ --include="pyproject.toml"
```

**What to capture:**
- Version distribution across repos
- Any v1 vs v2 (or similar) differences
- Deprecated patterns still in use

## Output Format

Create `data/{sdk_name}/patterns.md` with this structure:

```markdown
# {SDK_NAME} Integration Patterns

## Overview
- Total repositories analyzed: {N}
- Analysis date: {YYYY-MM-DD}

## Frameworks
- **{framework_1}**: {N} repositories
- **{framework_2}**: {N} repositories

## {SDK} Versions
- `^{version_1}`: {N} repositories
- `^{version_2}`: {N} repositories

## Ingredient 1: Initialization Patterns

### {Pattern Name}
\`\`\`{language}
{code_example}
\`\`\`
- **Usage**: {N} repositories
- **Variations**:
  - {variation_1}
  - {variation_2}

## Ingredient 2: Configuration Patterns

### Environment Variables
| Variable | Required | Usage Count |
|----------|----------|-------------|
| `{VAR_1}` | Yes | {N} repos |
| `{VAR_2}` | No | {N} repos |

## Ingredient 3: Integration Points

### {Integration Type 1}
- `{function_1}()`: {N} repos
- `{function_2}()`: {N} repos

### {Integration Type 2}
...

## Task Suitability

### task1_init
Found {N} suitable repositories:
- {repo_1} - {reason}
- {repo_2} - {reason}

### task2_{core_op}
Found {N} suitable repositories:
- {repo_1} - {reason}

### task3_{advanced}
Found {N} suitable repositories:
...

### task4_complete
Found {N} suitable repositories:
...

### task5_migration
Found {N} suitable repositories (using older version):
...
```

## Quality Indicators

For each pattern, note:
1. **Frequency** - How many repos use this pattern?
2. **Consistency** - Is it implemented the same way?
3. **Correctness** - Does it follow SDK best practices?
4. **Testability** - Can we write tests for this pattern?
```

---

## Before Running

Replace these placeholders:
- `{sdk_name}` - lowercase SDK name (e.g., `lancedb`, `clerk`)
- `{SDK_NAME}` - display name (e.g., `LanceDB`, `Clerk`)
- `{package}` - package name for imports
- `{ext}` - file extension (`py`, `ts`, `tsx`)
- `{init_function}` - main initialization function
- `{SDK_PREFIX}` - env var prefix (e.g., `CLERK_`, `OPENAI_`)
- `{N}` - number of repositories

---

## Example: LanceDB

```
Analyze the cloned repositories in `data/lancedb/cloned-repos/` to extract common LanceDB integration patterns.

Search patterns:
- grep -r "import lancedb" --include="*.py"
- grep -r "lancedb.connect" --include="*.py"
- grep -r "create_table" --include="*.py"
- grep -r ".search(" --include="*.py"
```

---

## After Analysis

1. Save output to `data/{sdk_name}/patterns.md`
2. Also create `data/{sdk_name}/patterns.json` with structured data
3. Use findings to inform Phase 4 sample generation
