"""F-CORR (Functional Correctness) metric evaluator.

Measures if the implementation actually works by running builds and tests.
"""

from typing import Dict, Optional
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, FCorrResult
from sdkbench.test_harness import BuildRunner, TestRunner


class FCorrEvaluator:
    """Evaluates functional correctness (F-CORR metric).

    F-CORR Score = 0-100%
    Components (weighted):
    - Build success (25%): Does the project build without errors?
    - Test pass rate (50%): What % of tests pass?
    - Runtime errors (25%): Are there runtime errors?
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth
        self.build_runner = BuildRunner(solution.solution_dir)
        self.test_runner = TestRunner(solution.solution_dir)

    def evaluate(self, run_build: bool = True, run_tests: bool = True) -> FCorrResult:
        """Evaluate functional correctness.

        Args:
            run_build: Whether to run build
            run_tests: Whether to run tests

        Returns:
            FCorrResult with component scores and overall score
        """
        build_success = False
        test_pass_rate = 0.0
        runtime_errors = 0

        # Run build
        if run_build:
            build_result = self.build_runner.run_build()
            build_success = build_result.success
            runtime_errors += len(build_result.errors)

        # Run tests
        if run_tests and build_success:
            test_result = self.test_runner.run_tests(install_deps=False)
            test_pass_rate = test_result.pass_rate

            # Count failures as runtime errors
            runtime_errors += test_result.failed

        # Calculate runtime error score
        # Penalize based on number of errors (exponential decay)
        # 0 errors = 1.0, 1 error = 0.9, 5 errors = 0.6, 10+ errors = 0.35
        runtime_score = max(0.0, 1.0 - (runtime_errors * 0.1))

        return FCorrResult(
            build_success=build_success,
            test_pass_rate=test_pass_rate,
            runtime_errors=runtime_errors,
            runtime_score=runtime_score,
        )

    def get_build_details(self) -> Dict:
        """Get detailed build results.

        Returns:
            Dict with build details
        """
        build_result = self.build_runner.run_build()

        return {
            "success": build_result.success,
            "duration": build_result.duration,
            "error_count": len(build_result.errors),
            "warning_count": len(build_result.warnings),
            "errors": build_result.errors[:10],  # Limit to first 10
            "warnings": build_result.warnings[:10],
        }

    def get_test_details(self) -> Dict:
        """Get detailed test results.

        Returns:
            Dict with test details
        """
        # Only run tests if build succeeds
        build_result = self.build_runner.run_build()

        if not build_result.success:
            return {
                "skipped": True,
                "reason": "Build failed",
            }

        test_result = self.test_runner.run_tests(install_deps=False)

        return {
            "skipped": False,
            "success": test_result.success,
            "duration": test_result.duration,
            "total": test_result.total,
            "passed": test_result.passed,
            "failed": test_result.failed,
            "skipped": test_result.skipped,
            "pass_rate": test_result.pass_rate,
            "failures": test_result.failures[:5],  # Limit to first 5
        }

    def get_type_check_details(self) -> Dict:
        """Get TypeScript type checking results.

        Returns:
            Dict with type check details
        """
        return self.build_runner.check_type_errors()

    def get_lint_details(self) -> Dict:
        """Get linter results.

        Returns:
            Dict with lint details
        """
        return self.build_runner.lint_code()

    def get_coverage_details(self) -> Optional[Dict]:
        """Get test coverage results.

        Returns:
            Dict with coverage details or None
        """
        return self.test_runner.check_test_coverage()

    def get_details(self) -> Dict:
        """Get detailed evaluation breakdown.

        Returns:
            Dict with detailed component results
        """
        result = self.evaluate()

        return {
            "build": self.get_build_details(),
            "tests": self.get_test_details(),
            "type_check": self.get_type_check_details(),
            "lint": self.get_lint_details(),
            "overall_score": result.score,
            "build_success": result.build_success,
            "test_pass_rate": result.test_pass_rate,
            "runtime_errors": result.runtime_errors,
        }

    def quick_check(self) -> Dict:
        """Quick check without full execution.

        Checks for common issues without running build/tests.

        Returns:
            Dict with quick check results
        """
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
        test_files = (
            list(self.solution.solution_dir.rglob('*.test.ts')) +
            list(self.solution.solution_dir.rglob('*.test.tsx')) +
            list(self.solution.solution_dir.rglob('*.test.js')) +
            list(self.solution.solution_dir.rglob('*.test.jsx')) +
            list(self.solution.solution_dir.rglob('*.spec.ts')) +
            list(self.solution.solution_dir.rglob('*.spec.tsx'))
        )

        has_tests = len(test_files) > 0

        # Check for build script
        scripts = self.build_runner.executor.get_package_scripts()
        has_build_script = 'build' in scripts

        # Check for test script
        has_test_script = 'test' in scripts

        return {
            "issues": issues,
            "has_tsconfig": has_tsconfig,
            "has_tests": has_tests,
            "test_file_count": len(test_files),
            "has_build_script": has_build_script,
            "has_test_script": has_test_script,
            "available_scripts": list(scripts.keys()),
            "ready_for_evaluation": len(issues) == 0,
        }

    def evaluate_without_execution(self) -> FCorrResult:
        """Evaluate based on static analysis only.

        Useful for quick evaluation without running build/tests.

        Returns:
            FCorrResult with conservative estimates
        """
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
