# F-CORR Implementation Plan: Enabling Functional Testing in SDKBench

## Overview

Enable F-CORR (Functional Correctness) metric evaluation locally by creating an extensible test runner framework that supports multiple languages (TypeScript, Python, and future SDKs).

## Current State

### Problems
1. F-CORR is disabled in `evaluate_quick()` - never runs
2. Test harness only supports JavaScript/TypeScript (Jest/Vitest/Mocha)
3. Python samples (LanceDB) have pytest tests but no runner
4. No CLI flag in multi-SDK pipeline to enable F-CORR

### User Requirements
- Run locally on developer machines
- Support all languages (extensible framework)
- Auto-install dependencies
- Strict scoring: any build/test failure = 0 F-CORR score

---

## Implementation Plan

### Phase 1: Create Pydantic Models for Test Results

**File: `sdkbench/test_harness/models.py`** (NEW)

```python
"""Pydantic models for test runner results."""

from pydantic import BaseModel, Field, computed_field
from typing import List, Optional
from enum import Enum


class TestStatus(str, Enum):
    """Status of a test run."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestFailure(BaseModel):
    """Details of a single test failure."""
    test_name: str = Field(..., description="Name of the failed test")
    error_message: str = Field(..., description="Error message from the failure")
    file_path: Optional[str] = Field(None, description="Path to the test file")
    line_number: Optional[int] = Field(None, description="Line number of failure")
    stack_trace: Optional[str] = Field(None, description="Full stack trace")


class TestResult(BaseModel):
    """Result of running tests."""
    success: bool = Field(..., description="Whether all tests passed")
    total: int = Field(0, description="Total number of tests")
    passed: int = Field(0, description="Number of passed tests")
    failed: int = Field(0, description="Number of failed tests")
    skipped: int = Field(0, description="Number of skipped tests")
    duration: float = Field(0.0, description="Total duration in seconds")
    output: str = Field("", description="Raw output from test runner")
    failures: List[TestFailure] = Field(default_factory=list, description="Details of failures")

    @computed_field
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100.0


class DependencyInstallResult(BaseModel):
    """Result of installing dependencies."""
    success: bool = Field(..., description="Whether installation succeeded")
    duration: float = Field(0.0, description="Installation duration in seconds")
    output: str = Field("", description="Installation output")
    error: Optional[str] = Field(None, description="Error message if failed")
    packages_installed: int = Field(0, description="Number of packages installed")


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"


class TestFramework(str, Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    VITEST = "vitest"
    MOCHA = "mocha"
    GO_TEST = "go_test"
    CARGO_TEST = "cargo_test"


class RunnerDetectionResult(BaseModel):
    """Result of detecting which runner to use."""
    detected: bool = Field(..., description="Whether a runner was detected")
    language: Optional[Language] = Field(None, description="Detected language")
    framework: Optional[TestFramework] = Field(None, description="Detected test framework")
    confidence: float = Field(0.0, description="Detection confidence 0-1")
    markers_found: List[str] = Field(default_factory=list, description="Files/patterns that triggered detection")


class FCorrResult(BaseModel):
    """Result of F-CORR evaluation."""
    score: float = Field(..., ge=0.0, le=100.0, description="F-CORR score (0-100)")
    test_results: Optional[TestResult] = Field(None, description="Detailed test results")
    install_results: Optional[DependencyInstallResult] = Field(None, description="Dependency install results")
    language: Optional[Language] = Field(None, description="Detected language")
    framework: Optional[TestFramework] = Field(None, description="Test framework used")
    error: Optional[str] = Field(None, description="Error message if evaluation failed")
    duration: float = Field(0.0, description="Total evaluation duration in seconds")

    @computed_field
    @property
    def passed(self) -> bool:
        """Whether F-CORR evaluation passed (score > 0)."""
        return self.score > 0.0
```

---

### Phase 2: Create Base Test Runner Abstract Class

**File: `sdkbench/test_harness/base_runner.py`** (NEW)

