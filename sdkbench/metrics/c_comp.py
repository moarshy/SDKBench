"""C-COMP (Configuration Completeness) metric evaluator.

Measures completeness of SDK configuration in the solution.
"""

import re
from typing import Dict, List, Optional
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, CCompResult
from sdkbench.parsers import EnvParser, ConfigParser, PythonParser


class CCompEvaluator:
    """Evaluates configuration completeness (C-COMP metric).

    C-COMP Score = 0-100%
    Components (weighted):
    - Environment variables (50%): Are all required env vars present?
    - Dependencies/Provider Props (30%): Are correct packages installed?
    - Middleware config (20%): Is middleware configured correctly?
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth

    def evaluate(self) -> CCompResult:
        """Evaluate configuration completeness.

        Returns:
            CCompResult with component scores and overall score
        """
        # Get configuration data from ground truth
        config_data = self.ground_truth.get_configuration()

        if not config_data:
            # No configuration expected - return perfect scores
            return CCompResult(
                env_vars_score=1.0,
                provider_props_score=1.0,  # Maps to dependencies
                middleware_config_score=1.0,
            )

        # Evaluate each component
        env_vars = self._check_env_vars(config_data)
        dependencies = self._check_dependencies(config_data)
        middleware = self._check_middleware(config_data)

        return CCompResult(
            env_vars_score=float(env_vars),
            provider_props_score=float(dependencies),  # Dependencies map to provider_props
            middleware_config_score=float(middleware),
        )

    def _check_env_vars(self, config_data: Dict) -> bool:
        """Check if required environment variables are present.

        Args:
            config_data: Configuration ingredient data

        Returns:
            True if all required env vars present
        """
        expected_env = config_data.get('env_vars', [])

        if not expected_env:
            return True

        # Extract env vars from solution
        solution_env_vars = self.solution.extract_env_vars()

        # Check each expected env var
        for expected_var in expected_env:
            # Handle both string and dict formats
            if isinstance(expected_var, str):
                var_name = expected_var
            elif isinstance(expected_var, dict):
                var_name = expected_var.get('name')
            else:
                continue

            if var_name not in solution_env_vars:
                return False

        return True

    def _check_env_vars_detailed(self, config_data: Dict) -> Dict:
        """Get detailed env vars check results.

        Args:
            config_data: Configuration ingredient data

        Returns:
            Dict with detailed results
        """
        expected_env = config_data.get('env_vars', [])
        solution_env_vars = self.solution.extract_env_vars()

        missing = []
        present = []

        for expected_var in expected_env:
            if isinstance(expected_var, str):
                var_name = expected_var
            elif isinstance(expected_var, dict):
                var_name = expected_var.get('name')
            else:
                continue

            if var_name in solution_env_vars:
                present.append(var_name)
            else:
                missing.append(var_name)

        return {
            'expected_count': len(expected_env),
            'present_count': len(present),
            'missing_count': len(missing),
            'present': present,
            'missing': missing,
            'all_present': len(missing) == 0,
        }

    def _check_dependencies(self, config_data: Dict) -> bool:
        """Check if required dependencies are installed.

        Args:
            config_data: Configuration ingredient data

        Returns:
            True if all required dependencies present
        """
        expected_deps = config_data.get('dependencies', {})

        if not expected_deps:
            return True

        # Determine project type by checking for config files
        package_json_path = self.solution.solution_dir / 'package.json'
        requirements_path = self.solution.solution_dir / 'requirements.txt'
        pyproject_path = self.solution.solution_dir / 'pyproject.toml'

        # Try package.json (Node.js/TypeScript)
        if package_json_path.exists():
            package_json = ConfigParser.parse_package_json(package_json_path)
            if package_json:
                solution_deps = ConfigParser.extract_dependencies(package_json)
                return self._verify_deps(expected_deps, solution_deps)

        # Try requirements.txt (Python)
        if requirements_path.exists():
            solution_deps = self._parse_requirements_txt(requirements_path)
            return self._verify_deps(expected_deps, solution_deps, is_python=True)

        # Try pyproject.toml (Python)
        if pyproject_path.exists():
            solution_deps = self._parse_pyproject_toml(pyproject_path)
            return self._verify_deps(expected_deps, solution_deps, is_python=True)

        # No dependency file found - check if any expected
        return len(expected_deps) == 0

    def _verify_deps(self, expected: Dict, actual: Dict, is_python: bool = False) -> bool:
        """Verify expected dependencies are present.

        Args:
            expected: Expected dependencies
            actual: Actual dependencies found
            is_python: Whether this is a Python project

        Returns:
            True if all expected deps present
        """
        for dep_name, dep_version in expected.items():
            # Normalize package name (Python uses underscores/hyphens interchangeably)
            if is_python:
                normalized_name = dep_name.lower().replace('-', '_').replace('_', '-')
                found = any(
                    actual_name.lower().replace('-', '_').replace('_', '-') == normalized_name
                    or actual_name.lower() == dep_name.lower()
                    for actual_name in actual.keys()
                )
            else:
                found = dep_name in actual

            if not found:
                return False

            # Version check (optional)
            if dep_version and dep_name in actual:
                actual_version = actual[dep_name]
                if not self._check_version_compatible(actual_version, dep_version):
                    return False

        return True

    def _parse_requirements_txt(self, path: Path) -> Dict[str, str]:
        """Parse requirements.txt file.

        Args:
            path: Path to requirements.txt

        Returns:
            Dict mapping package names to version specs
        """
        deps = {}
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # Skip -r includes
                    if line.startswith('-'):
                        continue

                    # Parse package name and version
                    # Formats: package, package==1.0, package>=1.0, package[extra]>=1.0
                    match = re.match(r'^([a-zA-Z0-9_-]+)(?:\[.*?\])?(.*)$', line)
                    if match:
                        name = match.group(1)
                        version = match.group(2).strip()
                        deps[name] = version
        except Exception:
            pass
        return deps

    def _parse_pyproject_toml(self, path: Path) -> Dict[str, str]:
        """Parse pyproject.toml for dependencies.

        Args:
            path: Path to pyproject.toml

        Returns:
            Dict mapping package names to version specs
        """
        deps = {}
        try:
            with open(path, 'r') as f:
                content = f.read()

            # Simple parsing - look for dependencies section
            in_deps = False
            for line in content.split('\n'):
                if 'dependencies' in line and '=' in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.startswith('[') or (line.strip() and not line.startswith(' ') and not line.startswith('"')):
                        in_deps = False
                        continue
                    # Parse "package>=version" format
                    match = re.search(r'"([a-zA-Z0-9_-]+)([<>=!].*?)?"', line)
                    if match:
                        name = match.group(1)
                        version = match.group(2) or ''
                        deps[name] = version
        except Exception:
            pass
        return deps

    def _check_version_compatible(self, actual: str, expected: str) -> bool:
        """Check if versions are compatible.

        Args:
            actual: Actual version string
            expected: Expected version string

        Returns:
            True if compatible
        """
        # Parse versions
        actual_parsed = ConfigParser.validate_clerk_version(actual)
        expected_parsed = ConfigParser.validate_clerk_version(expected)

        if not actual_parsed['is_valid'] or not expected_parsed['is_valid']:
            # If we can't parse, assume compatible
            return True

        # Check major version compatibility
        if actual_parsed['major'] != expected_parsed['major']:
            return False

        # Minor version should be >= expected
        if actual_parsed['minor'] < expected_parsed['minor']:
            return False

        return True

    def _check_dependencies_detailed(self, config_data: Dict) -> Dict:
        """Get detailed dependencies check results.

        Args:
            config_data: Configuration ingredient data

        Returns:
            Dict with detailed results
        """
        expected_deps = config_data.get('dependencies', {})

        package_json_path = self.solution.solution_dir / 'package.json'

        if not package_json_path.exists():
            return {
                'expected_count': len(expected_deps),
                'present_count': 0,
                'missing_count': len(expected_deps),
                'missing': list(expected_deps.keys()),
                'present': [],
                'version_mismatches': [],
                'all_present': False,
            }

        package_json = ConfigParser.parse_package_json(package_json_path)
        solution_deps = ConfigParser.extract_dependencies(package_json)

        missing = []
        present = []
        version_mismatches = []

        for dep_name, dep_version in expected_deps.items():
            if dep_name not in solution_deps:
                missing.append(dep_name)
            else:
                present.append(dep_name)

                # Check version
                actual_version = solution_deps[dep_name]
                if not self._check_version_compatible(actual_version, dep_version):
                    version_mismatches.append({
                        'dependency': dep_name,
                        'expected': dep_version,
                        'actual': actual_version,
                    })

        return {
            'expected_count': len(expected_deps),
            'present_count': len(present),
            'missing_count': len(missing),
            'missing': missing,
            'present': present,
            'version_mismatches': version_mismatches,
            'all_present': len(missing) == 0 and len(version_mismatches) == 0,
        }

    def _check_middleware(self, config_data: Dict) -> bool:
        """Check if middleware is configured correctly.

        Args:
            config_data: Configuration ingredient data

        Returns:
            True if middleware configured correctly
        """
        expected_middleware = config_data.get('middleware')

        if not expected_middleware:
            return True

        # Get middleware config from solution
        solution_middleware = self.solution.extract_middleware_config()

        if not solution_middleware:
            return False

        # Check middleware type
        expected_type = expected_middleware.get('type')
        if expected_type:
            if solution_middleware.get('type') != expected_type:
                return False

        # Check public routes if specified
        expected_public_routes = expected_middleware.get('public_routes', [])
        if expected_public_routes:
            solution_public_routes = solution_middleware.get('public_routes', [])

            # All expected routes should be present
            for route in expected_public_routes:
                if route not in solution_public_routes:
                    return False

        # Check ignored routes if specified
        expected_ignored_routes = expected_middleware.get('ignored_routes', [])
        if expected_ignored_routes:
            solution_ignored_routes = solution_middleware.get('ignored_routes', [])

            for route in expected_ignored_routes:
                if route not in solution_ignored_routes:
                    return False

        # Check matcher if specified
        if expected_middleware.get('has_matcher'):
            if not solution_middleware.get('has_matcher'):
                return False

        return True

    def _check_middleware_detailed(self, config_data: Dict) -> Dict:
        """Get detailed middleware check results.

        Args:
            config_data: Configuration ingredient data

        Returns:
            Dict with detailed results
        """
        expected_middleware = config_data.get('middleware')

        if not expected_middleware:
            return {
                'expected': None,
                'present': False,
                'correct': True,
            }

        solution_middleware = self.solution.extract_middleware_config()

        if not solution_middleware:
            return {
                'expected': expected_middleware,
                'present': False,
                'correct': False,
            }

        # Compare configurations
        type_match = (
            not expected_middleware.get('type') or
            solution_middleware.get('type') == expected_middleware.get('type')
        )

        expected_public = expected_middleware.get('public_routes', [])
        solution_public = solution_middleware.get('public_routes', [])
        missing_public = [r for r in expected_public if r not in solution_public]

        expected_ignored = expected_middleware.get('ignored_routes', [])
        solution_ignored = solution_middleware.get('ignored_routes', [])
        missing_ignored = [r for r in expected_ignored if r not in solution_ignored]

        matcher_match = (
            not expected_middleware.get('has_matcher') or
            solution_middleware.get('has_matcher')
        )

        return {
            'expected': expected_middleware,
            'actual': solution_middleware,
            'present': True,
            'type_match': type_match,
            'missing_public_routes': missing_public,
            'missing_ignored_routes': missing_ignored,
            'matcher_match': matcher_match,
            'correct': (
                type_match and
                len(missing_public) == 0 and
                len(missing_ignored) == 0 and
                matcher_match
            ),
        }

    def get_details(self) -> Dict:
        """Get detailed evaluation breakdown.

        Returns:
            Dict with detailed component results
        """
        config_data = self.ground_truth.get_configuration()

        if not config_data:
            return {"message": "No configuration expected for this task type"}

        result = self.evaluate()

        return {
            "env_vars": self._check_env_vars_detailed(config_data),
            "dependencies": self._check_dependencies_detailed(config_data),
            "middleware": self._check_middleware_detailed(config_data),
            "overall_score": result.score,
        }
