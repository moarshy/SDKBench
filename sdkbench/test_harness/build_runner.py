"""Build runner for executing project builds."""

import re
from pathlib import Path
from typing import Dict, List, Optional

from sdkbench.test_harness.executor import Executor, ExecutionResult


class BuildResult:
    """Result of a build execution."""

    def __init__(
        self,
        success: bool,
        duration: float,
        errors: List[str],
        warnings: List[str],
        output: str,
    ):
        """Initialize build result.

        Args:
            success: Whether build succeeded
            duration: Build duration in seconds
            errors: List of error messages
            warnings: List of warning messages
            output: Full build output
        """
        self.success = success
        self.duration = duration
        self.errors = errors
        self.warnings = warnings
        self.output = output

    def __repr__(self) -> str:
        """String representation."""
        status = "SUCCESS" if self.success else "FAILED"
        return (
            f"<BuildResult {status} "
            f"errors={len(self.errors)} warnings={len(self.warnings)} "
            f"duration={self.duration:.2f}s>"
        )


class BuildRunner:
    """Runner for executing project builds."""

    def __init__(self, solution_dir: Path):
        """Initialize build runner.

        Args:
            solution_dir: Path to solution directory
        """
        self.solution_dir = Path(solution_dir)
        self.executor = Executor(solution_dir, timeout=600)  # 10 min build timeout

    def run_build(self, install_deps: bool = True) -> BuildResult:
        """Run the project build.

        Args:
            install_deps: Whether to install dependencies first

        Returns:
            BuildResult with build status and details
        """
        # Check prerequisites
        if not self.executor.check_node_installed():
            return BuildResult(
                success=False,
                duration=0.0,
                errors=["Node.js not installed"],
                warnings=[],
                output="",
            )

        if not self.executor.check_npm_installed():
            return BuildResult(
                success=False,
                duration=0.0,
                errors=["npm not installed"],
                warnings=[],
                output="",
            )

        # Install dependencies if needed
        if install_deps:
            if not self.executor.check_dependencies_installed():
                install_result = self.executor.install_dependencies()

                if not install_result.success:
                    return BuildResult(
                        success=False,
                        duration=install_result.duration,
                        errors=["Failed to install dependencies"],
                        warnings=[],
                        output=install_result.stdout + "\n" + install_result.stderr,
                    )

        # Determine build command
        if self.executor.has_script('build'):
            build_result = self.executor.run_npm_script('build')
        elif self.executor.has_script('compile'):
            build_result = self.executor.run_npm_script('compile')
        else:
            # Try TypeScript compilation directly
            build_result = self.executor.run_command(['npx', 'tsc', '--noEmit'])

        # Parse build output
        errors = self._extract_errors(build_result.stdout, build_result.stderr)
        warnings = self._extract_warnings(build_result.stdout, build_result.stderr)

        return BuildResult(
            success=build_result.success,
            duration=build_result.duration,
            errors=errors,
            warnings=warnings,
            output=build_result.stdout + "\n" + build_result.stderr,
        )

    def _extract_errors(self, stdout: str, stderr: str) -> List[str]:
        """Extract error messages from build output.

        Args:
            stdout: Standard output
            stderr: Standard error

        Returns:
            List of error messages
        """
        errors = []
        combined = stdout + "\n" + stderr

        # Pattern 1: TypeScript errors
        ts_error_pattern = r'error TS\d+: (.+)'
        errors.extend(re.findall(ts_error_pattern, combined))

        # Pattern 2: Generic errors
        generic_error_pattern = r'(?:^|\n)(?:ERROR|Error): (.+)'
        errors.extend(re.findall(generic_error_pattern, combined))

        # Pattern 3: Next.js build errors
        next_error_pattern = r'Failed to compile\.[\s\S]*?(?=\n\n|\Z)'
        errors.extend(re.findall(next_error_pattern, combined))

        return errors

    def _extract_warnings(self, stdout: str, stderr: str) -> List[str]:
        """Extract warning messages from build output.

        Args:
            stdout: Standard output
            stderr: Standard error

        Returns:
            List of warning messages
        """
        warnings = []
        combined = stdout + "\n" + stderr

        # Pattern 1: TypeScript warnings
        ts_warning_pattern = r'warning TS\d+: (.+)'
        warnings.extend(re.findall(ts_warning_pattern, combined))

        # Pattern 2: Generic warnings
        generic_warning_pattern = r'(?:^|\n)(?:WARNING|Warning): (.+)'
        warnings.extend(re.findall(generic_warning_pattern, combined))

        return warnings

    def check_type_errors(self) -> Dict[str, any]:
        """Run TypeScript type checking.

        Returns:
            Dict with type check results
        """
        if not (self.solution_dir / "tsconfig.json").exists():
            return {
                "typescript_enabled": False,
                "errors": [],
                "warnings": [],
            }

        # Run tsc with --noEmit to check types only
        result = self.executor.run_command(['npx', 'tsc', '--noEmit'], timeout=120)

        errors = self._extract_errors(result.stdout, result.stderr)
        warnings = self._extract_warnings(result.stdout, result.stderr)

        return {
            "typescript_enabled": True,
            "success": result.success,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }

    def lint_code(self) -> Dict[str, any]:
        """Run linter if available.

        Returns:
            Dict with lint results
        """
        if not self.executor.has_script('lint'):
            return {
                "lint_enabled": False,
                "issues": [],
            }

        result = self.executor.run_npm_script('lint', timeout=120)

        # Parse lint output
        issues = []

        # ESLint format: file:line:col: message
        eslint_pattern = r'(.+):(\d+):(\d+): (.+)'

        for line in result.stdout.split('\n'):
            match = re.match(eslint_pattern, line.strip())
            if match:
                issues.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'column': int(match.group(3)),
                    'message': match.group(4),
                })

        return {
            "lint_enabled": True,
            "success": result.success,
            "issue_count": len(issues),
            "issues": issues,
        }

    def get_build_summary(self) -> Dict[str, any]:
        """Get comprehensive build summary.

        Returns:
            Dict with all build-related checks
        """
        build_result = self.run_build()
        type_check = self.check_type_errors()
        lint_result = self.lint_code()

        return {
            "build": {
                "success": build_result.success,
                "duration": build_result.duration,
                "error_count": len(build_result.errors),
                "warning_count": len(build_result.warnings),
            },
            "type_check": type_check,
            "lint": lint_result,
            "overall_success": (
                build_result.success and
                (not type_check.get('typescript_enabled') or type_check.get('success', True))
            ),
        }
