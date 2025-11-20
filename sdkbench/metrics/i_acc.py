"""I-ACC (Initialization Correctness) metric evaluator.

Measures whether the SDK was initialized correctly in the solution.
"""

from typing import Dict, List, Optional
from pathlib import Path

from sdkbench.core import Solution, GroundTruth, IAccResult
from sdkbench.parsers import TypeScriptParser


class IAccEvaluator:
    """Evaluates initialization correctness (I-ACC metric).

    I-ACC Score = 0-100%
    Components (weighted):
    - File location (20%): Is initialization in the correct file?
    - Imports (20%): Are all required imports present?
    - Pattern (30%): Is the correct initialization pattern used?
    - Placement (30%): Is it placed correctly in the component hierarchy?
    """

    def __init__(self, solution: Solution, ground_truth: GroundTruth):
        """Initialize evaluator.

        Args:
            solution: Solution to evaluate
            ground_truth: Expected patterns
        """
        self.solution = solution
        self.ground_truth = ground_truth
        self.targets = ground_truth.get_i_acc_targets()

    def evaluate(self) -> IAccResult:
        """Evaluate initialization correctness.

        Returns:
            IAccResult with component scores and overall score
        """
        # Get initialization data from ground truth
        init_data = self.ground_truth.get_initialization()

        if not init_data:
            # No initialization expected for this task type
            return IAccResult(
                file_location_correct=True,
                imports_correct=True,
                pattern_correct=True,
                placement_correct=True,
            )

        # Evaluate each component
        file_location = self._check_file_location(init_data)
        imports = self._check_imports(init_data)
        pattern = self._check_pattern(init_data)
        placement = self._check_placement(init_data)

        return IAccResult(
            file_location_correct=file_location,
            imports_correct=imports,
            pattern_correct=pattern,
            placement_correct=placement,
        )

    def _check_file_location(self, init_data: Dict) -> bool:
        """Check if initialization is in the correct file.

        Args:
            init_data: Initialization ingredient data

        Returns:
            True if file exists and is correct location
        """
        expected_file = init_data.get('file')

        if not expected_file:
            return True

        # Check if file exists in solution
        return self.solution.has_file(expected_file)

    def _check_imports(self, init_data: Dict) -> bool:
        """Check if all required imports are present.

        Args:
            init_data: Initialization ingredient data

        Returns:
            True if all required imports present
        """
        expected_imports = init_data.get('imports', [])
        expected_file = init_data.get('file')

        if not expected_imports or not expected_file:
            return True

        # Get file content
        file_content = self.solution.files.get(expected_file)
        if not file_content:
            return False

        # Extract actual imports
        actual_imports = TypeScriptParser.extract_imports(file_content)

        # Check each expected import
        for expected in expected_imports:
            found = False

            # Parse expected import
            exp_source = expected.get('source')
            exp_names = expected.get('names', [])

            # Look for matching import in actual imports
            for actual in actual_imports:
                if actual['source'] == exp_source:
                    # Check if all expected names are present
                    actual_names = actual['names']

                    if all(name in actual_names for name in exp_names):
                        found = True
                        break

            if not found:
                return False

        return True

    def _check_pattern(self, init_data: Dict) -> bool:
        """Check if the correct initialization pattern is used.

        Args:
            init_data: Initialization ingredient data

        Returns:
            True if correct pattern used
        """
        pattern_data = init_data.get('pattern')
        expected_file = init_data.get('file')

        if not pattern_data or not expected_file:
            return True

        # Get file content
        file_content = self.solution.files.get(expected_file)
        if not file_content:
            return False

        # Check pattern based on type
        pattern_type = pattern_data.get('type')

        if pattern_type == 'jsx_component':
            return self._check_jsx_component_pattern(file_content, pattern_data)
        elif pattern_type == 'function_call':
            return self._check_function_call_pattern(file_content, pattern_data)
        elif pattern_type == 'export':
            return self._check_export_pattern(file_content, pattern_data)
        else:
            return False

    def _check_jsx_component_pattern(self, content: str, pattern_data: Dict) -> bool:
        """Check JSX component pattern (e.g., <ClerkProvider>).

        Args:
            content: File content
            pattern_data: Pattern specification

        Returns:
            True if pattern found
        """
        component_name = pattern_data.get('name')
        required_props = pattern_data.get('required_props', [])

        if not component_name:
            return False

        # Extract component usage
        component = TypeScriptParser.extract_jsx_component_usage(content, component_name)

        if not component:
            return False

        # Check required props if specified
        if required_props:
            component_props = component.get('props', {})
            for prop in required_props:
                if prop not in component_props:
                    return False

        return True

    def _check_function_call_pattern(self, content: str, pattern_data: Dict) -> bool:
        """Check function call pattern (e.g., auth()).

        Args:
            content: File content
            pattern_data: Pattern specification

        Returns:
            True if pattern found
        """
        function_name = pattern_data.get('name')

        if not function_name:
            return False

        # Extract function calls
        calls = TypeScriptParser.extract_function_calls(content, function_name)

        return len(calls) > 0

    def _check_export_pattern(self, content: str, pattern_data: Dict) -> bool:
        """Check export pattern (e.g., export default clerkMiddleware()).

        Args:
            content: File content
            pattern_data: Pattern specification

        Returns:
            True if pattern found
        """
        function_name = pattern_data.get('name')

        if not function_name:
            return False

        # Check for export
        exported_func = TypeScriptParser.extract_exported_function(content, function_name)

        if not exported_func:
            # Also check for default export with function call
            # e.g., export default clerkMiddleware()
            pattern = f"export default {function_name}"
            return pattern in content

        return True

    def _check_placement(self, init_data: Dict) -> bool:
        """Check if initialization is placed correctly.

        Args:
            init_data: Initialization ingredient data

        Returns:
            True if placement correct
        """
        placement_data = init_data.get('placement')
        expected_file = init_data.get('file')

        if not placement_data or not expected_file:
            return True

        # Get file content
        file_content = self.solution.files.get(expected_file)
        if not file_content:
            return False

        # Check placement based on type
        placement_type = placement_data.get('type')

        if placement_type == 'wraps_children':
            return self._check_wraps_children(file_content, placement_data)
        elif placement_type == 'top_level':
            return self._check_top_level(file_content, placement_data)
        elif placement_type == 'in_function':
            return self._check_in_function(file_content, placement_data)
        else:
            return False

    def _check_wraps_children(self, content: str, placement_data: Dict) -> bool:
        """Check if component wraps children correctly.

        Args:
            content: File content
            placement_data: Placement specification

        Returns:
            True if wraps children
        """
        component_name = placement_data.get('component')

        if not component_name:
            return False

        # Extract component
        component = TypeScriptParser.extract_jsx_component_usage(content, component_name)

        if not component:
            return False

        # Check if it's self-closing (shouldn't be if it wraps children)
        if component.get('is_self_closing'):
            return False

        # Check for {children} inside the component
        # Find the component in content
        start_tag = f"<{component_name}"
        end_tag = f"</{component_name}>"

        if start_tag not in content or end_tag not in content:
            return False

        # Extract content between tags
        start_idx = content.find(start_tag)
        end_idx = content.find(end_tag, start_idx)

        if start_idx == -1 or end_idx == -1:
            return False

        between_tags = content[start_idx:end_idx]

        # Check if {children} is present
        return '{children}' in between_tags

    def _check_top_level(self, content: str, placement_data: Dict) -> bool:
        """Check if pattern is at top level of file.

        Args:
            content: File content
            placement_data: Placement specification

        Returns:
            True if at top level
        """
        # For now, just check if the pattern exists
        # More sophisticated checks could verify indentation level
        pattern_name = placement_data.get('pattern')

        if not pattern_name:
            return True

        return pattern_name in content

    def _check_in_function(self, content: str, placement_data: Dict) -> bool:
        """Check if pattern is inside a function.

        Args:
            content: File content
            placement_data: Placement specification

        Returns:
            True if in function
        """
        function_name = placement_data.get('function')
        pattern_name = placement_data.get('pattern')

        if not function_name or not pattern_name:
            return False

        # Find the function in content
        func_pattern = rf"(?:export\s+)?(?:async\s+)?function\s+{function_name}\s*\([^)]*\)\s*{{([^}}]*)}}"

        import re
        match = re.search(func_pattern, content, re.DOTALL)

        if not match:
            # Try arrow function
            func_pattern = rf"(?:export\s+)?const\s+{function_name}\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*{{([^}}]*)}}"
            match = re.search(func_pattern, content, re.DOTALL)

        if not match:
            return False

        # Check if pattern is inside function body
        function_body = match.group(1)
        return pattern_name in function_body

    def get_details(self) -> Dict:
        """Get detailed evaluation breakdown.

        Returns:
            Dict with detailed component results
        """
        init_data = self.ground_truth.get_initialization()

        if not init_data:
            return {"message": "No initialization expected for this task type"}

        result = self.evaluate()

        return {
            "file_location": {
                "expected": init_data.get('file'),
                "correct": result.file_location_correct,
            },
            "imports": {
                "expected": init_data.get('imports', []),
                "correct": result.imports_correct,
            },
            "pattern": {
                "expected": init_data.get('pattern'),
                "correct": result.pattern_correct,
            },
            "placement": {
                "expected": init_data.get('placement'),
                "correct": result.placement_correct,
            },
            "overall_score": result.score,
        }
