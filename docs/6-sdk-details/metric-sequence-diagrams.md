# Metric Sequence Diagrams

This document provides sequence diagrams showing the flow of each evaluation metric in SDKBench.

---

## Overview

SDKBench has 6 evaluation metrics:

| Metric | Type | What it Measures |
|--------|------|------------------|
| I-ACC | Static | Initialization Correctness |
| C-COMP | Static | Configuration Completeness |
| IPA | Static | Integration Point Accuracy |
| CQ | Static | Code Quality |
| SEM-SIM | Static | Semantic Similarity |
| F-CORR | Dynamic | Functional Correctness (runs tests) |

---

## 1. I-ACC (Initialization Correctness)

Checks if the SDK was initialized correctly in the right file with proper imports and placement.

```
┌─────────┐     ┌──────────────┐     ┌────────────┐     ┌─────────────────┐     ┌────────────┐
│Evaluator│     │IAccEvaluator │     │GroundTruth │     │    Solution     │     │   Parser   │
└────┬────┘     └──────┬───────┘     └─────┬──────┘     └────────┬────────┘     └─────┬──────┘
     │                 │                   │                     │                    │
     │  evaluate()     │                   │                     │                    │
     │────────────────>│                   │                     │                    │
     │                 │                   │                     │                    │
     │                 │ get_initialization()                    │                    │
     │                 │──────────────────>│                     │                    │
     │                 │                   │                     │                    │
     │                 │  {file, imports,  │                     │                    │
     │                 │   pattern, placement}                   │                    │
     │                 │<──────────────────│                     │                    │
     │                 │                   │                     │                    │
     │                 │                   │                     │                    │
     │                 │ ┌─────────────────────────────────────┐ │                    │
     │                 │ │ CHECK 1: File Location (20%)        │ │                    │
     │                 │ └─────────────────────────────────────┘ │                    │
     │                 │                   │                     │                    │
     │                 │ has_file(expected_file)                 │                    │
     │                 │────────────────────────────────────────>│                    │
     │                 │                   │                     │                    │
     │                 │                   │       bool          │                    │
     │                 │<────────────────────────────────────────│                    │
     │                 │                   │                     │                    │
     │                 │ ┌─────────────────────────────────────┐ │                    │
     │                 │ │ CHECK 2: Imports (20%)              │ │                    │
     │                 │ └─────────────────────────────────────┘ │                    │
     │                 │                   │                     │                    │
     │                 │ get_file_content(file)                  │                    │
     │                 │────────────────────────────────────────>│                    │
     │                 │                   │                     │                    │
     │                 │                   │    file_content     │                    │
     │                 │<────────────────────────────────────────│                    │
     │                 │                   │                     │                    │
     │                 │                   │                     │ extract_imports()  │
     │                 │─────────────────────────────────────────────────────────────>│
     │                 │                   │                     │                    │
     │                 │                   │                     │  [imports list]    │
     │                 │<─────────────────────────────────────────────────────────────│
     │                 │                   │                     │                    │
     │                 │  compare expected vs actual imports     │                    │
     │                 │                   │                     │                    │
     │                 │ ┌─────────────────────────────────────┐ │                    │
     │                 │ │ CHECK 3: Pattern (30%)              │ │                    │
     │                 │ └─────────────────────────────────────┘ │                    │
     │                 │                   │                     │                    │
     │                 │  check pattern type (jsx_component,     │                    │
     │                 │  function_call, export, etc.)           │                    │
     │                 │                   │                     │                    │
     │                 │                   │                     │ extract_jsx_component()
     │                 │─────────────────────────────────────────────────────────────>│
     │                 │                   │                     │    or              │
     │                 │                   │                     │ extract_function_calls()
     │                 │<─────────────────────────────────────────────────────────────│
     │                 │                   │                     │                    │
     │                 │ ┌─────────────────────────────────────┐ │                    │
     │                 │ │ CHECK 4: Placement (30%)            │ │                    │
     │                 │ └─────────────────────────────────────┘ │                    │
     │                 │                   │                     │                    │
     │                 │  check placement type (wraps_children,  │                    │
     │                 │  top_level, in_function)                │                    │
     │                 │                   │                     │                    │
     │                 │                   │                     │                    │
     │   IAccResult    │                   │                     │                    │
     │   {score: 0-100}│                   │                     │                    │
     │<────────────────│                   │                     │                    │
     │                 │                   │                     │                    │
```

**Score Calculation:**
```
score = (file_location * 20) + (imports * 20) + (pattern * 30) + (placement * 30)
```

---

## 2. C-COMP (Configuration Completeness)

Checks if all required configuration is present (env vars, dependencies, middleware).

