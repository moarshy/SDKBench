"""Python test runner using pytest."""

import subprocess
import re
import time
import os
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

    # Directories to exclude from test file detection
    EXCLUDED_DIRS = {"venv", ".venv", "env", ".env", "virtualenv", "__pycache__",
                     ".git", ".tox", ".nox", "build", "dist", "eggs", ".eggs",
                     "node_modules", ".mypy_cache", ".pytest_cache"}

    def _filter_excluded_dirs(self, files: List[Path]) -> List[Path]:
        """Filter out files in excluded directories like venv, node_modules."""
        return [f for f in files if not any(
            excluded in f.parts for excluded in self.EXCLUDED_DIRS
        )]

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

        # Check for pytest files (excluding venv, node_modules, etc.)
        test_patterns = ["test_*.py", "*_test.py"]
        for pattern in test_patterns:
            test_files = self._filter_excluded_dirs(list(self.working_dir.rglob(pattern)))
            if test_files:
                markers_found.append(f"{pattern} ({len(test_files)} files)")

        # Check for conftest.py (pytest marker)
        conftest_files = self._filter_excluded_dirs(list(self.working_dir.rglob("conftest.py")))
        if conftest_files:
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
        # Note: -v (verbose) and -q (quiet) conflict - use -v for detailed output
        cmd = ["python", "-m", "pytest", "-v", "--tb=short"]

        if test_dir:
            cmd.append(str(test_dir))

        try:
            # Set up environment - ensure we can find modules
            env = os.environ.copy()
            python_path = str(self.working_dir)
            # Use os.pathsep for cross-platform compatibility (: on Unix, ; on Windows)
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{python_path}{os.pathsep}{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = python_path

            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
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

        # Extract failure details with stack traces
        # Pattern: "FAILED test_file.py::test_name - AssertionError"
        failure_pattern = r"FAILED\s+([^\s]+)::([^\s]+)\s*-?\s*(.*)"
        failure_matches = re.findall(failure_pattern, output)

        # Extract stack traces from pytest output (between FAILURES and short test summary)
        stack_traces = self._extract_pytest_stack_traces(output)

        for file_path, test_name, error in failure_matches:
            # Try to find the full stack trace for this test
            full_test_id = f"{file_path}::{test_name}"
            stack_trace = stack_traces.get(full_test_id) or stack_traces.get(test_name)

            # Extract line number from stack trace if available
            line_number = None
            if stack_trace:
                line_match = re.search(rf'{re.escape(file_path)}:(\d+)', stack_trace)
                if line_match:
                    line_number = int(line_match.group(1))

            failures.append(TestFailure(
                test_name=test_name,
                error_message=error.strip() if error else "Test failed",
                file_path=file_path,
                line_number=line_number,
                stack_trace=stack_trace,
            ))

        # If we couldn't parse counts but have failures, estimate
        if total == 0 and failures:
            failed = len(failures)
            total = failed

        # If still no counts, try to find "X passed" type patterns
        if total == 0:
            # Try alternate pattern: "1 passed in 0.05s"
            alt_pattern = r"(\d+)\s+passed"
            alt_match = re.search(alt_pattern, output)
            if alt_match:
                passed = int(alt_match.group(1))
                total = passed + failed + skipped

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

    def _extract_pytest_stack_traces(self, output: str) -> dict:
        """Extract stack traces from pytest output.

        Args:
            output: Raw pytest output

        Returns:
            Dict mapping test names to their stack traces
        """
        stack_traces = {}

        # pytest formats failures between "= FAILURES =" and "= short test summary info ="
        failures_section_pattern = r'={3,}\s*FAILURES\s*={3,}(.*?)(?:={3,}\s*(?:short test summary|ERRORS|warnings summary)|\Z)'
        failures_match = re.search(failures_section_pattern, output, re.DOTALL | re.IGNORECASE)

        if not failures_match:
            return stack_traces

        failures_section = failures_match.group(1)

        # Split by test headers: "_ test_name _" or "_____ test_file.py::test_name _____"
        # Pattern matches word characters or :: in the test name
        test_pattern = r'_{3,}\s*([\w:]+(?:::[\w:]+)*)\s*_{3,}'
        parts = re.split(test_pattern, failures_section)

        # parts[0] is before first test, then alternating: test_name, traceback, test_name, traceback...
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                test_name = parts[i].strip()
                traceback = parts[i + 1].strip()
                stack_traces[test_name] = traceback

                # Also store by short name (without file path)
                if '::' in test_name:
                    short_name = test_name.split('::')[-1]
                    stack_traces[short_name] = traceback

        return stack_traces
