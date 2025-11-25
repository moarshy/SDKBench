# SDKBench Revised Metrics System

## Overview

This document describes the enhanced metrics system for SDKBench, including per-sample detailed breakdowns, weighted overall scoring, and F-CORR integration.

---

## Metrics Summary

| Metric | Full Name | Description | Score Range |
|--------|-----------|-------------|-------------|
| **I-ACC** | Initialization Accuracy | Correct SDK initialization patterns | 0-100 |
| **C-COMP** | Configuration Completeness | Required config/env vars present | 0-100 |
| **IPA** | Integration Point Accuracy | Correct integration points (F1 score) | 0-100 |
| **CQ** | Code Quality | Best practices, no errors | 0-100 |
| **SEM-SIM** | Semantic Similarity | Matches expected implementation | 0-100 |
| **F-CORR** | Functional Correctness | Tests pass (strict: all or nothing) | 0 or 100 |

---

## Weighted Overall Score

### Without F-CORR (5 metrics)

| Metric | Weight |
|--------|--------|
| I-ACC | 20% |
| C-COMP | 20% |
| IPA | 20% |
| CQ | 20% |
| SEM-SIM | 20% |

### With F-CORR Enabled (6 metrics)

| Metric | Weight |
|--------|--------|
| I-ACC | 15% |
| C-COMP | 15% |
| IPA | 15% |
| **F-CORR** | **25%** |
| CQ | 15% |
| SEM-SIM | 15% |

> **Rationale**: F-CORR receives higher weight (25%) because it tests actual functional correctness - whether the code actually works. This emphasizes that working code is the most important outcome.

---

## Grade Scale

| Grade | Score Range |
|-------|-------------|
| A | >= 90 |
| B | >= 80 |
| C | >= 70 |
| D | >= 60 |
| F | < 60 |

---

## Results Directory Structure

### New Per-Sample Metrics Folder

```
results/
├── {sdk}/
│   ├── {model}/
│   │   └── solutions/
│   │       └── {sample_id}/
│   │           ├── app/                      # Generated solution files
│   │           ├── middleware.ts
│   │           ├── package.json
│   │           ├── generation_metadata.json
│   │           └── metrics/                  # NEW: Per-sample metrics
│   │               ├── i_acc.json
│   │               ├── c_comp.json
│   │               ├── ipa.json
│   │               ├── cq.json
│   │               ├── sem_sim.json
│   │               ├── f_corr.json           # Only if F-CORR enabled
│   │               └── summary.json          # Overall score
│   └── {model}_summary.json                  # SDK-Model aggregate
└── overall_report_{timestamp}.json           # Cross-SDK/model report
```

---

## Detailed Metric Schemas

### I-ACC (Initialization Accuracy)

**File**: `metrics/i_acc.json`

```json
{
  "score": 100.0,
  "file_location_correct": true,
  "imports_correct": true,
  "pattern_correct": true,
  "placement_correct": true,
  "details": {
    "expected_file": "app/layout.tsx",
    "found_in_file": "app/layout.tsx",
    "required_imports": ["ClerkProvider", "@clerk/nextjs"],
    "found_imports": ["ClerkProvider", "@clerk/nextjs"],
    "missing_imports": [],
    "pattern_used": "provider_wrapper",
    "expected_pattern": "provider_wrapper"
  }
}
```

**Scoring Breakdown**:
- File location correct: 20%
- Imports correct: 20%
- Pattern correct: 30%
- Placement correct: 30%

---

### C-COMP (Configuration Completeness)

**File**: `metrics/c_comp.json`

```json
{
  "score": 75.0,
  "env_vars_score": 1.0,
  "provider_props_score": 0.5,
  "middleware_config_score": 1.0,
  "details": {
    "required_env_vars": [
      "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
      "CLERK_SECRET_KEY"
    ],
    "found_env_vars": [
      "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
      "CLERK_SECRET_KEY"
    ],
    "missing_env_vars": [],
    "required_deps": ["@clerk/nextjs"],
    "found_deps": ["@clerk/nextjs"],
    "missing_deps": [],
    "middleware_configured": true
  }
}
```

**Scoring Breakdown**:
- Environment variables: 50%
- Dependencies/Provider props: 30%
- Middleware configuration: 20%

---

### IPA (Integration Point Accuracy)

**File**: `metrics/ipa.json`

```json
{
  "score": 85.0,
  "precision": 0.9,
  "recall": 0.8,
  "f1": 0.85,
  "details": {
    "true_positives": [
      "app/layout.tsx",
      "middleware.ts"
    ],
    "false_positives": [],
    "false_negatives": [
      "app/sign-in/page.tsx"
    ],
    "expected_files": [
      "app/layout.tsx",
      "middleware.ts",
      "app/sign-in/page.tsx"
    ],
    "found_files": [
      "app/layout.tsx",
      "middleware.ts"
    ]
  }
}
```

**Scoring**: F1 score * 100

---

### CQ (Code Quality)

**File**: `metrics/cq.json`

```json
{
  "score": 100.0,
  "type_errors": 0,
  "eslint_errors": 0,
  "security_issues": 0,
  "details": {
    "type_error_list": [],
    "eslint_error_list": [],
    "security_issue_list": [],
    "warnings": []
  }
}
```

**Scoring**: Starts at 100, deductions:
- Type errors: -5 each
- ESLint errors: -2 each
- Security issues: -20 each

---

### SEM-SIM (Semantic Similarity)

**File**: `metrics/sem_sim.json`

```json
{
  "score": 70.0,
  "structure_score": 0.8,
  "pattern_score": 0.6,
  "approach_score": 0.7,
  "details": {
    "pattern_match": true,
    "approach_match": true,
    "matched_patterns": [
      "clerk_provider_wrapper",
      "middleware_auth_check"
    ],
    "missing_patterns": [
      "sign_in_redirect"
    ],
    "structure_similarity": 0.8
  }
}
```