```
┌─────────┐     ┌───────────────┐     ┌────────────┐     ┌──────────┐     ┌───────────┐
│Evaluator│     │CCompEvaluator │     │GroundTruth │     │ Solution │     │ EnvParser │
└────┬────┘     └───────┬───────┘     └─────┬──────┘     └────┬─────┘     └─────┬─────┘
     │                  │                   │                  │                 │
     │  evaluate()      │                   │                  │                 │
     │─────────────────>│                   │                  │                 │
     │                  │                   │                  │                 │
     │                  │ get_configuration()                  │                 │
     │                  │──────────────────>│                  │                 │
     │                  │                   │                  │                 │
     │                  │  {env_vars, deps, │                  │                 │
     │                  │   middleware}     │                  │                 │
     │                  │<──────────────────│                  │                 │
     │                  │                   │                  │                 │
     │                  │ ┌────────────────────────────────┐   │                 │
     │                  │ │ CHECK 1: Env Vars (50%)        │   │                 │
     │                  │ └────────────────────────────────┘   │                 │
     │                  │                   │                  │                 │
     │                  │ get .env file content                │                 │
     │                  │─────────────────────────────────────>│                 │
     │                  │                   │                  │                 │
     │                  │                   │    .env content  │                 │
     │                  │<─────────────────────────────────────│                 │
     │                  │                   │                  │                 │
     │                  │                   │                  │  parse_env_file()
     │                  │────────────────────────────────────────────────────────>│
     │                  │                   │                  │                 │
     │                  │                   │                  │   {VAR: value}  │
     │                  │<────────────────────────────────────────────────────────│
     │                  │                   │                  │                 │
     │                  │  compare: expected_vars ∩ actual_vars│                 │
     │                  │  missing_env_vars = expected - actual│                 │
     │                  │                   │                  │                 │
     │                  │ ┌────────────────────────────────┐   │                 │
     │                  │ │ CHECK 2: Dependencies (30%)    │   │                 │
     │                  │ └────────────────────────────────┘   │                 │
     │                  │                   │                  │                 │
     │                  │ Python: check requirements.txt       │                 │
     │                  │         or pyproject.toml            │                 │
     │                  │ JS/TS:  check package.json           │                 │
     │                  │                   │                  │                 │
     │                  │  compare: expected_deps ∩ actual_deps│                 │
     │                  │                   │                  │                 │
     │                  │ ┌────────────────────────────────┐   │                 │
     │                  │ │ CHECK 3: Middleware (20%)      │   │                 │
     │                  │ └────────────────────────────────┘   │                 │
     │                  │                   │                  │                 │
     │                  │  check middleware file exists        │                 │
     │                  │  check matcher/routes config         │                 │
     │                  │                   │                  │                 │
     │  CCompResult     │                   │                  │                 │
     │  {score, missing}│                   │                  │                 │
     │<─────────────────│                   │                  │                 │
     │                  │                   │                  │                 │
```

**Score Calculation:**
```
score = (env_vars_score * 50) + (deps_score * 30) + (middleware_score * 20)

where each component score = (found / expected) * 100
```

---

## 3. IPA (Integration Point Accuracy)

Measures precision and recall of integration points (files using the SDK).

```
┌─────────┐     ┌─────────────┐     ┌────────────┐     ┌──────────┐     ┌────────┐
│Evaluator│     │IPAEvaluator │     │GroundTruth │     │ Solution │     │ Parser │
└────┬────┘     └──────┬──────┘     └─────┬──────┘     └────┬─────┘     └───┬────┘
     │                 │                  │                  │               │
     │  evaluate()     │                  │                  │               │
     │────────────────>│                  │                  │               │
     │                 │                  │                  │               │
     │                 │ get_integration_points()            │               │
     │                 │─────────────────>│                  │               │
     │                 │                  │                  │               │
     │                 │  [{file, type,   │                  │               │
     │                 │    patterns}]    │                  │               │
     │                 │<─────────────────│                  │               │
     │                 │                  │                  │               │
     │                 │                  │                  │               │
     │                 │ ┌──────────────────────────────────────────────┐    │
     │                 │ │ EXTRACT: Actual Integration Points           │    │
     │                 │ └──────────────────────────────────────────────┘    │
     │                 │                  │                  │               │
     │                 │ get_all_files()  │                  │               │
     │                 │─────────────────────────────────────>│               │
     │                 │                  │                  │               │
     │                 │                  │  {path: content} │               │
     │                 │<─────────────────────────────────────│               │
     │                 │                  │                  │               │
     │                 │  for each file:  │                  │               │
     │                 │                  │                  │ has_sdk_import()
     │                 │──────────────────────────────────────────────────────>│
     │                 │                  │                  │               │
     │                 │                  │                  │     bool      │
     │                 │<──────────────────────────────────────────────────────│
     │                 │                  │                  │               │
     │                 │  actual_points = files with SDK imports             │
     │                 │                  │                  │               │
     │                 │ ┌──────────────────────────────────────────────┐    │
     │                 │ │ CALCULATE: Precision / Recall / F1           │    │
     │                 │ └──────────────────────────────────────────────┘    │
     │                 │                  │                  │               │
     │                 │  expected = set(ground_truth_points)│               │
     │                 │  actual = set(solution_points)      │               │
     │                 │                  │                  │               │
     │                 │  TP = expected ∩ actual             │               │
     │                 │  FP = actual - expected             │               │
     │                 │  FN = expected - actual             │               │
     │                 │                  │                  │               │
     │                 │  precision = TP / (TP + FP)         │               │
     │                 │  recall = TP / (TP + FN)            │               │
     │                 │  F1 = 2 * (P * R) / (P + R)         │               │
     │                 │                  │                  │               │
     │   IPAResult     │                  │                  │               │
     │   {P, R, F1,    │                  │                  │               │
     │    TP, FP, FN}  │                  │                  │               │
     │<────────────────│                  │                  │               │
     │                 │                  │                  │               │
```

