# {SDK_NAME} Research Summary

> Fill out this template during Phase 0 of SDK integration.
> Save the completed file to `docs/sdk-research/{sdk_name}.md`

## Basic Information

| Field | Value |
|-------|-------|
| **Package Name** | `{package_name}` |
| **Language** | {Python/TypeScript/Rust/Go} |
| **Category** | {Auth/Database/AI/API/etc.} |
| **Current Version** | {version} |
| **Documentation URL** | {url} |
| **GitHub URL** | {url} |
| **Package Registry** | {npm/PyPI/crates.io/etc.} |

## Installation

```bash
# Package manager command
{pip install package / npm install package / cargo add package}
```

## Initialization Pattern

### Minimal Setup

```{language}
// Minimal code to initialize the SDK
```

### Full Setup with Configuration

```{language}
// Complete initialization with all common options
```

## Required Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `{VAR_1}` | Yes | {description} |
| `{VAR_2}` | Yes | {description} |
| `{VAR_3}` | No | {description} |

### Config Files (if applicable)

```{format}
// Config file structure
```

## Common Imports

```{language}
// List the most common import statements
```

## Core Operations

### {Operation 1}

```{language}
// Code example
```

**Parameters:**
- `{param1}`: {description}
- `{param2}`: {description}

### {Operation 2}

```{language}
// Code example
```

### {Operation 3}

```{language}
// Code example
```

## Framework Integrations

### {Framework 1} (e.g., Next.js, FastAPI)

**Initialization location**: `{file_path}`

```{language}
// Framework-specific setup
```

**Special considerations:**
- {consideration_1}
- {consideration_2}

### {Framework 2}

**Initialization location**: `{file_path}`

```{language}
// Framework-specific setup
```

## Advanced Features

### {Feature 1} (e.g., Middleware)

```{language}
// Code example
```

### {Feature 2} (e.g., Hooks)

```{language}
// Code example
```

## Error Handling

### Common Error Patterns

```{language}
// Error handling example
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `{Error1}` | {cause} | {solution} |
| `{Error2}` | {cause} | {solution} |

## Version History

### Current Version: {version}

Key features:
- {feature_1}
- {feature_2}

### Breaking Changes from Previous Version

| Change | Before | After |
|--------|--------|-------|
| {change_1} | `{old_code}` | `{new_code}` |
| {change_2} | `{old_code}` | `{new_code}` |

### Migration Guide Link

{url_to_migration_guide}

---

## Task Type Definitions for SDKBench

Based on the research above, define 5 task types:

| Task | Name | Count | Description | Difficulty | Key Patterns |
|------|------|-------|-------------|------------|--------------|
| 1 | init | 15 | {description} | easy | {patterns} |
| 2 | {name} | 15 | {description} | easy-medium | {patterns} |
| 3 | {name} | 10 | {description} | medium | {patterns} |
| 4 | complete | 7 | {description} | hard | {patterns} |
| 5 | migration | 3 | {description} | hard | {patterns} |

### Task 1: Initialization (15 samples)

**What it tests**: Basic SDK setup

**Variations**:
1. {Framework 1} - minimal setup
2. {Framework 1} - with configuration
3. {Framework 2} - minimal setup
4. ...

**Key patterns to test**:
- [ ] Correct imports
- [ ] Provider/wrapper setup
- [ ] Environment variable configuration

### Task 2: {Core Operation} (15 samples)

**What it tests**: {description}

**Variations**:
1. {variation_1}
2. {variation_2}
3. ...

**Key patterns to test**:
- [ ] {pattern_1}
- [ ] {pattern_2}

### Task 3: {Advanced Feature} (10 samples)

**What it tests**: {description}

**Variations**:
1. {variation_1}
2. {variation_2}

**Key patterns to test**:
- [ ] {pattern_1}
- [ ] {pattern_2}

### Task 4: Complete Integration (7 samples)

**What it tests**: Full pipeline combining multiple features

**Scenarios**:
1. {scenario_1}
2. {scenario_2}

**Key patterns to test**:
- [ ] All of Task 1-3 patterns combined
- [ ] Error handling
- [ ] Configuration

### Task 5: Migration (3 samples)

**What it tests**: Migrating from previous version

**Breaking changes to cover**:
1. {change_1}
2. {change_2}
3. {change_3}

---

## GitHub Search Queries

Use these queries in Phase 1:

```python
searches = [
    # Direct package searches
    {"query": '"{package_name}"', "language": "{Language}", "min_stars": 2},
    {"query": '"import {package_name}"', "language": "{Language}", "min_stars": 1},

    # Framework-specific
    {"query": '"{package_name}" {framework}', "language": "{Language}", "min_stars": 3},

    # Manifest file searches
    {"query": '"{package_name}" in:file filename:{manifest}', "min_stars": 1},

    # Broader searches
    {"query": "{sdk_name}", "language": "{Language}", "min_stars": 5},
]
```

---

## Notes

### Challenges Anticipated

- {challenge_1}
- {challenge_2}

### Similar SDKs to Reference

- {similar_sdk_1} - for {reason}
- {similar_sdk_2} - for {reason}

### Open Questions

- [ ] {question_1}
- [ ] {question_2}

---

*Research completed on: {YYYY-MM-DD}*
*Researcher: {name}*
