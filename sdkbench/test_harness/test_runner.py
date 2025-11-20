"""Test runner for executing project tests."""

import re
from pathlib import Path
from typing import Dict, List, Optional

from sdkbench.test_harness.executor import Executor, ExecutionResult


class TestResult:
    """Result of test execution."""

    def __init__(
        self,
        success: bool,
        duration: float,
        total: int,
        passed: int,
        failed: int,
        skipped: int,
        output: str,
        failures: List[Dict] = None,
    ):
        """Initialize test result.

        Args:
            success: Whether all tests passed
            duration: Test duration in seconds
            total: Total number of tests
            passed: Number of passed tests
            failed: Number of failed tests
            skipped: Number of skipped tests
            output: Full test output
            failures: List of test failure details
        """
        self.success = success
        self.duration = duration
        self.total = total
        self.passed = passed
        self.failed = failed
        self.skipped = skipped
        self.output = output
        self.failures = failures or []

    @property
    def pass_rate(self) -> float:
        """Calculate test pass rate.

        Returns:
            Pass rate as 0-1 float
        """
        if self.total == 0:
            return 0.0
        return self.passed / self.total

    def __repr__(self) -> str:
        """String representation."""
        status = "SUCCESS" if self.success else "FAILED"
        return (
            f"<TestResult {status} "
            f"passed={self.passed}/{self.total} "
            f"duration={self.duration:.2f}s>"
        )