**Score Calculation:**
```
F1 = 2 * (precision * recall) / (precision + recall)
score = F1 * 100
```

---

## 4. CQ (Code Quality)

Evaluates code quality through static analysis with deduction-based scoring.

```
┌─────────┐     ┌────────────┐     ┌──────────┐     ┌────────┐
│Evaluator│     │CQEvaluator │     │ Solution │     │ Parser │
└────┬────┘     └─────┬──────┘     └────┬─────┘     └───┬────┘
     │                │                  │               │
     │  evaluate()    │                  │               │
     │───────────────>│                  │               │
     │                │                  │               │
     │                │  deductions = [] │               │
     │                │  score = 100     │               │
     │                │                  │               │
     │                │ ┌──────────────────────────────────────┐
     │                │ │ CHECK 1: Error Handling (-10 each)   │
     │                │ └──────────────────────────────────────┘
     │                │                  │               │
     │                │ get_all_files()  │               │
     │                │─────────────────>│               │
     │                │                  │               │
     │                │  {path: content} │               │
     │                │<─────────────────│               │
     │                │                  │               │
     │                │  for each file:  │               │
     │                │                  │ has_error_handling()
     │                │──────────────────────────────────>│
     │                │                  │               │
     │                │                  │     bool      │
     │                │<──────────────────────────────────│
     │                │                  │               │
     │                │  if missing → deductions.append(-10)
     │                │                  │               │
     │                │ ┌──────────────────────────────────────┐
     │                │ │ CHECK 2: Naming Consistency (-5 each)│
     │                │ └──────────────────────────────────────┘
     │                │                  │               │
     │                │                  │ extract_function_defs()
     │                │──────────────────────────────────>│
     │                │                  │               │
     │                │                  │  [functions]  │
     │                │<──────────────────────────────────│
     │                │                  │               │
     │                │  check: camelCase, snake_case,   │
     │                │         PascalCase consistency   │
     │                │                  │               │
     │                │ ┌──────────────────────────────────────┐
     │                │ │ CHECK 3: TypeScript Types (-5 each)  │
     │                │ └──────────────────────────────────────┘
     │                │                  │               │
     │                │  check for 'any' types           │
     │                │  check for untyped parameters    │
     │                │                  │               │
     │                │ ┌──────────────────────────────────────┐
     │                │ │ CHECK 4: Code Duplication (-10 each) │
     │                │ └──────────────────────────────────────┘
     │                │                  │               │
     │                │  find duplicate code blocks      │
     │                │                  │               │
     │                │ ┌──────────────────────────────────────┐
     │                │ │ CHECK 5: Structure (-15 each)        │
     │                │ └──────────────────────────────────────┘
     │                │                  │               │
     │                │  check file organization         │
     │                │  check middleware placement      │
     │                │                  │               │
     │                │  final_score = max(0, 100 - sum(deductions))
     │                │                  │               │
     │  CQResult      │                  │               │
     │  {score,       │                  │               │
     │   deductions}  │                  │               │
     │<───────────────│                  │               │
     │                │                  │               │
```

**Score Calculation:**
```
Deductions:
- Missing error handling: -10 per occurrence
- Inconsistent naming: -5 per occurrence
- Missing TypeScript types: -5 per occurrence
- Code duplication: -10 per duplicate block
- Poor structure: -15 per major issue

score = max(0, 100 - total_deductions)
```

