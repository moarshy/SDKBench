# Week 3: Evaluation Pipeline Infrastructure Plan

**Status:** Planning Phase
**Date:** 2025-11-20

---

## Directory Structure

```
SDKBench/
├── sdkbench/                      # NEW: Core evaluation package
│   ├── __init__.py
│   ├── core/                      # Core data structures
│   │   ├── __init__.py
│   │   ├── solution.py           # Solution class
│   │   ├── ground_truth.py       # GroundTruth class
│   │   └── result.py             # EvaluationResult class
│   ├── evaluator/                 # Main evaluator
│   │   ├── __init__.py
│   │   └── evaluator.py          # SDKBenchEvaluator class
│   ├── metrics/                   # Metric implementations
│   │   ├── __init__.py
│   │   ├── i_acc.py              # Initialization Correctness
│   │   ├── c_comp.py             # Configuration Completeness
│   │   ├── ipa.py                # Integration Point Accuracy
│   │   ├── f_corr.py             # Functional Correctness
│   │   ├── cq.py                 # Code Quality
│   │   └── sem_sim.py            # Semantic Similarity
│   ├── parsers/                   # Code parsing utilities
│   │   ├── __init__.py
│   │   ├── typescript_parser.py  # Parse TS/TSX files
│   │   ├── env_parser.py         # Parse .env files
│   │   └── config_parser.py      # Parse JS/JSON configs
│   ├── test_harness/              # Test execution
│   │   ├── __init__.py
│   │   ├── runner.py             # Run npm commands, tests
│   │   └── utils.py              # Helper functions
│   └── utils/                     # General utilities
│       ├── __init__.py
│       └── file_utils.py         # File operations
├── scripts/                       # CLI scripts
│   ├── __init__.py
│   ├── search_repos.py           # Week 1 - DONE
│   ├── mine_repos.py             # Week 1 - DONE
│   ├── extract_patterns.py       # Week 1 - DONE
│   ├── build_samples.py          # Week 2 - DONE
│   ├── evaluate_sample.py        # NEW: Evaluate single solution
│   └── evaluate_dataset.py       # NEW: Evaluate all 50 samples
├── validation/                    # NEW: Reference solutions
│   └── reference_solutions/
│       ├── task1_init_001/
│       ├── task2_middleware_016/
│       ├── task3_hooks_031/
│       ├── task4_complete_041/
│       └── task5_migration_048/
├── tests/                         # NEW: Unit tests for evaluator
│   ├── __init__.py
│   ├── test_i_acc.py
│   ├── test_c_comp.py
│   ├── test_ipa.py
│   ├── test_parsers.py
│   └── fixtures/
│       └── sample_solutions/
├── data/                          # Week 1 outputs - EXISTS
│   ├── repositories.json
│   ├── mined-repos.json
│   ├── patterns.json
│   └── patterns.md
├── samples/                       # Week 2 outputs - EXISTS
│   ├── task1_init_001/
│   ├── ...
│   └── dataset_manifest.json
├── results/                       # NEW: Week 4 evaluation results
│   └── (to be created in Week 4)
├── docs/                          # Documentation - EXISTS
│   ├── clerk-poc-plan.md
│   ├── week1-week2-process.md
│   └── week3-infrastructure-plan.md  # This file
├── pyproject.toml                # Project config - EXISTS
├── .env.example                  # Environment variables - EXISTS
└── README.md                     # Project README - EXISTS
```

---

## Phase 1: Core Data Structures

### 1.1 `sdkbench/core/solution.py`

**Purpose:** Represents an LLM-generated solution to a sample

