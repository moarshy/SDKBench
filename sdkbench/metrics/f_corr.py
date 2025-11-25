"""F-CORR (Functional Correctness) metric evaluator.

Measures if the implementation actually works by running builds and tests.
Supports multiple languages through the test runner registry.
"""

import time
from typing import Dict, Optional
from pathlib import Path

from sdkbench.core import Solution, GroundTruth
from sdkbench.core.result import FCorrResult
from sdkbench.test_harness import BuildRunner, TestRunner
from sdkbench.test_harness.registry import TestRunnerRegistry
from sdkbench.test_harness.models import (
    TestResult as NewTestResult,
    DependencyInstallResult,
    FCorrResult as NewFCorrResult,
)


class FCorrEvaluator:
    """Evaluates functional correctness (F-CORR metric).

    Now supports multiple languages via the TestRunnerRegistry:
    - TypeScript/JavaScript (Jest, Vitest, Mocha)
    - Python (pytest)

    Scoring modes:
    - STRICT (default): Any test failure = 0 score
    - PASS_RATE: Score equals test pass rate percentage
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth

        # Get language-appropriate runner from registry
        self.runner = TestRunnerRegistry.get_runner(solution.solution_dir)

        # Keep legacy runners for backwards compatibility
        self.build_runner = BuildRunner(solution.solution_dir)
        self.test_runner = TestRunner(solution.solution_dir)

    def evaluate(
        self,
        run_build: bool = True,
        run_tests: bool = True,
        auto_install: bool = True,
        strict: bool = True,
        test_dir: Optional[Path] = None,
    ) -> FCorrResult:
        """Evaluate functional correctness.

        Args:
            run_build: Whether to run build (TypeScript only)
            run_tests: Whether to run tests
            auto_install: Whether to auto-install dependencies
            strict: If True, any failure = 0 score. If False, use pass rate.
            test_dir: Optional specific test directory

        Returns:
            FCorrResult with test results and score
        """
        # Use the new multi-language runner if available
        if self.runner is not None:
            return self._evaluate_with_registry(
                auto_install=auto_install,
                strict=strict,
                test_dir=test_dir,
            )

        # Fall back to legacy TypeScript-only evaluation
        return self._evaluate_legacy(
            run_build=run_build,
            run_tests=run_tests,
        )

    def _evaluate_with_registry(
        self,
        auto_install: bool = True,
        strict: bool = True,
        test_dir: Optional[Path] = None,
    ) -> FCorrResult:
        """Evaluate using the new multi-language runner registry.

        Args:
            auto_install: Whether to auto-install dependencies
            strict: If True, any failure = 0 score
            test_dir: Optional specific test directory

        Returns:
            FCorrResult with test results and score
        """
        failed_tests = []
        error_messages = []

        # Install dependencies if requested
        if auto_install:
            install_result = self.runner.install_dependencies()
            if not install_result.success:
                error_messages.append(f"Dependency install failed: {install_result.error}")
                return FCorrResult(
                    tests_passed=0,
                    tests_total=0,
                    failed_tests=[],
                    error_messages=error_messages,
                )

        # Run tests
        try:
            test_result = self.runner.run_tests(test_dir)
        except Exception as e:
            error_messages.append(f"Test execution error: {str(e)}")
            return FCorrResult(
                tests_passed=0,
                tests_total=0,
                failed_tests=[],
                error_messages=error_messages,
            )

        # Extract failure details
        for failure in test_result.failures:
            failed_tests.append(failure.test_name)
            if failure.error_message:
                error_messages.append(f"{failure.test_name}: {failure.error_message}")

        # Create result
        result = FCorrResult(
            tests_passed=test_result.passed,
            tests_total=test_result.total,
            failed_tests=failed_tests,
            error_messages=error_messages,
        )

        # Apply strict scoring if requested
        if strict and (not test_result.success or test_result.failed > 0):
            result.score = 0.0
        elif strict:
            result.score = 100.0
        # Otherwise the default pass_rate scoring from model_post_init applies

        return result

    def _evaluate_legacy(
        self,
        run_build: bool = True,
        run_tests: bool = True,
    ) -> FCorrResult:
        """Legacy evaluation for TypeScript projects.

        Args:
            run_build: Whether to run build
            run_tests: Whether to run tests

        Returns:
            FCorrResult with component scores and overall score
        """
        failed_tests = []
        error_messages = []
        tests_passed = 0
        tests_total = 0

        # Run build (TypeScript only)
        if run_build:
            build_result = self.build_runner.run_build()
            if not build_result.success:
                error_messages.extend(build_result.errors[:5])
                return FCorrResult(
                    tests_passed=0,
                    tests_total=0,
                    failed_tests=[],
                    error_messages=error_messages,
                )

        # Run tests
        if run_tests:
            test_result = self.test_runner.run_tests(install_deps=False)
            tests_passed = test_result.passed
            tests_total = test_result.total
            failed_tests = test_result.failures[:10] if hasattr(test_result, 'failures') else []

        return FCorrResult(
            tests_passed=tests_passed,
            tests_total=tests_total,
            failed_tests=failed_tests,
            error_messages=error_messages,
        )

    def evaluate_new(
        self,
        auto_install: bool = True,
        test_dir: Optional[Path] = None,
        strict: bool = True,
    ) -> NewFCorrResult:
        """Evaluate and return the new FCorrResult model with full details.

        This method returns the richer Pydantic model from test_harness.models
        instead of the simpler core.result.FCorrResult.

        Args:
            auto_install: Whether to auto-install dependencies
            test_dir: Optional specific test directory
            strict: If True, any failure = 0 score

        Returns:
            NewFCorrResult with detailed test results
        """
        start_time = time.time()

        # Check if we have a compatible runner
        if self.runner is None:
            return NewFCorrResult(
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
                return NewFCorrResult(
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
            return NewFCorrResult(
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

        return NewFCorrResult(
            score=score,
            test_results=test_result,
            install_results=install_result,
            language=detection.language,
            framework=detection.framework,
            error=None if test_result.success else f"{test_result.failed} tests failed",
            duration=time.time() - start_time,
        )

    def quick_check(self) -> Dict:
        """Quick check without full execution.

        Uses the runner registry to detect language and test framework.

        Returns:
            Dict with quick check results
        """
        if self.runner is not None:
            detection = self.runner.detect()
            return {
                "ready": detection.detected,
                "language": detection.language.value if detection.language else None,
                "framework": detection.framework.value if detection.framework else None,
                "confidence": detection.confidence,
                "markers_found": detection.markers_found,
                "runner_type": type(self.runner).__name__,
            }

        # Legacy TypeScript-only quick check
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
            list(self.solution.solution_dir.rglob('*.spec.tsx')) +
            list(self.solution.solution_dir.rglob('test_*.py')) +
            list(self.solution.solution_dir.rglob('*_test.py'))
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
        """Get detailed test results using the new runner.

        Returns:
            Dict with test details
        """
        if self.runner is not None:
            detection = self.runner.detect()
            install_result = self.runner.install_dependencies()

            if not install_result.success:
                return {
                    "skipped": True,
                    "reason": f"Dependency install failed: {install_result.error}",
                }

            test_result = self.runner.run_tests()

            return {
                "skipped": False,
                "success": test_result.success,
                "duration": test_result.duration,
                "total": test_result.total,
                "passed": test_result.passed,
                "failed": test_result.failed,
                "skipped_count": test_result.skipped,
                "pass_rate": test_result.pass_rate,
                "language": detection.language.value if detection.language else None,
                "framework": detection.framework.value if detection.framework else None,
                "failures": [f.model_dump() for f in test_result.failures[:5]],
            }

        # Legacy TypeScript path
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
            "skipped_count": test_result.skipped,
            "pass_rate": test_result.pass_rate,
            "failures": test_result.failures[:5],
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
        quick = self.quick_check()

        return {
            "quick_check": quick,
            "tests": self.get_test_details(),
            "overall_score": result.score,
            "tests_passed": result.tests_passed,
            "tests_total": result.tests_total,
            "pass_rate": result.pass_rate,
        }

    def evaluate_without_execution(self) -> FCorrResult:
        """Evaluate based on static analysis only.

        Useful for quick evaluation without running build/tests.

        Returns:
            FCorrResult with conservative estimates
        """
        check = self.quick_check()

        # If we have a runner, base estimate on detection confidence
        if self.runner is not None:
            detection = self.runner.detect()
            if detection.detected:
                # Conservative: assume 50% pass rate if tests detected
                return FCorrResult(
                    tests_passed=1,
                    tests_total=2,
                    failed_tests=[],
                    error_messages=["Static analysis only - tests not executed"],
                )
            else:
                return FCorrResult(
                    tests_passed=0,
                    tests_total=0,
                    failed_tests=[],
                    error_messages=["No test runner detected"],
                )

        # Legacy static analysis
        has_tests = check.get('has_tests', False)

        if has_tests:
            return FCorrResult(
                tests_passed=1,
                tests_total=2,
                failed_tests=[],
                error_messages=["Static analysis only - tests not executed"],
            )
        else:
            return FCorrResult(
                tests_passed=0,
                tests_total=0,
                failed_tests=[],
                error_messages=["No tests detected"],
            )