```python
"""Abstract base class for language-specific test runners."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import time

from .models import (
    TestResult,
    DependencyInstallResult,
    RunnerDetectionResult,
    Language,
    TestFramework,
)


class BaseTestRunner(ABC):
    """Abstract base class for language-specific test runners.

    To add support for a new language:
    1. Create a new class inheriting from BaseTestRunner
    2. Implement all abstract methods
    3. Register the runner in TestRunnerRegistry

    Example:
        class GoTestRunner(BaseTestRunner):
            def get_language(self) -> Language:
                return Language.GO
            # ... implement other methods
    """

    def __init__(self, working_dir: Path, timeout: int = 300):
        """Initialize the test runner.

        Args:
            working_dir: Directory containing the project to test
            timeout: Default timeout for commands in seconds
        """
        self.working_dir = Path(working_dir)
        self.timeout = timeout

    @abstractmethod
    def get_language(self) -> Language:
        """Return the language this runner handles."""
        pass

    @abstractmethod
    def get_framework(self) -> TestFramework:
        """Return the test framework this runner uses."""
        pass

    @abstractmethod
    def detect(self) -> RunnerDetectionResult:
        """Detect if this runner can handle the project.

        Returns:
            RunnerDetectionResult with detection details
        """
        pass

    @abstractmethod
    def install_dependencies(self) -> DependencyInstallResult:
        """Install project dependencies.

        Returns:
            DependencyInstallResult with installation details
        """
        pass

    @abstractmethod
    def run_tests(self, test_dir: Optional[Path] = None) -> TestResult:
        """Run tests and return results.

        Args:
            test_dir: Optional specific directory containing tests

        Returns:
            TestResult with test execution details
        """
        pass

    def can_handle(self) -> bool:
        """Quick check if this runner can handle the project."""
        return self.detect().detected
```

---

### Phase 3: Implement Python Test Runner

**File: `sdkbench/test_harness/python_runner.py`** (NEW)

```python
"""Python test runner using pytest."""

import subprocess
import re
import time
from pathlib import Path
from typing import Optional, List

from .base_runner import BaseTestRunner
from .models import (
    TestResult,
    TestFailure,
    DependencyInstallResult,
    RunnerDetectionResult,
    Language,
    TestFramework,
)


class PythonTestRunner(BaseTestRunner):
    """Test runner for Python projects using pytest."""

    def get_language(self) -> Language:
        return Language.PYTHON

    def get_framework(self) -> TestFramework:
        return TestFramework.PYTEST

    def detect(self) -> RunnerDetectionResult:
        """Detect Python project by manifest files or test files."""
        markers_found = []

        # Check for Python project markers
        manifest_markers = [
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "Pipfile",
        ]

        for marker in manifest_markers:
            if (self.working_dir / marker).exists():
                markers_found.append(marker)

        # Check for pytest files
        test_patterns = ["test_*.py", "*_test.py"]
        for pattern in test_patterns:
            test_files = list(self.working_dir.rglob(pattern))
            if test_files:
                markers_found.append(f"{pattern} ({len(test_files)} files)")

        # Check for conftest.py (pytest marker)
        if list(self.working_dir.rglob("conftest.py")):
            markers_found.append("conftest.py")

        detected = len(markers_found) > 0
        confidence = min(1.0, len(markers_found) * 0.25)

        return RunnerDetectionResult(
            detected=detected,
            language=Language.PYTHON if detected else None,
            framework=TestFramework.PYTEST if detected else None,
            confidence=confidence,
            markers_found=markers_found,
        )

    def install_dependencies(self) -> DependencyInstallResult:
        """Install dependencies using pip."""
        start_time = time.time()

        # Try requirements.txt first
        req_file = self.working_dir / "requirements.txt"
        if req_file.exists():
            try:
                result = subprocess.run(
                    ["pip", "install", "-r", str(req_file), "-q"],
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                duration = time.time() - start_time

                if result.returncode == 0:
                    # Count packages from requirements.txt
                    packages = len([l for l in req_file.read_text().splitlines()
                                   if l.strip() and not l.startswith('#')])
                    return DependencyInstallResult(
                        success=True,
                        duration=duration,
                        output=result.stdout + result.stderr,
                        packages_installed=packages,
                    )
                else:
                    return DependencyInstallResult(
                        success=False,
                        duration=duration,
                        output=result.stdout + result.stderr,
                        error=f"pip install failed: {result.stderr}",
                    )
            except subprocess.TimeoutExpired:
                return DependencyInstallResult(
                    success=False,
                    duration=self.timeout,
                    error="Dependency installation timed out",
                )
            except Exception as e:
                return DependencyInstallResult(
                    success=False,
                    duration=time.time() - start_time,
                    error=str(e),
                )

        # Try pyproject.toml
        pyproject = self.working_dir / "pyproject.toml"
        if pyproject.exists():
            try:
                result = subprocess.run(
                    ["pip", "install", "-e", ".", "-q"],
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                duration = time.time() - start_time

                return DependencyInstallResult(
                    success=result.returncode == 0,
                    duration=duration,
                    output=result.stdout + result.stderr,
                    error=result.stderr if result.returncode != 0 else None,
                )
            except Exception as e:
                return DependencyInstallResult(
                    success=False,
                    duration=time.time() - start_time,
                    error=str(e),
                )

        # No dependency file found - assume success
        return DependencyInstallResult(
            success=True,
            duration=0.0,
            output="No dependency file found",
        )

    def run_tests(self, test_dir: Optional[Path] = None) -> TestResult:
        """Run pytest and parse output."""
        start_time = time.time()

        # Build pytest command
        cmd = ["python", "-m", "pytest", "-v", "--tb=short", "-q"]

        if test_dir:
            cmd.append(str(test_dir))

        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            duration = time.time() - start_time
            output = result.stdout + result.stderr

            return self._parse_pytest_output(output, duration, result.returncode == 0)

        except subprocess.TimeoutExpired:
            return TestResult(
                success=False,
                duration=self.timeout,
                output="Test execution timed out",
                failures=[TestFailure(
                    test_name="timeout",
                    error_message=f"Tests did not complete within {self.timeout} seconds"
                )],
            )
        except Exception as e:
            return TestResult(
                success=False,
                duration=time.time() - start_time,
                output=str(e),
                failures=[TestFailure(
                    test_name="error",
                    error_message=str(e)
                )],
            )

    def _parse_pytest_output(self, output: str, duration: float, success: bool) -> TestResult:
        """Parse pytest output for test counts and failures."""
        total = 0
        passed = 0
        failed = 0
        skipped = 0
        failures: List[TestFailure] = []

        # Pattern: "5 passed, 2 failed, 1 skipped" or "5 passed"
        summary_pattern = r"(\d+)\s+(passed|failed|skipped|error|warnings?)"
        matches = re.findall(summary_pattern, output, re.IGNORECASE)

        for count, status in matches:
            count = int(count)
            status = status.lower()
            if status == "passed":
                passed = count
            elif status == "failed":
                failed = count
            elif status == "skipped":
                skipped = count

        total = passed + failed + skipped

        # Extract failure details
        # Pattern: "FAILED test_file.py::test_name - AssertionError"
        failure_pattern = r"FAILED\s+([^\s]+)::([^\s]+)\s*-?\s*(.*)"
        failure_matches = re.findall(failure_pattern, output)

        for file_path, test_name, error in failure_matches:
            failures.append(TestFailure(
                test_name=test_name,
                error_message=error.strip() if error else "Test failed",
                file_path=file_path,
            ))

        # If we couldn't parse counts but have failures, estimate
        if total == 0 and failures:
            failed = len(failures)
            total = failed

        return TestResult(
            success=success and failed == 0,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            output=output,
            failures=failures,
        )
```

