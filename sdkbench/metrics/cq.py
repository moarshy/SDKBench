"""CQ (Code Quality) metric evaluator.

Measures code quality through static analysis and best practices checks.
"""

import re
from typing import Dict, List, Set
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, CQResult
from sdkbench.parsers import TypeScriptParser


class CQEvaluator:
    """Evaluates code quality (CQ metric).

    CQ Score = 0-100 with deductions
    Starting at 100, deduct points for:
    - Missing error handling (-10 per occurrence)
    - Inconsistent naming (-5 per occurrence)
    - Missing TypeScript types (-5 per occurrence)
    - Code duplication (-10 per duplicate block)
    - Poor structure (-15 per major issue)
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth

    def evaluate(self) -> CQResult:
        """Evaluate code quality.

        Returns:
            CQResult with deductions and overall score
        """
        deductions = []

        # Check error handling
        error_handling_issues = self._check_error_handling()
        for issue in error_handling_issues:
            deductions.append({
                'category': 'error_handling',
                'points': 10,
                'description': issue,
            })

        # Check naming consistency
        naming_issues = self._check_naming_consistency()
        for issue in naming_issues:
            deductions.append({
                'category': 'naming',
                'points': 5,
                'description': issue,
            })

        # Check TypeScript types
        type_issues = self._check_typescript_types()
        for issue in type_issues:
            deductions.append({
                'category': 'types',
                'points': 5,
                'description': issue,
            })

        # Check code duplication
        duplication_issues = self._check_code_duplication()
        for issue in duplication_issues:
            deductions.append({
                'category': 'duplication',
                'points': 10,
                'description': issue,
            })

        # Check structure
        structure_issues = self._check_structure()
        for issue in structure_issues:
            deductions.append({
                'category': 'structure',
                'points': 15,
                'description': issue,
            })

        return CQResult(deductions=deductions)

    def _check_error_handling(self) -> List[str]:
        """Check for missing error handling.

        Returns:
            List of error handling issues
        """
        issues = []

        for file_path, content in self.solution.files.items():
            # Skip non-code files
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue

            # Check for async functions without try-catch
            if 'async' in content or 'await' in content:
                # Count try-catch blocks
                try_count = content.count('try {')
                catch_count = content.count('catch')

                # Count async functions
                async_func_count = len(re.findall(r'async\s+(?:function|\()', content))

                # If there are async functions but no error handling
                if async_func_count > 0 and try_count == 0:
                    issues.append(
                        f"{file_path}: Async code without try-catch blocks"
                    )

            # Check for fetch/API calls without error handling
            if 'fetch(' in content or 'axios.' in content:
                if 'catch' not in content and '.catch(' not in content:
                    issues.append(
                        f"{file_path}: API calls without error handling"
                    )

        return issues

    def _check_naming_consistency(self) -> List[str]:
        """Check for naming inconsistencies.

        Returns:
            List of naming issues
        """
        issues = []

        # Patterns to check
        patterns = {
            'camelCase': r'[a-z][a-zA-Z0-9]*',
            'PascalCase': r'[A-Z][a-zA-Z0-9]*',
            'snake_case': r'[a-z][a-z0-9_]*',
        }

        for file_path, content in self.solution.files.items():
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue

            # Check for mixed naming in variables
            # Extract variable declarations
            var_pattern = r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='
            variables = re.findall(var_pattern, content)

            camel_count = sum(1 for v in variables if re.fullmatch(patterns['camelCase'], v))
            snake_count = sum(1 for v in variables if re.fullmatch(patterns['snake_case'], v))

            # If both styles are used significantly
            if camel_count > 0 and snake_count > 0:
                issues.append(
                    f"{file_path}: Mixed naming styles (camelCase and snake_case)"
                )

        return issues

    def _check_typescript_types(self) -> List[str]:
        """Check for missing TypeScript types.

        Returns:
            List of type issues
        """
        issues = []

        for file_path, content in self.solution.files.items():
            # Only check TypeScript files
            if not file_path.endswith(('.ts', '.tsx')):
                continue

            # Check for 'any' type usage
            any_count = len(re.findall(r':\s*any\b', content))
            if any_count > 0:
                issues.append(
                    f"{file_path}: Uses 'any' type {any_count} time(s)"
                )

            # Check for untyped function parameters
            # Pattern: function name(param) or (param) =>
            untyped_params = re.findall(
                r'(?:function\s+\w+|const\s+\w+\s*=)\s*\(([^)]+)\)\s*(?:=>|{)',
                content
            )

            for params in untyped_params:
                # Check if parameters have types
                if ':' not in params and params.strip() and params.strip() != '':
                    issues.append(
                        f"{file_path}: Function with untyped parameters"
                    )
                    break  # Only report once per file

        return issues

    def _check_code_duplication(self) -> List[str]:
        """Check for code duplication.

        Returns:
            List of duplication issues
        """
        issues = []

        # Simple duplication check: look for repeated code blocks
        file_contents = []

        for file_path, content in self.solution.files.items():
            if file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                file_contents.append((file_path, content))

        # Check for duplicate imports
        all_imports = []
        for file_path, content in file_contents:
            imports = TypeScriptParser.extract_imports(content)
            all_imports.extend(imports)

        # Check if same imports are repeated across files
        import_statements = [imp['statement'] for imp in all_imports]
        import_counts = {}
        for stmt in import_statements:
            import_counts[stmt] = import_counts.get(stmt, 0) + 1

        duplicate_imports = {k: v for k, v in import_counts.items() if v > 3}
        if duplicate_imports:
            issues.append(
                f"Duplicate imports across multiple files: {len(duplicate_imports)} patterns"
            )

        # Check for repeated code patterns (simple heuristic)
        # Extract function bodies and look for similar patterns
        for i, (file1, content1) in enumerate(file_contents):
            for file2, content2 in file_contents[i+1:]:
                # Check for similar large blocks (> 100 chars)
                lines1 = [l.strip() for l in content1.split('\n') if len(l.strip()) > 20]
                lines2 = [l.strip() for l in content2.split('\n') if len(l.strip()) > 20]

                # Count matching lines
                matching_lines = len(set(lines1).intersection(set(lines2)))

                if matching_lines > 5:
                    issues.append(
                        f"Similar code blocks in {file1} and {file2}"
                    )
                    break  # Only report first occurrence

        return issues[:3]  # Limit to 3 duplication issues

    def _check_structure(self) -> List[str]:
        """Check for structural issues.

        Returns:
            List of structure issues
        """
        issues = []

        # Check file organization
        files = list(self.solution.files.keys())

        # Check if middleware is in correct location
        middleware_files = [f for f in files if 'middleware' in f.lower()]
        for mw_file in middleware_files:
            # Should be at root or in app directory for Next.js
            if not (mw_file == 'middleware.ts' or mw_file.startswith('app/') or mw_file.startswith('src/')):
                issues.append(
                    f"Middleware file in unusual location: {mw_file}"
                )

        # Check for overly long files (> 500 lines)
        for file_path, content in self.solution.files.items():
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue

            line_count = len(content.split('\n'))
            if line_count > 500:
                issues.append(
                    f"{file_path}: File too long ({line_count} lines)"
                )

        # Check for missing key files
        expected_structure = self.ground_truth.metadata.get('expected_structure', {})

        if expected_structure:
            required_files = expected_structure.get('required_files', [])
            for req_file in required_files:
                if not self.solution.has_file(req_file):
                    issues.append(
                        f"Missing expected file: {req_file}"
                    )

        return issues

    def get_details(self) -> Dict:
        """Get detailed evaluation breakdown.

        Returns:
            Dict with detailed results
        """
        result = self.evaluate()

        # Group deductions by category
        by_category = {}
        for deduction in result.deductions:
            category = deduction['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(deduction)

        # Calculate totals per category
        category_totals = {}
        for category, deductions in by_category.items():
            category_totals[category] = {
                'count': len(deductions),
                'total_points': sum(d['points'] for d in deductions),
                'issues': [d['description'] for d in deductions],
            }

        return {
            "overall_score": result.score,
            "total_deductions": result.total_deductions,
            "deduction_count": len(result.deductions),
            "by_category": category_totals,
            "all_deductions": result.deductions,
        }

    def get_quality_summary(self) -> Dict:
        """Get high-level quality summary.

        Returns:
            Dict with quality summary
        """
        result = self.evaluate()

        # Categorize score
        if result.score >= 90:
            grade = "A"
            quality = "Excellent"
        elif result.score >= 80:
            grade = "B"
            quality = "Good"
        elif result.score >= 70:
            grade = "C"
            quality = "Fair"
        elif result.score >= 60:
            grade = "D"
            quality = "Poor"
        else:
            grade = "F"
            quality = "Very Poor"

        # Get top issues
        by_category = {}
        for deduction in result.deductions:
            category = deduction['category']
            by_category[category] = by_category.get(category, 0) + deduction['points']

        top_issues = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "score": result.score,
            "grade": grade,
            "quality": quality,
            "total_issues": len(result.deductions),
            "top_issue_categories": [cat for cat, _ in top_issues],
            "recommendations": self._get_recommendations(result.deductions),
        }

    def _get_recommendations(self, deductions: List[Dict]) -> List[str]:
        """Get recommendations based on deductions.

        Args:
            deductions: List of deductions

        Returns:
            List of recommendations
        """
        recommendations = []

        # Count by category
        categories = [d['category'] for d in deductions]

        if 'error_handling' in categories:
            recommendations.append(
                "Add try-catch blocks around async code and API calls"
            )

        if 'types' in categories:
            recommendations.append(
                "Add proper TypeScript types to function parameters and avoid 'any'"
            )

        if 'naming' in categories:
            recommendations.append(
                "Use consistent naming conventions (camelCase for variables/functions)"
            )

        if 'duplication' in categories:
            recommendations.append(
                "Extract common code into reusable functions or utilities"
            )

        if 'structure' in categories:
            recommendations.append(
                "Organize files according to framework conventions"
            )

        return recommendations[:3]  # Top 3 recommendations