class TestRunner:
    """Runner for executing project tests."""

    def __init__(self, solution_dir: Path):
        """Initialize test runner.

        Args:
            solution_dir: Path to solution directory
        """
        self.solution_dir = Path(solution_dir)
        self.executor = Executor(solution_dir, timeout=600)  # 10 min test timeout

    def run_tests(self, install_deps: bool = True) -> TestResult:
        """Run the project tests.

        Args:
            install_deps: Whether to install dependencies first

        Returns:
            TestResult with test status and details
        """
        # Check prerequisites
        if not self.executor.check_node_installed():
            return TestResult(
                success=False,
                duration=0.0,
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                output="Node.js not installed",
            )

        if not self.executor.check_npm_installed():
            return TestResult(
                success=False,
                duration=0.0,
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                output="npm not installed",
            )

        # Install dependencies if needed
        if install_deps:
            if not self.executor.check_dependencies_installed():
                install_result = self.executor.install_dependencies()

                if not install_result.success:
                    return TestResult(
                        success=False,
                        duration=install_result.duration,
                        total=0,
                        passed=0,
                        failed=0,
                        skipped=0,
                        output="Failed to install dependencies",
                    )

        # Determine test command
        if self.executor.has_script('test'):
            test_result = self.executor.run_npm_script('test')
        else:
            # No tests configured
            return TestResult(
                success=True,
                duration=0.0,
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                output="No test script configured",
            )

        # Parse test output
        stats = self._parse_test_output(test_result.stdout, test_result.stderr)

        return TestResult(
            success=test_result.success,
            duration=test_result.duration,
            total=stats['total'],
            passed=stats['passed'],
            failed=stats['failed'],
            skipped=stats['skipped'],
            output=test_result.stdout + "\n" + test_result.stderr,
            failures=stats.get('failures', []),
        )

    def _parse_test_output(self, stdout: str, stderr: str) -> Dict[str, any]:
        """Parse test output to extract statistics.

        Args:
            stdout: Standard output
            stderr: Standard error

        Returns:
            Dict with test statistics
        """
        combined = stdout + "\n" + stderr

        stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'failures': [],
        }

        # Try Jest format first
        jest_stats = self._parse_jest_output(combined)
        if jest_stats['total'] > 0:
            return jest_stats

        # Try Vitest format
        vitest_stats = self._parse_vitest_output(combined)
        if vitest_stats['total'] > 0:
            return vitest_stats

        # Try Mocha format
        mocha_stats = self._parse_mocha_output(combined)
        if mocha_stats['total'] > 0:
            return mocha_stats

        return stats

    def _parse_jest_output(self, output: str) -> Dict[str, any]:
        """Parse Jest test output.

        Args:
            output: Test output

        Returns:
            Dict with test statistics
        """
        stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'failures': [],
        }

        # Pattern: Tests:       1 failed, 2 passed, 3 total
        summary_pattern = r'Tests:\s+(?:(\d+) failed[,\s]+)?(?:(\d+) skipped[,\s]+)?(?:(\d+) passed[,\s]+)?(\d+) total'

        match = re.search(summary_pattern, output)
        if match:
            failed = int(match.group(1)) if match.group(1) else 0
            skipped = int(match.group(2)) if match.group(2) else 0
            passed = int(match.group(3)) if match.group(3) else 0
            total = int(match.group(4))

            stats['total'] = total
            stats['passed'] = passed
            stats['failed'] = failed
            stats['skipped'] = skipped

        # Extract failure details
        failure_pattern = r'● (.+)\n\n\s+(.+)'
        failures = re.findall(failure_pattern, output)

        for test_name, error_message in failures:
            stats['failures'].append({
                'test': test_name.strip(),
                'error': error_message.strip(),
            })

        return stats

    def _parse_vitest_output(self, output: str) -> Dict[str, any]:
        """Parse Vitest test output.

        Args:
            output: Test output

        Returns:
            Dict with test statistics
        """
        stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'failures': [],
        }

        # Pattern: Test Files  1 passed (1)
        #          Tests  3 passed (3)
        test_pattern = r'Tests\s+(?:(\d+) failed[,\s]+)?(?:(\d+) skipped[,\s]+)?(\d+) passed \((\d+)\)'

        match = re.search(test_pattern, output)
        if match:
            failed = int(match.group(1)) if match.group(1) else 0
            skipped = int(match.group(2)) if match.group(2) else 0
            passed = int(match.group(3))
            total = int(match.group(4))

            stats['total'] = total
            stats['passed'] = passed
            stats['failed'] = failed
            stats['skipped'] = skipped

        return stats

    def _parse_mocha_output(self, output: str) -> Dict[str, any]:
        """Parse Mocha test output.

        Args:
            output: Test output

        Returns:
            Dict with test statistics
        """
        stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'failures': [],
        }

        # Pattern: 3 passing (123ms)
        #          1 failing
        passing_pattern = r'(\d+) passing'
        failing_pattern = r'(\d+) failing'
        pending_pattern = r'(\d+) pending'

        passing_match = re.search(passing_pattern, output)
        if passing_match:
            stats['passed'] = int(passing_match.group(1))

        failing_match = re.search(failing_pattern, output)
        if failing_match:
            stats['failed'] = int(failing_match.group(1))

        pending_match = re.search(pending_pattern, output)
        if pending_match:
            stats['skipped'] = int(pending_match.group(1))

        stats['total'] = stats['passed'] + stats['failed'] + stats['skipped']

        return stats

    def check_test_coverage(self) -> Optional[Dict[str, any]]:
        """Run tests with coverage if available.

        Returns:
            Dict with coverage stats or None
        """
        if not self.executor.has_script('test:coverage'):
            # Try test with --coverage flag
            if not self.executor.has_script('test'):
                return None

        # Run tests with coverage
        if self.executor.has_script('test:coverage'):
            result = self.executor.run_npm_script('test:coverage')
        else:
            result = self.executor.run_command(['npm', 'test', '--', '--coverage'])

        if not result.success:
            return None

        # Parse coverage output
        coverage = self._parse_coverage_output(result.stdout)

        return coverage

    def _parse_coverage_output(self, output: str) -> Dict[str, any]:
        """Parse coverage output.

        Args:
            output: Test output with coverage

        Returns:
            Dict with coverage statistics
        """
        # Look for coverage summary table
        # Example:
        # All files      |   75.00 |   66.67 |   80.00 |   75.00 |
        summary_pattern = r'All files\s+\|\s+([\d.]+)\s+\|\s+([\d.]+)\s+\|\s+([\d.]+)\s+\|\s+([\d.]+)'

        match = re.search(summary_pattern, output)

        if match:
            return {
                'statements': float(match.group(1)),
                'branches': float(match.group(2)),
                'functions': float(match.group(3)),
                'lines': float(match.group(4)),
            }

        return {}

    def get_test_summary(self) -> Dict[str, any]:
        """Get comprehensive test summary.

        Returns:
            Dict with all test-related checks
        """
        test_result = self.run_tests()
        coverage = self.check_test_coverage()

        return {
            "tests": {
                "success": test_result.success,
                "duration": test_result.duration,
                "total": test_result.total,
                "passed": test_result.passed,
                "failed": test_result.failed,
                "skipped": test_result.skipped,
                "pass_rate": test_result.pass_rate,
            },
            "coverage": coverage,
            "failures": test_result.failures,
        }