---

### Phase 4: Implement TypeScript Test Runner

**File: `sdkbench/test_harness/typescript_runner.py`** (NEW)

```python
"""TypeScript/JavaScript test runner supporting Jest, Vitest, and Mocha."""

import subprocess
import re
import json
import time
from pathlib import Path
from typing import Optional, List

from .base_runner import BaseTestRunner
from .models import (
    TestResult,
    TestFailure,
    DependencyInstallResult,
    RunnerDetectionResult,
    Language,
    TestFramework,
)


class TypeScriptTestRunner(BaseTestRunner):
    """Test runner for TypeScript/JavaScript projects."""

    def __init__(self, working_dir: Path, timeout: int = 300):
        super().__init__(working_dir, timeout)
        self._detected_framework: Optional[TestFramework] = None

    def get_language(self) -> Language:
        return Language.TYPESCRIPT

    def get_framework(self) -> TestFramework:
        if self._detected_framework:
            return self._detected_framework
        # Default to Jest, will be updated during detection
        return TestFramework.JEST

    def detect(self) -> RunnerDetectionResult:
        """Detect TypeScript/JS project and test framework."""
        markers_found = []

        # Check for package.json
        package_json = self.working_dir / "package.json"
        if not package_json.exists():
            return RunnerDetectionResult(
                detected=False,
                confidence=0.0,
                markers_found=[],
            )

        markers_found.append("package.json")

        # Parse package.json to detect test framework
        try:
            pkg = json.loads(package_json.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            scripts = pkg.get("scripts", {})

            # Detect framework from dependencies
            if "jest" in deps or "@jest/core" in deps:
                self._detected_framework = TestFramework.JEST
                markers_found.append("jest in dependencies")
            elif "vitest" in deps:
                self._detected_framework = TestFramework.VITEST
                markers_found.append("vitest in dependencies")
            elif "mocha" in deps:
                self._detected_framework = TestFramework.MOCHA
                markers_found.append("mocha in dependencies")

            # Check for test script
            if "test" in scripts:
                markers_found.append(f"test script: {scripts['test']}")
                # Infer framework from test script if not detected
                if not self._detected_framework:
                    test_cmd = scripts["test"].lower()
                    if "jest" in test_cmd:
                        self._detected_framework = TestFramework.JEST
                    elif "vitest" in test_cmd:
                        self._detected_framework = TestFramework.VITEST
                    elif "mocha" in test_cmd:
                        self._detected_framework = TestFramework.MOCHA

        except json.JSONDecodeError:
            pass

        # Check for test files
        test_patterns = ["*.test.ts", "*.test.tsx", "*.test.js", "*.spec.ts", "*.spec.tsx"]
        for pattern in test_patterns:
            test_files = list(self.working_dir.rglob(pattern))
            if test_files:
                markers_found.append(f"{pattern} ({len(test_files)} files)")

        # Check for tsconfig.json
        if (self.working_dir / "tsconfig.json").exists():
            markers_found.append("tsconfig.json")

        detected = len(markers_found) > 1  # Need package.json + something else
        confidence = min(1.0, len(markers_found) * 0.2)

        return RunnerDetectionResult(
            detected=detected,
            language=Language.TYPESCRIPT if detected else None,
            framework=self._detected_framework,
            confidence=confidence,
            markers_found=markers_found,
        )

    def install_dependencies(self) -> DependencyInstallResult:
        """Install dependencies using npm."""
        start_time = time.time()

        # Check if node_modules already exists
        if (self.working_dir / "node_modules").exists():
            return DependencyInstallResult(
                success=True,
                duration=0.0,
                output="node_modules already exists",
            )

        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=600,  # npm can be slow
            )
            duration = time.time() - start_time

            return DependencyInstallResult(
                success=result.returncode == 0,
                duration=duration,
                output=result.stdout + result.stderr,
                error=result.stderr if result.returncode != 0 else None,
            )
        except subprocess.TimeoutExpired:
            return DependencyInstallResult(
                success=False,
                duration=600,
                error="npm install timed out",
            )
        except Exception as e:
            return DependencyInstallResult(
                success=False,
                duration=time.time() - start_time,
                error=str(e),
            )

    def run_tests(self, test_dir: Optional[Path] = None) -> TestResult:
        """Run tests using detected framework."""
        start_time = time.time()

        # Determine test command
        package_json = self.working_dir / "package.json"
        cmd = ["npm", "test"]

        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text())
                scripts = pkg.get("scripts", {})
                if "test" not in scripts:
                    # Fallback to npx jest
                    cmd = ["npx", "jest", "--no-coverage"]
            except json.JSONDecodeError:
                pass

        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**subprocess.os.environ, "CI": "true"},  # Prevent interactive mode
            )
            duration = time.time() - start_time
            output = result.stdout + result.stderr

            # Parse based on detected framework
            if self._detected_framework == TestFramework.VITEST:
                return self._parse_vitest_output(output, duration, result.returncode == 0)
            elif self._detected_framework == TestFramework.MOCHA:
                return self._parse_mocha_output(output, duration, result.returncode == 0)
            else:
                return self._parse_jest_output(output, duration, result.returncode == 0)

        except subprocess.TimeoutExpired:
            return TestResult(
                success=False,
                duration=self.timeout,
                output="Test execution timed out",
            )
        except Exception as e:
            return TestResult(
                success=False,
                duration=time.time() - start_time,
                output=str(e),
            )

    def _parse_jest_output(self, output: str, duration: float, success: bool) -> TestResult:
        """Parse Jest output."""
        # Pattern: "Tests: 2 failed, 5 passed, 7 total"
        pattern = r"Tests:\s+(?:(\d+)\s+failed,\s+)?(?:(\d+)\s+skipped,\s+)?(?:(\d+)\s+passed,\s+)?(\d+)\s+total"
        match = re.search(pattern, output)

        if match:
            failed = int(match.group(1) or 0)
            skipped = int(match.group(2) or 0)
            passed = int(match.group(3) or 0)
            total = int(match.group(4) or 0)
        else:
            # Try alternative patterns
            passed = len(re.findall(r"✓|PASS", output))
            failed = len(re.findall(r"✕|FAIL", output))
            total = passed + failed
            skipped = 0

        # Extract failures
        failures = self._extract_jest_failures(output)

        return TestResult(
            success=success and failed == 0,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            output=output,
            failures=failures,
        )

    def _parse_vitest_output(self, output: str, duration: float, success: bool) -> TestResult:
        """Parse Vitest output."""
        # Pattern: "Tests 2 failed | 1 skipped | 5 passed (8)"
        pattern = r"Tests\s+(?:(\d+)\s+failed\s+\|\s+)?(?:(\d+)\s+skipped\s+\|\s+)?(\d+)\s+passed\s+\((\d+)\)"
        match = re.search(pattern, output)

        if match:
            failed = int(match.group(1) or 0)
            skipped = int(match.group(2) or 0)
            passed = int(match.group(3) or 0)
            total = int(match.group(4) or 0)
        else:
            total = passed = failed = skipped = 0

        return TestResult(
            success=success and failed == 0,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            output=output,
            failures=[],
        )

    def _parse_mocha_output(self, output: str, duration: float, success: bool) -> TestResult:
        """Parse Mocha output."""
        passed = 0
        failed = 0
        skipped = 0

        # Patterns: "5 passing", "2 failing", "1 pending"
        passing_match = re.search(r"(\d+)\s+passing", output)
        failing_match = re.search(r"(\d+)\s+failing", output)
        pending_match = re.search(r"(\d+)\s+pending", output)

        if passing_match:
            passed = int(passing_match.group(1))
        if failing_match:
            failed = int(failing_match.group(1))
        if pending_match:
            skipped = int(pending_match.group(1))

        total = passed + failed + skipped

        return TestResult(
            success=success and failed == 0,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            output=output,
            failures=[],
        )

    def _extract_jest_failures(self, output: str) -> List[TestFailure]:
        """Extract failure details from Jest output."""
        failures = []

        # Pattern: "● Test Suite › test name"
        pattern = r"●\s+(.+?)(?:\n\n|\n\s+expect)"
        matches = re.findall(pattern, output)

        for match in matches:
            failures.append(TestFailure(
                test_name=match.strip(),
                error_message="Test failed",
            ))

        return failures
```

