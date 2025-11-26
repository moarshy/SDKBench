# SDKBench Architecture Documentation

This document provides a comprehensive overview of all files, classes, and functions in the `sdkbench` package.

---

## Table of Contents

1. [Package Structure](#package-structure)
2. [Core Module](#core-module)
3. [Parsers Module](#parsers-module)
4. [Metrics Module](#metrics-module)
5. [Test Harness Module](#test-harness-module)
6. [LLM Module](#llm-module)
7. [Evaluator Module](#evaluator-module)

---

## Package Structure

```
sdkbench/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── solution.py
│   ├── ground_truth.py
│   └── result.py
├── parsers/
│   ├── __init__.py
│   ├── python_parser.py
│   ├── typescript_parser.py
│   ├── env_parser.py
│   └── config_parser.py
├── metrics/
│   ├── __init__.py
│   ├── i_acc.py
│   ├── c_comp.py
│   ├── ipa.py
│   ├── cq.py
│   ├── sem_sim.py
│   └── f_corr.py
├── test_harness/
│   ├── __init__.py
│   ├── models.py
│   ├── registry.py
│   ├── base_runner.py
│   ├── python_runner.py
│   ├── typescript_runner.py
│   ├── executor.py
│   ├── build_runner.py
│   └── test_runner.py
├── llm/
│   ├── __init__.py
│   ├── base.py
│   ├── anthropic_provider.py
│   ├── openai_provider.py
│   ├── prompt_builder.py
│   └── solution_generator.py
└── evaluator/
    ├── __init__.py
    └── evaluator.py
```

---

## Core Module

**Location**: `sdkbench/core/`

The core module provides the fundamental data structures for evaluation.

### `solution.py`

#### Class: `Solution`

Represents an LLM-generated solution to evaluate.

**Constructor**:
- `__init__(self, solution_dir: Path)` - Initialize from a directory containing solution files

**Attributes**:
- `solution_dir: Path` - Path to the solution directory
- `files: Dict[str, str]` - Maps relative paths to file contents

**Methods**:

| Method | Description |
|--------|-------------|
| `_load_files()` | Load all files from solution directory into memory (`.ts`, `.tsx`, `.js`, `.jsx`, `.json`, `.env`) |
| `has_file(path: str) -> bool` | Check if solution contains a file at the given path |
| `get_file_content(path: str) -> Optional[str]` | Get content of a file in the solution |
| `get_all_files() -> Dict[str, str]` | Get all files in the solution |
| `extract_imports(file_path: Optional[str]) -> List[str]` | Extract import statements from solution files |
| `has_import(import_pattern: str) -> bool` | Check if solution has a specific import |
| `has_pattern(pattern: str, file_path: Optional[str]) -> bool` | Check if a pattern exists in solution files |
| `extract_jsx_component(component_name: str) -> Optional[Dict]` | Extract JSX component usage and props |
| `extract_env_vars() -> List[str]` | Extract environment variable names from `.env` files |
| `extract_clerk_env_vars() -> List[str]` | Extract Clerk-specific environment variables |
| `extract_provider_props() -> List[str]` | Extract ClerkProvider props from solution |
| `extract_middleware_config() -> Dict` | Extract authMiddleware configuration |
| `extract_integration_points() -> Set[str]` | Extract files that use Clerk authentication |
| `has_client_directive(file_path: str) -> bool` | Check if file has 'use client' directive |

---

### `ground_truth.py`

#### Class: `GroundTruth`

Represents ground truth for a sample (loaded from `metadata.json`).

**Constructor**:
- `__init__(self, metadata_path: Path)` - Load ground truth from metadata.json

**Attributes**:
- `metadata_path: Path` - Path to metadata.json
- `metadata: Dict` - Full metadata dictionary
- `sample_id: str` - Sample identifier
- `task_type: int` - Task type (1-5)
- `task_name: str` - Human-readable task name
- `framework: str` - Framework (e.g., "nextjs", "python")
- `difficulty: str` - Difficulty level
- `sdk: str` - SDK name (e.g., "clerk", "lancedb")
- `sdk_version: str` - SDK version
- `ground_truth: Dict` - Ground truth data
- `ingredients: Dict` - Ground truth ingredients
- `evaluation_targets: Dict` - Evaluation target data

**Ingredient Access Methods**:

| Method | Description |
|--------|-------------|
| `get_initialization() -> Optional[Dict]` | Get initialization ingredient data (location, pattern, imports) |
| `get_configuration() -> Optional[Dict]` | Get configuration ingredient data (env_vars, provider_props) |
| `get_integration_points() -> List[Dict]` | Get integration points data |
| `get_error_handling() -> List[Dict]` | Get error handling patterns |

**Evaluation Target Methods**:

| Method | Description |
|--------|-------------|
| `get_i_acc_targets() -> Dict` | Get I-ACC evaluation targets |
| `get_c_comp_targets() -> Dict` | Get C-COMP evaluation targets |
| `get_ipa_targets() -> Dict` | Get IPA evaluation targets |
| `get_f_corr_targets() -> Dict` | Get F-CORR evaluation targets |

**Convenience Methods**:

| Method | Description |
|--------|-------------|
| `get_expected_files() -> List[str]` | Get list of files that should be modified |
| `get_expected_imports() -> List[str]` | Get list of expected imports |
| `get_expected_env_vars() -> List[str]` | Get list of expected environment variables |
| `get_expected_patterns() -> List[str]` | Get list of expected patterns |
| `to_dict() -> Dict` | Convert to dictionary |

---

### `result.py`

#### Base Class: `MetricResult`

Base class for all metric results (Pydantic model).

**Fields**:
- `score: float = 0.0` - Score 0-100
- `details: Dict[str, Any]` - Additional details

#### Class: `IAccResult(MetricResult)`

I-ACC (Initialization Correctness) metric result.

**Fields**:
- `file_location_correct: bool = False`
- `imports_correct: bool = False`
- `pattern_correct: bool = False`
- `placement_correct: bool = False`

**Score Calculation**: Weighted sum (file: 20%, imports: 20%, pattern: 30%, placement: 30%)

#### Class: `CCompResult(MetricResult)`

C-COMP (Configuration Completeness) metric result.

**Fields**:
- `env_vars_score: float = 0.0` (0-1)
- `provider_props_score: float = 0.0` (0-1)
- `middleware_config_score: float = 0.0` (0-1)
- `missing_env_vars: List[str]`
- `missing_provider_props: List[str]`
- `missing_middleware_config: List[str]`

**Score Calculation**: Weighted sum (env_vars: 50%, provider_props: 30%, middleware: 20%)

#### Class: `IPAResult(MetricResult)`

IPA (Integration Point Accuracy) metric result.

**Fields**:
- `precision: float = 0.0` (0-100)
- `recall: float = 0.0` (0-100)
- `f1: float = 0.0` (0-100)
- `true_positives: List[str]`
- `false_positives: List[str]`
- `false_negatives: List[str]`

**Score Calculation**: F1 score * 100

#### Class: `FCorrResult(MetricResult)`

F-CORR (Functional Correctness) metric result.

**Fields**:
- `tests_passed: int = 0`
- `tests_total: int = 0`
- `tests_skipped: int = 0`
- `pass_rate: float = 0.0` (0-100)
- `failed_tests: List[str]`
- `error_messages: List[str]`
- `failure_details: List[Dict[str, Any]]` - Full stack traces
- `raw_output: Optional[str]` - Raw test output
- `install_error: Optional[str]`
- `build_error: Optional[str]`

**Score Calculation**: pass_rate = (tests_passed / tests_total) * 100

#### Class: `CQResult(MetricResult)`

CQ (Code Quality) metric result.

**Fields**:
- `type_errors: int = 0`
- `eslint_errors: int = 0`
- `security_issues: int = 0`
- `deductions: List[Dict[str, Any]]` - Detailed quality deductions

**Properties**:
- `total_deductions: int` - Sum of deduction points

**Score Calculation**: 100 - total_deductions (min 0)

#### Class: `SemSimResult(MetricResult)`

SEM-SIM (Semantic Similarity) metric result.

**Fields**:
- `similarity_score: float = 0.0` (0-100)
- `pattern_match: bool = False`
- `approach_match: bool = False`
- `matched_patterns: List[str]`
- `missing_patterns: List[str]`
- `structure_similarity: float = 0.0`
- `pattern_matching: float = 0.0`
- `approach_alignment: float = 0.0`

#### Class: `EvaluationResult`

Complete evaluation result for a solution.

**Fields**:
- `sample_id: str`
- `solution_dir: Path`
- `task_type: int`
- `timestamp: str`
- `duration_seconds: float`
- `i_acc: Optional[IAccResult]`
- `c_comp: Optional[CCompResult]`
- `ipa: Optional[IPAResult]`
- `f_corr: Optional[FCorrResult]`
- `cq: Optional[CQResult]`
- `sem_sim: Optional[SemSimResult]`
- `evaluation_error: Optional[str]`

**Computed Properties**:
- `overall_score: float` - Average of all metric scores

**Methods**:
- `has_errors -> bool` - Check if evaluation encountered errors
- `get_metric_summary() -> Dict[str, float]` - Get summary of all metric scores
- `to_dict() -> Dict` - Convert to dictionary
- `to_json_file(path: Path)` - Save results to JSON file
- `from_dict(data: Dict) -> EvaluationResult` - Load from dictionary
- `from_json_file(path: Path) -> EvaluationResult` - Load from JSON file
- `print_summary()` - Print formatted summary to console

---

## Parsers Module

**Location**: `sdkbench/parsers/`

Provides code analysis utilities using regex-based parsing.

### `python_parser.py`

#### Class: `PythonParser`

Parser for Python files using regex-based pattern matching.

**Static Methods**:

| Method | Description |
|--------|-------------|
| `extract_imports(content: str) -> List[Dict]` | Extract all import statements (import, from...import) |
| `has_import(content: str, module: str, name: Optional[str]) -> bool` | Check if file has a specific import |
| `extract_function_definitions(content: str) -> List[Dict]` | Extract all function definitions with args, return types, async status |
| `extract_class_definitions(content: str) -> List[Dict]` | Extract all class definitions with bases |
| `extract_function_calls(content: str, function_name: str) -> List[Dict]` | Extract function call locations and contexts |
| `extract_method_calls(content: str, method_name: str) -> List[Dict]` | Extract method calls on any object |
| `has_pattern(content: str, pattern: str) -> bool` | Check if content contains a pattern |
| `extract_decorators(content: str, function_name: Optional[str]) -> List[Dict]` | Extract decorator usage |
| `extract_variable_assignments(content: str, var_name: Optional[str]) -> List[Dict]` | Extract variable assignments |
| `has_error_handling(content: str) -> bool` | Check if content has try-except blocks |
| `has_type_hints(content: str) -> bool` | Check if functions have type hints |
| `extract_string_values(content: str, pattern: str) -> List[str]` | Extract string values near a pattern |
| `count_patterns(content: str, patterns: Dict[str, str]) -> Dict[str, int]` | Count occurrences of various patterns |
| `extract_docstring(content: str, function_name: Optional[str]) -> Optional[str]` | Extract docstring from module or function |
| `get_sdk_patterns(sdk: str) -> Dict[str, str]` | Get SDK-specific regex patterns (e.g., lancedb) |

---

### `typescript_parser.py`

#### Class: `TypeScriptParser`

Parser for TypeScript/JavaScript/JSX files.

**Static Methods**:

| Method | Description |
|--------|-------------|
| `extract_imports(content: str) -> List[Dict]` | Extract import statements (ES6, require) |
| `has_clerk_import(content: str, import_name: Optional[str]) -> bool` | Check if file has Clerk imports |
| `extract_jsx_component_usage(content: str, component_name: str) -> Optional[Dict]` | Extract JSX component usage with props |
| `extract_function_calls(content: str, function_name: str) -> List[Dict]` | Extract function call locations |
| `extract_hook_usage(content: str, hook_name: str) -> Optional[Dict]` | Extract React hook usage (destructured props) |
| `has_client_directive(content: str) -> bool` | Check for 'use client' directive |
| `has_server_directive(content: str) -> bool` | Check for 'use server' directive |
| `extract_exported_function(content: str, function_name: str) -> Optional[Dict]` | Extract exported function definition |
| `extract_middleware_config(content: str) -> Dict` | Extract middleware configuration (routes, matcher) |
| `extract_api_route_protection(content: str) -> Dict` | Extract API route protection patterns |
| `count_clerk_patterns(content: str) -> Dict[str, int]` | Count Clerk-specific patterns |

---

### `env_parser.py`

#### Class: `EnvParser`

Parser for `.env` and `.env.local` files.

**Static Methods**:

| Method | Description |
|--------|-------------|
| `parse_env_file(file_path: Path) -> Dict[str, Optional[str]]` | Parse .env file and extract variables |
| `extract_from_content(content: str) -> Dict[str, Optional[str]]` | Extract environment variables from content |
| `has_clerk_keys(env_vars: Dict) -> bool` | Check if env vars contain Clerk keys |
| `extract_clerk_keys(env_vars: Dict) -> Dict[str, Optional[str]]` | Extract Clerk-specific variables |
| `get_required_clerk_keys() -> Set[str]` | Get set of required Clerk env vars |
| `validate_clerk_keys(env_vars: Dict) -> Dict[str, bool]` | Validate required Clerk keys are present |
| `find_env_references_in_code(content: str) -> List[str]` | Find env var references in code (process.env, import.meta.env) |
| `check_env_usage_consistency(env_file_vars, code_references) -> Dict` | Check if code references match .env file |
| `extract_env_example_vars(file_path: Path) -> Set[str]` | Extract variable names from .env.example |
| `compare_env_files(env_path, env_example_path) -> Dict` | Compare .env with .env.example |

---

### `config_parser.py`

#### Class: `ConfigParser`

Parser for configuration files (package.json, tsconfig.json, etc.).

**Static Methods**:

| Method | Description |
|--------|-------------|
| `parse_package_json(file_path: Path) -> Dict` | Parse package.json file |
| `extract_dependencies(package_json: Dict) -> Dict[str, str]` | Extract all dependencies (deps + devDeps) |
| `has_clerk_dependency(package_json: Dict) -> bool` | Check for Clerk dependency |
| `extract_clerk_dependencies(package_json: Dict) -> Dict[str, str]` | Extract Clerk-related dependencies |
| `get_clerk_package_for_framework(framework: str) -> str` | Get expected Clerk package for framework |
| `validate_clerk_version(version: str) -> Dict` | Validate Clerk package version |
| `parse_next_config(file_path: Path) -> Dict` | Parse next.config.js file |
| `extract_middleware_matcher(content: str) -> Optional[List[str]]` | Extract matcher config from middleware |
| `parse_tsconfig(file_path: Path) -> Dict` | Parse tsconfig.json (with comment removal) |
| `check_typescript_setup(solution_dir: Path) -> Dict[str, bool]` | Check TypeScript setup status |
| `extract_scripts(package_json: Dict) -> Dict[str, str]` | Extract npm scripts |
| `has_required_scripts(package_json: Dict, required: List[str]) -> Dict[str, bool]` | Check for required scripts |
| `parse_eslint_config(file_path: Path) -> Dict` | Parse .eslintrc.json |
| `extract_framework_from_dependencies(package_json: Dict) -> Optional[str]` | Detect framework from dependencies |
| `compare_dependency_versions(actual, expected) -> Dict` | Compare actual vs expected dependencies |
| `extract_git_info(solution_dir: Path) -> Dict` | Extract git information |

---

## Metrics Module

**Location**: `sdkbench/metrics/`

Implements the 6 evaluation metrics.

### `i_acc.py` - Initialization Correctness

#### Class: `IAccEvaluator`

Evaluates initialization correctness.

**Scoring Weights**:
- File location: 20%
- Imports: 20%
- Pattern: 30%
- Placement: 30%

**Methods**:

| Method | Description |
|--------|-------------|
| `evaluate() -> IAccResult` | Evaluate initialization correctness |
| `get_details() -> Dict` | Get detailed evaluation breakdown |

**Internal Checks**:
- `_check_file_location(init_data)` - Verify file exists at expected location
- `_check_imports(init_data)` - Verify all required imports are present
- `_check_pattern(init_data)` - Verify correct initialization pattern (JSX component, function call, export)
- `_check_placement(init_data)` - Verify placement (wraps_children, top_level, in_function)

---

### `c_comp.py` - Configuration Completeness

#### Class: `CCompEvaluator`

Evaluates configuration completeness.

**Scoring Weights**:
- Environment variables: 50%
- Dependencies/Provider props: 30%
- Middleware config: 20%

**Methods**:

| Method | Description |
|--------|-------------|
| `evaluate() -> CCompResult` | Evaluate configuration completeness |
| `get_details() -> Dict` | Get detailed evaluation breakdown |

**Internal Checks**:
- `_check_env_vars(config_data)` - Check required env vars present
- `_check_dependencies(config_data)` - Check dependencies (package.json, requirements.txt, pyproject.toml)
- `_check_middleware(config_data)` - Check middleware configuration

---

### `ipa.py` - Integration Point Accuracy

#### Class: `IPAEvaluator`

Evaluates integration point accuracy using Precision/Recall/F1.

**Metrics**:
- **Precision**: % of solution's integration points that are correct
- **Recall**: % of expected integration points that were found
- **F1**: Harmonic mean of precision and recall

**Methods**:

| Method | Description |
|--------|-------------|
| `evaluate() -> IPAResult` | Evaluate integration point accuracy |
| `get_details() -> Dict` | Get detailed evaluation breakdown |
| `analyze_integration_patterns() -> Dict` | Analyze SDK-specific patterns |
| `check_integration_quality() -> Dict` | Check quality metrics (error handling, loading states) |
| `compare_with_expected_patterns() -> Dict` | Compare solution vs expected patterns |

---

### `cq.py` - Code Quality

#### Class: `CQEvaluator`

Evaluates code quality through static analysis.

**Deduction Points**:
- Missing error handling: -10 per occurrence
- Inconsistent naming: -5 per occurrence
- Missing TypeScript types: -5 per occurrence
- Code duplication: -10 per duplicate block
- Poor structure: -15 per major issue

**Methods**:

| Method | Description |
|--------|-------------|
| `evaluate() -> CQResult` | Evaluate code quality |
| `get_details() -> Dict` | Get detailed evaluation breakdown |
| `get_quality_summary() -> Dict` | Get high-level quality summary with grade (A-F) |

**Internal Checks**:
- `_check_error_handling()` - Check for missing try-catch/try-except
- `_check_naming_consistency()` - Check naming conventions (camelCase, snake_case, PascalCase)
- `_check_typescript_types()` - Check for `any` types, untyped params
- `_check_code_duplication()` - Check for duplicate code blocks
- `_check_structure()` - Check file organization, middleware placement

---

### `sem_sim.py` - Semantic Similarity

#### Class: `SemSimEvaluator`

Evaluates semantic similarity to expected approach.

**Scoring Weights**:
- Code structure similarity: 30%
- Pattern matching: 40%
- Approach alignment: 30%

**Methods**:

| Method | Description |
|--------|-------------|
| `evaluate() -> SemSimResult` | Evaluate semantic similarity |
| `get_details() -> Dict` | Get detailed evaluation breakdown |
| `get_similarity_summary() -> Dict` | Get high-level similarity summary |

**Internal Checks**:
- `_check_structure_similarity()` - Check file/directory structure similarity (Jaccard)
- `_check_pattern_matching()` - Check initialization, configuration, integration patterns
- `_check_approach_alignment()` - Check SDK patterns, conventions, server/client usage

---

### `f_corr.py` - Functional Correctness

#### Class: `FCorrEvaluator`

Evaluates functional correctness by running tests.

**Supported Languages**:
- TypeScript/JavaScript (Jest, Vitest, Mocha)
- Python (pytest)

**Scoring Modes**:
- **STRICT** (default): Any test failure = 0 score
- **PASS_RATE**: Score equals test pass rate percentage

**Methods**:

| Method | Description |
|--------|-------------|
| `evaluate(run_build, run_tests, auto_install, strict, test_dir) -> FCorrResult` | Full evaluation with tests |
| `evaluate_new(auto_install, test_dir, strict) -> NewFCorrResult` | Return richer Pydantic model |
| `quick_check() -> Dict` | Quick check without full execution |
| `get_build_details() -> Dict` | Get detailed build results |
| `get_test_details() -> Dict` | Get detailed test results |
| `get_type_check_details() -> Dict` | Get TypeScript type checking results |
| `get_lint_details() -> Dict` | Get linter results |
| `get_coverage_details() -> Optional[Dict]` | Get test coverage results |
| `get_details() -> Dict` | Get full evaluation breakdown |
| `evaluate_without_execution() -> FCorrResult` | Static analysis only (conservative estimate) |

---

## Test Harness Module

**Location**: `sdkbench/test_harness/`

Provides language-agnostic test running capabilities.

### `models.py`

#### Enum: `TestStatus`

- `PASSED`, `FAILED`, `SKIPPED`, `ERROR`

#### Enum: `Language`

- `PYTHON`, `TYPESCRIPT`, `JAVASCRIPT`, `GO`, `RUST`

#### Enum: `TestFramework`

- `PYTEST`, `UNITTEST`, `JEST`, `VITEST`, `MOCHA`, `GO_TEST`, `CARGO_TEST`

#### Class: `TestFailure`

Details of a single test failure.

**Fields**:
- `test_name: str`
- `error_message: str`
- `file_path: Optional[str]`
- `line_number: Optional[int]`
- `stack_trace: Optional[str]`

#### Class: `TestResult`

Result of running tests.

**Fields**:
- `success: bool`
- `total: int`
- `passed: int`
- `failed: int`
- `skipped: int`
- `duration: float`
- `output: str`
- `failures: List[TestFailure]`

**Computed**:
- `pass_rate: float` - Percentage

#### Class: `DependencyInstallResult`

**Fields**:
- `success: bool`
- `duration: float`
- `output: str`
- `error: Optional[str]`
- `packages_installed: int`

#### Class: `RunnerDetectionResult`

**Fields**:
- `detected: bool`
- `language: Optional[Language]`
- `framework: Optional[TestFramework]`
- `confidence: float` (0-1)
- `markers_found: List[str]`

#### Class: `FCorrResult` (test_harness version)

**Fields**:
- `score: float` (0-100)
- `test_results: Optional[TestResult]`
- `install_results: Optional[DependencyInstallResult]`
- `language: Optional[Language]`
- `framework: Optional[TestFramework]`
- `error: Optional[str]`
- `duration: float`

---

### `registry.py`

#### Class: `TestRunnerRegistry`

Registry of available test runners with auto-detection.

**Class Methods**:

| Method | Description |
|--------|-------------|
| `register(runner_class: Type[BaseTestRunner])` | Register a new test runner |
| `get_runner(working_dir: Path) -> Optional[BaseTestRunner]` | Get appropriate runner (highest confidence) |
| `get_all_runners() -> List[Type[BaseTestRunner]]` | Get all registered runner classes |
| `detect_all(working_dir: Path) -> List[RunnerDetectionResult]` | Run detection for all runners |
| `clear()` | Clear all registered runners (for testing) |

**Default Runners**: TypeScriptTestRunner, PythonTestRunner

---

### `base_runner.py`

#### Abstract Class: `BaseTestRunner`

Base class for language-specific test runners.

**Constructor**:
- `__init__(self, working_dir: Path, timeout: int = 300)`

**Abstract Methods**:

| Method | Description |
|--------|-------------|
| `get_language() -> Language` | Return the language this runner handles |
| `get_framework() -> TestFramework` | Return the test framework this runner uses |
| `detect() -> RunnerDetectionResult` | Detect if this runner can handle the project |
| `install_dependencies() -> DependencyInstallResult` | Install project dependencies |
| `run_tests(test_dir: Optional[Path]) -> TestResult` | Run tests and return results |

**Concrete Methods**:
- `can_handle() -> bool` - Quick check if runner can handle project

---

### `python_runner.py`

#### Class: `PythonTestRunner(BaseTestRunner)`

Test runner for Python projects using pytest.

**Excluded Directories**: `venv`, `.venv`, `env`, `__pycache__`, `.git`, `node_modules`, etc.

**Detection Markers**:
- `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`
- `test_*.py`, `*_test.py` files
- `conftest.py`

**Dependency Installation**:
- Tries `pip install -r requirements.txt`
- Falls back to `pip install -e .` (pyproject.toml)

**Test Execution**:
- Command: `python -m pytest -v --tb=short -q`
- Sets `PYTHONPATH` to working directory

**Output Parsing**:
- Extracts passed/failed/skipped counts from pytest output
- Extracts failure details with stack traces

---

### `typescript_runner.py`

#### Class: `TypeScriptTestRunner(BaseTestRunner)`

Test runner for TypeScript/JavaScript projects.

**Supported Frameworks**: Jest, Vitest, Mocha

**Excluded Directories**: `node_modules`, `.git`, `dist`, `build`, `.next`, etc.

**Detection Markers**:
- `package.json` (required)
- Jest/Vitest/Mocha in dependencies
- Test script in package.json
- `*.test.ts`, `*.test.tsx`, `*.spec.ts` files
- `tsconfig.json`

**Dependency Installation**:
- Runs `npm install`
- Auto-installs Jest/ts-jest if detected from imports but not in dependencies
- Creates `jest.config.js` if missing

**Test Execution**:
- Primary: `npm test`
- Fallback: `npx jest --no-coverage`
- Sets `CI=true` to prevent interactive mode

**Output Parsing**:
- `_parse_jest_output()` - Parse Jest format
- `_parse_vitest_output()` - Parse Vitest format
- `_parse_mocha_output()` - Parse Mocha format

---

## LLM Module

**Location**: `sdkbench/llm/`

Provides LLM integration for generating solutions.

### `base.py`

#### Class: `LLMConfig`

Configuration for LLM providers.

**Fields**:
- `model: str`
- `temperature: float = 0.1`
- `max_tokens: int = 4000`
- `top_p: float = 0.95`
- `api_key: Optional[str]`
- `base_url: Optional[str]`
- `retry_count: int = 3`
- `retry_delay: float = 1.0`

#### Class: `LLMResponse`

Response from LLM provider.

**Fields**:
- `content: str`
- `model: str`
- `tokens_used: int`
- `prompt_tokens: int`
- `completion_tokens: int`
- `finish_reason: str`
- `cost: Optional[float]`
- `latency_ms: Optional[float]`
- `raw_response: Optional[Dict]`

#### Abstract Class: `LLMProvider`

Base class for LLM providers.

**Abstract Methods**:
- `generate(prompt: str, system_prompt: Optional[str]) -> LLMResponse`
- `generate_with_retry(prompt, system_prompt, validation_fn) -> LLMResponse`

**Concrete Methods**:

| Method | Description |
|--------|-------------|
| `extract_code_blocks(content: str) -> List[Dict]` | Extract code blocks with language hints |
| `extract_files_from_response(content: str) -> Dict[str, str]` | Extract file paths and contents |
| `calculate_cost(prompt_tokens, completion_tokens) -> float` | Calculate cost (override in subclass) |
| `save_response(response, output_path)` | Save response to JSON file |
| `load_response(response_path) -> LLMResponse` | Load response from JSON file |

---

### `anthropic_provider.py`

#### Class: `AnthropicProvider(LLMProvider)`

Anthropic Claude provider implementation.

**Pricing** (per 1M tokens):
- claude-3-5-sonnet: $3 input, $15 output
- claude-3-opus: $15 input, $75 output
- claude-3-haiku: $0.25 input, $1.25 output
- claude-haiku-4.5: $1 input, $5 output

**Methods**:
- `generate(prompt, system_prompt) -> LLMResponse`
- `generate_with_retry(prompt, system_prompt, validation_fn) -> LLMResponse`
- `calculate_cost(prompt_tokens, completion_tokens) -> float`

**Notes**:
- Uses `ANTHROPIC_API_KEY` env var if not provided
- Claude 4.5 models don't support both temperature and top_p

---

### `openai_provider.py`

#### Class: `OpenAIProvider(LLMProvider)`

OpenAI provider implementation.

**Pricing** (per 1M tokens):
- gpt-4-turbo: $10 input, $30 output
- gpt-4: $30 input, $60 output
- gpt-4o: $5 input, $15 output
- gpt-4o-mini: $0.15 input, $0.60 output
- gpt-3.5-turbo: $0.50 input, $1.50 output

**Methods**:
- `generate(prompt, system_prompt) -> LLMResponse`
- `generate_with_retry(prompt, system_prompt, validation_fn) -> LLMResponse`
- `calculate_cost(prompt_tokens, completion_tokens) -> float`

**Notes**:
- Uses `OPENAI_API_KEY` env var if not provided
- Supports custom `base_url` for API proxies
- Uses `max_completion_tokens` for newer models (gpt-5, 2025)

---

### `prompt_builder.py`

#### Class: `PromptBuilder`

Build prompts for SDK instrumentation tasks.

**SDK Contexts**: Clerk, LanceDB

**Task Types by SDK**:
| SDK | Task 1 | Task 2 | Task 3 | Task 4 | Task 5 |
|-----|--------|--------|--------|--------|--------|
| Clerk | Initialization | Middleware Config | Hooks Integration | Complete Integration | Migration |
| LanceDB | Initialization | Data Operations | Search | Pipeline Integration | Migration |

**Methods**:

| Method | Description |
|--------|-------------|
| `build_prompt(sdk, task_type, description, framework, sdk_version, input_files, additional_context) -> Tuple[str, str]` | Build system and user prompts |
| `build_from_metadata(metadata_path, input_dir) -> Tuple[str, str]` | Build prompt from metadata.json and input files |

**Prompt Features**:
- SDK-specific context and examples
- Task-specific instructions
- Enforces filepath comments in code blocks (`# filepath: app.py`)
- Lists expected output files

---

### `solution_generator.py`

#### Class: `SolutionGenerator`

Generate solution directories from LLM responses.

**Methods**:

| Method | Description |
|--------|-------------|
| `generate_solution(llm_response, output_dir, sample_id, model_name, copy_input) -> Path` | Generate solution directory from LLM response |

**File Extraction Patterns**:
1. Explicit markers: `// filepath: path/to/file.ext`, `File: path/to/file.ext`
2. Path comments in code: `// app/layout.tsx`
3. Fallback: Infer from code blocks with language hints

**Generated Files**:
- Solution files extracted from LLM response
- `generation_metadata.json` - Sample ID, model, timestamp, files list
- `llm_response.txt` - Raw LLM response

---

## Evaluator Module

**Location**: `sdkbench/evaluator/`

Orchestrates all metrics for comprehensive evaluation.

### `evaluator.py`

#### Class: `Evaluator`

Main evaluator that runs all metrics and generates results.

**Constructor**:
```python
Evaluator(
    solution_dir: Path,
    metadata_path: Optional[Path] = None  # Defaults to solution_dir/metadata.json
)
```

**Metric Evaluators** (initialized automatically):
- `i_acc_evaluator: IAccEvaluator`
- `c_comp_evaluator: CCompEvaluator`
- `ipa_evaluator: IPAEvaluator`
- `f_corr_evaluator: FCorrEvaluator`
- `cq_evaluator: CQEvaluator`
- `sem_sim_evaluator: SemSimEvaluator`

**Methods**:

| Method | Description |
|--------|-------------|
| `evaluate(run_build, run_tests, metrics) -> EvaluationResult` | Run full evaluation with selected metrics |
| `evaluate_quick() -> EvaluationResult` | Quick evaluation without build/tests (skips F-CORR) |
| `get_detailed_report() -> Dict` | Get comprehensive evaluation details |
| `get_summary() -> Dict` | Get high-level summary with grade |
| `save_results(output_path, detailed)` | Save results to JSON file |

**Static Methods**:

| Method | Description |
|--------|-------------|
| `evaluate_directory(solution_dir, output_dir, run_build, run_tests) -> EvaluationResult` | Convenience method to evaluate a directory |
| `batch_evaluate(sample_dirs, output_dir, run_build, run_tests) -> List[EvaluationResult]` | Evaluate multiple samples |

**Grading Scale**:
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: 0-59

---

## Usage Examples

### Evaluating a Solution

```python
from pathlib import Path
from sdkbench.evaluator import Evaluator

# Full evaluation
evaluator = Evaluator(Path("./solutions/sample_001"))
result = evaluator.evaluate(run_build=True, run_tests=True)
result.print_summary()

# Quick evaluation (no tests)
result = evaluator.evaluate_quick()

# Get detailed report
report = evaluator.get_detailed_report()
```

### Using Individual Metrics

```python
from sdkbench.core import Solution, GroundTruth
from sdkbench.metrics import IAccEvaluator, FCorrEvaluator

solution = Solution(Path("./solution"))
ground_truth = GroundTruth(Path("./metadata.json"))

# I-ACC evaluation
i_acc = IAccEvaluator(solution, ground_truth)
result = i_acc.evaluate()
print(f"I-ACC Score: {result.score}%")

# F-CORR evaluation
f_corr = FCorrEvaluator(solution, ground_truth)
result = f_corr.evaluate(strict=True)
print(f"Tests passed: {result.tests_passed}/{result.tests_total}")
```

### Generating Solutions with LLM

```python
from sdkbench.llm import AnthropicProvider, LLMConfig, PromptBuilder, SolutionGenerator

# Configure provider
config = LLMConfig(model="claude-3-5-sonnet-20241022")
provider = AnthropicProvider(config)

# Build prompt
builder = PromptBuilder()
system_prompt, user_prompt = builder.build_from_metadata(
    Path("./samples/sample_001/metadata.json"),
    Path("./samples/sample_001/input")
)

# Generate response
response = provider.generate(user_prompt, system_prompt)

# Create solution files
generator = SolutionGenerator()
solution_path = generator.generate_solution(
    response.content,
    Path("./solutions"),
    "sample_001",
    "claude-3-5-sonnet"
)
```