---

## 5. SEM-SIM (Semantic Similarity)

Evaluates how semantically similar the solution is to the expected approach.

```
┌─────────┐     ┌───────────────┐     ┌────────────┐     ┌──────────┐     ┌────────┐
│Evaluator│     │SemSimEvaluator│     │GroundTruth │     │ Solution │     │ Parser │
└────┬────┘     └───────┬───────┘     └─────┬──────┘     └────┬─────┘     └───┬────┘
     │                  │                   │                  │               │
     │  evaluate()      │                   │                  │               │
     │─────────────────>│                   │                  │               │
     │                  │                   │                  │               │
     │                  │ ┌────────────────────────────────────────────────┐   │
     │                  │ │ CHECK 1: Structure Similarity (30%)            │   │
     │                  │ └────────────────────────────────────────────────┘   │
     │                  │                   │                  │               │
     │                  │ get_expected_files()                 │               │
     │                  │──────────────────>│                  │               │
     │                  │                   │                  │               │
     │                  │   [expected_files]│                  │               │
     │                  │<──────────────────│                  │               │
     │                  │                   │                  │               │
     │                  │ get_all_files()   │                  │               │
     │                  │─────────────────────────────────────>│               │
     │                  │                   │                  │               │
     │                  │                   │  {actual_files}  │               │
     │                  │<─────────────────────────────────────│               │
     │                  │                   │                  │               │
     │                  │  Jaccard similarity:                 │               │
     │                  │  |expected ∩ actual| / |expected ∪ actual|           │
     │                  │                   │                  │               │
     │                  │ ┌────────────────────────────────────────────────┐   │
     │                  │ │ CHECK 2: Pattern Matching (40%)                │   │
     │                  │ └────────────────────────────────────────────────┘   │
     │                  │                   │                  │               │
     │                  │ get_expected_patterns()              │               │
     │                  │──────────────────>│                  │               │
     │                  │                   │                  │               │
     │                  │   [init_pattern,  │                  │               │
     │                  │    config_pattern,│                  │               │
     │                  │    integration]   │                  │               │
     │                  │<──────────────────│                  │               │
     │                  │                   │                  │               │
     │                  │  for each expected_pattern:          │               │
     │                  │                   │                  │ has_pattern()  │
     │                  │─────────────────────────────────────────────────────>│
     │                  │                   │                  │               │
     │                  │                   │                  │     bool      │
     │                  │<─────────────────────────────────────────────────────│
     │                  │                   │                  │               │
     │                  │  matched / total patterns            │               │
     │                  │                   │                  │               │
     │                  │ ┌────────────────────────────────────────────────┐   │
     │                  │ │ CHECK 3: Approach Alignment (30%)              │   │
     │                  │ └────────────────────────────────────────────────┘   │
     │                  │                   │                  │               │
     │                  │  check SDK-specific patterns:        │               │
     │                  │  - lancedb.connect() usage           │               │
     │                  │  - ClerkProvider wrapping            │               │
     │                  │  - server vs client components       │               │
     │                  │                   │                  │               │
     │                  │  check conventions:                  │               │
     │                  │  - 'use client' directive            │               │
     │                  │  - middleware exports                │               │
     │                  │                   │                  │               │
     │  SemSimResult    │                   │                  │               │
     │  {score,         │                   │                  │               │
     │   matched,       │                   │                  │               │
     │   missing}       │                   │                  │               │
     │<─────────────────│                   │                  │               │
     │                  │                   │                  │               │
```

**Score Calculation:**
```
score = (structure_similarity * 30) + (pattern_matching * 40) + (approach_alignment * 30)
```

---

## 6. F-CORR (Functional Correctness)

The only **dynamic** metric - actually runs the code and tests.