---

### Phase 5: Create Test Runner Registry

**File: `sdkbench/test_harness/registry.py`** (NEW)

```python
"""Registry for test runners with auto-detection."""

from typing import List, Type, Optional
from pathlib import Path

from .base_runner import BaseTestRunner
from .models import RunnerDetectionResult, Language


class TestRunnerRegistry:
    """Registry of available test runners with auto-detection.

    Usage:
        # Get appropriate runner for a project
        runner = TestRunnerRegistry.get_runner(Path("/path/to/project"))
        if runner:
            result = runner.run_tests()

        # Register a custom runner
        TestRunnerRegistry.register(MyCustomRunner)
    """

    _runners: List[Type[BaseTestRunner]] = []

    @classmethod
    def register(cls, runner_class: Type[BaseTestRunner]) -> None:
        """Register a new test runner.

        Args:
            runner_class: A class inheriting from BaseTestRunner
        """
        if runner_class not in cls._runners:
            cls._runners.append(runner_class)

    @classmethod
    def get_runner(cls, working_dir: Path) -> Optional[BaseTestRunner]:
        """Get appropriate runner for the project.

        Tries each registered runner and returns the one with highest confidence.

        Args:
            working_dir: Directory containing the project

        Returns:
            Best matching runner or None if no runner can handle the project
        """
        best_runner: Optional[BaseTestRunner] = None
        best_confidence = 0.0

        for runner_class in cls._runners:
            runner = runner_class(working_dir)
            detection = runner.detect()

            if detection.detected and detection.confidence > best_confidence:
                best_runner = runner
                best_confidence = detection.confidence

        return best_runner

    @classmethod
    def get_all_runners(cls) -> List[Type[BaseTestRunner]]:
        """Get all registered runner classes."""
        return cls._runners.copy()

    @classmethod
    def detect_all(cls, working_dir: Path) -> List[RunnerDetectionResult]:
        """Run detection for all runners.

        Useful for debugging or showing what was detected.

        Args:
            working_dir: Directory to check

        Returns:
            List of detection results from all runners
        """
        results = []
        for runner_class in cls._runners:
            runner = runner_class(working_dir)
            results.append(runner.detect())
        return results


# Import and register default runners
def _register_default_runners():
    """Register the built-in runners."""
    from .typescript_runner import TypeScriptTestRunner
    from .python_runner import PythonTestRunner

    # Register TypeScript first (more specific detection)
    TestRunnerRegistry.register(TypeScriptTestRunner)
    TestRunnerRegistry.register(PythonTestRunner)


# Auto-register on import
_register_default_runners()
```

