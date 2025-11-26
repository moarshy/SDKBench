"""Registry for test runners with auto-detection."""

from typing import List, Type, Optional
from pathlib import Path

from .base_runner import BaseTestRunner
from .models import RunnerDetectionResult


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
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure default runners are registered."""
        if not cls._initialized:
            cls._register_default_runners()
            cls._initialized = True

    @classmethod
    def _register_default_runners(cls) -> None:
        """Register the built-in runners."""
        # Import here to avoid circular imports
        from .typescript_runner import TypeScriptTestRunner
        from .python_runner import PythonTestRunner

        # Register TypeScript first (more specific detection due to package.json)
        if TypeScriptTestRunner not in cls._runners:
            cls._runners.append(TypeScriptTestRunner)
        if PythonTestRunner not in cls._runners:
            cls._runners.append(PythonTestRunner)

    @classmethod
    def register(cls, runner_class: Type[BaseTestRunner]) -> None:
        """Register a new test runner.

        Args:
            runner_class: A class inheriting from BaseTestRunner
        """
        cls._ensure_initialized()
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
        cls._ensure_initialized()

        best_runner: Optional[BaseTestRunner] = None
        best_confidence = 0.0

        for runner_class in cls._runners:
            try:
                runner = runner_class(working_dir)
                detection = runner.detect()

                if detection.detected and detection.confidence > best_confidence:
                    best_runner = runner
                    best_confidence = detection.confidence
            except Exception:
                # Skip this runner if detection fails
                continue

        return best_runner

    @classmethod
    def get_all_runners(cls) -> List[Type[BaseTestRunner]]:
        """Get all registered runner classes."""
        cls._ensure_initialized()
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
        cls._ensure_initialized()

        results = []
        for runner_class in cls._runners:
            runner = runner_class(working_dir)
            results.append(runner.detect())
        return results

    @classmethod
    def clear(cls) -> None:
        """Clear all registered runners. Useful for testing."""
        cls._runners = []
        cls._initialized = False
