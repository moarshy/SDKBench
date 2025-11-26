# SDKBench Comprehensive Testing Plan

## Executive Summary

This testing plan addresses critical issues discovered during a thorough audit of the SDKBench benchmark system. The audit revealed **40+ bugs** across metrics implementations, test harness issues causing **86-94% F-CORR failure rates**, and fundamental misalignments between what we measure and what actually matters for SDK instrumentation quality.

### Key Findings
- **F-CORR Failure Rate**: 94% (Clerk), 86% (LanceDB) - indicating systemic issues
- **Root Cause**: Tests run against `expected/` directory, NOT against LLM-generated solutions
- **Perfect Static Scores**: I-ACC, C-COMP, IPA show near-perfect scores while F-CORR fails
- **Missing Error Traces**: 37% of F-CORR failures report "No compatible test runner found" with no details
- **Critical Bugs**: SemSim crashes on `get_similarity_summary()`, CQ passes undefined field

---

## Phase 1 Progress (Updated: 2025-11-26)

### ✅ Completed Fixes

| Bug ID | Description | Status | Files Modified |
|--------|-------------|--------|----------------|
| BUG-001 | F-CORR test setup missing conftest.py and __init__.py | ✅ **FIXED** | `run.py`, `run_fcorr.py`, 28 test files (sys.path fix) |
| BUG-002 | SemSim `get_similarity_summary()` AttributeError | ✅ **FIXED** | `result.py`, `sem_sim.py` |
| BUG-003 | CQResult missing `deductions` field | ✅ **FIXED** | `result.py` |
| BUG-004 | F-CORR missing error tracebacks | ✅ **FIXED** | `result.py`, `f_corr.py`, `python_runner.py`, `typescript_runner.py` |
| BUG-005 | Python runner includes venv in test detection | ✅ **FIXED** | `python_runner.py` |
| BUG-006 | TypeScript runner includes node_modules | ✅ **FIXED** | `typescript_runner.py` |
| BUG-007 | LanceDB module-level variable coupling | ✅ **FIXED** | 28 test files, `conftest.py`, `build_samples.py` |

### ⏳ Pending Fixes

All Phase 1 P0 bugs have been fixed.

### 📝 Documentation Updated

- Added "Lessons Learned & Best Practices" appendix to `docs/5-adding-sdks/adding-new-sdk.md`
- Documents 9 best practices for future SDK additions
- Includes checklist, common bugs table, and reference files

---

## Related Documents

- **LanceDB-specific evaluation**: `testing-plans/lancedb/lancedb-evaluation.md`
- **LanceDB bug fixing plan**: `testing-plans/lancedb/bug-fixing-plan.md`
- **Adding new SDKs guide**: `docs/5-adding-sdks/adding-new-sdk.md` (includes lessons learned)

---

## Table of Contents