---

### Phase 6: Update F-CORR Evaluator

**File: `sdkbench/metrics/f_corr.py`** (MODIFY)

```python
"""F-CORR (Functional Correctness) metric evaluator.

Measures if the implementation actually works by running builds and tests.
"""

import time
from pathlib import Path
from typing import Optional

from sdkbench.core import Solution, GroundTruth
from sdkbench.test_harness.registry import TestRunnerRegistry
from sdkbench.test_harness.models import FCorrResult, TestResult, DependencyInstallResult


class FCorrEvaluator:
    """Evaluates functional correctness (F-CORR metric).

    F-CORR Score with STRICT mode (default):
    - 100% if all tests pass
    - 0% if any test fails, build fails, or dependencies fail to install

    This strict scoring ensures LLM-generated code must be fully functional.
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth
        self.runner = TestRunnerRegistry.get_runner(solution.solution_dir)

    def evaluate(
        self,
        auto_install: bool = True,
        test_dir: Optional[Path] = None,
        strict: bool = True,
    ) -> FCorrResult:
        """Evaluate functional correctness.

        Args:
            auto_install: Whether to auto-install dependencies
            test_dir: Optional specific test directory
            strict: If True, any failure = 0 score. If False, use pass rate.

        Returns:
            FCorrResult with score and details
        """
        start_time = time.time()

        # Check if we have a compatible runner
        if self.runner is None:
            return FCorrResult(
                score=0.0,
                error="No compatible test runner found for this project",
                duration=time.time() - start_time,
            )

        detection = self.runner.detect()
        install_result: Optional[DependencyInstallResult] = None

        # Install dependencies if requested
        if auto_install:
            install_result = self.runner.install_dependencies()
            if not install_result.success:
                return FCorrResult(
                    score=0.0,
                    install_results=install_result,
                    language=detection.language,
                    framework=detection.framework,
                    error=f"Dependency installation failed: {install_result.error}",
                    duration=time.time() - start_time,
                )

        # Run tests
        try:
            test_result = self.runner.run_tests(test_dir)
        except Exception as e:
            return FCorrResult(
                score=0.0,
                install_results=install_result,
                language=detection.language,
                framework=detection.framework,
                error=f"Test execution error: {str(e)}",
                duration=time.time() - start_time,
            )

        # Calculate score
        if strict:
            # STRICT: Any failure = 0 score
            if not test_result.success or test_result.failed > 0:
                score = 0.0
            else:
                score = 100.0
        else:
            # Non-strict: Use pass rate
            score = test_result.pass_rate

        return FCorrResult(
            score=score,
            test_results=test_result,
            install_results=install_result,
            language=detection.language,
            framework=detection.framework,
            error=None if test_result.success else f"{test_result.failed} tests failed",
            duration=time.time() - start_time,
        )

    def quick_check(self) -> dict:
        """Quick check without full execution.

        Returns:
            Dict with quick check results
        """
        if self.runner is None:
            return {
                "ready": False,
                "error": "No compatible test runner found",
            }

        detection = self.runner.detect()

        return {
            "ready": detection.detected,
            "language": detection.language.value if detection.language else None,
            "framework": detection.framework.value if detection.framework else None,
            "confidence": detection.confidence,
            "markers_found": detection.markers_found,
        }
```

