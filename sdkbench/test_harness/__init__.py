"""Test harness for F-CORR evaluation.

Provides language-agnostic test running capabilities with
auto-detection of project type and test framework.
"""

# New Pydantic models
from sdkbench.test_harness.models import (
    TestStatus,
    TestFailure,
    TestResult,
    DependencyInstallResult,
    Language,
    TestFramework,
    RunnerDetectionResult,
    FCorrResult,
)

# New runner framework
from sdkbench.test_harness.base_runner import BaseTestRunner
from sdkbench.test_harness.registry import TestRunnerRegistry
from sdkbench.test_harness.python_runner import PythonTestRunner
from sdkbench.test_harness.typescript_runner import TypeScriptTestRunner

# Legacy classes (backwards compatibility)
from sdkbench.test_harness.executor import Executor
from sdkbench.test_harness.build_runner import BuildRunner
from sdkbench.test_harness.test_runner import TestRunner

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
    "Executor",
    "BuildRunner",
    "TestRunner",
]