```
┌─────────┐     ┌──────────────┐     ┌────────────────┐     ┌─────────────┐     ┌───────────┐
│Evaluator│     │FCorrEvaluator│     │RunnerRegistry  │     │ TestRunner  │     │  pytest/  │
│         │     │              │     │                │     │(Py or TS)   │     │  jest     │
└────┬────┘     └──────┬───────┘     └───────┬────────┘     └──────┬──────┘     └─────┬─────┘
     │                 │                     │                     │                   │
     │  evaluate()     │                     │                     │                   │
     │────────────────>│                     │                     │                   │
     │                 │                     │                     │                   │
     │                 │ ┌─────────────────────────────────────────────────────────┐   │
     │                 │ │ STEP 1: Detect Language & Framework                     │   │
     │                 │ └─────────────────────────────────────────────────────────┘   │
     │                 │                     │                     │                   │
     │                 │ get_runner(solution_dir)                  │                   │
     │                 │────────────────────>│                     │                   │
     │                 │                     │                     │                   │
     │                 │                     │  for each runner:   │                   │
     │                 │                     │  runner.detect()    │                   │
     │                 │                     │────────────────────>│                   │
     │                 │                     │                     │                   │
     │                 │                     │  {detected: bool,   │                   │
     │                 │                     │   language: py/ts,  │                   │
     │                 │                     │   framework: pytest/jest,              │
     │                 │                     │   confidence: 0-1}  │                   │
     │                 │                     │<────────────────────│                   │
     │                 │                     │                     │                   │
     │                 │   best_runner       │                     │                   │
     │                 │<────────────────────│                     │                   │
     │                 │                     │                     │                   │
     │                 │ ┌─────────────────────────────────────────────────────────┐   │
     │                 │ │ STEP 2: Install Dependencies                            │   │
     │                 │ └─────────────────────────────────────────────────────────┘   │
     │                 │                     │                     │                   │
     │                 │ install_dependencies()                    │                   │
     │                 │────────────────────────────────────────────>                  │
     │                 │                     │                     │                   │
     │                 │                     │                     │  pip install -r  │
     │                 │                     │                     │  requirements.txt│
     │                 │                     │                     │  ─────────────────>
     │                 │                     │                     │       or         │
     │                 │                     │                     │  npm install     │
     │                 │                     │                     │  ─────────────────>
     │                 │                     │                     │                   │
     │                 │  DependencyInstallResult                  │                   │
     │                 │<────────────────────────────────────────────                  │
     │                 │                     │                     │                   │
     │                 │  if install failed → return error         │                   │
     │                 │                     │                     │                   │
     │                 │ ┌─────────────────────────────────────────────────────────┐   │
     │                 │ │ STEP 3: Run Tests                                       │   │
     │                 │ └─────────────────────────────────────────────────────────┘   │
     │                 │                     │                     │                   │
     │                 │ run_tests(test_dir) │                     │                   │
     │                 │────────────────────────────────────────────>                  │
     │                 │                     │                     │                   │
     │                 │                     │                     │ python -m pytest │
     │                 │                     │                     │ -v --tb=short    │
     │                 │                     │                     │──────────────────>│
     │                 │                     │                     │       or         │
     │                 │                     │                     │ npm test         │
     │                 │                     │                     │──────────────────>│
     │                 │                     │                     │                   │
     │                 │                     │                     │  raw output      │
     │                 │                     │                     │<──────────────────│
     │                 │                     │                     │                   │
     │                 │ ┌─────────────────────────────────────────────────────────┐   │
     │                 │ │ STEP 4: Parse Test Output                               │   │
     │                 │ └─────────────────────────────────────────────────────────┘   │
     │                 │                     │                     │                   │
     │                 │                     │                     │ _parse_pytest_output()
     │                 │                     │                     │ or               │
     │                 │                     │                     │ _parse_jest_output()
     │                 │                     │                     │                   │
     │                 │                     │                     │  extract:        │
     │                 │                     │                     │  - passed count  │
     │                 │                     │                     │  - failed count  │
     │                 │                     │                     │  - failure details│
     │                 │                     │                     │  - stack traces  │
     │                 │                     │                     │                   │
     │                 │  TestResult         │                     │                   │
     │                 │  {success, passed,  │                     │                   │
     │                 │   failed, failures} │                     │                   │
     │                 │<────────────────────────────────────────────                  │
     │                 │                     │                     │                   │
     │                 │ ┌─────────────────────────────────────────────────────────┐   │
     │                 │ │ STEP 5: Calculate Score                                 │   │
     │                 │ └─────────────────────────────────────────────────────────┘   │
     │                 │                     │                     │                   │
     │                 │  STRICT mode:       │                     │                   │
     │                 │    any failure → score = 0                │                   │
     │                 │    all pass → score = 100                 │                   │
     │                 │                     │                     │                   │
     │                 │  PASS_RATE mode:    │                     │                   │
     │                 │    score = (passed/total) * 100           │                   │
     │                 │                     │                     │                   │
     │  FCorrResult    │                     │                     │                   │
     │  {score,        │                     │                     │                   │
     │   passed,       │                     │                     │                   │
     │   total,        │                     │                     │                   │
     │   failures}     │                     │                     │                   │
     │<────────────────│                     │                     │                   │
     │                 │                     │                     │                   │
```

**Runner Detection Logic:**