---

### Phase 7: Update Test Harness __init__.py

**File: `sdkbench/test_harness/__init__.py`** (MODIFY)

```python
"""Test harness for F-CORR evaluation.

Provides language-agnostic test running capabilities with
auto-detection of project type and test framework.
"""

from .models import (
    TestStatus,
    TestFailure,
    TestResult,
    DependencyInstallResult,
    Language,
    TestFramework,
    RunnerDetectionResult,
    FCorrResult,
)
from .base_runner import BaseTestRunner
from .registry import TestRunnerRegistry
from .python_runner import PythonTestRunner
from .typescript_runner import TypeScriptTestRunner

# Re-export existing classes for backwards compatibility
from .build_runner import BuildRunner
from .test_runner import TestRunner
from .executor import Executor, ExecutionResult

__all__ = [
    # New Pydantic models
    "TestStatus",
    "TestFailure",
    "TestResult",
    "DependencyInstallResult",
    "Language",
    "TestFramework",
    "RunnerDetectionResult",
    "FCorrResult",
    # New runners
    "BaseTestRunner",
    "TestRunnerRegistry",
    "PythonTestRunner",
    "TypeScriptTestRunner",
    # Legacy (backwards compatibility)
    "BuildRunner",
    "TestRunner",
    "Executor",
    "ExecutionResult",
]
```

