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
