"""Unit tests for TypeScript test runner."""

import pytest
from pathlib import Path
from unittest.mock import patch
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.test_harness.typescript_runner import TypeScriptTestRunner
from sdkbench.test_harness.models import (
    Language, TestFramework, RunnerDetectionResult, TestResult, TestFailure
)


class TestTypeScriptRunnerDetection:
    """Tests for TypeScript project detection."""

    def test_detects_package_json(self, temp_dir):
        """Should detect project with package.json."""
        pkg = {
            "name": "test-project",
            "scripts": {"test": "jest"},
            "devDependencies": {"jest": "^29.0.0"}
        }
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.detected is True
        assert result.language == Language.TYPESCRIPT
        assert "package.json" in result.markers_found

    def test_detects_jest_framework(self, temp_dir):
        """Should detect Jest as test framework."""
        pkg = {
            "devDependencies": {"jest": "^29.0.0"},
            "scripts": {"test": "jest"}
        }
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.framework == TestFramework.JEST
        assert "jest in dependencies" in result.markers_found

    def test_detects_vitest_framework(self, temp_dir):
        """Should detect Vitest as test framework."""
        pkg = {
            "devDependencies": {"vitest": "^0.34.0"},
            "scripts": {"test": "vitest"}
        }
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.framework == TestFramework.VITEST
        assert "vitest in dependencies" in result.markers_found

    def test_detects_mocha_framework(self, temp_dir):
        """Should detect Mocha as test framework."""
        pkg = {
            "devDependencies": {"mocha": "^10.0.0"},
            "scripts": {"test": "mocha"}
        }
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.framework == TestFramework.MOCHA
        assert "mocha in dependencies" in result.markers_found

    def test_detects_test_files(self, temp_dir):
        """Should detect test files."""
        pkg = {"name": "test", "scripts": {"test": "jest"}}
        (temp_dir / "package.json").write_text(json.dumps(pkg))
        (temp_dir / "app.test.ts").write_text("test('x', () => {})")
        (temp_dir / "app.spec.ts").write_text("test('y', () => {})")

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.detected is True
        assert any(".test.ts" in marker for marker in result.markers_found)

    def test_excludes_node_modules_from_detection(self, temp_dir):
        """Should exclude node_modules from test file detection."""
        pkg = {"name": "test", "scripts": {"test": "jest"}}
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        # Create test file in node_modules (should be excluded)
        nm_dir = temp_dir / "node_modules" / "some-package"
        nm_dir.mkdir(parents=True)
        (nm_dir / "index.test.ts").write_text("test('x', () => {})")

        # Create real test file
        (temp_dir / "app.test.ts").write_text("test('y', () => {})")

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.detected is True
        # Should only count the real test file

    def test_detects_tsconfig(self, temp_dir):
        """Should detect tsconfig.json."""
        pkg = {"name": "test"}
        (temp_dir / "package.json").write_text(json.dumps(pkg))
        (temp_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert "tsconfig.json" in result.markers_found

    def test_no_detection_without_package_json(self, temp_dir):
        """Should not detect without package.json."""
        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.detected is False

    def test_infers_framework_from_test_script(self, temp_dir):
        """Should infer framework from test script command."""
        pkg = {
            "name": "test",
            "scripts": {"test": "vitest run"}
        }
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)
        result = runner.detect()

        assert result.framework == TestFramework.VITEST


class TestTypeScriptRunnerParsing:
    """Tests for output parsing."""

    def test_parses_jest_success(self, temp_dir):
        """Should correctly parse successful Jest output."""
        pkg = {"scripts": {"test": "jest"}, "devDependencies": {"jest": "^29.0.0"}}
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)

        output = """
 PASS  ./app.test.ts
  ✓ should do something (5 ms)
  ✓ should do another thing (2 ms)

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
Snapshots:   0 total
Time:        1.234 s
"""
        result = runner._parse_jest_output(output, 1.234, True)

        assert result.success is True
        assert result.passed == 2
        assert result.total == 2

    def test_parses_jest_failures(self, temp_dir):
        """Should correctly parse Jest output with failures."""
        pkg = {"scripts": {"test": "jest"}, "devDependencies": {"jest": "^29.0.0"}}
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)

        output = """
 FAIL  ./app.test.ts
  ✓ should pass (5 ms)
  ✕ should fail (10 ms)

  ● should fail

    expect(received).toBe(expected)

    Expected: 2
    Received: 1

      at Object.<anonymous> (app.test.ts:5:14)

Test Suites: 1 failed, 1 total
Tests:       1 failed, 1 passed, 2 total
"""
        result = runner._parse_jest_output(output, 1.0, False)

        assert result.success is False
        assert result.passed == 1
        assert result.failed == 1
        assert result.total == 2