---

### Phase 8: Create Standalone F-CORR Runner Script

**File: `scripts/run_fcorr.py`** (NEW)

```python
#!/usr/bin/env python
"""Standalone F-CORR evaluation runner.

Run functional correctness tests on samples or solutions.

Usage:
    # Run on a single sample's expected/ directory
    python scripts/run_fcorr.py --sample samples/lancedb/lancedb_task1_init_001

    # Run on all samples for an SDK
    python scripts/run_fcorr.py --sdk lancedb

    # Run on a generated solution
    python scripts/run_fcorr.py --solution solutions/clerk/claude-sonnet-4-5/task1_init_001

    # Verbose output
    python scripts/run_fcorr.py --sample samples/clerk/task1_init_001 --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sdkbench.test_harness import TestRunnerRegistry, FCorrResult


def run_fcorr_on_directory(
    project_dir: Path,
    test_dir: Optional[Path] = None,
    auto_install: bool = True,
    verbose: bool = False,
) -> FCorrResult:
    """Run F-CORR evaluation on a directory.

    Args:
        project_dir: Directory containing the project
        test_dir: Optional specific test directory
        auto_install: Whether to install dependencies
        verbose: Print detailed output

    Returns:
        FCorrResult with evaluation results
    """
    if verbose:
        print(f"Evaluating: {project_dir}")

    runner = TestRunnerRegistry.get_runner(project_dir)

    if runner is None:
        return FCorrResult(
            score=0.0,
            error="No compatible test runner found",
        )

    detection = runner.detect()
    if verbose:
        print(f"  Language: {detection.language}")
        print(f"  Framework: {detection.framework}")
        print(f"  Markers: {detection.markers_found}")

    # Install dependencies
    if auto_install:
        if verbose:
            print("  Installing dependencies...")
        install_result = runner.install_dependencies()
        if not install_result.success:
            return FCorrResult(
                score=0.0,
                install_results=install_result,
                language=detection.language,
                framework=detection.framework,
                error=f"Install failed: {install_result.error}",
            )
        if verbose:
            print(f"  Install completed in {install_result.duration:.1f}s")

    # Run tests
    if verbose:
        print("  Running tests...")
    test_result = runner.run_tests(test_dir)

    # Calculate strict score
    if test_result.success and test_result.failed == 0:
        score = 100.0
    else:
        score = 0.0

    if verbose:
        print(f"  Results: {test_result.passed} passed, {test_result.failed} failed")
        print(f"  Duration: {test_result.duration:.1f}s")
        print(f"  F-CORR Score: {score}%")

    return FCorrResult(
        score=score,
        test_results=test_result,
        language=detection.language,
        framework=detection.framework,
        error=None if score == 100.0 else f"{test_result.failed} tests failed",
    )


def run_on_sample(sample_path: Path, verbose: bool = False) -> FCorrResult:
    """Run F-CORR on a sample's expected/ directory."""
    expected_dir = sample_path / "expected"
    tests_dir = sample_path / "tests"

    if not expected_dir.exists():
        return FCorrResult(score=0.0, error=f"No expected/ directory in {sample_path}")

    # For samples, we need to run tests from tests/ against expected/
    # This requires copying tests into expected/ or adjusting paths
    return run_fcorr_on_directory(expected_dir, tests_dir, verbose=verbose)


def run_on_sdk(sdk_name: str, samples_dir: Path, verbose: bool = False) -> List[dict]:
    """Run F-CORR on all samples for an SDK."""
    sdk_dir = samples_dir / sdk_name
    if not sdk_dir.exists():
        print(f"SDK directory not found: {sdk_dir}")
        return []

    results = []
    for sample_dir in sorted(sdk_dir.iterdir()):
        if sample_dir.is_dir() and not sample_dir.name.startswith("."):
            print(f"\n{'='*60}")
            print(f"Sample: {sample_dir.name}")
            print(f"{'='*60}")

            result = run_on_sample(sample_dir, verbose=verbose)
            results.append({
                "sample_id": sample_dir.name,
                "score": result.score,
                "passed": result.passed,
                "error": result.error,
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run F-CORR (Functional Correctness) evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sample",
        type=Path,
        help="Path to a single sample directory",
    )
    group.add_argument(
        "--sdk",
        type=str,
        help="SDK name to evaluate all samples",
    )
    group.add_argument(
        "--solution",
        type=Path,
        help="Path to a generated solution directory",
    )
    group.add_argument(
        "--directory",
        type=Path,
        help="Path to any project directory",
    )

    parser.add_argument(
        "--samples-dir",
        type=Path,
        default=Path(__file__).parent.parent / "samples",
        help="Base samples directory (default: ./samples)",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Skip dependency installation",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    if args.sample:
        result = run_on_sample(args.sample, verbose=args.verbose)
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(f"\nF-CORR Score: {result.score}%")
            if result.error:
                print(f"Error: {result.error}")

    elif args.sdk:
        results = run_on_sdk(args.sdk, args.samples_dir, verbose=args.verbose)

        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")

        passed = sum(1 for r in results if r["score"] == 100.0)
        total = len(results)

        print(f"Passed: {passed}/{total}")
        print(f"Pass Rate: {passed/total*100:.1f}%" if total > 0 else "N/A")

        if args.json:
            print(json.dumps(results, indent=2))

    elif args.solution:
        result = run_fcorr_on_directory(
            args.solution,
            auto_install=not args.no_install,
            verbose=args.verbose,
        )
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(f"\nF-CORR Score: {result.score}%")

    elif args.directory:
        result = run_fcorr_on_directory(
            args.directory,
            auto_install=not args.no_install,
            verbose=args.verbose,
        )
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(f"\nF-CORR Score: {result.score}%")


if __name__ == "__main__":
    main()
```

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `sdkbench/test_harness/models.py` | NEW | Pydantic models for all test results |
| `sdkbench/test_harness/base_runner.py` | NEW | Abstract base class for test runners |
| `sdkbench/test_harness/python_runner.py` | NEW | Pytest runner implementation |
| `sdkbench/test_harness/typescript_runner.py` | NEW | Jest/Vitest/Mocha runner implementation |
| `sdkbench/test_harness/registry.py` | NEW | Runner registry for auto-detection |
| `sdkbench/test_harness/__init__.py` | MODIFY | Export new classes |
| `sdkbench/metrics/f_corr.py` | MODIFY | Use new registry and models |
| `scripts/run_fcorr.py` | NEW | Standalone F-CORR runner script |