**Key Methods:**
```python
class Solution:
    """Represents a solution (collection of files) to evaluate."""

    def __init__(self, solution_dir: Path):
        """Initialize from a directory containing solution files."""
        self.solution_dir = solution_dir
        self.files: Dict[str, str] = {}  # path -> content
        self._load_files()

    # File operations
    def has_file(self, path: str) -> bool: ...
    def get_file_content(self, path: str) -> Optional[str]: ...
    def get_all_files(self) -> Dict[str, str]: ...

    # Import extraction
    def extract_imports(self, file_path: str = None) -> List[str]: ...
    def has_import(self, import_statement: str) -> bool: ...

    # Pattern detection
    def has_pattern(self, pattern: str, file_path: str = None) -> bool: ...
    def extract_jsx_component(self, component_name: str) -> Optional[Dict]: ...

    # Environment variables
    def extract_env_vars(self) -> List[str]: ...

    # Configuration
    def extract_provider_props(self) -> List[str]: ...
    def extract_middleware_config(self) -> Dict: ...

    # Integration points
    def extract_integration_points(self) -> Set[str]: ...
```

**Design Decisions:**
- Load all files into memory on init (small files, <10MB total)
- Cache expensive operations (AST parsing)
- Use regex for simple patterns, AST for complex ones

---

### 1.2 `sdkbench/core/ground_truth.py`

**Purpose:** Load and represent ground truth from metadata.json

**Key Methods:**
```python
class GroundTruth:
    """Represents ground truth for a sample (from metadata.json)."""

    def __init__(self, metadata_path: Path):
        """Load ground truth from metadata.json."""
        self.metadata = self._load_json(metadata_path)
        self.sample_id = self.metadata["sample_id"]
        self.task_type = self.metadata["task_type"]
        self.ingredients = self.metadata["ground_truth"]["ingredients"]
        self.evaluation_targets = self.metadata["evaluation_targets"]

    # Ingredient access
    def get_initialization(self) -> Dict: ...
    def get_configuration(self) -> Dict: ...
    def get_integration_points(self) -> List[Dict]: ...

    # Evaluation targets
    def get_i_acc_targets(self) -> Dict: ...
    def get_c_comp_targets(self) -> Dict: ...
    def get_ipa_targets(self) -> Dict: ...
    def get_f_corr_targets(self) -> Dict: ...
```

**Design Decisions:**
- Immutable after loading
- Validate schema on load
- Provide convenience methods for common access patterns

---

### 1.3 `sdkbench/core/result.py`

**Purpose:** Store evaluation results for a solution

**Key Structure:**
```python
@dataclass
class MetricResult:
    """Base class for metric results."""
    score: float  # 0-100
    details: Dict[str, Any]

@dataclass
class IAccResult(MetricResult):
    """I-ACC metric result."""
    file_location_correct: bool
    imports_correct: bool
    pattern_correct: bool
    placement_correct: bool

@dataclass
class CCompResult(MetricResult):
    """C-COMP metric result."""
    env_vars_score: float
    provider_props_score: float
    middleware_config_score: float
    missing_env_vars: List[str]

@dataclass
class IPAResult(MetricResult):
    """IPA metric result."""
    precision: float
    recall: float
    f1: float
    true_positives: List[str]
    false_positives: List[str]
    false_negatives: List[str]

@dataclass
class FCorrResult(MetricResult):
    """F-CORR metric result."""
    tests_passed: int
    tests_total: int
    pass_rate: float
    failed_tests: List[str]
    error_messages: List[str]

@dataclass
class CQResult(MetricResult):
    """CQ metric result."""
    type_errors: int
    eslint_errors: int
    security_issues: int
    issues_detail: Dict[str, List[str]]

@dataclass
class SemSimResult(MetricResult):
    """SEM-SIM metric result."""
    similarity_score: float
    pattern_match: bool
    approach_match: bool
    matched_patterns: List[str]

@dataclass
class EvaluationResult:
    """Complete evaluation result for a solution."""
    sample_id: str
    solution_dir: Path
    task_type: int

    # Metric results
    i_acc: IAccResult
    c_comp: CCompResult
    ipa: IPAResult
    f_corr: FCorrResult
    cq: CQResult
    sem_sim: SemSimResult

    # Metadata
    timestamp: str
    duration_seconds: float

    # Overall score (average of all metrics)
    @property
    def overall_score(self) -> float:
        return (
            self.i_acc.score +
            self.c_comp.score +
            self.ipa.score +
            self.f_corr.score +
            self.cq.score +
            self.sem_sim.score
        ) / 6

    def to_dict(self) -> Dict: ...
    def to_json(self, path: Path): ...
```