```
Python Detection:
├── requirements.txt exists? → confidence +0.25
├── pyproject.toml exists?   → confidence +0.25
├── setup.py exists?         → confidence +0.25
├── test_*.py files exist?   → confidence +0.25
└── conftest.py exists?      → confidence +0.25

TypeScript Detection:
├── package.json exists?     → required
├── jest in deps?            → framework = Jest
├── vitest in deps?          → framework = Vitest
├── mocha in deps?           → framework = Mocha
├── *.test.ts files exist?   → confidence +0.2
└── tsconfig.json exists?    → confidence +0.2
```

**Score Calculation:**
```
STRICT mode (default):
  if any_test_failed:
      score = 0
  else:
      score = 100

PASS_RATE mode:
  score = (tests_passed / tests_total) * 100
```

---

## Complete Evaluation Flow

When `Evaluator.evaluate()` is called, all 6 metrics run:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Evaluator.evaluate()                           │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
   ┌───────────┐             ┌───────────┐             ┌───────────┐
   │  I-ACC    │             │  C-COMP   │             │   IPA     │
   │  (static) │             │  (static) │             │  (static) │
   └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
         │                          │                          │
         ▼                          ▼                          ▼
   ┌───────────┐             ┌───────────┐             ┌───────────┐
   │    CQ     │             │  SEM-SIM  │             │  F-CORR   │
   │  (static) │             │  (static) │             │ (dynamic) │
   └─────┬─────┘             └─────┬─────┘             └─────┬─────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   EvaluationResult    │
                        │                       │
                        │  overall_score =      │
                        │  avg(all 6 metrics)   │
                        └───────────────────────┘
