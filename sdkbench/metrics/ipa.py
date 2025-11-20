"""IPA (Integration Point Accuracy) metric evaluator.

Measures how accurately SDK integration points are identified.
"""

from typing import Dict, List, Set, Optional
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, IPAResult
from sdkbench.parsers import TypeScriptParser


class IPAEvaluator:
    """Evaluates integration point accuracy (IPA metric).

    IPA Score = Precision, Recall, F1
    An "integration point" is any file where SDK functionality is used.

    Metrics:
    - Precision: % of solution's integration points that are correct
    - Recall: % of expected integration points that were found
    - F1: Harmonic mean of precision and recall
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth

    def evaluate(self) -> IPAResult:
        """Evaluate integration point accuracy.

        Returns:
            IPAResult with precision, recall, and F1 scores
        """
        # Get expected integration points from ground truth
        expected_points = self.ground_truth.get_integration_points()

        if not expected_points:
            # No integration points expected
            return IPAResult(
                precision=1.0,
                recall=1.0,
                f1_score=1.0,
                true_positives=0,
                false_positives=0,
                false_negatives=0,
            )

        # Extract integration points from solution
        solution_points = self.solution.extract_integration_points()

        # Convert to sets of file paths for comparison
        expected_files = set(self._normalize_paths(expected_points))
        solution_files = set(self._normalize_paths(solution_points))

        # Calculate metrics
        true_positives = len(expected_files.intersection(solution_files))
        false_positives = len(solution_files - expected_files)
        false_negatives = len(expected_files - solution_files)

        # Calculate precision and recall
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0.0
        )

        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0.0
        )

        # Calculate F1 score
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return IPAResult(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
        )

    def _normalize_paths(self, paths: List[str]) -> List[str]:
        """Normalize file paths for comparison.

        Args:
            paths: List of file paths

        Returns:
            List of normalized paths
        """
        normalized = []

        for path in paths:
            # Remove leading ./ or /
            path = path.lstrip('./')
            path = path.lstrip('/')

            # Convert backslashes to forward slashes
            path = path.replace('\\', '/')

            normalized.append(path)

        return normalized

    def get_details(self) -> Dict:
        """Get detailed evaluation breakdown.

        Returns:
            Dict with detailed results
        """
        expected_points = self.ground_truth.get_integration_points()
        solution_points = self.solution.extract_integration_points()

        expected_files = set(self._normalize_paths(expected_points))
        solution_files = set(self._normalize_paths(solution_points))

        true_positives = expected_files.intersection(solution_files)
        false_positives = solution_files - expected_files
        false_negatives = expected_files - solution_files

        result = self.evaluate()

        return {
            "expected_count": len(expected_files),
            "solution_count": len(solution_files),
            "true_positives": {
                "count": len(true_positives),
                "files": sorted(list(true_positives)),
            },
            "false_positives": {
                "count": len(false_positives),
                "files": sorted(list(false_positives)),
                "description": "Files with SDK usage in solution but not expected",
            },
            "false_negatives": {
                "count": len(false_negatives),
                "files": sorted(list(false_negatives)),
                "description": "Expected files with SDK usage that are missing",
            },
            "precision": result.precision,
            "recall": result.recall,
            "f1_score": result.f1_score,
        }

    def analyze_integration_patterns(self) -> Dict:
        """Analyze what types of integration patterns are used.

        Returns:
            Dict with pattern analysis
        """
        solution_points = self.solution.extract_integration_points()

        pattern_counts = {
            'auth_helper': 0,
            'current_user': 0,
            'use_user_hook': 0,
            'use_auth_hook': 0,
            'use_clerk_hook': 0,
            'clerk_provider': 0,
            'middleware': 0,
        }

        file_patterns = {}

        for file_path in solution_points:
            file_content = self.solution.files.get(file_path)

            if not file_content:
                continue

            # Count patterns in this file
            patterns_in_file = []

            # Check for auth()
            if TypeScriptParser.extract_function_calls(file_content, 'auth'):
                pattern_counts['auth_helper'] += 1
                patterns_in_file.append('auth()')

            # Check for currentUser()
            if 'currentUser()' in file_content:
                pattern_counts['current_user'] += 1
                patterns_in_file.append('currentUser()')

            # Check for useUser()
            if TypeScriptParser.extract_hook_usage(file_content, 'useUser'):
                pattern_counts['use_user_hook'] += 1
                patterns_in_file.append('useUser()')

            # Check for useAuth()
            if TypeScriptParser.extract_hook_usage(file_content, 'useAuth'):
                pattern_counts['use_auth_hook'] += 1
                patterns_in_file.append('useAuth()')

            # Check for useClerk()
            if TypeScriptParser.extract_hook_usage(file_content, 'useClerk'):
                pattern_counts['use_clerk_hook'] += 1
                patterns_in_file.append('useClerk()')

            # Check for ClerkProvider
            if TypeScriptParser.extract_jsx_component_usage(file_content, 'ClerkProvider'):
                pattern_counts['clerk_provider'] += 1
                patterns_in_file.append('ClerkProvider')

            # Check for middleware
            if 'authMiddleware' in file_content or 'clerkMiddleware' in file_content:
                pattern_counts['middleware'] += 1
                patterns_in_file.append('middleware')

            file_patterns[file_path] = patterns_in_file

        return {
            'pattern_counts': pattern_counts,
            'file_patterns': file_patterns,
            'total_patterns': sum(pattern_counts.values()),
        }

    def check_integration_quality(self) -> Dict:
        """Check quality of integration implementations.

        Returns:
            Dict with quality metrics
        """
        solution_points = self.solution.extract_integration_points()

        quality_issues = {
            'missing_error_handling': [],
            'missing_loading_states': [],
            'missing_null_checks': [],
            'unused_imports': [],
        }

        for file_path in solution_points:
            file_content = self.solution.files.get(file_path)

            if not file_content:
                continue

            # Check for error handling
            if 'try' not in file_content and 'catch' not in file_content:
                # Only flag if there's async code
                if 'async' in file_content or 'await' in file_content:
                    quality_issues['missing_error_handling'].append(file_path)

            # Check for loading states in hooks
            if 'useUser()' in file_content or 'useAuth()' in file_content:
                if 'isLoaded' not in file_content and 'loading' not in file_content:
                    quality_issues['missing_loading_states'].append(file_path)

            # Check for null checks on user/auth
            if 'userId' in file_content or 'user' in file_content:
                if '!userId' not in file_content and '!user' not in file_content:
                    # This is a weak check, but gives a signal
                    pass

        return {
            'quality_issues': quality_issues,
            'total_issues': sum(len(v) for v in quality_issues.values()),
        }

    def compare_with_expected_patterns(self) -> Dict:
        """Compare solution patterns with expected patterns.

        Returns:
            Dict with comparison results
        """
        expected_points = self.ground_truth.get_integration_points()
        expected_details = self.ground_truth.metadata.get('ingredients', {}).get(
            'integration_points', []
        )

        comparison = []

        for expected_point in expected_details:
            file_path = expected_point.get('file')
            expected_pattern = expected_point.get('pattern')

            if not file_path or not expected_pattern:
                continue

            # Check if file exists in solution
            file_content = self.solution.files.get(file_path)

            result = {
                'file': file_path,
                'expected_pattern': expected_pattern,
                'file_exists': file_content is not None,
                'pattern_found': False,
                'pattern_details': None,
            }

            if file_content:
                # Check for specific pattern
                pattern_type = expected_pattern.get('type')
                pattern_name = expected_pattern.get('name')

                if pattern_type == 'function_call':
                    calls = TypeScriptParser.extract_function_calls(file_content, pattern_name)
                    result['pattern_found'] = len(calls) > 0
                    result['pattern_details'] = calls

                elif pattern_type == 'hook_usage':
                    hook = TypeScriptParser.extract_hook_usage(file_content, pattern_name)
                    result['pattern_found'] = hook is not None
                    result['pattern_details'] = hook

                elif pattern_type == 'jsx_component':
                    component = TypeScriptParser.extract_jsx_component_usage(
                        file_content, pattern_name
                    )
                    result['pattern_found'] = component is not None
                    result['pattern_details'] = component

            comparison.append(result)

        return {
            'comparisons': comparison,
            'total_expected': len(comparison),
            'patterns_found': sum(1 for c in comparison if c['pattern_found']),
            'files_missing': sum(1 for c in comparison if not c['file_exists']),
        }
