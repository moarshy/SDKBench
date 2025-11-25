# SEM-SIM (Semantic Similarity) Deep Dive

## Table of Contents
1. [Overview](#overview)
2. [Score Composition](#score-composition)
3. [Three-Component Analysis](#three-component-analysis)
4. [Code Walkthrough](#code-walkthrough)
5. [Similarity Algorithms](#similarity-algorithms)
6. [Pattern Matching Logic](#pattern-matching-logic)
7. [Approach Alignment](#approach-alignment)
8. [Results Summary](#results-summary)

## Overview

**SEM-SIM (Semantic Similarity)** measures if the solution semantically matches the expected approach and patterns. It has a **10% weight** in the overall SDK-Bench evaluation, equal to CQ.

The metric evaluates semantic alignment across three dimensions:
- **Code Structure Similarity** (30%): Similar file and directory organization
- **Pattern Matching** (40%): Uses expected SDK patterns and idioms
- **Approach Alignment** (30%): Follows expected implementation philosophy

SEM-SIM is unique because it evaluates whether the solution "thinks" the same way as the expected implementation, not just whether it works.

## Score Composition

```python
# From sdkbench/metrics/sem_sim.py:45-50
# Calculate overall similarity score (weighted average)
overall_similarity = (
    (structure_score * 0.30) +  # 30% weight
    (pattern_score * 0.40) +    # 40% weight
    (approach_score * 0.30)      # 30% weight
)
```

The final score is converted to 0-100 scale:

```python
# From sdkbench/core/result.py:122-125
def model_post_init(self, __context: Any) -> None:
    """Use similarity score as main score."""
    if self.score == 0:
        self.score = self.similarity_score
```

## Three-Component Analysis

### 1. Code Structure Similarity (30% weight)

**Purpose**: Measures how closely the file/directory organization matches expectations.

```python
# sdkbench/metrics/sem_sim.py:59-103
def _check_structure_similarity(self) -> float:
    """Check code structure similarity."""

    # Check file organization
    expected_files = set(expected_structure.get('files', []))
    solution_files = set(self.solution.files.keys())

    # Calculate Jaccard similarity for files
    intersection = len(expected_files.intersection(solution_files))
    union = len(expected_files.union(solution_files))
    file_similarity = intersection / union if union > 0 else 0.0

    # Check directory structure
    expected_dirs = set(expected_structure.get('directories', []))
    solution_dirs = extract_directories_from_files()

    # Calculate directory similarity
    dir_similarity = jaccard_similarity(expected_dirs, solution_dirs)

    # Combine scores: 70% files, 30% directories
    structure_score = (file_similarity * 0.7) + (dir_similarity * 0.3)
```

**Jaccard Similarity Formula**:
```
J(A, B) = |A ∩ B| / |A ∪ B|

Where:
- A = expected file/directory set
- B = solution file/directory set
- Range: 0 (no overlap) to 1 (perfect match)
```

### 2. Pattern Matching (40% weight)

**Purpose**: Verifies the solution uses expected SDK patterns and idioms.

```python
# sdkbench/metrics/sem_sim.py:105-134
def _check_pattern_matching(self) -> float:
    """Check pattern matching against expected patterns."""

    scores = []

    # Check initialization patterns (ClerkProvider, etc.)
    if initialization:
        init_score = self._check_initialization_patterns(initialization)
        scores.append(init_score)

    # Check configuration patterns (env vars, middleware)
    if configuration:
        config_score = self._check_configuration_patterns(configuration)
        scores.append(config_score)

    # Check integration patterns (where SDK is used)
    if integration_points:
        integration_score = self._check_integration_patterns(integration_points)
        scores.append(integration_score)

    # Average all pattern scores
    return sum(scores) / len(scores) if scores else 1.0
```

**Pattern Types Checked**:
- **JSX Components**: `<ClerkProvider>`, `<SignIn>`, etc.
- **Function Calls**: `auth()`, `currentUser()`, etc.
- **Exports**: `export default clerkMiddleware()`
- **Hooks**: `useUser()`, `useAuth()`, etc.

### 3. Approach Alignment (30% weight)

**Purpose**: Evaluates if the solution follows the expected implementation philosophy.

```python
# sdkbench/metrics/sem_sim.py:247-267
def _check_approach_alignment(self) -> float:
    """Check if solution follows expected implementation approach."""

    scores = []

    # Check server vs client component usage
    server_client_score = self._check_server_client_usage()
    scores.append(server_client_score)

    # Check Clerk version patterns (v4 vs v5)
    version_score = self._check_version_patterns()
    scores.append(version_score)

    # Check framework conventions
    conventions_score = self._check_framework_conventions()
    scores.append(conventions_score)

    return sum(scores) / len(scores) if scores else 1.0
```

## Code Walkthrough

### Structure Similarity Deep Dive

```python
# sdkbench/metrics/sem_sim.py:86-92
# Extract directories from file paths
for file_path in solution_files:
    parts = Path(file_path).parts
    if len(parts) > 1:
        # Add all parent directories
        for i in range(1, len(parts)):
            solution_dirs.add('/'.join(parts[:i]))
```

**Example**:
```
File: app/dashboard/page.tsx
Extracted dirs: ['app', 'app/dashboard']
```

### Pattern Matching Deep Dive

#### Initialization Pattern Check
```python
# sdkbench/metrics/sem_sim.py:136-172
def _check_initialization_patterns(self, initialization: Dict) -> float:
    pattern_type = pattern.get('type')
    pattern_name = pattern.get('name')

    if pattern_type == 'jsx_component':
        component = TypeScriptParser.extract_jsx_component_usage(
            file_content, pattern_name
        )
        return 1.0 if component else 0.0

    elif pattern_type == 'function_call':
        calls = TypeScriptParser.extract_function_calls(file_content, pattern_name)
        return 1.0 if calls else 0.0

    elif pattern_type == 'export':
        exported = TypeScriptParser.extract_exported_function(file_content, pattern_name)
        return 1.0 if exported else 0.0
```

#### Configuration Pattern Check
```python
# sdkbench/metrics/sem_sim.py:174-213
def _check_configuration_patterns(self, configuration: Dict) -> float:
    scores = []

    # Check env vars presence
    expected_env = configuration.get('env_vars', [])
    if expected_env:
        solution_env = self.solution.extract_env_vars()
        present_count = count_matching_env_vars()
        env_score = present_count / expected_count
        scores.append(env_score)

    # Check middleware type
    if expected_middleware:
        solution_middleware = self.solution.extract_middleware_config()
        type_match = solution_middleware.get('type') == expected_middleware.get('type')
        scores.append(1.0 if type_match else 0.5)
```

### Approach Alignment Deep Dive

#### Server vs Client Component Check
```python
# sdkbench/metrics/sem_sim.py:269-312
def _check_server_client_usage(self) -> float:
    """Check correct usage of server vs client components."""

    # Identify client components ('use client' directive)
    for file_path, content in self.solution.files.items():
        if TypeScriptParser.has_client_directive(content):
            client_files.append(file_path)

    # Hooks should be in client components
    for file_path in client_files:
        content = self.solution.files[file_path]
        has_hooks = (
            'useUser()' in content or
            'useAuth()' in content or
            'useClerk()' in content
        )
        if has_hooks:
            return 1.0  # Correct usage

    # Server actions should use server-side helpers
    for file_path in server_files:
        if 'auth()' in content:
            return 1.0  # Correct server-side usage
```

#### Version Pattern Check
```python
# sdkbench/metrics/sem_sim.py:314-361
def _check_version_patterns(self) -> float:
    """Check if using correct Clerk version patterns."""

    # Determine Clerk version from package.json
    clerk_pkg = deps.get('@clerk/nextjs', '')
    is_v5 = '5.' in clerk_pkg or '^5' in clerk_pkg

    # Define version-specific patterns
    v5_patterns = ['clerkMiddleware', 'auth()']
    v4_patterns = ['authMiddleware', 'getAuth(']

    # Check pattern usage matches version
    if is_v5:
        if any(p in content for p in v5_patterns):
            pattern_count += 1
    else:
        if any(p in content for p in v4_patterns):
            pattern_count += 1

    return pattern_count / total_files
```

#### Framework Convention Check
```python
# sdkbench/metrics/sem_sim.py:363-404
def _check_framework_conventions(self) -> float:
    scores = []

    # Middleware should be at root
    if has_middleware:
        middleware_at_root = (
            'middleware.ts' in self.solution.files or
            'middleware.js' in self.solution.files
        )
        scores.append(1.0 if middleware_at_root else 0.5)

    # Layout should be in app directory (Next.js App Router)
    if has_layout:
        layout_in_app = any(
            file_path.startswith('app/') and 'layout' in file_path
            for file_path in self.solution.files.keys()
        )
        scores.append(1.0 if layout_in_app else 0.5)

    # Check TypeScript vs JavaScript consistency
    if ts_files and not js_files:
        scores.append(1.0)  # Consistent TypeScript
    elif js_files and not ts_files:
        scores.append(1.0)  # Consistent JavaScript
    else:
        scores.append(0.7)  # Mixed (penalty)
```

## Similarity Algorithms

### Jaccard Similarity
Used for file and directory comparison:
```python
def jaccard_similarity(set_a, set_b):
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0
```

### Binary Pattern Matching
Used for SDK pattern detection:
```python
# Returns 1.0 if pattern found, 0.0 if not
def check_pattern(content, pattern):
    return 1.0 if pattern in content else 0.0
```

### Weighted Average Scoring
Combines multiple sub-scores:
```python
def weighted_average(scores, weights):
    return sum(s * w for s, w in zip(scores, weights))
```

## Pattern Matching Logic

### Expected vs Actual Patterns

| Pattern Type | Expected | Detection Method | Score Impact |
|--------------|----------|------------------|--------------|
| JSX Component | `<ClerkProvider>` | AST parsing | Binary (1.0 or 0.0) |
| Function Call | `auth()` | Regex match | Binary (1.0 or 0.0) |
| Hook Usage | `useUser()` | Pattern extraction | Binary (1.0 or 0.0) |
| Export | `export default` | AST/Regex | Binary (1.0 or 0.0) |

### Pattern Scoring Example

```javascript
// Expected: ClerkProvider in app/layout.tsx
// Solution file: app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>  // ✅ Pattern found: 1.0
      {children}
    </ClerkProvider>
  )
}

// Score calculation:
// Pattern found: 1.0
// In correct file: 1.0
// Combined: 1.0
```

## Approach Alignment

### Similarity Categories

```python
# sdkbench/metrics/sem_sim.py:475-490
if result.score >= 0.90:
    similarity = "Very High"
    description = "Solution closely matches expected approach"
elif result.score >= 0.75:
    similarity = "High"
    description = "Solution generally follows expected approach"
elif result.score >= 0.60:
    similarity = "Moderate"
    description = "Solution partially follows expected approach"
elif result.score >= 0.40:
    similarity = "Low"
    description = "Solution differs from expected approach"
else:
    similarity = "Very Low"
    description = "Solution significantly differs from expected approach"
```

### Real-World Alignment Examples

**High Alignment (>75%)**:
- Uses App Router with `app/` directory
- ClerkProvider wraps children in layout
- Middleware at root level
- Consistent TypeScript usage
- Correct server/client component split

**Low Alignment (<40%)**:
- Mixed Pages/App Router
- Clerk initialization in wrong files
- Inconsistent TypeScript/JavaScript
- Client components using server-only features
- v4 patterns with v5 package

## Results Summary

### Available Results from `/Users/arshath/play/naptha/better-onboarding/SDKBench/results`

Based on the evaluation results:

| Task ID | SEM-SIM Score | Structure | Patterns | Approach | Details |
|---------|---------------|-----------|----------|----------|---------|
| task5_migration_050 | **0.0%** | 0% | 0% | 0% | No similarity detected |
| task1_init_001 | Expected ~70% | Good | Most | Aligned | Standard implementation |
| task2_middleware_020 | Expected ~80% | Good | All | Aligned | Follows conventions |

### Why task5_migration_050 Has 0% SEM-SIM

The 0% score indicates:
- File structure doesn't match expectations
- Expected patterns not found
- Implementation approach differs completely
- Possible reasons:
  - Migration task has different requirements
  - Solution used alternative approach
  - Ground truth mismatch

## Calculation Example

### Full Scoring Walkthrough

**Given Solution**:
```
Files:
- app/layout.tsx (with ClerkProvider)
- middleware.ts (with clerkMiddleware)
- app/page.tsx (with auth())
- .env.local (with keys)
```

**Expected Structure**:
```
Files: [app/layout.tsx, middleware.ts, app/page.tsx]
Directories: [app]
```

**Step 1: Structure Similarity**
```
File Jaccard = 3/3 = 1.0
Dir Jaccard = 1/1 = 1.0
Structure Score = (1.0 * 0.7) + (1.0 * 0.3) = 1.0
```

**Step 2: Pattern Matching**
```
Initialization: ClerkProvider found = 1.0
Configuration: Env vars present = 1.0
Integration: auth() in correct file = 1.0
Pattern Score = (1.0 + 1.0 + 1.0) / 3 = 1.0
```

**Step 3: Approach Alignment**
```
Server/Client: Correct usage = 1.0
Version: v5 patterns with v5 package = 1.0
Conventions: Follows Next.js structure = 1.0
Approach Score = (1.0 + 1.0 + 1.0) / 3 = 1.0
```

**Final Score**:
```
SEM-SIM = (1.0 * 0.30) + (1.0 * 0.40) + (1.0 * 0.30)
        = 0.30 + 0.40 + 0.30
        = 1.0 (100%)
```

## Key Insights

1. **Pattern Matching Dominates**: With 40% weight, correct SDK pattern usage has the biggest impact

2. **Binary Scoring**: Most checks are binary (1.0 or 0.0), making scores discrete rather than continuous

3. **Version Awareness**: The metric adapts expectations based on SDK version (v4 vs v5)

4. **Framework Conventions Matter**: Following Next.js conventions (app router, middleware location) impacts score

5. **Semantic != Functional**: A solution can work perfectly (high F-CORR) but have low semantic similarity if it uses a different approach

## Best Practices for High SEM-SIM

### 1. Match File Structure
```
✅ Expected structure:
app/
  layout.tsx      # ClerkProvider here
  page.tsx        # Public home page
  dashboard/
    page.tsx      # Protected page
middleware.ts     # At root level
```

### 2. Use Correct Patterns
```typescript
// ✅ v5 patterns (if using Clerk v5)
import { auth } from '@clerk/nextjs/server'
export default clerkMiddleware()

// ❌ v4 patterns with v5
import { getAuth } from '@clerk/nextjs/server'
export default authMiddleware()
```

### 3. Follow Framework Conventions
```typescript
// ✅ Client component with hooks
'use client'
import { useUser } from '@clerk/nextjs'

// ❌ Server component with hooks
import { useUser } from '@clerk/nextjs'  // Won't work
```

### 4. Maintain Consistency
```typescript
// ✅ All TypeScript
app/layout.tsx
app/page.tsx
middleware.ts

// ❌ Mixed
app/layout.tsx
app/page.js      // JavaScript mixed in
middleware.ts
```

## Conclusion

SEM-SIM is the most abstract metric in SDK-Bench, measuring not just whether code works but whether it "thinks" like the expected solution. With its three-component structure (30% structure, 40% patterns, 30% approach), it ensures LLM-generated solutions follow established patterns and conventions.

The metric's emphasis on pattern matching (40%) reflects the importance of using SDK idioms correctly. The approach alignment component ensures solutions use modern best practices (server/client components, correct version patterns).

While SEM-SIM has only 10% weight in the overall evaluation, it provides valuable insights into whether an LLM truly understands SDK integration patterns or is just mimicking syntax. A high SEM-SIM score indicates deep understanding of the SDK's design philosophy and intended usage patterns.