```

**Overall Score:**
```python
overall_score = (i_acc + c_comp + ipa + cq + sem_sim + f_corr) / 6
```

---

## 7. LLM Solution Generation

This diagram shows how solutions are generated from LLM responses before evaluation.

```
┌────────┐     ┌───────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────────────┐
│ Script │     │ PromptBuilder │     │ LLMProvider │     │  Anthropic/ │     │SolutionGenerator  │
│(run.py)│     │               │     │   (base)    │     │   OpenAI    │     │                   │
└───┬────┘     └───────┬───────┘     └──────┬──────┘     └──────┬──────┘     └─────────┬─────────┘
    │                  │                    │                   │                      │
    │ ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ │ STEP 1: Load Sample Metadata                                                           │
    │ └────────────────────────────────────────────────────────────────────────────────────────┘
    │                  │                    │                   │                      │
    │  load metadata.json                   │                   │                      │
    │  load input/ files                    │                   │                      │
    │                  │                    │                   │                      │
    │  sample = {      │                    │                   │                      │
    │    sdk: "lancedb",                    │                   │                      │
    │    task_type: 1, │                    │                   │                      │
    │    description,  │                    │                   │                      │
    │    framework,    │                    │                   │                      │
    │    input_files   │                    │                   │                      │
    │  }               │                    │                   │                      │
    │                  │                    │                   │                      │
    │ ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ │ STEP 2: Build Prompts                                                                  │
    │ └────────────────────────────────────────────────────────────────────────────────────────┘
    │                  │                    │                   │                      │
    │ build_from_metadata(metadata_path, input_dir)             │                      │
    │─────────────────>│                    │                   │                      │
    │                  │                    │                   │                      │
    │                  │ ┌──────────────────────────────────┐   │                      │
    │                  │ │ _build_system_prompt()           │   │                      │
    │                  │ │                                  │   │                      │
    │                  │ │ "You are an expert developer     │   │                      │
    │                  │ │  specializing in {sdk}..."       │   │                      │
    │                  │ │                                  │   │                      │
    │                  │ │ + SDK_CONTEXTS[sdk]              │   │                      │
    │                  │ │   (lancedb patterns, clerk       │   │                      │
    │                  │ │    patterns, etc.)               │   │                      │
    │                  │ │                                  │   │                      │
    │                  │ │ + filepath comment instructions  │   │                      │
    │                  │ └──────────────────────────────────┘   │                      │
    │                  │                    │                   │                      │
    │                  │ ┌──────────────────────────────────┐   │                      │
    │                  │ │ _build_user_prompt()             │   │                      │
    │                  │ │                                  │   │                      │
    │                  │ │ "Task: {task_name}               │   │                      │
    │                  │ │  {description}                   │   │                      │
    │                  │ │                                  │   │                      │
    │                  │ │  Current project files:          │   │                      │
    │                  │ │  === app.py ===                  │   │                      │
    │                  │ │  ```                             │   │                      │
    │                  │ │  {input_file_content}            │   │                      │
    │                  │ │  ```                             │   │                      │
    │                  │ │                                  │   │                      │
    │                  │ │  {task_instructions}             │   │                      │
    │                  │ │                                  │   │                      │
    │                  │ │  Files to output: app.py"        │   │                      │
    │                  │ └──────────────────────────────────┘   │                      │
    │                  │                    │                   │                      │
    │  (system_prompt, │                    │                   │                      │
    │   user_prompt)   │                    │                   │                      │
    │<─────────────────│                    │                   │                      │
    │                  │                    │                   │                      │
    │ ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ │ STEP 3: Call LLM API                                                                   │
    │ └────────────────────────────────────────────────────────────────────────────────────────┘
    │                  │                    │                   │                      │
    │ generate(user_prompt, system_prompt)  │                   │                      │
    │──────────────────────────────────────>│                   │                      │
    │                  │                    │                   │                      │
    │                  │                    │ messages.create() │                      │
    │                  │                    │──────────────────>│                      │
    │                  │                    │                   │                      │
    │                  │                    │                   │  API Request:        │
    │                  │                    │                   │  {                   │
    │                  │                    │                   │    model: "claude-3.5-sonnet",
    │                  │                    │                   │    messages: [...],  │
    │                  │                    │                   │    max_tokens: 4000, │
    │                  │                    │                   │    temperature: 0.1  │
    │                  │                    │                   │  }                   │
    │                  │                    │                   │                      │
    │                  │                    │                   │  ~~~~ LLM thinks ~~~~│
    │                  │                    │                   │                      │
    │                  │                    │   API Response    │                      │
    │                  │                    │<──────────────────│                      │
    │                  │                    │                   │                      │
    │                  │                    │ ┌────────────────────────────────────┐   │
    │                  │                    │ │ Build LLMResponse:                 │   │
    │                  │                    │ │ - content (code)                   │   │
    │                  │                    │ │ - tokens_used                      │   │
    │                  │                    │ │ - cost                             │   │
    │                  │                    │ │ - latency_ms                       │   │
    │                  │                    │ └────────────────────────────────────┘   │
    │                  │                    │                   │                      │
    │  LLMResponse     │                    │                   │                      │
    │<──────────────────────────────────────│                   │                      │
    │                  │                    │                   │                      │
    │ ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ │ STEP 4: Extract Files from Response                                                    │
    │ └────────────────────────────────────────────────────────────────────────────────────────┘
    │                  │                    │                   │                      │
    │ generate_solution(response.content, output_dir, sample_id, model_name)           │
    │─────────────────────────────────────────────────────────────────────────────────>│
    │                  │                    │                   │                      │
    │                  │                    │                   │    ┌────────────────────────┐
    │                  │                    │                   │    │_extract_files_from_    │
    │                  │                    │                   │    │response()              │
    │                  │                    │                   │    │                        │
    │                  │                    │                   │    │ LLM Response:          │
    │                  │                    │                   │    │ ```python              │
    │                  │                    │                   │    │ # filepath: app.py     │
    │                  │                    │                   │    │ import lancedb         │
    │                  │                    │                   │    │ ...                    │
    │                  │                    │                   │    │ ```                    │
    │                  │                    │                   │    │                        │
    │                  │                    │                   │    │ Pattern matching:      │
    │                  │                    │                   │    │ 1. "# filepath: X"     │
    │                  │                    │                   │    │ 2. "// filepath: X"    │
    │                  │                    │                   │    │ 3. "File: X"           │
    │                  │                    │                   │    │ 4. Infer from lang     │
    │                  │                    │                   │    └────────────────────────┘
    │                  │                    │                   │                      │
    │                  │                    │                   │    ┌────────────────────────┐
    │                  │                    │                   │    │_write_file()           │
    │                  │                    │                   │    │                        │
    │                  │                    │                   │    │ Write each extracted   │
    │                  │                    │                   │    │ file to:               │
    │                  │                    │                   │    │ output_dir/            │
    │                  │                    │                   │    │   sample_id/           │
    │                  │                    │                   │    │     model_name/        │
    │                  │                    │                   │    │       app.py           │
    │                  │                    │                   │    └────────────────────────┘
    │                  │                    │                   │                      │
    │                  │                    │                   │    ┌────────────────────────┐
    │                  │                    │                   │    │_save_metadata()        │
    │                  │                    │                   │    │                        │
    │                  │                    │                   │    │ generation_metadata.json
    │                  │                    │                   │    │ {                      │
    │                  │                    │                   │    │   sample_id,           │
    │                  │                    │                   │    │   model,               │
    │                  │                    │                   │    │   generated_at,        │
    │                  │                    │                   │    │   files_generated      │
    │                  │                    │                   │    │ }                      │
    │                  │                    │                   │    │                        │
    │                  │                    │                   │    │ llm_response.txt       │
    │                  │                    │                   │    │ (raw response)         │
    │                  │                    │                   │    └────────────────────────┘
    │                  │                    │                   │                      │
    │  solution_path   │                    │                   │                      │
    │<─────────────────────────────────────────────────────────────────────────────────│
    │                  │                    │                   │                      │
    │ ┌────────────────────────────────────────────────────────────────────────────────────────┐
    │ │ STEP 5: Ready for Evaluation                                                           │
    │ └────────────────────────────────────────────────────────────────────────────────────────┘
    │                  │                    │                   │                      │
    │  Solution directory structure:        │                   │                      │
    │                  │                    │                   │                      │
    │  results/        │                    │                   │                      │
    │  └── lancedb/    │                    │                   │                      │
    │      └── claude-sonnet-4-5/           │                   │                      │
    │          └── solutions/               │                   │                      │
    │              └── lancedb_task1_init_001/                  │                      │
    │                  ├── app.py           │  ← LLM generated  │                      │
    │                  ├── generation_metadata.json             │                      │
    │                  └── llm_response.txt │                   │                      │
    │                  │                    │                   │                      │
    │  → Now Evaluator can run all 6 metrics                   │                      │
    │                  │                    │                   │                      │
