"""C-COMP (Configuration Completeness) metric evaluator.

Measures completeness of SDK configuration in the solution.
"""

from typing import Dict, List, Optional
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, CCompResult
from sdkbench.parsers import EnvParser, ConfigParser


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

        # Get package.json from solution
        package_json_path = self.solution.solution_dir / 'package.json'

        if not package_json_path.exists():
            return False

        package_json = ConfigParser.parse_package_json(package_json_path)

        if not package_json:
            return False

        # Extract dependencies
        solution_deps = ConfigParser.extract_dependencies(package_json)

        # Check each expected dependency
        for dep_name, dep_version in expected_deps.items():
            if dep_name not in solution_deps:
                return False

            # Optionally check version compatibility
            if dep_version:
                actual_version = solution_deps[dep_name]
                if not self._check_version_compatible(actual_version, dep_version):
                    return False

        return True

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
