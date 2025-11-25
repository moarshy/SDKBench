# Task Types Definition Template

> Use this template to define the 5 task types for a new SDK.
> Each SDK needs 50 samples distributed across 5 task types.
>
> **Important**: Task names are SDK-specific! Only the distribution (15-15-10-7-3) is fixed.

## SDK: {SDK_NAME}

**Language**: {Python/TypeScript/etc.}
**Category**: {Auth/Database/AI/API/etc.}

---

## Distribution Overview

| Task | Name | Count | Difficulty Range |
|------|------|-------|------------------|
| 1 | init | 15 | Easy |
| 2 | {task2_name} | 15 | Easy - Medium |
| 3 | {task3_name} | 10 | Medium |
| 4 | {task4_name} | 7 | Hard |
| 5 | migration | 3 | Hard |

**Total: 50 samples**

### Reference: Task Names by SDK Category

| Category | Task 2 | Task 3 | Task 4 |
|----------|--------|--------|--------|
| Auth (Clerk) | middleware | hooks | complete |
| Database (LanceDB) | data_ops | search | pipeline |
| Payments (Stripe) | charges | webhooks | complete |
| AI/ML (OpenAI) | completions | streaming | pipeline |
| ORM (Prisma) | queries | relations | complete |

---

## Task 1: Initialization (15 samples)

### Description

Basic SDK setup and initialization.

### What It Tests

- Correct imports
- Provider/wrapper setup (if applicable)
- Basic configuration
- Environment variable setup

### Variations

| # | Variation | Framework | Complexity | Description |
|---|-----------|-----------|------------|-------------|
| 001-003 | Minimal | {framework_1} | Easy | Bare minimum setup |
| 004-006 | Standard | {framework_1} | Easy | Common setup pattern |
| 007-009 | Full config | {framework_1} | Easy | With all options |
| 010-012 | Minimal | {framework_2} | Easy | Bare minimum setup |
| 013-015 | Standard | {framework_2} | Easy | Common setup pattern |

### Key Patterns to Verify

```{language}
// Pattern 1: Basic import
{import_pattern}

// Pattern 2: Initialization
{init_pattern}

// Pattern 3: Configuration
{config_pattern}
```

### Input Template

```{language}
// TODO: Initialize {SDK_NAME}
{starter_code_without_sdk}
```

### Expected Output

```{language}
{import_statement}
{initialization_code}
```

### Required Environment Variables

- `{VAR_1}`: {description}
- `{VAR_2}`: {description}

---

## Task 2: {task2_name} (15 samples)

> **Examples**: `middleware` (Clerk), `data_ops` (LanceDB), `charges` (Stripe)

### Description

{Describe the primary operation this SDK performs - this should be the most common use case}

### What It Tests

- {test_point_1}
- {test_point_2}
- {test_point_3}

### Variations

| # | Variation | Operation | Complexity | Description |
|---|-----------|-----------|------------|-------------|
| 016-018 | {op_1} | {operation} | Easy | {description} |
| 019-021 | {op_2} | {operation} | Easy | {description} |
| 022-024 | {op_3} | {operation} | Medium | {description} |
| 025-027 | {op_4} | {operation} | Medium | {description} |
| 028-030 | {op_5} | {operation} | Medium | {description} |

### Key Patterns to Verify

```{language}
// Pattern 1: {description}
{code_pattern_1}

// Pattern 2: {description}
{code_pattern_2}
```

### Input Template

```{language}
// Assume SDK is already initialized
// TODO: Implement {operation}
{starter_code}
```

### Expected Output

```{language}
{complete_code}
```

---

## Task 3: {task3_name} (10 samples)

> **Examples**: `hooks` (Clerk), `search` (LanceDB), `webhooks` (Stripe), `streaming` (OpenAI)

### Description

{Describe the advanced/secondary feature - this should be a commonly used but more complex feature}

### What It Tests

- {test_point_1}
- {test_point_2}
- {test_point_3}

### Variations

| # | Variation | Feature | Complexity | Description |
|---|-----------|---------|------------|-------------|
| 031-033 | {feature_1} | {feature} | Medium | {description} |
| 034-036 | {feature_2} | {feature} | Medium | {description} |
| 037-038 | {feature_3} | {feature} | Medium | {description} |
| 039-040 | {feature_4} | {feature} | Medium-Hard | {description} |

