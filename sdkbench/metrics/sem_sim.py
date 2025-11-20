"""SEM-SIM (Semantic Similarity) metric evaluator.

Measures if the solution semantically matches the expected approach.
"""

import re
from typing import Dict, List, Set, Optional
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, SemSimResult
from sdkbench.parsers import TypeScriptParser


class SemSimEvaluator:
    """Evaluates semantic similarity (SEM-SIM metric).

    SEM-SIM Score = 0-100%
    Components (weighted):
    - Code structure similarity (30%): Similar file organization
    - Pattern matching (40%): Uses expected SDK patterns
    - Approach alignment (30%): Follows expected implementation approach
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth

    def evaluate(self) -> SemSimResult:
        """Evaluate semantic similarity.

        Returns:
            SemSimResult with component scores and overall score
        """
        # Evaluate each component
        structure_score = self._check_structure_similarity()
        pattern_score = self._check_pattern_matching()
        approach_score = self._check_approach_alignment()

        return SemSimResult(
            structure_similarity=structure_score,
            pattern_matching=pattern_score,
            approach_alignment=approach_score,
        )

    def _check_structure_similarity(self) -> float:
        """Check code structure similarity.

        Returns:
            Score 0-1 for structure similarity
        """
        expected_structure = self.ground_truth.metadata.get('expected_structure', {})

        if not expected_structure:
            return 1.0

        # Check file organization
        expected_files = set(expected_structure.get('files', []))
        solution_files = set(self.solution.files.keys())

        if not expected_files:
            return 1.0

        # Calculate Jaccard similarity
        intersection = len(expected_files.intersection(solution_files))
        union = len(expected_files.union(solution_files))

        file_similarity = intersection / union if union > 0 else 0.0

        # Check directory structure
        expected_dirs = set(expected_structure.get('directories', []))
        solution_dirs = set()

        for file_path in solution_files:
            parts = Path(file_path).parts
            if len(parts) > 1:
                # Add all parent directories
                for i in range(1, len(parts)):
                    solution_dirs.add('/'.join(parts[:i]))

        dir_similarity = 1.0
        if expected_dirs:
            dir_intersection = len(expected_dirs.intersection(solution_dirs))
            dir_union = len(expected_dirs.union(solution_dirs))
            dir_similarity = dir_intersection / dir_union if dir_union > 0 else 0.0

        # Combine scores
        structure_score = (file_similarity * 0.7) + (dir_similarity * 0.3)

        return structure_score

    def _check_pattern_matching(self) -> float:
        """Check pattern matching against expected patterns.

        Returns:
            Score 0-1 for pattern matching
        """
        # Get expected patterns from ground truth
        initialization = self.ground_truth.get_initialization()
        configuration = self.ground_truth.get_configuration()
        integration_points = self.ground_truth.get_integration_points()

        scores = []

        # Check initialization patterns
        if initialization:
            init_score = self._check_initialization_patterns(initialization)
            scores.append(init_score)

        # Check configuration patterns
        if configuration:
            config_score = self._check_configuration_patterns(configuration)
            scores.append(config_score)

        # Check integration patterns
        if integration_points:
            integration_score = self._check_integration_patterns(integration_points)
            scores.append(integration_score)

        # Average all pattern scores
        return sum(scores) / len(scores) if scores else 1.0

    def _check_initialization_patterns(self, initialization: Dict) -> float:
        """Check initialization pattern matching.

        Args:
            initialization: Initialization data

        Returns:
            Score 0-1
        """
        pattern = initialization.get('pattern', {})
        file_path = initialization.get('file')

        if not pattern or not file_path:
            return 1.0

        file_content = self.solution.files.get(file_path)
        if not file_content:
            return 0.0

        pattern_type = pattern.get('type')
        pattern_name = pattern.get('name')

        if pattern_type == 'jsx_component':
            component = TypeScriptParser.extract_jsx_component_usage(
                file_content, pattern_name
            )
            return 1.0 if component else 0.0

        elif pattern_type == 'function_call':
            calls = TypeScriptParser.extract_function_calls(file_content, pattern_name)
            return 1.0 if calls else 0.0

        elif pattern_type == 'export':
            exported = TypeScriptParser.extract_exported_function(file_content, pattern_name)
            return 1.0 if exported else 0.0

        return 0.5  # Unknown pattern type

    def _check_configuration_patterns(self, configuration: Dict) -> float:
        """Check configuration pattern matching.

        Args:
            configuration: Configuration data

        Returns:
            Score 0-1
        """
        scores = []

        # Check env vars
        expected_env = configuration.get('env_vars', [])
        if expected_env:
            solution_env = self.solution.extract_env_vars()
            expected_count = len(expected_env)
            present_count = sum(
                1 for var in expected_env
                for var_name in ([var] if isinstance(var, str) else [var.get('name')])
                if var_name in solution_env
            )
            env_score = present_count / expected_count if expected_count > 0 else 1.0
            scores.append(env_score)

        # Check middleware
        expected_middleware = configuration.get('middleware')
        if expected_middleware:
            solution_middleware = self.solution.extract_middleware_config()

            if solution_middleware:
                # Check type match
                type_match = (
                    not expected_middleware.get('type') or
                    solution_middleware.get('type') == expected_middleware.get('type')
                )
                scores.append(1.0 if type_match else 0.5)
            else:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 1.0

    def _check_integration_patterns(self, integration_points: List[str]) -> float:
        """Check integration pattern matching.

        Args:
            integration_points: Expected integration point files

        Returns:
            Score 0-1
        """
        if not integration_points:
            return 1.0

        solution_points = self.solution.extract_integration_points()

        # Normalize paths
        expected_normalized = set(self._normalize_path(p) for p in integration_points)
        solution_normalized = set(self._normalize_path(p) for p in solution_points)

        # Calculate overlap
        intersection = len(expected_normalized.intersection(solution_normalized))
        union = len(expected_normalized.union(solution_normalized))

        return intersection / union if union > 0 else 0.0

    def _check_approach_alignment(self) -> float:
        """Check if solution follows expected implementation approach.

        Returns:
            Score 0-1 for approach alignment
        """
        scores = []

        # Check if using server vs client components correctly
        server_client_score = self._check_server_client_usage()
        scores.append(server_client_score)

        # Check if using correct Clerk patterns (v4 vs v5)
        version_score = self._check_version_patterns()
        scores.append(version_score)

        # Check if following Next.js conventions
        conventions_score = self._check_framework_conventions()
        scores.append(conventions_score)

        return sum(scores) / len(scores) if scores else 1.0

    def _check_server_client_usage(self) -> float:
        """Check correct usage of server vs client components.

        Returns:
            Score 0-1
        """
        # Count 'use client' and 'use server' directives
        client_files = []
        server_files = []

        for file_path, content in self.solution.files.items():
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue

            if TypeScriptParser.has_client_directive(content):
                client_files.append(file_path)

            if TypeScriptParser.has_server_directive(content):
                server_files.append(file_path)

        # Check if hooks are in client components
        for file_path in client_files:
            content = self.solution.files[file_path]

            # These should be in client components
            has_hooks = (
                'useUser()' in content or
                'useAuth()' in content or
                'useClerk()' in content
            )

            if has_hooks:
                return 1.0  # Correct usage

        # Check if server actions use 'use server'
        for file_path in server_files:
            content = self.solution.files[file_path]

            # Check for auth() usage (server-side)
            if 'auth()' in content:
                return 1.0  # Correct usage

        # If no directives found, assume default behavior (0.5)
        return 0.5

    def _check_version_patterns(self) -> float:
        """Check if using correct Clerk version patterns.

        Returns:
            Score 0-1
        """
        # Check package.json for Clerk version
        package_json_path = self.solution.solution_dir / 'package.json'

        if not package_json_path.exists():
            return 0.5

        import json
        try:
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
        except:
            return 0.5

        deps = package_json.get('dependencies', {})
        clerk_pkg = deps.get('@clerk/nextjs', '')

        # Determine version
        is_v5 = '5.' in clerk_pkg or '^5' in clerk_pkg

        # Check for v5 patterns
        v5_patterns = ['clerkMiddleware', 'auth()']
        v4_patterns = ['authMiddleware', 'getAuth(']

        pattern_count = 0
        total_files = 0

        for file_path, content in self.solution.files.items():
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue

            total_files += 1

            if is_v5:
                # Should use v5 patterns
                if any(p in content for p in v5_patterns):
                    pattern_count += 1
            else:
                # Should use v4 patterns
                if any(p in content for p in v4_patterns):
                    pattern_count += 1

        return pattern_count / total_files if total_files > 0 else 0.5

    def _check_framework_conventions(self) -> float:
        """Check if following framework conventions.

        Returns:
            Score 0-1
        """
        scores = []

        # Check if middleware is at root
        has_middleware = any(
            'middleware' in file_path for file_path in self.solution.files.keys()
        )

        if has_middleware:
            middleware_at_root = (
                'middleware.ts' in self.solution.files or
                'middleware.js' in self.solution.files
            )
            scores.append(1.0 if middleware_at_root else 0.5)

        # Check if layout is in app directory
        has_layout = any('layout' in file_path for file_path in self.solution.files.keys())

        if has_layout:
            layout_in_app = any(
                file_path.startswith('app/') and 'layout' in file_path
                for file_path in self.solution.files.keys()
            )
            scores.append(1.0 if layout_in_app else 0.5)

        # Check if using TypeScript consistently
        ts_files = [f for f in self.solution.files.keys() if f.endswith(('.ts', '.tsx'))]
        js_files = [f for f in self.solution.files.keys() if f.endswith(('.js', '.jsx'))]

        if ts_files and not js_files:
            scores.append(1.0)  # Consistent TypeScript
        elif js_files and not ts_files:
            scores.append(1.0)  # Consistent JavaScript
        else:
            scores.append(0.7)  # Mixed

        return sum(scores) / len(scores) if scores else 1.0

    def _normalize_path(self, path: str) -> str:
        """Normalize file path.

        Args:
            path: File path

        Returns:
            Normalized path
        """
        # Remove leading ./ or /
        path = path.lstrip('./')
        path = path.lstrip('/')

        # Convert backslashes
        path = path.replace('\\', '/')

        return path

    def get_details(self) -> Dict:
        """Get detailed evaluation breakdown.

        Returns:
            Dict with detailed component results
        """
        result = self.evaluate()

        return {
            "overall_score": result.score,
            "structure_similarity": result.structure_similarity,
            "pattern_matching": result.pattern_matching,
            "approach_alignment": result.approach_alignment,
            "breakdown": {
                "structure": {
                    "score": result.structure_similarity,
                    "weight": 0.30,
                    "contribution": result.structure_similarity * 0.30,
                },
                "patterns": {
                    "score": result.pattern_matching,
                    "weight": 0.40,
                    "contribution": result.pattern_matching * 0.40,
                },
                "approach": {
                    "score": result.approach_alignment,
                    "weight": 0.30,
                    "contribution": result.approach_alignment * 0.30,
                },
            },
        }

    def get_similarity_summary(self) -> Dict:
        """Get high-level similarity summary.

        Returns:
            Dict with similarity summary
        """
        result = self.evaluate()

        # Categorize similarity
        if result.score >= 0.90:
            similarity = "Very High"
            description = "Solution closely matches expected approach"
        elif result.score >= 0.75:
            similarity = "High"
            description = "Solution generally follows expected approach"
        elif result.score >= 0.60:
            similarity = "Moderate"
            description = "Solution partially follows expected approach"
        elif result.score >= 0.40:
            similarity = "Low"
            description = "Solution differs from expected approach"
        else:
            similarity = "Very Low"
            description = "Solution significantly differs from expected approach"

        return {
            "score": result.score,
            "similarity": similarity,
            "description": description,
            "strongest_component": max(
                [
                    ("structure", result.structure_similarity),
                    ("patterns", result.pattern_matching),
                    ("approach", result.approach_alignment),
                ],
                key=lambda x: x[1],
            )[0],
            "weakest_component": min(
                [
                    ("structure", result.structure_similarity),
                    ("patterns", result.pattern_matching),
                    ("approach", result.approach_alignment),
                ],
                key=lambda x: x[1],
            )[0],
        }