**Design Decisions:**
- Use dataclasses for type safety
- Include detailed breakdowns for debugging
- Easy serialization to JSON

---

## Phase 2: Parser Infrastructure

### 2.1 `sdkbench/parsers/typescript_parser.py`

**Purpose:** Parse TypeScript/JavaScript files

**Strategy:** Start with regex, upgrade to AST if needed

**Key Functions:**
```python
def extract_imports(content: str) -> List[str]:
    """Extract all import statements."""
    patterns = [
        r"import\s+{([^}]+)}\s+from\s+['\"]([^'\"]+)['\"]",
        r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]",
        r"const\s+\w+\s*=\s*require\(['\"]([^'\"]+)['\"]\)"
    ]
    # Return list of import statements

def extract_jsx_component(content: str, component_name: str) -> Optional[Dict]:
    """Extract JSX component usage."""
    # Find <ClerkProvider ...> ... </ClerkProvider>
    # Return props and children structure

def extract_function_calls(content: str, function_name: str) -> List[Dict]:
    """Extract function calls like auth() or currentUser()."""
    # Find all instances of function_name()
    # Return locations and context

def check_client_directive(content: str) -> bool:
    """Check if file has 'use client' directive."""
    return "'use client'" in content or '"use client"' in content
```

**Fallback to AST if needed:**
```python
# If regex becomes insufficient, use tree-sitter
from tree_sitter import Language, Parser

def parse_with_ast(content: str, language: str = "typescript") -> Dict:
    """Parse using tree-sitter for accurate AST."""
    # More complex but more accurate
```

---

### 2.2 `sdkbench/parsers/env_parser.py`

**Purpose:** Parse .env files

**Key Functions:**
```python
def parse_env_file(file_path: Path) -> Dict[str, str]:
    """Parse .env file into key-value pairs."""
    env_vars = {}
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def extract_clerk_env_vars(env_vars: Dict[str, str]) -> List[str]:
    """Filter Clerk-related environment variables."""
    return [k for k in env_vars.keys() if k.startswith("CLERK_") or k.startswith("NEXT_PUBLIC_CLERK_")]
```

---

### 2.3 `sdkbench/parsers/config_parser.py`

**Purpose:** Parse middleware and config objects

**Key Functions:**
```python
def extract_middleware_config(content: str) -> Dict:
    """Extract authMiddleware configuration."""
    config = {}

    # Extract publicRoutes
    public_match = re.search(r"publicRoutes:\s*\[(.*?)\]", content, re.DOTALL)
    if public_match:
        routes_text = public_match.group(1)
        config["publicRoutes"] = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)

    # Extract ignoredRoutes
    ignored_match = re.search(r"ignoredRoutes:\s*\[(.*?)\]", content, re.DOTALL)
    if ignored_match:
        routes_text = ignored_match.group(1)
        config["ignoredRoutes"] = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)

    return config

def extract_provider_props(content: str) -> List[str]:
    """Extract ClerkProvider props."""
    # Match <ClerkProvider ...>
    match = re.search(r"<ClerkProvider([^>]*)>", content, re.DOTALL)
    if not match:
        return []

    props_text = match.group(1)
    # Extract prop names: publishableKey, appearance, afterSignInUrl, etc.
    props = re.findall(r"(\w+)=", props_text)
    return props
```

---

## Phase 3: Test Harness

### 3.1 `sdkbench/test_harness/runner.py`

**Purpose:** Execute npm commands and tests