### Key Patterns to Verify

```{language}
// Pattern 1: {description}
{code_pattern_1}

// Pattern 2: {description}
{code_pattern_2}
```

### Prerequisites

- Task 1 initialization complete
- {other_prerequisite}

---

## Task 4: {task4_name} (7 samples)

> **Examples**: `complete` (Clerk), `pipeline` (LanceDB)
>
> This task combines Tasks 1-3 into a full integration.

### Description

Full end-to-end integration combining multiple SDK features.

### What It Tests

- All of Task 1-3 patterns combined
- Error handling
- Production-ready patterns
- Best practices

### Scenarios

| # | Scenario | Components Used | Complexity | Description |
|---|----------|-----------------|------------|-------------|
| 041-042 | {scenario_1} | Init + Task2 | Hard | {description} |
| 043-044 | {scenario_2} | Init + Task2 + Task3 | Hard | {description} |
| 045-046 | {scenario_3} | Full stack | Hard | {description} |
| 047 | {scenario_4} | Full stack + extras | Hard | {description} |

### Example Scenario: {scenario_name}

**Components**:
- Initialization: {details}
- Core Operation: {details}
- Advanced Feature: {details}
- Configuration: {details}

**Input Structure**:
```
input/
├── {file_1}        # Missing {component}
├── {file_2}        # Missing {component}
├── {manifest}      # Without SDK
└── .env.example    # Empty
```

**Expected Structure**:
```
expected/
├── {file_1}        # Complete with {component}
├── {file_2}        # Complete with {component}
├── {manifest}      # With SDK dependency
├── .env.example    # All variables
└── metadata.json   # Ground truth
```

---

## Task 5: Migration (3 samples)

### Description

Migrate from previous SDK version to current version.

### What It Tests

- Understanding of breaking changes
- Ability to update deprecated patterns
- Configuration changes
- Import path changes

### Breaking Changes to Cover

| # | Breaking Change | Old Pattern | New Pattern |
|---|-----------------|-------------|-------------|
| 048 | {change_1} | `{old_code}` | `{new_code}` |
| 049 | {change_2} | `{old_code}` | `{new_code}` |
| 050 | {change_3} | `{old_code}` | `{new_code}` |

### Sample 048: {Change 1}

**Old Code (Input)**:
```{language}
// v{old_version} pattern
{old_code}
```

**New Code (Expected)**:
```{language}
// v{new_version} pattern
{new_code}
```

**Changes Required**:
1. {change_detail_1}
2. {change_detail_2}

### Sample 049: {Change 2}

...

### Sample 050: {Change 3}

...

---

## Naming Convention

### Sample ID Format

```
{sdk}_task{type}_{name}_{sequential_id}
```

### Sequential ID Ranges

| Task | ID Range |
|------|----------|
| 1 | 001-015 |
| 2 | 016-030 |
| 3 | 031-040 |
| 4 | 041-047 |
| 5 | 048-050 |

### Examples

- `{sdk}_task1_init_001`
- `{sdk}_task1_init_015`
- `{sdk}_task2_{core_op}_016`
- `{sdk}_task2_{core_op}_030`
- `{sdk}_task3_{advanced}_031`
- `{sdk}_task4_complete_041`
- `{sdk}_task5_migration_048`

---

## Test Requirements

### Test Framework

- **Python**: pytest
- **TypeScript**: Jest or Vitest
- **Rust**: Built-in test framework

### Test File Naming

| Language | Pattern |
|----------|---------|
| Python | `test_{task_name}.py` |
| TypeScript | `{task_name}.test.ts` |
| Rust | `{task_name}_test.rs` |

### What Each Test Should Verify

1. **Imports present** - SDK is imported correctly
2. **Initialization correct** - SDK is initialized properly
3. **Pattern present** - Key patterns are implemented
4. **No old patterns** - Deprecated patterns removed (for migration)

---

## Checklist Before Building

- [ ] All 5 task types defined
- [ ] Variations cover different frameworks/scenarios
- [ ] Breaking changes identified for Task 5
- [ ] Naming convention documented
- [ ] Test requirements specified
- [ ] Sample count totals 50
