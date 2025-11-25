"""Abstract base class for language-specific test runners."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

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