class TestJestFailureExtraction:
    """Tests for extracting failure details from Jest output."""

    def test_extracts_failure_from_jest_output(self, temp_dir):
        """Should extract failure details from Jest output."""
        pkg = {"devDependencies": {"jest": "^29.0.0"}}
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)

        output = """
● Test Suite › should handle authentication

    expect(received).toContain(expected)

    Expected: "ClerkProvider"
    Received: "<html></html>"

      at Object.<anonymous> (app.test.ts:15:20)

● Another Test › should validate input

    TypeError: Cannot read property 'x' of undefined

      at Object.<anonymous> (validation.test.ts:8:10)
"""
        failures = runner._extract_jest_failures(output)

        assert len(failures) >= 2
        # Check first failure
        assert any("authentication" in f.test_name.lower() for f in failures)

    def test_extracts_file_path_and_line_number(self, temp_dir):
        """Should extract file path and line number from stack trace."""
        pkg = {"devDependencies": {"jest": "^29.0.0"}}
        (temp_dir / "package.json").write_text(json.dumps(pkg))

        runner = TypeScriptTestRunner(temp_dir)

        output = """
● should fail

    expect(received).toBe(expected)

    Expected: 2
    Received: 1

      at Object.<anonymous> (app.test.ts:15:20)
"""
        failures = runner._extract_jest_failures(output)

        assert len(failures) >= 1
        failure = failures[0]
        assert failure.file_path == "app.test.ts"
        assert failure.line_number == 15


class TestFilterExcludedDirs:
    """Tests for directory exclusion filtering."""

    def test_filters_node_modules(self, temp_dir):
        """Should filter out node_modules directories."""
        runner = TypeScriptTestRunner(temp_dir)

        files = [
            temp_dir / "app.test.ts",
            temp_dir / "node_modules" / "pkg" / "index.test.ts",
            temp_dir / "src" / "utils.test.ts",
        ]

        filtered = runner._filter_excluded_dirs(files)

        assert len(filtered) == 2
        assert temp_dir / "app.test.ts" in filtered
        assert temp_dir / "src" / "utils.test.ts" in filtered
        assert temp_dir / "node_modules" / "pkg" / "index.test.ts" not in filtered

    def test_filters_multiple_excluded_dirs(self, temp_dir):
        """Should filter out multiple excluded directories."""
        runner = TypeScriptTestRunner(temp_dir)

        files = [
            temp_dir / "app.test.ts",
            temp_dir / "node_modules" / "test.ts",
            temp_dir / "dist" / "test.ts",
            temp_dir / "build" / "test.ts",
            temp_dir / ".next" / "test.ts",
        ]

        filtered = runner._filter_excluded_dirs(files)

        assert len(filtered) == 1
        assert temp_dir / "app.test.ts" in filtered


class TestTypeScriptRunnerLanguageAndFramework:
    """Tests for language and framework identification."""

    def test_get_language(self, temp_dir):
        """Should return TypeScript as language."""
        runner = TypeScriptTestRunner(temp_dir)

        assert runner.get_language() == Language.TYPESCRIPT

    def test_get_framework_default(self, temp_dir):
        """Should return Jest as default framework."""
        runner = TypeScriptTestRunner(temp_dir)

        # Default framework should be Jest
        assert runner.get_framework() == TestFramework.JEST


class TestTypeScriptRunnerInstantiation:
    """Tests for runner instantiation."""

    def test_accepts_working_dir(self, temp_dir):
        """Should accept working directory."""
        runner = TypeScriptTestRunner(temp_dir)

        assert runner.working_dir == temp_dir

    def test_default_timeout(self, temp_dir):
        """Should have default timeout."""
        runner = TypeScriptTestRunner(temp_dir)

        assert runner.timeout > 0

    def test_custom_timeout(self, temp_dir):
        """Should accept custom timeout."""
        runner = TypeScriptTestRunner(temp_dir, timeout=600)

        assert runner.timeout == 600


class TestTypeScriptRunnerHasRequiredMethods:
    """Tests for required method existence."""

    def test_has_detect_method(self, temp_dir):
        """Should have detect method."""
        runner = TypeScriptTestRunner(temp_dir)

        assert hasattr(runner, 'detect')
        assert callable(runner.detect)

    def test_has_run_tests_method(self, temp_dir):
        """Should have run_tests method."""
        runner = TypeScriptTestRunner(temp_dir)

        assert hasattr(runner, 'run_tests')
        assert callable(runner.run_tests)

    def test_has_install_dependencies_method(self, temp_dir):
        """Should have install_dependencies method."""
        runner = TypeScriptTestRunner(temp_dir)

        assert hasattr(runner, 'install_dependencies')
        assert callable(runner.install_dependencies)
