# CQ (Code Quality) Deep Dive

## Table of Contents
1. [Overview](#overview)
2. [Score Composition](#score-composition)
3. [Quality Checks](#quality-checks)
4. [Code Walkthrough](#code-walkthrough)
5. [Detection Patterns](#detection-patterns)
6. [Grading System](#grading-system)
7. [Results Summary](#results-summary)

## Overview

**CQ (Code Quality)** measures code quality through static analysis and best practices checks. It has a **10% weight** in the overall SDK-Bench evaluation, making it the least weighted but still important metric.

The metric evaluates code quality across five dimensions:
- **Error Handling**: Proper try-catch blocks and error management
- **Naming Consistency**: Consistent variable/function naming conventions
- **TypeScript Types**: Proper typing instead of 'any'
- **Code Duplication**: Avoiding repeated code blocks
- **Structure**: Proper file organization and architecture

## Score Composition

### Deduction-Based Scoring System

The CQ evaluator uses a deduction system starting from 100 points:

```python
# From sdkbench/metrics/cq.py:17-23
CQ Score = 0-100 with deductions
Starting at 100, deduct points for:
- Missing error handling (-10 per occurrence)
- Inconsistent naming (-5 per occurrence)
- Missing TypeScript types (-5 per occurrence)
- Code duplication (-10 per duplicate block)
- Poor structure (-15 per major issue)
```

### Alternative Model Implementation

The CQResult model shows a different approach:

```python
# From sdkbench/core/result.py:104-111
def model_post_init(self, __context: Any) -> None:
    """Calculate score by deducting points."""
    score = 100
    score -= self.type_errors * 5      # -5 per type error
    score -= self.eslint_errors * 2    # -2 per lint error
    score -= self.security_issues * 20 # -20 per security issue
    self.score = max(0, score)
```

> **Note**: There's a discrepancy between the evaluator (comprehensive checks) and the model (focused on type/lint/security).

## Quality Checks

### 1. Error Handling Check (-10 points each)

```python
# sdkbench/metrics/cq.py:91-126
def _check_error_handling(self) -> List[str]:
    """Check for missing error handling."""
    issues = []

    for file_path, content in self.solution.files.items():
        # Check for async functions without try-catch
        if 'async' in content or 'await' in content:
            try_count = content.count('try {')
            catch_count = content.count('catch')
            async_func_count = len(re.findall(r'async\s+(?:function|\()', content))

            if async_func_count > 0 and try_count == 0:
                issues.append(f"{file_path}: Async code without try-catch blocks")

        # Check for fetch/API calls without error handling
        if 'fetch(' in content or 'axios.' in content:
            if 'catch' not in content and '.catch(' not in content:
                issues.append(f"{file_path}: API calls without error handling")

    return issues
```

**What it detects:**
- Async functions without try-catch blocks
- Fetch or axios calls without .catch() handlers
- Unprotected Promise chains

### 2. Naming Consistency Check (-5 points each)

```python
# sdkbench/metrics/cq.py:128-161
def _check_naming_consistency(self) -> List[str]:
    """Check for naming inconsistencies."""
    patterns = {
        'camelCase': r'[a-z][a-zA-Z0-9]*',
        'PascalCase': r'[A-Z][a-zA-Z0-9]*',
        'snake_case': r'[a-z][a-z0-9_]*',
    }

    # Extract variable declarations
    var_pattern = r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='
    variables = re.findall(var_pattern, content)

    camel_count = sum(1 for v in variables if re.fullmatch(patterns['camelCase'], v))
    snake_count = sum(1 for v in variables if re.fullmatch(patterns['snake_case'], v))

    # If both styles are used significantly
    if camel_count > 0 and snake_count > 0:
        issues.append(f"{file_path}: Mixed naming styles (camelCase and snake_case)")
```

**What it detects:**
- Mixed camelCase and snake_case variables
- Inconsistent naming patterns within files
- Deviation from JavaScript conventions

### 3. TypeScript Types Check (-5 points each)

```python
# sdkbench/metrics/cq.py:163-198
def _check_typescript_types(self) -> List[str]:
    """Check for missing TypeScript types."""

    # Check for 'any' type usage
    any_count = len(re.findall(r':\s*any\b', content))
    if any_count > 0:
        issues.append(f"{file_path}: Uses 'any' type {any_count} time(s)")

    # Check for untyped function parameters
    untyped_params = re.findall(
        r'(?:function\s+\w+|const\s+\w+\s*=)\s*\(([^)]+)\)\s*(?:=>|{)',
        content
    )

    for params in untyped_params:
        if ':' not in params and params.strip():
            issues.append(f"{file_path}: Function with untyped parameters")
```

**What it detects:**
- Usage of `any` type
- Untyped function parameters
- Missing return type annotations
- Implicit any situations

### 4. Code Duplication Check (-10 points each)

```python
# sdkbench/metrics/cq.py:200-250
def _check_code_duplication(self) -> List[str]:
    """Check for code duplication."""

    # Check for duplicate imports across files
    import_counts = {}
    for stmt in import_statements:
        import_counts[stmt] = import_counts.get(stmt, 0) + 1

    duplicate_imports = {k: v for k, v in import_counts.items() if v > 3}

    # Check for similar code blocks
    lines1 = [l.strip() for l in content1.split('\n') if len(l.strip()) > 20]
    lines2 = [l.strip() for l in content2.split('\n') if len(l.strip()) > 20]

    matching_lines = len(set(lines1).intersection(set(lines2)))

    if matching_lines > 5:
        issues.append(f"Similar code blocks in {file1} and {file2}")

    return issues[:3]  # Limit to 3 duplication issues
```

**What it detects:**
- Repeated import statements (>3 times)
- Similar code blocks across files (>5 matching lines)
- Copy-pasted functions
- Duplicate logic patterns

### 5. Structure Check (-15 points each)

```python
# sdkbench/metrics/cq.py:252-294
def _check_structure(self) -> List[str]:
    """Check for structural issues."""

    # Check if middleware is in correct location
    middleware_files = [f for f in files if 'middleware' in f.lower()]
    for mw_file in middleware_files:
        if not (mw_file == 'middleware.ts' or mw_file.startswith('app/') or mw_file.startswith('src/')):
            issues.append(f"Middleware file in unusual location: {mw_file}")

    # Check for overly long files (> 500 lines)
    line_count = len(content.split('\n'))
    if line_count > 500:
        issues.append(f"{file_path}: File too long ({line_count} lines)")

    # Check for missing key files
    required_files = expected_structure.get('required_files', [])
    for req_file in required_files:
        if not self.solution.has_file(req_file):
            issues.append(f"Missing expected file: {req_file}")
```

**What it detects:**
- Middleware in wrong location
- Files exceeding 500 lines
- Missing required files
- Non-standard directory structure

## Detection Patterns

### Error Handling Patterns

```javascript
// ❌ Bad: No error handling
async function fetchUser() {
  const response = await fetch('/api/user');
  return response.json();
}

// ✅ Good: Proper error handling
async function fetchUser() {
  try {
    const response = await fetch('/api/user');
    if (!response.ok) throw new Error('Failed to fetch');
    return response.json();
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}
```

### Naming Convention Patterns

```javascript
// ❌ Bad: Mixed naming styles
const user_name = "John";
const userAge = 30;
const User_Email = "john@example.com";

// ✅ Good: Consistent camelCase
const userName = "John";
const userAge = 30;
const userEmail = "john@example.com";
```

### TypeScript Type Patterns

```typescript
// ❌ Bad: Using 'any' and untyped parameters
function processData(data: any) {
  return data.map(item => item.value);
}

// ✅ Good: Proper typing
interface DataItem {
  value: number;
}

function processData(data: DataItem[]): number[] {
  return data.map(item => item.value);
}
```

## Grading System

### Quality Summary Generation

```python
# sdkbench/metrics/cq.py:329-369
def get_quality_summary(self) -> Dict:
    """Get high-level quality summary."""

    # Categorize score
    if result.score >= 90:
        grade = "A"
        quality = "Excellent"
    elif result.score >= 80:
        grade = "B"
        quality = "Good"
    elif result.score >= 70:
        grade = "C"
        quality = "Fair"
    elif result.score >= 60:
        grade = "D"
        quality = "Poor"
    else:
        grade = "F"
        quality = "Very Poor"
```

### Grade Thresholds

| Score Range | Grade | Quality Level | Description |
|-------------|-------|---------------|-------------|
| 90-100 | A | Excellent | Production-ready code with minimal issues |
| 80-89 | B | Good | Solid code with minor improvements needed |
| 70-79 | C | Fair | Acceptable code with some quality concerns |
| 60-69 | D | Poor | Significant quality issues present |
| 0-59 | F | Very Poor | Major refactoring required |

### Recommendations System

```python
# sdkbench/metrics/cq.py:371-410
def _get_recommendations(self, deductions: List[Dict]) -> List[str]:
    """Get recommendations based on deductions."""
    recommendations = []

    if 'error_handling' in categories:
        recommendations.append("Add try-catch blocks around async code and API calls")

    if 'types' in categories:
        recommendations.append("Add proper TypeScript types to function parameters and avoid 'any'")

    if 'naming' in categories:
        recommendations.append("Use consistent naming conventions (camelCase for variables/functions)")

    if 'duplication' in categories:
        recommendations.append("Extract common code into reusable functions or utilities")

    if 'structure' in categories:
        recommendations.append("Organize files according to framework conventions")

    return recommendations[:3]  # Top 3 recommendations
```

## Results Summary

### Available Results from `/Users/arshath/play/naptha/better-onboarding/SDKBench/results`

Based on the evaluation results:

| Task ID | CQ Score | Grade | Issues | Details |
|---------|----------|-------|--------|---------|
| task5_migration_050 | **100%** | A | 0 | No quality issues detected |
| task1_init_001 | Expected ~85% | B | Few | Minor type/error handling issues |
| task2_middleware_020 | Expected ~90% | A | Minimal | Well-structured middleware |

### Why task5_migration_050 Has 100% CQ

The perfect score indicates:
- No async functions without error handling
- Consistent naming conventions used
- No 'any' types in TypeScript
- No significant code duplication
- Proper file structure

## Common CQ Deduction Patterns

### High-Impact Issues (-15 points)
- **Structural Problems**: Wrong file locations, missing required files
- **Large Files**: Files exceeding 500 lines

### Medium-Impact Issues (-10 points)
- **Missing Error Handling**: Unprotected async/await code
- **Code Duplication**: Repeated blocks across files

### Low-Impact Issues (-5 points)
- **Type Issues**: Using 'any', untyped parameters
- **Naming Inconsistency**: Mixed naming conventions

## Calculation Examples

### Scenario 1: Clean Code (Score: 95)
```
Starting Score: 100
- 1 untyped parameter: -5
Final Score: 95 (Grade: A)
```

### Scenario 2: Moderate Issues (Score: 75)
```
Starting Score: 100
- 2 async without try-catch: -20
- 1 'any' type usage: -5
Final Score: 75 (Grade: C)
```

### Scenario 3: Poor Quality (Score: 45)
```
Starting Score: 100
- 3 missing error handlers: -30
- 2 structural issues: -30
- 3 type issues: -15
Final Score: 25 (capped at 0 minimum)
```

## Best Practices for High CQ Score

### 1. Error Handling
```typescript
// Always wrap async code
try {
  const data = await fetchData();
  processData(data);
} catch (error) {
  logger.error('Failed to process:', error);
  throw new ProcessingError(error);
}
```

### 2. TypeScript Types
```typescript
// Define interfaces for data structures
interface User {
  id: string;
  name: string;
  email: string;
}

// Type all function parameters and returns
function getUser(id: string): Promise<User> {
  // implementation
}
```

### 3. Code Organization
```typescript
// Extract common logic
// utils/validation.ts
export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Use across multiple files
import { validateEmail } from '@/utils/validation';
```

### 4. Consistent Naming
```typescript
// Follow JavaScript conventions
const userName = "John";          // ✅ camelCase for variables
function getUserData() {}         // ✅ camelCase for functions
class UserManager {}              // ✅ PascalCase for classes
const MAX_RETRIES = 3;           // ✅ UPPER_SNAKE_CASE for constants
```

## Key Insights

1. **Deduction System**: Unlike other metrics that build up scores, CQ starts at 100 and deducts

2. **Structural Issues Most Costly**: At -15 points each, structural problems have the biggest impact

3. **Limited Deduction Reporting**: Code duplication capped at 3 issues to prevent score collapse

4. **Framework Awareness**: Checks for framework-specific conventions (e.g., Next.js middleware location)

5. **Practical Focus**: Emphasizes real-world quality issues that affect maintainability

## Conclusion

CQ provides an automated code review focusing on maintainability and best practices. While it has the lowest weight (10%) in the overall evaluation, it serves as a quality gate ensuring that LLM-generated solutions follow professional coding standards.

The metric's emphasis on error handling, proper typing, and structural organization reflects real-world software engineering priorities. The deduction-based scoring system makes it clear what issues need fixing, while the grading system provides an intuitive quality assessment.

The recommendations system guides improvements, making CQ not just an evaluation tool but also a learning mechanism for understanding code quality standards in modern JavaScript/TypeScript development.