**Key Functions:**
```python
import asyncio
from pathlib import Path
from typing import Dict, Optional

class TestRunner:
    """Run tests for a solution."""

    def __init__(self, solution_dir: Path, sample_dir: Path):
        self.solution_dir = solution_dir
        self.sample_dir = sample_dir
        self.test_env = self._create_test_env()

    def _create_test_env(self) -> Path:
        """Create isolated test environment."""
        # Copy sample test files + solution files
        test_env = self.sample_dir / "test_env"
        test_env.mkdir(exist_ok=True)

        # Copy solution files to test env
        self._copy_solution_files()

        # Copy test files from sample
        self._copy_test_files()

        return test_env

    async def install_dependencies(self) -> bool:
        """Run npm install."""
        result = await self._run_command("npm install")
        return result.returncode == 0

    async def run_tests(self) -> Dict:
        """Run Jest tests and parse results."""
        # Run: npm test -- --json
        result = await self._run_command("npm test -- --json")

        # Parse Jest JSON output
        test_results = self._parse_jest_output(result.stdout)

        return {
            "passed": test_results["numPassedTests"],
            "total": test_results["numTotalTests"],
            "failures": test_results["testResults"][0]["assertionResults"]
        }

    async def _run_command(self, cmd: str, timeout: int = 120) -> asyncio.subprocess.Process:
        """Run shell command asynchronously."""
        process = await asyncio.create_subprocess_shell(
            cmd,
            cwd=self.test_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
        except asyncio.TimeoutError:
            process.kill()
            raise TimeoutError(f"Command timed out after {timeout}s: {cmd}")

    def _parse_jest_output(self, stdout: str) -> Dict:
        """Parse Jest JSON output."""
        import json
        return json.loads(stdout)

    def cleanup(self):
        """Remove test environment."""
        shutil.rmtree(self.test_env)
```

---

## Phase 4: Main Evaluator

### 4.1 `sdkbench/evaluator/evaluator.py`

**Purpose:** Orchestrate all metric evaluations

**Key Class:**
```python
class SDKBenchEvaluator:
    """Main evaluator for SDK-Bench."""

    def __init__(self, samples_dir: Path):
        self.samples_dir = samples_dir

    async def evaluate_solution(
        self,
        sample_id: str,
        solution_dir: Path,
        run_tests: bool = True
    ) -> EvaluationResult:
        """Evaluate a solution against a sample."""

        start_time = time.time()

        # 1. Load sample and ground truth
        sample = self._load_sample(sample_id)
        ground_truth = GroundTruth(sample["expected"] / "metadata.json")

        # 2. Load solution
        solution = Solution(solution_dir)

        # 3. Run all metrics
        result = EvaluationResult(
            sample_id=sample_id,
            solution_dir=solution_dir,
            task_type=ground_truth.task_type,
            timestamp=datetime.now().isoformat()
        )

        # Static analysis metrics (fast)
        result.i_acc = evaluate_i_acc(solution, ground_truth)
        result.c_comp = evaluate_c_comp(solution, ground_truth)
        result.ipa = evaluate_ipa(solution, ground_truth)
        result.sem_sim = evaluate_sem_sim(solution, ground_truth)

        # Dynamic metrics (slower)
        if run_tests:
            result.f_corr = await evaluate_f_corr(solution, sample["dir"])
            result.cq = await evaluate_cq(solution)

        result.duration_seconds = time.time() - start_time

        return result

    async def evaluate_dataset(
        self,
        solutions: Dict[str, Path]  # {sample_id: solution_dir}
    ) -> List[EvaluationResult]:
        """Evaluate multiple solutions."""

        results = []
        for sample_id, solution_dir in tqdm(solutions.items()):
            try:
                result = await self.evaluate_solution(sample_id, solution_dir)
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to evaluate {sample_id}: {e}")
                # Continue with other samples

        return results

    def _load_sample(self, sample_id: str) -> Dict:
        """Load sample directories."""
        sample_dir = self.samples_dir / sample_id
        return {
            "dir": sample_dir,
            "input": sample_dir / "input",
            "expected": sample_dir / "expected",
            "tests": sample_dir / "tests"
        }
```

---

## Phase 5: CLI Scripts

### 5.1 `scripts/evaluate_sample.py`

**Purpose:** Evaluate a single solution

**Usage:**
```bash
uv run evaluate-sample \
  --sample-id task1_init_001 \
  --solution-dir /path/to/solution \
  --output results/my_evaluation.json
```

