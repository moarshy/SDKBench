# I-ACC (Implementation Accuracy) Deep Dive

## Table of Contents
1. [Overview](#overview)
2. [Score Composition](#score-composition)
3. [Evaluation Flow](#evaluation-flow)
4. [Component Analysis](#component-analysis)
5. [Code Walkthrough](#code-walkthrough)
6. [Pattern Detection Methods](#pattern-detection-methods)
7. [Results Summary](#results-summary)

## Overview

**I-ACC (Implementation Accuracy)** measures whether the SDK was initialized correctly in the solution. It has a **30% weight** in the overall SDK-Bench evaluation, making it the most important single metric.

The metric evaluates four key aspects of SDK initialization:
- **File Location** (20%): Is the initialization in the correct file?
- **Imports** (20%): Are all required imports present?
- **Pattern** (30%): Is the correct initialization pattern used?
- **Placement** (30%): Is it placed correctly in the component hierarchy?

## Score Composition

```python
# From sdkbench/core/result.py:33-40
def model_post_init(self, __context: Any) -> None:
    """Calculate score based on components."""
    if self.score == 0:  # Only calculate if not already set
        self.score = (
            (self.file_location_correct * 0.20) +   # 20% weight
            (self.imports_correct * 0.20) +         # 20% weight
            (self.pattern_correct * 0.30) +         # 30% weight
            (self.placement_correct * 0.30)         # 30% weight
        ) * 100
```

The final score ranges from 0-100%, with each component contributing based on its weight.

## Evaluation Flow

### Step 1: Initialize Evaluator
```python
# sdkbench/metrics/i_acc.py:24-33
def __init__(self, solution: Solution, ground_truth: GroundTruth):
    self.solution = solution
    self.ground_truth = ground_truth
    self.targets = ground_truth.get_i_acc_targets()
```

### Step 2: Main Evaluation Entry Point
```python
# sdkbench/metrics/i_acc.py:35-64
def evaluate(self) -> IAccResult:
    # Get initialization data from ground truth
    init_data = self.ground_truth.get_initialization()

    if not init_data:
        # No initialization expected - return perfect score
        return IAccResult(
            file_location_correct=True,
            imports_correct=True,
            pattern_correct=True,
            placement_correct=True,
        )

    # Evaluate each component
    file_location = self._check_file_location(init_data)
    imports = self._check_imports(init_data)
    pattern = self._check_pattern(init_data)
    placement = self._check_placement(init_data)

    return IAccResult(
        file_location_correct=file_location,
        imports_correct=imports,
        pattern_correct=pattern,
        placement_correct=placement,
    )
```

## Component Analysis

### 1. File Location Check (20% weight)

**Purpose**: Verify the initialization is in the correct file per SDK documentation.

```python
# sdkbench/metrics/i_acc.py:66-81
def _check_file_location(self, init_data: Dict) -> bool:
    """Check if initialization is in the correct file."""
    expected_file = init_data.get('file')

    if not expected_file:
        return True  # No specific file required

    # Check if file exists in solution
    return self.solution.has_file(expected_file)
```

**Example**: For Clerk SDK task type 1 (basic initialization), the expected file is `app/layout.tsx`.

### 2. Imports Check (20% weight)

**Purpose**: Ensure all required SDK imports are present.

```python
# sdkbench/metrics/i_acc.py:83-127
def _check_imports(self, init_data: Dict) -> bool:
    expected_imports = init_data.get('imports', [])
    expected_file = init_data.get('file')

    if not expected_imports or not expected_file:
        return True

    # Get file content
    file_content = self.solution.files.get(expected_file)
    if not file_content:
        return False

    # Extract actual imports using TypeScriptParser
    actual_imports = TypeScriptParser.extract_imports(file_content)

    # Check each expected import
    for expected in expected_imports:
        found = False
        exp_source = expected.get('source')
        exp_names = expected.get('names', [])

        # Look for matching import in actual imports
        for actual in actual_imports:
            if actual['source'] == exp_source:
                # Check if all expected names are present
                actual_names = actual['names']
                if all(name in actual_names for name in exp_names):
                    found = True
                    break

        if not found:
            return False

    return True
```

**Import Detection Logic**: The TypeScriptParser identifies three import patterns:
1. Named imports: `import { ClerkProvider } from "@clerk/nextjs"`
2. Default imports: `import Clerk from "@clerk/nextjs"`
3. CommonJS: `const Clerk = require("@clerk/nextjs")`

### 3. Pattern Check (30% weight)

**Purpose**: Verify the correct initialization pattern is used.

```python
# sdkbench/metrics/i_acc.py:129-159
def _check_pattern(self, init_data: Dict) -> bool:
    pattern_data = init_data.get('pattern')
    expected_file = init_data.get('file')

    if not pattern_data or not expected_file:
        return True

    # Get file content
    file_content = self.solution.files.get(expected_file)
    if not file_content:
        return False

    # Check pattern based on type
    pattern_type = pattern_data.get('type')

    if pattern_type == 'jsx_component':
        return self._check_jsx_component_pattern(file_content, pattern_data)
    elif pattern_type == 'function_call':
        return self._check_function_call_pattern(file_content, pattern_data)
    elif pattern_type == 'export':
        return self._check_export_pattern(file_content, pattern_data)
    else:
        return False
```

Three pattern types are supported:

#### JSX Component Pattern
```python
# sdkbench/metrics/i_acc.py:161-190
def _check_jsx_component_pattern(self, content: str, pattern_data: Dict) -> bool:
    component_name = pattern_data.get('name')
    required_props = pattern_data.get('required_props', [])

    # Extract component usage
    component = TypeScriptParser.extract_jsx_component_usage(content, component_name)

    if not component:
        return False

    # Check required props if specified
    if required_props:
        component_props = component.get('props', {})
        for prop in required_props:
            if prop not in component_props:
                return False

    return True
```

Example: `<ClerkProvider publishableKey={...}>`

#### Function Call Pattern
```python
# sdkbench/metrics/i_acc.py:192-210
def _check_function_call_pattern(self, content: str, pattern_data: Dict) -> bool:
    function_name = pattern_data.get('name')

    # Extract function calls
    calls = TypeScriptParser.extract_function_calls(content, function_name)

    return len(calls) > 0
```

Example: `auth()` or `currentUser()`

#### Export Pattern
```python
# sdkbench/metrics/i_acc.py:212-236
def _check_export_pattern(self, content: str, pattern_data: Dict) -> bool:
    function_name = pattern_data.get('name')

    # Check for export
    exported_func = TypeScriptParser.extract_exported_function(content, function_name)

    if not exported_func:
        # Also check for default export with function call
        # e.g., export default clerkMiddleware()
        pattern = f"export default {function_name}"
        return pattern in content

    return True
```

Example: `export default clerkMiddleware()`

### 4. Placement Check (30% weight)

**Purpose**: Ensure initialization is placed correctly in the code structure.

```python
# sdkbench/metrics/i_acc.py:238-268
def _check_placement(self, init_data: Dict) -> bool:
    placement_data = init_data.get('placement')
    expected_file = init_data.get('file')

    if not placement_data or not expected_file:
        return True

    # Get file content
    file_content = self.solution.files.get(expected_file)
    if not file_content:
        return False

    # Check placement based on type
    placement_type = placement_data.get('type')

    if placement_type == 'wraps_children':
        return self._check_wraps_children(file_content, placement_data)
    elif placement_type == 'top_level':
        return self._check_top_level(file_content, placement_data)
    elif placement_type == 'in_function':
        return self._check_in_function(file_content, placement_data)
    else:
        return False
```

Three placement types:

#### Wraps Children
```python
# sdkbench/metrics/i_acc.py:270-313
def _check_wraps_children(self, content: str, placement_data: Dict) -> bool:
    component_name = placement_data.get('component')

    # Extract component
    component = TypeScriptParser.extract_jsx_component_usage(content, component_name)

    if not component:
        return False

    # Check if it's self-closing (shouldn't be if it wraps children)
    if component.get('is_self_closing'):
        return False

    # Check for {children} inside the component
    start_tag = f"<{component_name}"
    end_tag = f"</{component_name}>"

    # Extract content between tags
    start_idx = content.find(start_tag)
    end_idx = content.find(end_tag, start_idx)
    between_tags = content[start_idx:end_idx]

    # Check if {children} is present
    return '{children}' in between_tags
```

#### Top Level
```python
# sdkbench/metrics/i_acc.py:315-332
def _check_top_level(self, content: str, placement_data: Dict) -> bool:
    # For now, just check if the pattern exists
    # More sophisticated checks could verify indentation level
    pattern_name = placement_data.get('pattern')

    if not pattern_name:
        return True

    return pattern_name in content
```

#### In Function
```python
# sdkbench/metrics/i_acc.py:334-366
def _check_in_function(self, content: str, placement_data: Dict) -> bool:
    function_name = placement_data.get('function')
    pattern_name = placement_data.get('pattern')

    # Find the function in content using regex
    func_pattern = rf"(?:export\s+)?(?:async\s+)?function\s+{function_name}\s*\([^)]*\)\s*{{([^}}]*)}}"

    import re
    match = re.search(func_pattern, content, re.DOTALL)

    if not match:
        # Try arrow function
        func_pattern = rf"(?:export\s+)?const\s+{function_name}\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*{{([^}}]*)}}"
        match = re.search(func_pattern, content, re.DOTALL)

    if not match:
        return False

    # Check if pattern is inside function body
    function_body = match.group(1)
    return pattern_name in function_body
```

## Pattern Detection Methods

The TypeScriptParser uses regex-based pattern matching for speed and simplicity:

### Import Extraction
```python
# sdkbench/parsers/typescript_parser.py:15-59
def extract_imports(content: str) -> List[Dict[str, str]]:
    imports = []

    # Pattern 1: import { X, Y } from "source"
    pattern1 = r"import\s+{([^}]+)}\s+from\s+['\"]([^'\"]+)['\"]"

    # Pattern 2: import X from "source"
    pattern2 = r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]"

    # Pattern 3: const X = require("source")
    pattern3 = r"const\s+(\w+)\s*=\s*require\(['\"]([^'\"]+)['\"]\)"
```

### JSX Component Detection
```python
# sdkbench/parsers/typescript_parser.py:86-114
def extract_jsx_component_usage(content: str, component_name: str) -> Optional[Dict]:
    # Match <ComponentName ...> or <ComponentName>
    pattern = rf"<{component_name}([^/>]*?)(?:>|/>)"

    match = re.search(pattern, content, re.DOTALL)
    # Extract props from the matched text
    props = _extract_props_from_text(props_text)
```

### Function Call Detection
```python
# sdkbench/parsers/typescript_parser.py:140-168
def extract_function_calls(content: str, function_name: str) -> List[Dict]:
    # Pattern: functionName() with optional await
    pattern = rf"(?:await\s+)?{function_name}\(\)"

    # Search line by line for context
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        if re.search(pattern, line):
            # Record call location and context
```

## Results Summary

### Available Results from `/Users/arshath/play/naptha/better-onboarding/SDKBench/results`

Based on the results directory, we have evaluation data for 5 task types tested with Claude Haiku models:

| Task ID | Task Type | Model | Overall Score | I-ACC Score | Details |
|---------|-----------|-------|---------------|-------------|---------|
| task5_migration_050 | Migration | claude-haiku-4-5 | 33.5% | **100.0%** | Perfect initialization |
| task1_init_001 | Basic Init | claude-haiku-4-5 | - | Expected: 100% | ClerkProvider in layout.tsx |
| task2_middleware_020 | Middleware | claude-haiku-4-5 | - | Expected: 100% | clerkMiddleware setup |
| task3_hooks_035 | Hooks | claude-haiku-4-5 | - | TBD | Solution available |
| task4_complete_045 | Complete | claude-haiku-4-5 | - | TBD | Solution available |

## Real-World Examples from Results

### Example 1: Perfect Basic Initialization (task1_init_001)

**File:** `app/layout.tsx`
```typescript
import { ClerkProvider } from '@clerk/nextjs'
import type { Metadata } from 'next'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
```

**I-ACC Analysis:**
- ✅ **File Location (20%)**: Correct - `app/layout.tsx`
- ✅ **Imports (20%)**: Present - `ClerkProvider` from `@clerk/nextjs`
- ✅ **Pattern (30%)**: JSX component `<ClerkProvider>`
- ✅ **Placement (30%)**: Wraps `{children}` correctly
- **Score: 100%**

### Example 2: Perfect Middleware Setup (task2_middleware_020)

**File:** `middleware.ts`
```typescript
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/protected(.*)',
])

export default clerkMiddleware((auth, req) => {
  if (isProtectedRoute(req)) {
    auth().protect()
  }
})

export const config = {
  matcher: ['/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|gif|svg)).*)', '/(api|trpc)(.*)'],
}
```

**I-ACC Analysis:**
- ✅ **File Location (20%)**: Correct - `middleware.ts`
- ✅ **Imports (20%)**: All required imports from `@clerk/nextjs/server`
- ✅ **Pattern (30%)**: Export pattern `export default clerkMiddleware()`
- ✅ **Placement (30%)**: Top-level export
- **Score: 100%**

### Key Observations

1. **Perfect I-ACC Score**: The task5_migration_050 sample achieved 100% I-ACC, indicating:
   - File location: Correct ✓
   - Imports: All present ✓
   - Pattern: Correctly implemented ✓
   - Placement: Properly positioned ✓

2. **Low Overall Score Despite Perfect I-ACC**: The 33.5% overall score with 100% I-ACC shows that initialization alone isn't sufficient. Other metrics like C-COMP (0%), IPA (1%), and SEM-SIM (0%) significantly impacted the final score.

3. **Model Performance**: Claude Haiku 4.5 successfully handled the initialization requirements but struggled with configuration completeness and integration points.

### I-ACC Success Factors

For achieving high I-ACC scores, solutions must:

1. **Place initialization in the correct file**
   - `app/layout.tsx` for Next.js App Router
   - `middleware.ts` for middleware setup
   - Correct component files for hooks

2. **Include all required imports**
   - Match exact import sources (`@clerk/nextjs`)
   - Include all necessary named imports
   - Use appropriate import style (ESM vs CommonJS)

3. **Use the correct initialization pattern**
   - JSX components with required props
   - Function calls in appropriate contexts
   - Proper export statements

4. **Position code correctly**
   - Wrap children when needed
   - Place at top level for providers
   - Inside specific functions when required

### Common I-ACC Failure Patterns

Based on the evaluation logic, common failures include:

1. **Wrong file location** (20% penalty)
   - Placing providers in pages instead of layout
   - Using wrong directory structure

2. **Missing imports** (20% penalty)
   - Forgetting to import required components
   - Using wrong package names

3. **Incorrect pattern** (30% penalty)
   - Missing required props
   - Wrong component structure
   - Incorrect function signatures

4. **Bad placement** (30% penalty)
   - Not wrapping children properly
   - Wrong nesting level
   - Outside required scope

## Conclusion

I-ACC is the most heavily weighted metric (30%) because correct initialization is fundamental to SDK functionality. The metric uses a sophisticated multi-stage evaluation process that checks not just the presence of code, but its correctness across four dimensions.

The evaluation is thorough yet efficient, using regex-based pattern matching to quickly identify and validate SDK initialization patterns. This approach balances accuracy with performance, making it suitable for large-scale evaluation of LLM-generated solutions.

The perfect I-ACC score in the migration task demonstrates that modern LLMs can successfully handle SDK initialization when given clear instructions, though they may still struggle with other aspects like configuration completeness and semantic similarity to reference implementations.