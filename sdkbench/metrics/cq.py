"""CQ (Code Quality) metric evaluator.

Measures code quality through static analysis and best practices checks.
"""

import re
from typing import Dict, List, Set
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, CQResult
from sdkbench.parsers import TypeScriptParser, PythonParser


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
            is_python = file_path.endswith('.py')
            is_typescript = file_path.endswith(('.ts', '.tsx', '.js', '.jsx'))

            # Skip non-code files
            if not is_python and not is_typescript:
                continue

            if is_python:
                # Python error handling checks
                # Check for async functions without try-except
                if 'async def' in content or 'await' in content:
                    try_count = content.count('try:')
                    except_count = content.count('except')

                    async_func_count = len(re.findall(r'async\s+def\s+', content))

                    if async_func_count > 0 and try_count == 0:
                        issues.append(
                            f"{file_path}: Async code without try-except blocks"
                        )

                # Check for API/DB operations without error handling
                dangerous_patterns = ['requests.', 'httpx.', '.connect(', 'open(']
                has_dangerous = any(p in content for p in dangerous_patterns)
                if has_dangerous and 'except' not in content:
                    issues.append(
                        f"{file_path}: I/O operations without error handling"
                    )

            else:
                # TypeScript/JavaScript error handling checks
                if 'async' in content or 'await' in content:
                    try_count = content.count('try {')
                    catch_count = content.count('catch')

                    async_func_count = len(re.findall(r'async\s+(?:function|\()', content))

                    if async_func_count > 0 and try_count == 0:
                        issues.append(
                            f"{file_path}: Async code without try-catch blocks"
                        )

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
            is_python = file_path.endswith('.py')
            is_typescript = file_path.endswith(('.ts', '.tsx', '.js', '.jsx'))

            if not is_python and not is_typescript:
                continue

            if is_python:
                # Python naming: should use snake_case for functions/variables, PascalCase for classes
                # Extract function names
                func_names = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content)

                # Check for camelCase in function names (should be snake_case)
                camel_funcs = [f for f in func_names if re.match(r'^[a-z]+[A-Z]', f)]
                if camel_funcs:
                    issues.append(
                        f"{file_path}: Functions using camelCase instead of snake_case: {', '.join(camel_funcs[:3])}"
                    )

                # Check class names are PascalCase
                class_names = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                bad_classes = [c for c in class_names if c[0].islower()]
                if bad_classes:
                    issues.append(
                        f"{file_path}: Class names should be PascalCase: {', '.join(bad_classes[:3])}"
                    )

            else:
                # TypeScript/JavaScript naming checks
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
        """Check for missing TypeScript types or Python type hints.

        Returns:
            List of type issues
        """
        issues = []

        for file_path, content in self.solution.files.items():
            is_python = file_path.endswith('.py')
            is_typescript = file_path.endswith(('.ts', '.tsx'))

            if is_python:
                # Python type hint checks
                functions = PythonParser.extract_function_definitions(content)

                # Check for functions without type hints (optional - don't penalize too much)
                # Only flag if there are some typed and some untyped (inconsistency)
                typed_funcs = [f for f in functions if f.get('return_type') or ':' in f.get('args', '')]
                untyped_funcs = [f for f in functions if not f.get('return_type') and ':' not in f.get('args', '')]

                if typed_funcs and untyped_funcs and len(untyped_funcs) > len(typed_funcs):
                    issues.append(
                        f"{file_path}: Inconsistent type hints - some functions typed, others not"
                    )

            elif is_typescript:
                # TypeScript type checks
                any_count = len(re.findall(r':\s*any\b', content))
                if any_count > 0:
                    issues.append(
                        f"{file_path}: Uses 'any' type {any_count} time(s)"
                    )

                # Check for untyped function parameters
                untyped_params = re.findall(
                    r'(?:function\s+\w+|const\s+\w+\s*=)\s*\(([^)]+)\)\s*(?:=>|{)',
                    content
                )

                for params in untyped_params:
                    if ':' not in params and params.strip() and params.strip() != '':
                        issues.append(
                            f"{file_path}: Function with untyped parameters"
                        )
                        break

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
            if file_path.endswith(('.ts', '.tsx', '.js', '.jsx', '.py')):
                file_contents.append((file_path, content))

        # Check for duplicate imports
        all_imports = []
        for file_path, content in file_contents:
            if file_path.endswith('.py'):
                imports = PythonParser.extract_imports(content)
            else:
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
                    break

        return issues[:3]

    def _check_structure(self) -> List[str]:
        """Check for structural issues.

        Returns:
            List of structure issues
        """
        issues = []

        # Check file organization
        files = list(self.solution.files.keys())

        # Check if middleware is in correct location (TypeScript/Next.js)
        middleware_files = [f for f in files if 'middleware' in f.lower() and f.endswith(('.ts', '.js'))]
        for mw_file in middleware_files:
            # Should be at root or in app directory for Next.js
            if not (mw_file == 'middleware.ts' or mw_file.startswith('app/') or mw_file.startswith('src/')):
                issues.append(
                    f"Middleware file in unusual location: {mw_file}"
                )

        # Check for overly long files (> 500 lines)
        for file_path, content in self.solution.files.items():
            is_code = file_path.endswith(('.ts', '.tsx', '.js', '.jsx', '.py'))
            if not is_code:
                continue

            line_count = len(content.split('\n'))
            if line_count > 500:
                issues.append(
                    f"{file_path}: File too long ({line_count} lines)"
                )

        # Python-specific structure checks
        python_files = [f for f in files if f.endswith('.py')]
        if python_files:
            # Check for __init__.py in package directories
            dirs_with_py = set()
            for f in python_files:
                if '/' in f:
                    dirs_with_py.add(f.rsplit('/', 1)[0])

            for dir_path in dirs_with_py:
                init_path = f"{dir_path}/__init__.py"
                # Only flag if it looks like a package (multiple .py files)
                py_in_dir = [f for f in python_files if f.startswith(dir_path)]
                if len(py_in_dir) > 1 and init_path not in python_files:
                    # This is minor - don't add as issue
                    pass

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