---

## Usage Examples

### Run F-CORR on a Single Sample

```bash
# Python sample (LanceDB)
python scripts/run_fcorr.py --sample samples/lancedb/lancedb_task1_init_001 -v

# Output:
# Evaluating: samples/lancedb/lancedb_task1_init_001/expected
#   Language: python
#   Framework: pytest
#   Markers: ['requirements.txt', 'test_*.py (3 files)']
#   Installing dependencies...
#   Install completed in 2.3s
#   Running tests...
#   Results: 3 passed, 0 failed
#   Duration: 1.2s
#   F-CORR Score: 100%
```

### Run F-CORR on All SDK Samples

```bash
python scripts/run_fcorr.py --sdk lancedb -v

# Runs all 50 samples, shows summary at end
```

### Run F-CORR on Generated Solution

```bash
python scripts/run_fcorr.py --solution solutions/clerk/claude-sonnet-4-5/task1_init_001 -v
```

### JSON Output

```bash
python scripts/run_fcorr.py --sample samples/clerk/task1_init_001 --json
```

---

## Future Language Support

To add a new language (e.g., Go):

1. Create `sdkbench/test_harness/go_runner.py`:

```python
class GoTestRunner(BaseTestRunner):
    def get_language(self) -> Language:
        return Language.GO

    def get_framework(self) -> TestFramework:
        return TestFramework.GO_TEST

    def detect(self) -> RunnerDetectionResult:
        go_mod = self.working_dir / "go.mod"
        return RunnerDetectionResult(
            detected=go_mod.exists(),
            language=Language.GO if go_mod.exists() else None,
            framework=TestFramework.GO_TEST if go_mod.exists() else None,
            confidence=1.0 if go_mod.exists() else 0.0,
            markers_found=["go.mod"] if go_mod.exists() else [],
        )

    def install_dependencies(self) -> DependencyInstallResult:
        result = subprocess.run(["go", "mod", "download"], ...)
        return DependencyInstallResult(success=result.returncode == 0, ...)

    def run_tests(self, test_dir=None) -> TestResult:
        result = subprocess.run(["go", "test", "-v", "./..."], ...)
        return self._parse_go_output(result)
```

2. Register in `registry.py`:

```python
from .go_runner import GoTestRunner
TestRunnerRegistry.register(GoTestRunner)
```

---

## Prerequisites

**For TypeScript/JavaScript:**
- Node.js 18+
- npm

**For Python:**
- Python 3.10+
- pip
- pytest (`pip install pytest`)

**General:**
- 2GB disk space for dependencies
- Internet connection for package installation
