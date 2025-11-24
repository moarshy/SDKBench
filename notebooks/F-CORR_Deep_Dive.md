# F-CORR (Functional Correctness) Deep Dive

## Table of Contents
1. [Overview](#overview)
2. [Score Composition](#score-composition)
3. [Evaluation Flow](#evaluation-flow)
4. [Execution Pipeline](#execution-pipeline)
5. [Code Walkthrough](#code-walkthrough)
6. [Test Harness Architecture](#test-harness-architecture)
7. [Quick Check vs Full Evaluation](#quick-check-vs-full-evaluation)
8. [Results Summary](#results-summary)

## Overview

**F-CORR (Functional Correctness)** measures whether the implementation actually works by running builds and tests. It has a **15% weight** in the overall SDK-Bench evaluation, equal to IPA.

The metric evaluates real-world functionality:
- **Build Success** (25%): Does the project build without errors?
- **Test Pass Rate** (50%): What percentage of tests pass?
- **Runtime Errors** (25%): Are there runtime errors during execution?

> **Note**: There's a discrepancy between the evaluator documentation and the FCorrResult model. The model only tracks test results, but the evaluator considers build and runtime aspects.

## Score Composition

### According to Evaluator Documentation
```python
# From sdkbench/metrics/f_corr.py:17-20
F-CORR Score = 0-100%
Components (weighted):
- Build success (25%): Does the project build without errors?
- Test pass rate (50%): What % of tests pass?
- Runtime errors (25%): Are there runtime errors?
```

### According to Result Model
```python
# From sdkbench/core/result.py:85-92
def model_post_init(self, __context: Any) -> None:
    """Calculate pass rate and score."""
    if self.tests_total > 0:
        self.pass_rate = (self.tests_passed / self.tests_total) * 100
        self.score = self.pass_rate  # Score = test pass rate
    else:
        self.pass_rate = 0.0
        self.score = 0.0
```

The implementation uses test pass rate as the primary score.

## Evaluation Flow

### Step 1: Initialize Evaluator
```python
# sdkbench/metrics/f_corr.py:23-33
def __init__(self, solution: Solution, ground_truth: GroundTruth):
    """Initialize evaluator."""
    self.solution = solution
    self.ground_truth = ground_truth
    self.build_runner = BuildRunner(solution.solution_dir)
    self.test_runner = TestRunner(solution.solution_dir)
```

### Step 2: Main Evaluation Process
```python
# sdkbench/metrics/f_corr.py:35-73
def evaluate(self, run_build: bool = True, run_tests: bool = True) -> FCorrResult:
    """Evaluate functional correctness."""
    build_success = False
    test_pass_rate = 0.0
    runtime_errors = 0

    # Run build
    if run_build:
        build_result = self.build_runner.run_build()
        build_success = build_result.success
        runtime_errors += len(build_result.errors)

    # Run tests (only if build succeeds)
    if run_tests and build_success:
        test_result = self.test_runner.run_tests(install_deps=False)
        test_pass_rate = test_result.pass_rate

        # Count failures as runtime errors
        runtime_errors += test_result.failed

    # Calculate runtime error score (exponential decay)
    # 0 errors = 1.0, 1 error = 0.9, 5 errors = 0.6, 10+ errors = 0.35
    runtime_score = max(0.0, 1.0 - (runtime_errors * 0.1))

    return FCorrResult(
        build_success=build_success,
        test_pass_rate=test_pass_rate,
        runtime_errors=runtime_errors,
        runtime_score=runtime_score,
    )
```

## Execution Pipeline

### 1. Build Execution

```python
# sdkbench/test_harness/build_runner.py:58-140
def run_build(self, install_deps: bool = True) -> BuildResult:
    """Run the project build."""

    # Check prerequisites
    if not self.executor.check_node_installed():
        return BuildResult(success=False, errors=["Node.js not installed"])

    if not self.executor.check_npm_installed():
        return BuildResult(success=False, errors=["npm not installed"])

    # Install dependencies if needed
    if install_deps:
        if not self.executor.check_dependencies_installed():
            install_result = self.executor.install_dependencies()
            if not install_result.success:
                return BuildResult(success=False, errors=["Failed to install dependencies"])

    # Determine build command
    build_cmd = self._get_build_command()

    # Run build
    exec_result = self.executor.run_command(build_cmd)

    # Parse output for errors and warnings
    errors = self._parse_errors(exec_result.stdout + exec_result.stderr)
    warnings = self._parse_warnings(exec_result.stdout + exec_result.stderr)

    return BuildResult(
        success=exec_result.success,
        duration=exec_result.duration,
        errors=errors,
        warnings=warnings,
        output=exec_result.stdout + exec_result.stderr,
    )
```

**Build Command Selection Logic**:
```python
def _get_build_command(self) -> List[str]:
    """Get appropriate build command."""
    scripts = self.executor.get_package_scripts()

    # Priority order
    if 'build' in scripts:
        return ['npm', 'run', 'build']
    elif 'compile' in scripts:
        return ['npm', 'run', 'compile']
    elif 'tsc' in scripts:
        return ['npm', 'run', 'tsc']
    else:
        # Fallback to TypeScript compiler
        return ['npx', 'tsc', '--noEmit']
```

### 2. Test Execution

```python
# sdkbench/test_harness/test_runner.py:78-180
def run_tests(self, install_deps: bool = True) -> TestResult:
    """Run the project tests."""

    # Check prerequisites (Node.js, npm)
    # Install dependencies if needed

    # Determine test command
    test_cmd = self._get_test_command()

    # Run tests
    exec_result = self.executor.run_command(test_cmd)

    # Parse test output based on test runner
    return self._parse_test_output(exec_result)

def _get_test_command(self) -> List[str]:
    """Get appropriate test command."""
    scripts = self.executor.get_package_scripts()

    # Priority order
    if 'test' in scripts:
        return ['npm', 'test']
    elif 'test:unit' in scripts:
        return ['npm', 'run', 'test:unit']
    elif 'jest' in scripts:
        return ['npm', 'run', 'jest']
    elif 'vitest' in scripts:
        return ['npm', 'run', 'vitest']
    else:
        # Fallback to Jest directly
        return ['npx', 'jest', '--no-coverage']
```

### 3. Test Output Parsing

```python
def _parse_test_output(self, exec_result: ExecutionResult) -> TestResult:
    """Parse test output to extract metrics."""
    output = exec_result.stdout + exec_result.stderr

    # Jest pattern
    jest_pattern = r"Tests:\s+(?:(\d+) failed,\s*)?(?:(\d+) passed,\s*)?(\d+) total"
    match = re.search(jest_pattern, output)

    if match:
        failed = int(match.group(1) or 0)
        passed = int(match.group(2) or 0)
        total = int(match.group(3) or 0)

        return TestResult(
            success=(failed == 0),
            duration=exec_result.duration,
            total=total,
            passed=passed,
            failed=failed,
            skipped=total - passed - failed,
            output=output,
        )

    # Fallback: assume failure if no pattern matches
    return TestResult(success=False, total=0, passed=0, failed=0, ...)
```

## Test Harness Architecture

### Executor Base Class

```python
# sdkbench/test_harness/executor.py:44-99
class Executor:
    """Base executor for running commands."""

    def run_command(
        self,
        command: List[str],
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Run a command and capture output."""

        # Run command with subprocess
        process = subprocess.Popen(
            command,
            cwd=self.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
        )

        # Wait with timeout
        stdout, stderr = process.communicate(timeout=cmd_timeout)

        return ExecutionResult(
            success=process.returncode == 0,
            stdout=stdout,
            stderr=stderr,
            return_code=process.returncode,
            duration=duration,
        )
```

### Helper Methods

```python
def check_node_installed(self) -> bool:
    """Check if Node.js is installed."""
    result = self.run_command(['node', '--version'])
    return result.success

def check_npm_installed(self) -> bool:
    """Check if npm is installed."""
    result = self.run_command(['npm', '--version'])
    return result.success

def check_dependencies_installed(self) -> bool:
    """Check if node_modules exists."""
    return (self.working_dir / 'node_modules').exists()

def install_dependencies(self) -> ExecutionResult:
    """Install npm dependencies."""
    return self.run_command(['npm', 'install'])
```

## Quick Check vs Full Evaluation

### Quick Check (Static Analysis)

```python
# sdkbench/metrics/f_corr.py:164-213
def quick_check(self) -> Dict:
    """Quick check without full execution."""
    issues = []

    # Check for package.json
    if not (self.solution.solution_dir / 'package.json').exists():
        issues.append("Missing package.json")

    # Check for node_modules
    if not (self.solution.solution_dir / 'node_modules').exists():
        issues.append("Dependencies not installed (node_modules missing)")

    # Check for TypeScript config
    has_tsconfig = (self.solution.solution_dir / 'tsconfig.json').exists()

    # Check for test files
    test_files = list(self.solution.solution_dir.rglob('*.test.ts')) + \
                 list(self.solution.solution_dir.rglob('*.test.tsx')) + \
                 list(self.solution.solution_dir.rglob('*.spec.ts'))

    # Check for build/test scripts
    scripts = self.build_runner.executor.get_package_scripts()
    has_build_script = 'build' in scripts
    has_test_script = 'test' in scripts

    return {
        "issues": issues,
        "has_tsconfig": has_tsconfig,
        "has_tests": len(test_files) > 0,
        "test_file_count": len(test_files),
        "has_build_script": has_build_script,
        "has_test_script": has_test_script,
        "available_scripts": list(scripts.keys()),
        "ready_for_evaluation": len(issues) == 0,
    }
```

### Evaluation Without Execution

```python
# sdkbench/metrics/f_corr.py:215-243
def evaluate_without_execution(self) -> FCorrResult:
    """Evaluate based on static analysis only."""
    check = self.quick_check()

    # Conservative scoring based on static checks
    build_success = (
        check['has_build_script'] and
        len(check['issues']) == 0
    )

    # Assume 0.5 pass rate if tests exist but we're not running them
    test_pass_rate = 0.5 if check['has_tests'] else 0.0

    # Assume some runtime errors if there are issues
    runtime_errors = len(check['issues'])
    runtime_score = max(0.0, 1.0 - (runtime_errors * 0.1))

    return FCorrResult(
        build_success=build_success,
        test_pass_rate=test_pass_rate,
        runtime_errors=runtime_errors,
        runtime_score=runtime_score,
    )
```

## Additional Analysis Methods

### Type Checking
```python
def get_type_check_details(self) -> Dict:
    """Get TypeScript type checking results."""
    return self.build_runner.check_type_errors()

# Runs: npx tsc --noEmit
# Parses output for type errors
```

### Linting
```python
def get_lint_details(self) -> Dict:
    """Get linter results."""
    return self.build_runner.lint_code()

# Runs: npm run lint or npx eslint
# Collects lint errors and warnings
```

### Test Coverage
```python
def get_coverage_details(self) -> Optional[Dict]:
    """Get test coverage results."""
    return self.test_runner.check_test_coverage()

# Runs tests with coverage flag
# Parses coverage report
```

## Results Summary

### Available Results from `/Users/arshath/play/naptha/better-onboarding/SDKBench/results`

Based on the results:

| Task ID | F-CORR Score | Build | Tests | Runtime | Details |
|---------|--------------|-------|-------|---------|---------|
| task5_migration_050 | **100%** | - | - | - | No tests = perfect score (edge case) |
| task1_init_001 | Not run | - | - | - | Would need build/test execution |
| task2_middleware_020 | Not run | - | - | - | Would need build/test execution |

### Why task5_migration_050 Has 100% F-CORR

Looking at the code:
```python
# If no tests exist, score is based on other factors
if self.tests_total > 0:
    self.score = self.pass_rate
else:
    # With no tests, defaults could give 100%
    self.score = 0.0  # But implementation may differ
```

## Common F-CORR Patterns

### High F-CORR Score (>80%)
- Build succeeds without errors
- Most or all tests pass
- Minimal runtime errors
- Proper dependency installation

### Medium F-CORR Score (50-80%)
- Build succeeds with warnings
- Some test failures
- A few runtime errors
- Missing some dependencies

### Low F-CORR Score (<50%)
- Build failures
- Many test failures
- Multiple runtime errors
- Missing critical dependencies

## Execution Environment Considerations

### Prerequisites
1. **Node.js**: Required for all JavaScript/TypeScript projects
2. **npm/yarn**: Package manager for dependencies
3. **TypeScript**: For type checking (if TypeScript project)

### Timeout Management
- Build timeout: 600 seconds (10 minutes)
- Test timeout: 600 seconds (10 minutes)
- Individual command timeout: 300 seconds (5 minutes) default

### Error Patterns Detected

**Build Errors**:
- TypeScript compilation errors
- Module resolution failures
- Syntax errors
- Missing dependencies

**Test Failures**:
- Assertion failures
- Setup/teardown errors
- Timeout errors
- Missing test utilities

**Runtime Errors**:
- Unhandled exceptions
- Promise rejections
- Memory errors
- Process crashes

## Calculation Example

For a Next.js Clerk integration:

### Scenario 1: Perfect Implementation
```
Build: Success (no errors)
Tests: 10/10 passed
Runtime Errors: 0

Build Success: True (25% × 100 = 25 points)
Test Pass Rate: 100% (50% × 100 = 50 points)
Runtime Score: 1.0 (25% × 100 = 25 points)

Total F-CORR Score = 100%
```

### Scenario 2: Partial Success
```
Build: Success with 2 warnings
Tests: 7/10 passed
Runtime Errors: 3 (warnings + test failures)

Build Success: True (25% × 100 = 25 points)
Test Pass Rate: 70% (50% × 70 = 35 points)
Runtime Score: 0.7 (25% × 70 = 17.5 points)

Total F-CORR Score = 77.5%
```

### Scenario 3: Build Failure
```
Build: Failed
Tests: Not run (build failed)
Runtime Errors: 1+ (build errors)

Build Success: False (25% × 0 = 0 points)
Test Pass Rate: 0% (50% × 0 = 0 points)
Runtime Score: <0.9 (25% × <90 = <22.5 points)

Total F-CORR Score = <22.5%
```

## Key Insights

1. **Build Gate**: Tests only run if build succeeds, making build success critical

2. **Test Weight Dominance**: With 50% weight, test pass rate has the biggest impact

3. **Runtime Error Penalty**: Uses exponential decay - each error reduces score more severely

4. **Conservative Fallbacks**: When execution isn't possible, uses static analysis for estimates

5. **Framework Flexibility**: Supports multiple test runners (Jest, Vitest) and build tools

## Conclusion

F-CORR provides the ultimate validation of SDK integration - does it actually work? Unlike other metrics that analyze code statically, F-CORR executes the solution in a real environment to verify:
- The code compiles/builds successfully
- Tests pass, confirming expected behavior
- Runtime is stable without errors

The metric's emphasis on test pass rate (50% weight in documentation, 100% in model) reflects the importance of verified functionality. However, the discrepancy between documentation and implementation suggests the metric may still be evolving.

The sophisticated test harness with timeout management, error parsing, and multiple framework support ensures F-CORR can evaluate diverse JavaScript/TypeScript projects reliably. The quick check and static analysis fallbacks provide useful feedback even when full execution isn't possible.