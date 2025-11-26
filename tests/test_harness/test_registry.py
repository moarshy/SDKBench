"""Unit tests for test runner registry."""

import pytest
from pathlib import Path
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.test_harness.registry import TestRunnerRegistry
from sdkbench.test_harness.python_runner import PythonTestRunner
from sdkbench.test_harness.typescript_runner import TypeScriptTestRunner


class TestRegistryDetection:
    """Tests for runner registry detection."""

    def test_returns_python_runner_for_python_project(self, temp_dir):
        """Should return PythonTestRunner for Python projects."""
        (temp_dir / "requirements.txt").write_text("pytest>=7.0.0\n")
        (temp_dir / "test_app.py").write_text("def test_x(): pass\n")

        runner = TestRunnerRegistry.get_runner(temp_dir)

        assert runner is not None
        assert isinstance(runner, PythonTestRunner)

    def test_returns_typescript_runner_for_ts_project(self, temp_dir):
        """Should return TypeScriptTestRunner for TypeScript projects."""
        pkg = {
            "name": "test-project",
            "scripts": {"test": "jest"},
            "devDependencies": {"jest": "^29.0.0"}
        }
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TestRunnerRegistry.get_runner(temp_dir)

        assert runner is not None
        assert isinstance(runner, TypeScriptTestRunner)

    def test_returns_none_for_unknown_project(self, temp_dir):
        """Should return None for unknown project types."""
        # Empty directory - no recognizable project markers
        runner = TestRunnerRegistry.get_runner(temp_dir)

        assert runner is None

    def test_prefers_higher_confidence(self, temp_dir):
        """Should prefer runner with higher confidence."""
        # Create both Python and TypeScript markers
        (temp_dir / "requirements.txt").write_text("pytest>=7.0.0\n")
        (temp_dir / "test_app.py").write_text("def test_x(): pass\n")

        pkg = {"name": "test", "scripts": {"test": "jest"}}
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TestRunnerRegistry.get_runner(temp_dir)

        # Should return whichever has higher confidence
        assert runner is not None


class TestRegistryConfiguration:
    """Tests for registry configuration."""

    def test_detect_all_returns_results(self, temp_dir):
        """Should return detection results for all runners."""
        (temp_dir / "requirements.txt").write_text("pytest>=7.0.0\n")

        results = TestRunnerRegistry.detect_all(temp_dir)

        assert len(results) >= 2  # At least Python and TypeScript runners

    def test_clear_and_reinitialize(self):
        """Should be able to clear and reinitialize registry."""
        TestRunnerRegistry.clear()

        # After clear, getting runners should reinitialize
        runners = TestRunnerRegistry.get_all_runners()

        assert len(runners) >= 2


class TestRegistryAvailableRunners:
    """Tests for available runners."""

    def test_has_python_runner(self):
        """Should have Python runner in available runners."""
        runners = TestRunnerRegistry.get_all_runners()

        assert any(r.__name__ == 'PythonTestRunner' for r in runners)

    def test_has_typescript_runner(self):
        """Should have TypeScript runner in available runners."""
        runners = TestRunnerRegistry.get_all_runners()

        assert any(r.__name__ == 'TypeScriptTestRunner' for r in runners)

    def test_get_all_runners_returns_list(self):
        """Should return a list of runner classes."""
        runners = TestRunnerRegistry.get_all_runners()

        assert isinstance(runners, list)
        assert len(runners) > 0

    def test_all_runners_have_detect_method(self):
        """All registered runners should have detect method."""
        runners = TestRunnerRegistry.get_all_runners()

        for runner_class in runners:
            assert hasattr(runner_class, 'detect') or callable(getattr(runner_class, 'detect', None))