**Scoring Breakdown**:
- Structure similarity: 30%
- Pattern matching: 40%
- Approach alignment: 30%

---

### F-CORR (Functional Correctness)

**File**: `metrics/f_corr.json`

```json
{
  "score": 100.0,
  "tests_passed": 3,
  "tests_failed": 0,
  "tests_total": 3,
  "tests_skipped": 0,
  "pass_rate": 100.0,
  "duration": 2.5,
  "language": "typescript",
  "framework": "jest",
  "details": {
    "test_output": "PASS tests/init.test.ts\n  ✓ should have ClerkProvider\n  ✓ should have @clerk/nextjs\n  ✓ should have env vars",
    "failed_tests": [],
    "error_messages": []
  }
}
```

**Scoring**: Strict binary
- All tests pass: 100
- Any test fails: 0

---

### Summary (Overall Score)

**File**: `metrics/summary.json`

```json
{
  "sample_id": "task1_init_001",
  "timestamp": "2025-11-25T15:30:00.000Z",
  "overall_score": 87.5,
  "grade": "B",
  "f_corr_enabled": true,
  "metrics": {
    "i_acc": 100.0,
    "c_comp": 75.0,
    "ipa": 85.0,
    "cq": 100.0,
    "sem_sim": 70.0,
    "f_corr": 100.0
  },
  "weights_used": {
    "i_acc": 0.15,
    "c_comp": 0.15,
    "ipa": 0.15,
    "cq": 0.15,
    "sem_sim": 0.15,
    "f_corr": 0.25
  },
  "score_calculation": {
    "i_acc": "100.0 × 0.15 = 15.0",
    "c_comp": "75.0 × 0.15 = 11.25",
    "ipa": "85.0 × 0.15 = 12.75",
    "cq": "100.0 × 0.15 = 15.0",
    "sem_sim": "70.0 × 0.15 = 10.5",
    "f_corr": "100.0 × 0.25 = 25.0",
    "total": "87.5"
  }
}
```

---

## SDK-Model Summary Schema

**File**: `results/{sdk}/{model}_summary.json`

```json
{
  "sdk": "clerk",
  "model": "claude-sonnet-4-5",
  "timestamp": "2025-11-25T14:11:09.000Z",
  "f_corr_enabled": true,
  "total_samples": 50,
  "generation": {
    "success": 50,
    "failed": 0
  },
  "evaluation": {
    "success": 50,
    "failed": 0
  },
  "average_metrics": {
    "i_acc": 100.0,
    "c_comp": 78.0,
    "ipa": 65.5,
    "cq": 100.0,
    "sem_sim": 73.9,
    "f_corr": 80.0,
    "overall": 82.3
  },
  "samples": [
    {
      "sample_id": "task1_init_001",
      "generation": { "success": true, "error": null },
      "evaluation": { "success": true, "error": null },
      "metrics": {
        "i_acc": 100.0,
        "c_comp": 75.0,
        "ipa": 85.0,
        "cq": 100.0,
        "sem_sim": 70.0,
        "f_corr": 100.0
      },
      "overall_score": 87.5,
      "grade": "B"
    }
  ]
}
```

---

## Overall Report Schema

**File**: `results/overall_report_{timestamp}.json`

```json
{
  "timestamp": "2025-11-25T14:46:49.000Z",
  "elapsed_seconds": 156.5,
  "f_corr_enabled": true,
  "models": ["claude-sonnet-4-5", "gpt-4o"],
  "sdks": ["clerk", "lancedb"],
  "total_evaluations": 200,
  "by_sdk": {
    "clerk": {
      "total": 100,
      "gen_success": 100,
      "eval_success": 100,
      "average_metrics": {
        "i_acc": 100.0,
        "c_comp": 78.0,
        "ipa": 65.5,
        "cq": 100.0,
        "sem_sim": 73.9,
        "f_corr": 80.0,
        "overall": 82.3
      }
    }
  },
  "by_model": {
    "claude-sonnet-4-5": {
      "total": 100,
      "gen_success": 100,
      "eval_success": 100,
      "average_metrics": { "...": "..." }
    }
  },
  "by_sdk_model": {
    "clerk/claude-sonnet-4-5": {
      "total": 50,
      "gen_success": 50,
      "eval_success": 50,
      "average_metrics": { "...": "..." }
    }
  }
}
```

---

## Usage

### Run Evaluation with F-CORR

```bash
# Full evaluation with F-CORR enabled
python scripts/run.py --sdk clerk --model claude-sonnet-4-5 --run-fcorr

# Without F-CORR (faster, static analysis only)
python scripts/run.py --sdk clerk --model claude-sonnet-4-5
```

### View Per-Sample Metrics

```bash
# View summary for a specific sample
cat results/clerk/claude-sonnet-4-5/solutions/task1_init_001/metrics/summary.json

# View detailed F-CORR results
cat results/clerk/claude-sonnet-4-5/solutions/task1_init_001/metrics/f_corr.json
```

### Compare Results

```bash
# View SDK-Model aggregate
cat results/clerk/claude-sonnet-4-5_summary.json

# View cross-SDK report
cat results/overall_report_*.json
```

---

## Implementation Notes

1. **IPA Normalization**: IPA is stored as F1 score (0-1) internally but displayed as 0-100 in summaries
2. **F-CORR Strict Scoring**: Binary scoring ensures only fully working solutions get credit
3. **Backward Compatibility**: Existing results without metrics folders remain unchanged
4. **Missing Metrics**: If a metric fails to evaluate, it's excluded from overall score calculation