```

**Prompt Structure:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SYSTEM PROMPT                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ You are an expert developer specializing in {sdk} integration.              │
│ You are helping integrate {sdk} (version {version}) into a {framework} app. │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ SDK_CONTEXT (from prompt_builder.py)                                    │ │
│ │                                                                         │ │
│ │ LanceDB example:                                                        │ │
│ │ - Connection: db = lancedb.connect("./my_lancedb")                      │ │
│ │ - Create table: db.create_table("name", data)                           │ │
│ │ - Vector search: table.search(query_vector).limit(k).to_pandas()        │ │
│ │ - etc.                                                                  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ Your responses should:                                                      │
│ 1. Provide working code that follows best practices                         │
│ 2. Include all necessary imports                                            │
│ 3. Add appropriate error handling                                           │
│                                                                             │
│ IMPORTANT: Output files with EXACT same filenames as input.                 │
│ Use filepath comments: # filepath: app.py                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                             USER PROMPT                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Task: Initialization                                                        │
│ {description from metadata.json}                                            │
│                                                                             │
│ Current project files:                                                      │
│                                                                             │
│ === app.py ===                                                              │
│ ```                                                                         │
│ # TODO: Initialize LanceDB connection                                       │
│ ```                                                                         │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ TASK_INSTRUCTIONS (from prompt_builder.py)                              │ │
│ │                                                                         │ │
│ │ For this initialization task:                                           │ │
│ │ 1. Import lancedb library                                               │ │
│ │ 2. Create database connection with lancedb.connect()                    │ │
│ │ 3. Handle connection path appropriately                                 │ │
│ │ 4. Verify connection is working                                         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ Please provide the complete solution by modifying the input files above.    │
│ Files to output: app.py                                                     │
│                                                                             │
│ CRITICAL: Each code block MUST start with a filepath comment.               │
└─────────────────────────────────────────────────────────────────────────────┘
```

**File Extraction Patterns:**

```
LLM Response Content:
─────────────────────────────────────────────────────────
Here's the solution:

```python
# filepath: app.py                    ← Pattern 1: # filepath: X
import lancedb

def get_database():
    db = lancedb.connect("./my_lancedb")
    return db

def main():
    db = get_database()
    print(db.table_names())

if __name__ == "__main__":
    main()
```

```python
# filepath: requirements.txt          ← Pattern 1 (also works for non-code)
lancedb>=0.4.0
pandas
```
─────────────────────────────────────────────────────────

                    │
                    ▼

Extracted Files:
─────────────────────────────────────────────────────────
{
  "app.py": "import lancedb\n\ndef get_database():\n...",
  "requirements.txt": "lancedb>=0.4.0\npandas"
}
─────────────────────────────────────────────────────────
```

**Complete Generation → Evaluation Pipeline:**

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   samples/   │     │PromptBuilder │     │  LLM API     │     │  Solution    │
│              │     │              │     │              │     │  Generator   │
│ metadata.json│────>│ Build system │────>│ Generate     │────>│ Extract      │
│ input/       │     │ + user prompt│     │ response     │     │ files        │
└──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                      │
                                                                      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   results/   │     │  Evaluator   │     │  6 Metrics   │     │  Solution    │
│              │     │              │     │              │     │  Directory   │
│ metrics/     │<────│ Run all      │<────│ I-ACC,C-COMP │<────│              │
│ f_corr.json  │     │ evaluations  │     │ IPA,CQ,SEM   │     │ app.py       │
│ etc.         │     │              │     │ F-CORR       │     │ metadata     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```