1. [Critical Issues Requiring Immediate Attention](#1-critical-issues-requiring-immediate-attention)
2. [Test Infrastructure Testing](#2-test-infrastructure-testing)
3. [Metrics Unit Testing](#3-metrics-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [Sample Validation Testing](#5-sample-validation-testing)
6. [End-to-End Testing](#6-end-to-end-testing)
7. [Regression Testing](#7-regression-testing)
8. [Performance Testing](#8-performance-testing)
9. [Test Data Validation](#9-test-data-validation)
10. [Implementation Priority](#10-implementation-priority)

---

## 1. Critical Issues Requiring Immediate Attention

### 1.1 F-CORR Test Execution Misalignment (CRITICAL)

**Issue**: Sample tests import from `expected/` directory, not from LLM-generated solutions.

```python
# Current test (samples/lancedb/lancedb_task1_init_001/tests/test_init.py)
from expected import app  # Tests the reference solution, NOT the generated code!
```

**Impact**: F-CORR scores measure reference solution correctness, not LLM output.

**Required Tests**:
```python
# tests/test_fcorr_execution.py

def test_fcorr_runs_against_generated_solution():
    """Verify F-CORR tests execute against LLM-generated code, not expected/"""
    # Setup: Create a solution with intentionally wrong code
    # Execute: Run F-CORR
    # Assert: Tests should FAIL (proving they ran against solution, not expected)

def test_fcorr_test_file_copying():
    """Verify test files are properly copied and paths adjusted"""
    # Tests should have their imports rewritten to point to solution directory

def test_fcorr_isolated_environment():
    """Verify each solution runs in isolated environment"""
    # No cross-contamination between samples
```

### 1.2 SemSim AttributeError Crash (CRITICAL)

**Issue**: `sem_sim.py:589-604` accesses non-existent attributes.

```python
# Bug: SemSimResult doesn't have these attributes
"strongest_component": max([
    ("structure", result.structure_similarity),  # DOESN'T EXIST
    ("patterns", result.pattern_matching),       # DOESN'T EXIST
    ("approach", result.approach_alignment),     # DOESN'T EXIST
])
```

**Required Tests**:
```python
# tests/metrics/test_sem_sim.py

def test_get_similarity_summary_no_crash():
    """Verify get_similarity_summary() doesn't crash with AttributeError"""
    evaluator = SemSimEvaluator(solution, ground_truth)
    summary = evaluator.get_similarity_summary()  # Should not crash
    assert "strongest_component" in summary

def test_sem_sim_result_attributes():
    """Verify SemSimResult has all expected attributes"""
    result = SemSimResult(similarity_score=75.0, pattern_match=True, approach_match=True)
    assert hasattr(result, 'score')
    assert hasattr(result, 'similarity_score')
```

### 1.3 CQResult Undefined Field (CRITICAL)

**Issue**: `cq.py:89` passes `deductions` field not defined in Result model.

```python
# Bug: CQResult doesn't have 'deductions' field
return CQResult(deductions=deductions)  # Pydantic validation error
```

**Required Tests**:
```python
# tests/metrics/test_cq.py

def test_cq_evaluator_returns_valid_result():
    """Verify CQEvaluator returns properly structured CQResult"""
    evaluator = CQEvaluator(solution, ground_truth)
    result = evaluator.evaluate()
    assert isinstance(result, CQResult)
    # All fields should be present and valid
    assert hasattr(result, 'type_errors')
    assert hasattr(result, 'eslint_errors')
    assert hasattr(result, 'security_issues')
```

### 1.4 F-CORR Missing Error Tracebacks (CRITICAL)

**Issue**: F-CORR results don't capture actual test failure tracebacks, making debugging impossible.

**Current f_corr.json output**:
```json
{
  "score": 0.0,
  "tests_passed": 2,
  "tests_failed": 1,
  "tests_total": 3,
  "tests_skipped": 0,
  "duration": 15.96,
  "error": "1 tests failed"  // NO TRACEBACK! Which test? What error?
}
```

**Root Cause Analysis**:

1. **Result Model Gap**: `FCorrResult` in `result.py:77-92` only has:
   - `failed_tests: List[str]` - just test names, no details
   - `error_messages: List[str]` - generic messages, no stack traces

2. **Test Harness Has Details But They're Lost**: `TestFailure` model in `test_harness/models.py:16-22` has:
   - `test_name`, `error_message`, `file_path`, `line_number`, `stack_trace`
   - But this rich data is NOT propagated to the final f_corr.json

3. **Serialization Drops Data**: In `f_corr.py:128-132`, failures are reduced to just names:
   ```python
   for failure in test_result.failures:
       failed_tests.append(failure.test_name)  # Only name kept!
       if failure.error_message:
           error_messages.append(f"{failure.test_name}: {failure.error_message}")
   # stack_trace, file_path, line_number ALL LOST!
   ```

4. **JSON Output Missing Fields**: The saved f_corr.json doesn't include:
   - `failed_tests` list (even though it's in the model)
   - `error_messages` list (even though it's in the model)
   - Any traceback information

**Required Schema Enhancement**:

```python
# Enhanced FCorrResult for result.py
class FCorrResult(MetricResult):
    """F-CORR (Functional Correctness) metric result."""
    tests_passed: int = 0
    tests_total: int = 0
    tests_skipped: int = 0
    pass_rate: float = 0.0

    # Enhanced failure tracking
    failed_tests: List[str] = Field(default_factory=list)
    error_messages: List[str] = Field(default_factory=list)

    # NEW: Detailed failure information
    failure_details: List[Dict[str, Any]] = Field(default_factory=list)
    # Each entry: {
    #   "test_name": "test_database_connection",
    #   "file_path": "tests/test_init.py",
    #   "line_number": 18,
    #   "error_message": "AssertionError: assert app.db is not None",
    #   "stack_trace": "Traceback (most recent call last):\n..."
    # }

    # NEW: Raw test output for debugging
    raw_output: Optional[str] = None

    # NEW: Build/install error details
    install_error: Optional[str] = None
    build_error: Optional[str] = None
```

**Required Tests**:

```python
# tests/metrics/test_fcorr_traceback.py

class TestFCorrTracebackCapture:
    """Tests for F-CORR error traceback capture"""

    def test_failure_details_captured(self):
        """Verify test failure details are captured in result"""
        # Setup: Create solution with intentionally failing test
        result = evaluator.evaluate()

        assert len(result.failure_details) > 0
        failure = result.failure_details[0]
        assert "test_name" in failure
        assert "error_message" in failure
        assert "stack_trace" in failure

    def test_stack_trace_included(self):
        """Verify stack traces are included for failed tests"""
        result = evaluator.evaluate()

        for failure in result.failure_details:
            if failure.get("error_message"):
                assert failure.get("stack_trace") is not None
                assert "Traceback" in failure["stack_trace"] or "Error" in failure["stack_trace"]

    def test_file_and_line_captured(self):
        """Verify file path and line number captured"""
        result = evaluator.evaluate()

        for failure in result.failure_details:
            assert failure.get("file_path") is not None
            assert failure.get("line_number") is not None or failure.get("file_path") is not None

    def test_raw_output_preserved(self):
        """Verify raw test output is preserved for debugging"""
        result = evaluator.evaluate()

        assert result.raw_output is not None
        assert len(result.raw_output) > 0

    def test_fcorr_json_contains_details(self):
        """Verify f_corr.json output includes failure details"""
        result = evaluator.evaluate()
        result_dict = result.model_dump()

        assert "failure_details" in result_dict
        assert "raw_output" in result_dict or result_dict.get("failure_details")

    def test_install_error_captured(self):
        """Verify dependency install errors are captured"""
        # Setup: Create project with bad dependencies
        result = evaluator.evaluate()

        if result.score == 0 and result.tests_total == 0:
            assert result.install_error is not None or result.error_messages

    def test_no_runner_error_detailed(self):
        """Verify 'no compatible runner' includes detection details"""
        # Setup: Create project with no recognizable structure
        result = evaluator.evaluate()

        # Should explain WHY no runner was found
        assert "error" in result.model_dump()
        error = result.model_dump().get("error", "")
        assert "runner" in error.lower() or "detect" in error.lower()

    def test_traceback_not_truncated(self):
        """Verify long tracebacks are not truncated"""
        # Setup: Create test with deep stack trace
        result = evaluator.evaluate()

        for failure in result.failure_details:
            trace = failure.get("stack_trace", "")
            # Should contain the actual assertion, not just "..."
            assert "..." not in trace[-50:] if trace else True

    def test_multiple_failures_all_captured(self):
        """Verify all failures captured, not just first"""
        # Setup: Create solution with multiple failing tests
        result = evaluator.evaluate()

        # Should capture ALL failures
        assert len(result.failure_details) == result.tests_failed

    def test_pytest_traceback_parsing(self):
        """Verify pytest-specific traceback format parsed correctly"""
        # Pytest uses specific format: FAILED test_file.py::test_name - reason
        result = evaluator.evaluate()

        for failure in result.failure_details:
            assert "::" in failure.get("test_name", "") or failure.get("file_path")

    def test_jest_traceback_parsing(self):
        """Verify Jest-specific traceback format parsed correctly"""
        # Jest uses: ● Test Suite › test name
        result = evaluator.evaluate()

        # Should extract meaningful test name
        for failure in result.failure_details:
            assert failure.get("test_name") != ""
```

**Implementation Checklist**:

- [ ] Add `failure_details: List[Dict]` to `FCorrResult` in `result.py`
- [ ] Add `raw_output: Optional[str]` to `FCorrResult`
- [ ] Update `f_corr.py:_evaluate_with_registry()` to populate `failure_details`
- [ ] Update Python runner to extract full traceback from pytest output
- [ ] Update TypeScript runner to extract full traceback from Jest/Vitest output
- [ ] Ensure JSON serialization includes all new fields
- [ ] Add tests for traceback capture
- [ ] Update existing f_corr.json files (re-run evaluation)

**Expected f_corr.json After Fix**:

```json
{
  "score": 0.0,
  "tests_passed": 2,
  "tests_failed": 1,
  "tests_total": 3,
  "tests_skipped": 0,
  "duration": 15.96,
  "error": "1 tests failed",
  "failed_tests": ["test_required_environment_variables"],
  "error_messages": [
    "test_required_environment_variables: AssertionError: Expected .env.example to contain CLERK_SECRET_KEY"
  ],
  "failure_details": [
    {
      "test_name": "test_required_environment_variables",
      "file_path": "tests/init.test.ts",
      "line_number": 23,
      "error_message": "AssertionError: Expected .env.example to contain CLERK_SECRET_KEY",
      "stack_trace": "Error: expect(received).toContain(expected)\n\nExpected substring: \"CLERK_SECRET_KEY\"\nReceived string: \"NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx\"\n\n    at Object.<anonymous> (tests/init.test.ts:23:16)\n    at ..."
    }
  ],
  "raw_output": "PASS tests/init.test.ts\n  Clerk Initialization\n    ✓ should have ClerkProvider (5ms)\n    ✓ should have @clerk/nextjs (2ms)\n    ✕ should have required env vars (8ms)\n\n  ● should have required env vars\n    ..."
}
```

---

### 1.5 Test Runner Virtual Environment/node_modules Inclusion (CRITICAL)

**Issue**: Both runners use `rglob()` which matches test files in `venv/`, `node_modules/`.

```python
# Bug: python_runner.py:48-52
test_files = list(self.working_dir.rglob("test_*.py"))  # Matches venv files!

# Bug: typescript_runner.py:87-106
test_files = list(self.working_dir.rglob("*.test.ts"))  # Matches node_modules!
```

**Required Tests**:
```python
# tests/test_harness/test_runners.py

def test_python_runner_excludes_venv():
    """Verify Python runner excludes virtualenv test files"""
    # Setup: Create project with venv containing test files
    # Execute: Detect tests
    # Assert: venv test files NOT included

def test_typescript_runner_excludes_node_modules():
    """Verify TypeScript runner excludes node_modules test files"""
    # Setup: Create project with node_modules containing test files
    # Execute: Detect tests
    # Assert: node_modules test files NOT included

def test_runner_detection_accuracy():
    """Verify runner detection returns correct file counts"""
    # Setup: Known project structure
    # Execute: detect()
    # Assert: Exact expected file count
```

---

## 2. Test Infrastructure Testing

### 2.1 Test Harness Unit Tests

**File**: `tests/test_harness/test_registry.py`

```python
class TestRunnerRegistry:
    """Tests for TestRunnerRegistry"""

    def test_registry_initialization(self):
        """Registry initializes with default runners"""
        TestRunnerRegistry.clear()
        TestRunnerRegistry._ensure_initialized()
        runners = TestRunnerRegistry.get_all_runners()
        assert len(runners) >= 2  # Python and TypeScript

    def test_get_runner_returns_best_match(self):
        """get_runner() returns runner with highest confidence"""
        # Setup: Create TypeScript project
        runner = TestRunnerRegistry.get_runner(ts_project_dir)
        assert isinstance(runner, TypeScriptRunner)

    def test_get_runner_handles_detection_exceptions(self):
        """get_runner() doesn't crash when detection raises"""
        # Setup: Create project that causes detection to throw
        # Execute: get_runner()
        # Assert: Returns None, doesn't crash

    def test_registration_order_priority(self):
        """First registered runner wins on tie confidence"""
        # Verify behavior with equal confidence scores

    def test_clear_resets_state(self):
        """clear() removes all registered runners"""
        TestRunnerRegistry.register(MockRunner)
        TestRunnerRegistry.clear()
        assert len(TestRunnerRegistry._runners) == 0
```

### 2.2 Python Runner Tests

**File**: `tests/test_harness/test_python_runner.py`

```python
class TestPythonRunner:
    """Tests for PythonRunner"""

    # Detection Tests
    def test_detect_with_requirements_txt(self):
        """Detects Python project with requirements.txt"""

    def test_detect_with_pyproject_toml(self):
        """Detects Python project with pyproject.toml"""

    def test_detect_with_setup_py(self):
        """Detects Python project with setup.py"""

    def test_detect_without_manifest(self):
        """Returns low confidence without dependency manifest"""

    def test_detect_excludes_venv_files(self):
        """Test files in venv/ are excluded from detection"""

    def test_confidence_calculation(self):
        """Confidence scales with number of markers found"""

    # Dependency Installation Tests
    def test_install_dependencies_requirements(self):
        """Installs from requirements.txt"""

    def test_install_dependencies_pyproject(self):
        """Installs from pyproject.toml"""

    def test_install_no_manifest_returns_success(self):
        """Returns success=True when no manifest (questionable behavior)"""

    def test_install_handles_pip_failure(self):
        """Handles pip install failures gracefully"""

    # Test Execution Tests
    def test_run_tests_pytest(self):
        """Runs pytest and parses output correctly"""

    def test_run_tests_handles_timeout(self):
        """Handles test timeout gracefully"""

    def test_pythonpath_setup_unix(self):
        """PYTHONPATH uses : separator on Unix"""

    def test_pythonpath_setup_windows(self):
        """PYTHONPATH uses ; separator on Windows"""

    # Output Parsing Tests
    def test_parse_output_standard_format(self):
        """Parses standard pytest output correctly"""

    def test_parse_output_with_warnings(self):
        """Doesn't confuse warnings with test counts"""

    def test_parse_output_failure_extraction(self):
        """Extracts failure details correctly"""

    def test_parse_output_empty(self):
        """Handles empty output gracefully"""

    def test_conflicting_flags_removed(self):
        """Verify -v and -q aren't both used"""
```

### 2.3 TypeScript Runner Tests

**File**: `tests/test_harness/test_typescript_runner.py`

```python
class TestTypeScriptRunner:
    """Tests for TypeScriptRunner"""

    # Detection Tests
    def test_detect_with_package_json(self):
        """Detects TypeScript project with package.json"""

    def test_detect_jest_framework(self):
        """Correctly identifies Jest from dependencies"""

    def test_detect_vitest_framework(self):
        """Correctly identifies Vitest from dependencies"""

    def test_detect_mocha_framework(self):
        """Correctly identifies Mocha from dependencies"""

    def test_detect_from_test_file_imports(self):
        """Detects framework from test file imports"""

    def test_detect_excludes_node_modules(self):
        """Test files in node_modules/ excluded"""

    def test_detect_requires_multiple_markers(self):
        """Detection requires package.json + something else"""

    # Framework State Tests
    def test_detected_framework_persists(self):
        """_detected_framework set correctly after detect()"""

    def test_framework_state_isolation(self):
        """Different runner instances have independent state"""

    def test_get_framework_without_detect(self):
        """get_framework() before detect() returns default"""

    # Dependency Installation Tests
    def test_install_npm_dependencies(self):
        """Runs npm install correctly"""

    def test_install_skips_existing_node_modules(self):
        """Skips install when node_modules exists (note: risky behavior)"""

    def test_install_jest_auto_install(self):
        """Auto-installs Jest when detected but not in deps"""

    def test_jest_config_creation(self):
        """Creates jest.config.js when missing"""

    # Test Execution Tests
    def test_run_tests_npm_test(self):
        """Runs npm test when test script exists"""

    def test_run_tests_npx_jest_fallback(self):
        """Falls back to npx jest when no test script"""

    def test_run_tests_handles_timeout(self):
        """Handles test timeout gracefully"""

    # Output Parsing Tests
    def test_parse_jest_output(self):
        """Parses Jest output correctly"""

    def test_parse_vitest_output(self):
        """Parses Vitest output correctly"""

    def test_parse_mocha_output(self):
        """Parses Mocha output correctly"""

    def test_parse_output_with_checkmarks(self):
        """Handles checkmark symbols in output"""

    def test_failure_extraction_multiline(self):
        """Extracts multi-line failure messages"""
```

---

## 3. Metrics Unit Testing

### 3.1 I-ACC (Initialization Accuracy) Tests

**File**: `tests/metrics/test_i_acc.py`

```python
class TestIAccEvaluator:
    """Tests for Initialization Accuracy metric"""

    # Import Detection Tests
    def test_import_detection_named_import(self):
        """Detects named imports: import { foo } from 'bar'"""

    def test_import_detection_default_import(self):
        """Detects default imports: import foo from 'bar'"""

    def test_import_detection_namespace_import(self):
        """Detects namespace imports: import * as foo from 'bar'"""

    def test_import_detection_python_from_import(self):
        """Detects Python from imports: from foo import bar"""

    def test_import_detection_python_import(self):
        """Detects Python imports: import foo"""

    # Pattern Matching Tests
    def test_pattern_string_exact_match(self):
        """Exact string pattern matching"""

    def test_pattern_string_word_boundary(self):
        """Pattern 'connect' shouldn't match 'disconnected'"""

    def test_pattern_in_comments_excluded(self):
        """Patterns in comments shouldn't count"""

    def test_pattern_in_strings_excluded(self):
        """Patterns in string literals shouldn't count"""

    # Placement Tests
    def test_placement_wraps_children(self):
        """Detects component wrapping children"""

    def test_placement_top_level(self):
        """Detects top-level placement"""

    def test_placement_in_function(self):
        """Detects placement inside function"""

    def test_placement_unknown_type(self):
        """Handles unknown placement type gracefully"""

    # JSX Component Tests
    def test_jsx_component_detection(self):
        """Detects JSX component usage"""

    def test_jsx_component_required_props(self):
        """Validates required props present"""

    def test_jsx_nested_braces(self):
        """Handles nested braces in JSX correctly"""

    # Edge Cases
    def test_empty_solution(self):
        """Handles solution with no files"""

    def test_missing_ground_truth(self):
        """Handles missing ground truth gracefully"""

    def test_malformed_jsx(self):
        """Doesn't crash on malformed JSX"""
```

### 3.2 C-COMP (Configuration Completeness) Tests

**File**: `tests/metrics/test_c_comp.py`

```python
class TestCCompEvaluator:
    """Tests for Configuration Completeness metric"""

    # Environment Variable Tests
    def test_env_vars_dotenv_format(self):
        """Parses .env format correctly"""

    def test_env_vars_yaml_format(self):
        """Parses YAML env format"""

    def test_env_vars_with_quotes(self):
        """Handles quoted values: KEY="value" """

    def test_env_vars_with_comments(self):
        """Ignores commented env vars"""

    # Dependency Parsing Tests
    def test_parse_requirements_txt_standard(self):
        """Parses standard requirements.txt"""

    def test_parse_requirements_txt_with_extras(self):
        """Parses: package[extra]==1.0.0"""

    def test_parse_requirements_txt_url_based(self):
        """Parses: package @ https://..."""

    def test_parse_requirements_txt_editable(self):
        """Parses: -e . or -e git+..."""

    def test_parse_requirements_txt_markers(self):
        """Parses: package; python_version > '3.6'"""

    def test_parse_pyproject_toml(self):
        """Parses pyproject.toml dependencies - KNOWN BUG: uses line parsing"""

    def test_parse_package_json_dependencies(self):
        """Parses package.json dependencies"""

    def test_parse_package_json_dev_dependencies(self):
        """Parses package.json devDependencies"""

    # Version Compatibility Tests
    def test_version_exact_match(self):
        """Exact version match: 1.0.0 == 1.0.0"""

    def test_version_minor_compatible(self):
        """Minor version compatible: 1.1.0 >= 1.0.0"""

    def test_version_major_incompatible(self):
        """Major version incompatible: 2.0.0 != 1.x.x"""

    def test_version_prerelease(self):
        """Handles prerelease versions: 1.0.0-beta"""

    def test_version_missing(self):
        """Handles missing version specs"""

    # Middleware Configuration Tests
    def test_middleware_type_matching(self):
        """Validates middleware type matches expected"""

    def test_middleware_config_extraction(self):
        """Extracts middleware configuration correctly"""

    # Edge Cases
    def test_no_dependency_file(self):
        """Handles project with no dependency manifest"""

    def test_malformed_json(self):
        """Handles malformed package.json gracefully"""

    def test_malformed_toml(self):
        """Handles malformed pyproject.toml gracefully"""
```

### 3.3 IPA (Integration Point Accuracy) Tests

**File**: `tests/metrics/test_ipa.py`

```python
class TestIPAEvaluator:
    """Tests for Integration Point Accuracy metric"""

    # Path Normalization Tests
    def test_normalize_leading_dot_slash(self):
        """Normalizes ./path to path"""

    def test_normalize_leading_slash(self):
        """Normalizes /path to path"""

    def test_normalize_backslashes(self):
        """Converts backslashes to forward slashes"""

    def test_normalize_preserves_hidden_files(self):
        """Preserves .hidden files correctly"""

    # Precision/Recall Tests
    def test_perfect_precision_recall(self):
        """All expected found, no extras: P=R=F1=1.0"""

    def test_zero_precision(self):
        """No correct predictions: P=0"""

    def test_zero_recall(self):
        """No expected found: R=0"""

    def test_f1_calculation(self):
        """F1 = 2*P*R/(P+R)"""

    def test_empty_expected(self):
        """Empty expected list handling - should be 1.0 or undefined?"""

    def test_empty_solution(self):
        """Empty solution list handling"""

    def test_both_empty(self):
        """Both empty - should be 1.0 (nothing expected, nothing found)"""

    # Integration Point Extraction Tests
    def test_extract_from_dict(self):
        """Extracts 'location' from dict points"""

    def test_extract_from_string(self):
        """Uses string points directly"""

    def test_extract_ignores_invalid(self):
        """Ignores non-string, non-dict items"""

    def test_extract_handles_none_location(self):
        """Handles {'location': None} gracefully"""

    # Consistency Tests
    def test_evaluate_get_details_consistency(self):
        """evaluate() and get_details() return consistent results"""
```

### 3.4 F-CORR (Functional Correctness) Tests

**File**: `tests/metrics/test_f_corr.py`

```python
class TestFCorrEvaluator:
    """Tests for Functional Correctness metric"""

    # Runner Selection Tests
    def test_registry_runner_selection(self):
        """Selects appropriate runner from registry"""

    def test_legacy_fallback(self):
        """Falls back to legacy when no runner found"""

    def test_no_runner_available(self):
        """Handles case when no runner can handle project"""

    # Strict Mode Tests
    def test_strict_mode_any_failure_zero(self):
        """Strict mode: any test failure = 0 score"""

    def test_strict_mode_all_pass_hundred(self):
        """Strict mode: all tests pass = 100 score"""

    def test_pass_rate_mode(self):
        """Pass rate mode: score = pass percentage"""

    # Test Result Handling Tests
    def test_test_result_with_failures(self):
        """Correctly counts failures"""

    def test_test_result_with_skips(self):
        """Correctly handles skipped tests"""

    def test_test_result_zero_tests(self):
        """Handles zero tests case"""

    def test_test_result_missing_fields(self):
        """Handles test result missing fields"""

    # Dependency Installation Tests
    def test_auto_install_enabled(self):
        """Installs dependencies when auto_install=True"""

    def test_auto_install_disabled(self):
        """Skips installation when auto_install=False"""

    def test_install_failure_handling(self):
        """Handles dependency install failure"""

    # Quick Check Tests
    def test_quick_check_finds_tests(self):
        """Quick check detects test presence"""

    def test_quick_check_python_patterns(self):
        """Finds test_*.py and *_test.py"""

    def test_quick_check_typescript_patterns(self):
        """Finds *.test.ts, *.spec.ts, etc."""

    # Result Consistency Tests
    def test_registry_legacy_result_consistency(self):
        """Registry and legacy paths produce consistent result format"""
```

### 3.5 CQ (Code Quality) Tests

**File**: `tests/metrics/test_cq.py`

```python
class TestCQEvaluator:
    """Tests for Code Quality metric"""

    # Async Detection Tests
    def test_async_function_detection_python(self):
        """Detects async def functions"""

    def test_async_function_detection_typescript(self):
        """Detects async function declarations"""

    def test_await_without_async_function(self):
        """Handles await outside async function"""

    def test_async_arrow_functions(self):
        """Detects async arrow functions"""

    # Try-Except Detection Tests
    def test_try_except_present(self):
        """Detects try-except blocks in async code"""

    def test_try_catch_typescript(self):
        """Detects try-catch in TypeScript"""

    def test_async_without_error_handling(self):
        """Flags async code without error handling"""

    # Type Annotation Tests
    def test_typed_parameters(self):
        """Detects typed function parameters"""

    def test_untyped_parameters(self):
        """Flags untyped parameters"""

    def test_optional_parameters(self):
        """Handles optional parameters: (a?: string)"""

    # Duplication Detection Tests
    def test_duplicate_imports(self):
        """Detects duplicate imports across files"""

    def test_similar_code_blocks(self):
        """Detects similar code blocks"""

    def test_legitimate_common_patterns(self):
        """Doesn't flag legitimate common patterns"""

    # Score Calculation Tests
    def test_deduction_calculation(self):
        """Score = 100 - deductions"""

    def test_score_floor_at_zero(self):
        """Score doesn't go below 0"""

    def test_deduction_weights(self):
        """Type: -5, Lint: -2, Security: -20"""
```

### 3.6 SEM-SIM (Semantic Similarity) Tests

**File**: `tests/metrics/test_sem_sim.py`

```python
class TestSemSimEvaluator:
    """Tests for Semantic Similarity metric"""

    # Score Calculation Tests
    def test_weighted_score_calculation(self):
        """Verifies 30-40-30 weighting"""

    def test_score_overflow_prevention(self):
        """Score capped at 100 - KNOWN BUG: currently can exceed"""

    def test_score_range_validation(self):
        """Score in 0-100 range"""

    # Structure Similarity Tests
    def test_file_structure_matching(self):
        """Matches expected file structure"""

    def test_component_structure_matching(self):
        """Matches component/class structure"""

    # Pattern Matching Tests
    def test_sdk_pattern_detection(self):
        """Detects SDK-specific patterns"""

    def test_pattern_counting(self):
        """Counts pattern occurrences correctly"""

    # Approach Alignment Tests
    def test_python_conventions(self):
        """Checks Python conventions (docstrings, etc.)"""

    def test_framework_conventions(self):
        """Checks framework-specific conventions"""

    def test_version_detection(self):
        """Detects SDK version patterns"""

    # Integration Point Tests
    def test_integration_point_extraction(self):
        """Extracts integration points correctly"""

    def test_path_normalization(self):
        """Normalizes paths for comparison"""

    # Result Attribute Tests
    def test_result_has_required_attributes(self):
        """SemSimResult has all required attributes - CRITICAL"""

    def test_get_similarity_summary_works(self):
        """get_similarity_summary() doesn't crash - CRITICAL"""
```

---

## 4. Integration Testing

### 4.1 Evaluator Integration Tests

**File**: `tests/integration/test_evaluator.py`

```python
class TestEvaluatorIntegration:
    """Integration tests for the Evaluator orchestrator"""

    def test_evaluate_all_metrics(self):
        """Full evaluation runs all 6 metrics"""

    def test_evaluate_quick_skips_fcorr(self):
        """Quick evaluation skips F-CORR"""

    def test_evaluate_handles_metric_failure(self):
        """Continues evaluation when single metric fails"""

    def test_overall_score_calculation(self):
        """Overall score is average of all metric scores"""

    def test_grade_assignment(self):
        """Grade assigned correctly based on score"""

    def test_report_generation(self):
        """get_detailed_report() returns complete data"""

    def test_summary_generation(self):
        """get_summary() returns correct format"""
```

### 4.2 Result Model Integration Tests

**File**: `tests/integration/test_results.py`

```python
class TestResultIntegration:
    """Integration tests for Result models"""

    def test_iacc_result_scoring(self):
        """IAccResult calculates score correctly"""

    def test_ccomp_result_scoring(self):
        """CCompResult calculates score correctly"""

    def test_ipa_result_scoring(self):
        """IPAResult uses F1 for score"""

    def test_fcorr_result_scoring(self):
        """FCorrResult uses pass_rate for score"""

    def test_cq_result_scoring(self):
        """CQResult uses deduction-based scoring"""

    def test_semsim_result_scoring(self):
        """SemSimResult uses similarity_score"""

    def test_evaluation_result_aggregation(self):
        """EvaluationResult aggregates all metrics correctly"""

    def test_metric_summary_format(self):
        """get_metric_summary() returns correct format"""
```

### 4.3 Sample-to-Evaluation Pipeline Tests

**File**: `tests/integration/test_pipeline.py`

```python
class TestPipelineIntegration:
    """End-to-end pipeline integration tests"""

    def test_sample_loading(self):
        """Samples load correctly with all components"""

    def test_ground_truth_parsing(self):
        """metadata.json parses into GroundTruth"""

    def test_solution_creation(self):
        """Solution object created from files"""

    def test_evaluation_execution(self):
        """Full evaluation completes without errors"""

    def test_result_serialization(self):
        """Results serialize to JSON correctly"""

    def test_result_deserialization(self):
        """Results deserialize from JSON correctly"""
```

---

## 5. Sample Validation Testing

### 5.1 Sample Structure Validation

**File**: `tests/samples/test_sample_structure.py`

```python
class TestSampleStructure:
    """Validates all samples have correct structure"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_sample_has_input_directory(self, sample_path):
        """Every sample has input/ directory"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_sample_has_expected_directory(self, sample_path):
        """Every sample has expected/ directory"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_sample_has_tests_directory(self, sample_path):
        """Every sample has tests/ directory"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_sample_has_metadata(self, sample_path):
        """Every sample has expected/metadata.json"""
```

### 5.2 Metadata Validation

**File**: `tests/samples/test_metadata.py`

```python
class TestMetadataValidation:
    """Validates metadata.json files"""

    @pytest.mark.parametrize("metadata_path", get_all_metadata_paths())
    def test_metadata_has_sample_id(self, metadata_path):
        """metadata has sample_id field"""

    @pytest.mark.parametrize("metadata_path", get_all_metadata_paths())
    def test_metadata_has_task_type(self, metadata_path):
        """metadata has task_type field (1-5)"""

    @pytest.mark.parametrize("metadata_path", get_all_metadata_paths())
    def test_metadata_has_sdk(self, metadata_path):
        """metadata has sdk field"""

    @pytest.mark.parametrize("metadata_path", get_all_metadata_paths())
    def test_metadata_has_ground_truth(self, metadata_path):
        """metadata has ground_truth section"""

    @pytest.mark.parametrize("metadata_path", get_all_metadata_paths())
    def test_metadata_has_evaluation_targets(self, metadata_path):
        """metadata has evaluation_targets section"""

    @pytest.mark.parametrize("metadata_path", get_all_metadata_paths())
    def test_evaluation_targets_complete(self, metadata_path):
        """evaluation_targets has all metric sections"""
```

### 5.3 Test File Validation

**File**: `tests/samples/test_sample_tests.py`

```python
class TestSampleTests:
    """Validates sample test files"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_tests_are_runnable(self, sample_path):
        """Test files can be parsed without syntax errors"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_tests_import_correctly(self, sample_path):
        """Tests import from expected/ directory"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_expected_solution_passes_tests(self, sample_path):
        """Running tests against expected/ should pass"""
```

### 5.4 Cross-Sample Consistency Tests

**File**: `tests/samples/test_consistency.py`

```python
class TestCrossSampleConsistency:
    """Cross-sample consistency validation"""

    def test_all_clerk_samples_have_same_structure(self):
        """All Clerk samples follow same patterns"""

    def test_all_lancedb_samples_have_same_structure(self):
        """All LanceDB samples follow same patterns"""

    def test_task_type_distribution(self):
        """Task types distributed as expected (15-15-10-7-3)"""

    def test_difficulty_progression(self):
        """Difficulty increases with task type"""

    def test_no_duplicate_sample_ids(self):
        """All sample_ids are unique"""
```

---

## 6. End-to-End Testing

### 6.1 Full Benchmark Run Tests

**File**: `tests/e2e/test_full_run.py`

```python
class TestFullBenchmarkRun:
    """End-to-end benchmark run tests"""

    def test_single_sample_evaluation(self):
        """Single sample evaluates completely"""

    def test_multi_sample_batch_evaluation(self):
        """Batch evaluation of multiple samples"""

    def test_cross_sdk_evaluation(self):
        """Evaluation works across both SDKs"""

    def test_result_aggregation(self):
        """Results aggregate correctly into summary"""

    def test_report_generation(self):
        """Full report generates without errors"""
```

### 6.2 CLI Integration Tests

**File**: `tests/e2e/test_cli.py`

```python
class TestCLIIntegration:
    """CLI script integration tests"""

    def test_run_py_single_sdk(self):
        """run.py --sdk clerk works"""

    def test_run_py_multiple_sdks(self):
        """run.py --sdk clerk,lancedb works"""

    def test_run_py_with_fcorr(self):
        """run.py --run-fcorr works"""

    def test_run_py_limit_samples(self):
        """run.py --limit 5 works"""

    def test_run_fcorr_py(self):
        """run_fcorr.py standalone works"""

    def test_compare_sdk_results(self):
        """compare_sdk_results.py works"""
```

### 6.3 Golden File Tests

**File**: `tests/e2e/test_golden.py`

```python
class TestGoldenFiles:
    """Golden file comparison tests"""

    def test_expected_solution_scores_high(self):
        """Expected solutions should score 90%+ on all metrics"""

    def test_known_bad_solution_scores_low(self):
        """Intentionally bad solutions should score low"""

    def test_score_stability(self):
        """Same input produces same scores (deterministic)"""
```

---

## 7. Regression Testing

### 7.1 Score Regression Tests

**File**: `tests/regression/test_scores.py`

```python
class TestScoreRegression:
    """Prevent score calculation regressions"""

    # Store known good scores as fixtures
    KNOWN_GOOD_SCORES = {
        "task1_init_001": {"i_acc": 100.0, "c_comp": 80.0, ...},
        # ... more samples
    }

    @pytest.mark.parametrize("sample_id,expected", KNOWN_GOOD_SCORES.items())
    def test_score_matches_known_good(self, sample_id, expected):
        """Scores match previously validated values"""
```

### 7.2 Bug Fix Regression Tests

**File**: `tests/regression/test_bug_fixes.py`

```python
class TestBugFixRegressions:
    """Regression tests for fixed bugs"""

    def test_semsim_no_attribute_error(self):
        """SemSim doesn't crash on get_similarity_summary()"""
        # Regression test for AttributeError bug

    def test_cq_result_valid_fields(self):
        """CQResult has all required fields"""
        # Regression test for undefined 'deductions' field

    def test_path_normalization_preserves_hidden(self):
        """Path normalization preserves hidden files (.gitignore)"""
        # Regression test for lstrip bug

    def test_venv_excluded_from_detection(self):
        """Virtual environments excluded from test detection"""
        # Regression test for rglob bug
```

---

## 8. Performance Testing

### 8.1 Timing Tests

**File**: `tests/performance/test_timing.py`

```python
class TestPerformance:
    """Performance and timing tests"""

    def test_single_evaluation_under_30s(self):
        """Single sample evaluation completes in <30s"""

    def test_batch_evaluation_scales_linearly(self):
        """Batch evaluation time scales linearly with samples"""

    def test_fcorr_timeout_respected(self):
        """F-CORR respects timeout settings"""

    def test_parallel_evaluation_faster(self):
        """Parallel evaluation faster than sequential"""
```

### 8.2 Resource Tests

**File**: `tests/performance/test_resources.py`

```python
class TestResourceUsage:
    """Resource usage tests"""

    def test_memory_stable_over_batch(self):
        """Memory usage stable during batch evaluation"""

    def test_no_file_handle_leaks(self):
        """File handles cleaned up after evaluation"""

    def test_subprocess_cleanup(self):
        """Subprocesses cleaned up after test runs"""
```

---

## 9. Test Data Validation

### 9.1 Reference Solution Validation

**File**: `tests/validation/test_reference_solutions.py`

```python
class TestReferenceSolutions:
    """Validate reference solutions (expected/) are correct"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_reference_passes_all_tests(self, sample_path):
        """Reference solution passes its own test suite"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_reference_scores_above_90(self, sample_path):
        """Reference solution scores 90%+ on all metrics"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_reference_has_no_syntax_errors(self, sample_path):
        """Reference solution has no syntax errors"""
```

### 9.2 Input Validation

**File**: `tests/validation/test_inputs.py`

```python
class TestInputValidation:
    """Validate input/ directories are valid starting points"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_input_is_incomplete(self, sample_path):
        """Input code is intentionally incomplete"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_input_is_parseable(self, sample_path):
        """Input code has valid syntax (but incomplete logic)"""

    @pytest.mark.parametrize("sample_path", get_all_sample_paths())
    def test_input_has_clear_todos(self, sample_path):
        """Input has TODO comments for LLM guidance"""
```

---

## 10. Implementation Priority

### Phase 1: Critical Bug Fixes (Immediate)

| Priority | Issue | Impact | Effort | Status |
|----------|-------|--------|--------|--------|
| P0 | F-CORR test execution against wrong directory | All F-CORR scores invalid | High | ✅ Fixed |
| P0 | F-CORR missing error tracebacks | Cannot debug failures | Medium | ✅ Fixed |
| P0 | SemSim AttributeError crash | Metric unusable | Low | ✅ Fixed |
| P0 | CQResult undefined field | Metric crashes | Low | ✅ Fixed |
| P0 | venv/node_modules in test detection | False test counts | Medium | ✅ Fixed |
| P0 | LanceDB module-level variable coupling | 85% false negatives | Medium | ✅ Fixed |

**Phase 1 Status**: ✅ All 6/6 P0 bugs fixed!

### Phase 2: Test Infrastructure (Week 1-2) ✅ COMPLETED

| Priority | Task | Tests | Status |
|----------|------|-------|--------|
| P1 | Test harness unit tests | 55 tests | ✅ Done |
| P1 | Metrics unit tests | 105 tests | ✅ Done |
| P1 | Sample validation tests | 56 tests | ✅ Done |

**Phase 2 Summary (Completed 2025-11-26)**:
- **Total Tests Created**: 216 tests
- **Pass Rate**: 100% (216/216 passing)
- **Test Files Created**:
  - `tests/test_harness/test_python_runner.py` - Python runner detection, parsing, exclusions
  - `tests/test_harness/test_typescript_runner.py` - TypeScript runner detection, Jest/Vitest/Mocha
  - `tests/test_harness/test_registry.py` - Registry detection and configuration
  - `tests/test_harness/test_models.py` - Pydantic model validation
  - `tests/metrics/test_i_acc.py` - Initialization correctness metric
  - `tests/metrics/test_f_corr.py` - Functional correctness result model
  - `tests/metrics/test_sem_sim.py` - Semantic similarity metric
  - `tests/metrics/test_cq.py` - Code quality metric
  - `tests/metrics/test_c_comp.py` - Configuration completeness metric
  - `tests/metrics/test_ipa.py` - Integration pattern accuracy metric
  - `tests/samples/test_sample_structure.py` - Sample directory validation

**Known Issues Found During Testing**:
- `_extract_pytest_stack_traces` has a regex limitation with test names containing underscores (documented in test file)

### Phase 3: Integration Tests (Week 2-3) ✅ COMPLETED

| Priority | Task | Tests | Status |
|----------|------|-------|--------|
| P2 | Evaluator integration tests | 38 tests | ✅ Done |
| P2 | Pipeline integration tests | 30 tests | ✅ Done |
| P2 | Result model integration tests | 37 tests | ✅ Done |
| P2 | E2E benchmark tests (full run) | 15 tests | ✅ Done |
| P2 | Golden file tests | 18 tests | ✅ Done |

**Phase 3 Summary (Completed 2025-11-26)**:
- **Total Integration/E2E Tests Created**: 138 tests (125 passing, 13 skipped for missing fixtures)
- **Test Files Created**:
  - `tests/integration/test_evaluator.py` - Evaluator initialization, methods, static methods
  - `tests/integration/test_results.py` - Result model scoring, serialization, consistency
  - `tests/integration/test_pipeline.py` - Sample loading, ground truth, evaluation execution
  - `tests/e2e/test_full_run.py` - Single/batch evaluation, cross-SDK, report generation
  - `tests/e2e/test_golden.py` - Expected solution quality, score stability, boundaries

**Key Test Coverage**:
- Evaluator orchestration and initialization
- All 6 metric result model validation (IAccResult, CCompResult, IPAResult, FCorrResult, CQResult, SemSimResult)
- EvaluationResult aggregation and overall_score calculation
- Grade calculation (A-F)
- Report generation (summary and detailed)
- Solution and GroundTruth loading
- Cross-SDK evaluation (LanceDB and Clerk)
- Score determinism and stability

### Phase 4: Quality & Regression (Week 3-4)

| Priority | Task | Tests |
|----------|------|-------|
| P3 | Regression test suite | 30+ tests |
| P3 | Performance tests | 10+ tests |
| P3 | Reference solution validation | 100 tests |

---

## Test Coverage Goals

| Component | Current Coverage | Target Coverage | Status |
|-----------|-----------------|-----------------|--------|
| Metrics (6 files) | ~80% | 90%+ | ✅ Phase 2 |
| Test Harness (6 files) | ~75% | 85%+ | ✅ Phase 2 |
| Evaluator | ~85% | 90%+ | ✅ Phase 3 |
| Core Models | ~90% | 95%+ | ✅ Phase 2+3 |
| Samples (100) | Partial | 100% validated | ✅ Phase 2 |
| E2E | ~70% | 80%+ | ✅ Phase 3 |

**Current Test Summary (as of 2025-11-26)**:
- **Total Tests**: 341
- **Pass Rate**: 100% (341 passing, 0 failing, 13 skipped)
- **Test Distribution**:
  - Unit tests (Phase 2): 216 tests
  - Integration/E2E tests (Phase 3): 125 tests (138 total, 13 skipped)

---

## Appendix A: Known Bugs Summary

| ID | Component | Description | Severity | Status |
|----|-----------|-------------|----------|--------|
| BUG-001 | f_corr | Test setup missing conftest.py copy and wrong sys.path | Critical | ✅ **Fixed** |
| BUG-002 | sem_sim | AttributeError on get_similarity_summary() | Critical | ✅ **Fixed** |
| BUG-003 | cq | Passes undefined 'deductions' field | Critical | ✅ **Fixed** |
| BUG-004 | f_corr | Missing error tracebacks in f_corr.json output | Critical | ✅ **Fixed** |
| BUG-005 | python_runner | rglob includes venv test files | High | ✅ **Fixed** |
| BUG-006 | typescript_runner | rglob includes node_modules test files | High | ✅ **Fixed** |
| BUG-007 | lancedb tests | Module-level variable coupling (see lancedb/bug-fixing-plan.md) | High | ✅ **Fixed** |
| BUG-008 | python_runner | -v and -q flags conflict in pytest | Medium | ⏳ Pending |
| BUG-009 | i_acc | Regex fails on nested braces | Medium | ⏳ Pending |
| BUG-010 | c_comp | TOML parsing is line-based, not proper | Medium | ⏳ Pending |
| BUG-011 | ipa | Path normalization uses lstrip incorrectly | Medium | ⏳ Pending |
| BUG-012 | sem_sim | Score can exceed 100 | Medium | ⏳ Pending |
| BUG-013 | typescript_runner | Framework state persists between runs | Medium | ⏳ Pending |
| BUG-014 | python_runner | PYTHONPATH uses wrong separator on Windows | Medium | ⏳ Pending |
| BUG-015 | registry | No exception handling in detection loop | Medium | ⏳ Pending |
| BUG-016 | Result | score==0 check doesn't distinguish unset from actual 0 | Low | ⏳ Pending |
| BUG-017 | evaluator | IPA returns f1 instead of score in reports | Low | ⏳ Pending |

### Fix Summary (Phase 1)
- **Fixed**: 7 bugs (BUG-001 through BUG-007) ✅
- **Pending**: 10 bugs (BUG-008 through BUG-017)
- **All Critical/High severity bugs resolved!**

---

## Appendix B: Test File Organization

```
SDKBench/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── fixtures/                # Test data fixtures
│   │   ├── mock_solutions/
│   │   ├── mock_ground_truths/
│   │   └── expected_results/
│   │
│   ├── metrics/                 # Metric unit tests
│   │   ├── test_i_acc.py
│   │   ├── test_c_comp.py
│   │   ├── test_ipa.py
│   │   ├── test_f_corr.py
│   │   ├── test_cq.py
│   │   └── test_sem_sim.py
│   │
│   ├── test_harness/           # Test harness tests
│   │   ├── test_registry.py
│   │   ├── test_python_runner.py
│   │   ├── test_typescript_runner.py
│   │   └── test_models.py
│   │
│   ├── integration/            # Integration tests
│   │   ├── test_evaluator.py
│   │   ├── test_results.py
│   │   └── test_pipeline.py
│   │
│   ├── samples/                # Sample validation
│   │   ├── test_sample_structure.py
│   │   ├── test_metadata.py
│   │   ├── test_sample_tests.py
│   │   └── test_consistency.py
│   │
│   ├── e2e/                    # End-to-end tests
│   │   ├── test_full_run.py
│   │   ├── test_cli.py
│   │   └── test_golden.py
│   │
│   ├── regression/             # Regression tests
│   │   ├── test_scores.py
│   │   └── test_bug_fixes.py
│   │
│   ├── performance/            # Performance tests
│   │   ├── test_timing.py
│   │   └── test_resources.py
│   │
│   └── validation/             # Data validation
│       ├── test_reference_solutions.py
│       └── test_inputs.py
│
├── pytest.ini                  # Pytest configuration
└── pyproject.toml             # Test dependencies
```

---

## Appendix C: Pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks integration tests
    e2e: marks end-to-end tests
    regression: marks regression tests
filterwarnings =
    ignore::DeprecationWarning
```

---

## Appendix D: Recommended conftest.py Fixtures

```python
# tests/conftest.py

import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def sample_dir():
    """Provides path to samples directory"""
    return Path(__file__).parent.parent / "samples"

@pytest.fixture
def clerk_samples(sample_dir):
    """List of all Clerk sample paths"""
    return list((sample_dir / "clerk").iterdir())

@pytest.fixture
def lancedb_samples(sample_dir):
    """List of all LanceDB sample paths"""
    return list((sample_dir / "lancedb").iterdir())

@pytest.fixture
def temp_project():
    """Creates a temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_solution(temp_project):
    """Creates a mock solution for testing"""
    # Create minimal solution structure
    (temp_project / "app.py").write_text("import lancedb\ndb = lancedb.connect('./db')")
    return temp_project

@pytest.fixture
def mock_ground_truth():
    """Creates a mock ground truth object"""
    from sdkbench.core.GroundTruth import GroundTruth
    # Return configured GroundTruth
    pass
```

---

*This testing plan was generated based on a comprehensive audit of the SDKBench codebase. Implementation should prioritize Phase 1 critical bug fixes before expanding test coverage.*