**Implementation:**
```python
import click
import asyncio
from pathlib import Path
from sdkbench.evaluator import SDKBenchEvaluator

@click.command()
@click.option("--sample-id", required=True, help="Sample ID to evaluate against")
@click.option("--solution-dir", required=True, type=click.Path(exists=True), help="Directory containing solution")
@click.option("--output", default=None, help="Output JSON file")
@click.option("--skip-tests", is_flag=True, help="Skip functional tests (faster)")
def main(sample_id: str, solution_dir: str, output: str, skip_tests: bool):
    """Evaluate a solution against a sample."""

    evaluator = SDKBenchEvaluator(samples_dir=Path("samples"))

    result = asyncio.run(evaluator.evaluate_solution(
        sample_id=sample_id,
        solution_dir=Path(solution_dir),
        run_tests=not skip_tests
    ))

    # Print summary
    print(f"\n📊 Evaluation Results: {sample_id}")
    print(f"   I-ACC:    {result.i_acc.score:.1f}%")
    print(f"   C-COMP:   {result.c_comp.score:.1f}%")
    print(f"   IPA:      {result.ipa.score:.1f}% (F1)")
    print(f"   F-CORR:   {result.f_corr.score:.1f}% ({result.f_corr.tests_passed}/{result.f_corr.tests_total} tests)")
    print(f"   CQ:       {result.cq.score:.1f}%")
    print(f"   SEM-SIM:  {result.sem_sim.score:.1f}%")
    print(f"\n   Overall:  {result.overall_score:.1f}%")

    # Save to file
    if output:
        result.to_json(Path(output))
        print(f"\n✅ Saved to {output}")

if __name__ == "__main__":
    main()
```

---

## Implementation Timeline

### Day 1: Core Infrastructure
- [ ] Create `sdkbench/` package structure
- [ ] Implement `core/solution.py`
- [ ] Implement `core/ground_truth.py`
- [ ] Implement `core/result.py`
- [ ] Add unit tests for core classes

### Day 2: Parsers
- [ ] Implement `parsers/typescript_parser.py`
- [ ] Implement `parsers/env_parser.py`
- [ ] Implement `parsers/config_parser.py`
- [ ] Add unit tests for parsers

### Day 3: Metrics 1-3 (Static)
- [ ] Implement `metrics/i_acc.py`
- [ ] Implement `metrics/c_comp.py`
- [ ] Implement `metrics/ipa.py`
- [ ] Add unit tests for metrics

### Day 4: Test Harness
- [ ] Implement `test_harness/runner.py`
- [ ] Test npm install + test execution
- [ ] Add timeout handling
- [ ] Add error handling

### Day 5: Metrics 4-6 (Dynamic)
- [ ] Implement `metrics/f_corr.py`
- [ ] Implement `metrics/cq.py`
- [ ] Implement `metrics/sem_sim.py`
- [ ] Add unit tests

### Day 6: Main Evaluator + CLI
- [ ] Implement `evaluator/evaluator.py`
- [ ] Implement `scripts/evaluate_sample.py`
- [ ] Implement `scripts/evaluate_dataset.py`
- [ ] Update `pyproject.toml` with new scripts

### Day 7: Validation
- [ ] Create 5 reference solutions
- [ ] Run evaluator on reference solutions
- [ ] Validate scores ≥95% on all metrics
- [ ] Debug and fix issues
- [ ] Document evaluation API

---

## Dependencies to Add

Update `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies ...

    # New for Week 3:
    "aiofiles>=23.2.1",      # Async file operations
    "tree-sitter>=0.20.4",   # Already present - AST parsing
]
```

---

## Success Criteria

Before starting Week 4, validate:

1. ✅ All 6 metrics implemented
2. ✅ Reference solutions score ≥95% on all metrics
3. ✅ CLI works for single sample evaluation
4. ✅ Tests pass for all core components
5. ✅ Documentation complete

---

## Next Steps

Ready to start implementation:

1. **Start with Phase 1**: Create core data structures
2. **Then Phase 2**: Build parsers
3. **Then Phase 3-6**: Implement metrics and evaluator

Shall we begin with Phase 1?
