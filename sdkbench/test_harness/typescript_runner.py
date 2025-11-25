"""TypeScript/JavaScript test runner supporting Jest, Vitest, and Mocha."""

import subprocess
import re
import json
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

        # Check for test files and infer framework from imports
        test_patterns = ["*.test.ts", "*.test.tsx", "*.test.js", "*.spec.ts", "*.spec.tsx"]
        for pattern in test_patterns:
            test_files = list(self.working_dir.rglob(pattern))
            if test_files:
                markers_found.append(f"{pattern} ({len(test_files)} files)")
                # If framework not detected yet, check test file imports
                if not self._detected_framework:
                    for test_file in test_files[:3]:  # Check first few files
                        try:
                            content = test_file.read_text()
                            if "@jest/globals" in content or "from 'jest'" in content:
                                self._detected_framework = TestFramework.JEST
                                markers_found.append("jest imports in test files")
                                break
                            elif "vitest" in content:
                                self._detected_framework = TestFramework.VITEST
                                markers_found.append("vitest imports in test files")
                                break
                        except Exception:
                            pass

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
        """Install dependencies using npm.

        Also auto-installs Jest/ts-jest if tests use Jest imports but
        Jest isn't in package.json dependencies.
        """
        start_time = time.time()
        output_parts = []

        # Run detection to get framework info
        detection = self.detect()

        # Check if we need to install Jest
        needs_jest_install = False
        package_json = self.working_dir / "package.json"
        if package_json.exists() and self._detected_framework == TestFramework.JEST:
            try:
                pkg = json.loads(package_json.read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                scripts = pkg.get("scripts", {})
                # If Jest detected from imports but not in dependencies
                if "jest" not in deps and "@jest/core" not in deps:
                    needs_jest_install = True
            except json.JSONDecodeError:
                pass

        # Check if node_modules already exists (skip main install but still may need jest)
        skip_main_install = (self.working_dir / "node_modules").exists()

        if skip_main_install and not needs_jest_install:
            return DependencyInstallResult(
                success=True,
                duration=0.0,
                output="node_modules already exists",
            )

        try:
            # Install main dependencies
            if not skip_main_install:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                output_parts.append(result.stdout + result.stderr)
                if result.returncode != 0:
                    return DependencyInstallResult(
                        success=False,
                        duration=time.time() - start_time,
                        output="\n".join(output_parts),
                        error=result.stderr,
                    )

            # Install Jest if needed
            if needs_jest_install:
                # Install jest, ts-jest, and @jest/globals for TypeScript tests
                jest_result = subprocess.run(
                    ["npm", "install", "--save-dev", "jest", "ts-jest", "@jest/globals", "@types/jest"],
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                output_parts.append(f"Auto-installing Jest: {jest_result.stdout + jest_result.stderr}")

                if jest_result.returncode != 0:
                    return DependencyInstallResult(
                        success=False,
                        duration=time.time() - start_time,
                        output="\n".join(output_parts),
                        error=f"Failed to install Jest: {jest_result.stderr}",
                    )

                # Create jest.config.js if it doesn't exist
                jest_config = self.working_dir / "jest.config.js"
                if not jest_config.exists():
                    jest_config.write_text("""module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  testMatch: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { useESM: true }]
  },
};
""")
                    output_parts.append("Created jest.config.js")

            duration = time.time() - start_time
            return DependencyInstallResult(
                success=True,
                duration=duration,
                output="\n".join(output_parts),
            )
        except subprocess.TimeoutExpired:
            return DependencyInstallResult(
                success=False,
                duration=600,
                error="npm install timed out",
            )
        except FileNotFoundError:
            return DependencyInstallResult(
                success=False,
                duration=time.time() - start_time,
                error="npm not found. Please install Node.js",
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
            # Set CI=true to prevent interactive mode
            env = os.environ.copy()
            env["CI"] = "true"

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
                failures=[TestFailure(
                    test_name="timeout",
                    error_message=f"Tests did not complete within {self.timeout} seconds"
                )],
            )
        except FileNotFoundError:
            return TestResult(
                success=False,
                duration=time.time() - start_time,
                output="npm not found",
                failures=[TestFailure(
                    test_name="error",
                    error_message="npm not found. Please install Node.js"
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

    def _parse_jest_output(self, output: str, duration: float, success: bool) -> TestResult:
        """Parse Jest output."""
        total = 0
        passed = 0
        failed = 0
        skipped = 0

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
        total = 0
        passed = 0
        failed = 0
        skipped = 0

        # Pattern: "Tests 2 failed | 1 skipped | 5 passed (8)"
        pattern = r"Tests\s+(?:(\d+)\s+failed\s+\|\s+)?(?:(\d+)\s+skipped\s+\|\s+)?(\d+)\s+passed\s+\((\d+)\)"
        match = re.search(pattern, output)

        if match:
            failed = int(match.group(1) or 0)
            skipped = int(match.group(2) or 0)
            passed = int(match.group(3) or 0)
            total = int(match.group(4) or 0)

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
