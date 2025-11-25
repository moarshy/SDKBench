"""Python parser for extracting code patterns."""

import re
from typing import Dict, List, Optional, Set, Tuple


class PythonParser:
    """Parser for Python files.

    Uses regex-based parsing for speed and simplicity.
    Mirrors TypeScriptParser interface for consistency.
    """

    @staticmethod
    def extract_imports(content: str) -> List[Dict[str, str]]:
        """Extract all import statements from Python code.

        Args:
            content: File content

        Returns:
            List of import dicts with 'statement', 'names', 'source'
        """
        imports = []

        # Pattern 1: import module
        pattern1 = r"^import\s+([\w.]+)(?:\s+as\s+(\w+))?"
        for match in re.finditer(pattern1, content, re.MULTILINE):
            module = match.group(1)
            alias = match.group(2)
            imports.append({
                'statement': match.group(0),
                'names': [alias or module.split('.')[-1]],
                'source': module,
                'type': 'import',
                'alias': alias
            })

        # Pattern 2: from module import names
        pattern2 = r"^from\s+([\w.]+)\s+import\s+(.+?)(?:\s*#|$)"
        for match in re.finditer(pattern2, content, re.MULTILINE):
            module = match.group(1)
            names_str = match.group(2).strip()

            # Handle parenthesized imports
            if '(' in names_str:
                # Multi-line import - find the closing paren
                start_pos = match.end()
                paren_match = re.search(r'\)', content[match.start():])
                if paren_match:
                    full_import = content[match.start():match.start() + paren_match.end()]
                    names_str = re.search(r'import\s*\(?\s*(.+?)\s*\)?$', full_import, re.DOTALL)
                    if names_str:
                        names_str = names_str.group(1)

            # Parse individual names (handling aliases)
            names = []
            for name_part in re.split(r',\s*', names_str):
                name_part = name_part.strip()
                if not name_part:
                    continue
                # Handle "name as alias"
                as_match = re.match(r'(\w+)\s+as\s+(\w+)', name_part)
                if as_match:
                    names.append(as_match.group(1))
                else:
                    names.append(name_part)

            imports.append({
                'statement': match.group(0),
                'names': names,
                'source': module,
                'type': 'from_import'
            })

        return imports

    @staticmethod
    def has_import(content: str, module: str, name: Optional[str] = None) -> bool:
        """Check if file has a specific import.

        Args:
            content: File content
            module: Module name (e.g., "lancedb")
            name: Optional specific import name (e.g., "connect")

        Returns:
            True if import found
        """
        imports = PythonParser.extract_imports(content)

        for imp in imports:
            # Check module match
            if imp['source'] == module or imp['source'].startswith(f"{module}."):
                if name is None:
                    return True
                if name in imp['names']:
                    return True
            # Also check if module is in names (from X import Y where Y is the module)
            if module in imp['names']:
                return True

        return False

    @staticmethod
    def extract_function_definitions(content: str) -> List[Dict]:
        """Extract all function definitions.

        Args:
            content: File content

        Returns:
            List of dicts with function info
        """
        functions = []

        # Pattern: def function_name(args):
        pattern = r"^(\s*)def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?\s*:"

        for match in re.finditer(pattern, content, re.MULTILINE):
            indent = len(match.group(1))
            name = match.group(2)
            args = match.group(3)
            return_type = match.group(4)

            # Check if async
            line_start = content.rfind('\n', 0, match.start()) + 1
            line = content[line_start:match.start()]
            is_async = 'async' in line

            functions.append({
                'name': name,
                'args': args.strip(),
                'return_type': return_type.strip() if return_type else None,
                'is_async': is_async,
                'indent': indent,
                'line': content[:match.start()].count('\n') + 1
            })

        return functions

    @staticmethod
    def extract_class_definitions(content: str) -> List[Dict]:
        """Extract all class definitions.

        Args:
            content: File content

        Returns:
            List of dicts with class info
        """
        classes = []

        # Pattern: class ClassName(bases):
        pattern = r"^(\s*)class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:"

        for match in re.finditer(pattern, content, re.MULTILINE):
            indent = len(match.group(1))
            name = match.group(2)
            bases = match.group(3)

            classes.append({
                'name': name,
                'bases': [b.strip() for b in bases.split(',')] if bases else [],
                'indent': indent,
                'line': content[:match.start()].count('\n') + 1
            })

        return classes

    @staticmethod
    def extract_function_calls(content: str, function_name: str) -> List[Dict]:
        """Extract function call locations and contexts.

        Args:
            content: File content
            function_name: Function to find (e.g., "lancedb.connect")

        Returns:
            List of dicts with line numbers and context
        """
        calls = []

        # Escape dots for regex
        escaped_name = re.escape(function_name)

        # Pattern: function_name( with optional arguments
        pattern = rf"(?:await\s+)?{escaped_name}\s*\("

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # Check if it's an assignment
                is_assignment = bool(re.search(r'=\s*(?:await\s+)?' + escaped_name, line))

                calls.append({
                    'line': line_num,
                    'content': line.strip(),
                    'has_await': 'await' in line,
                    'is_assignment': is_assignment
                })

        return calls

    @staticmethod
    def extract_method_calls(content: str, method_name: str) -> List[Dict]:
        """Extract method calls on any object.

        Args:
            content: File content
            method_name: Method name (e.g., "connect", "table_names")

        Returns:
            List of dicts with line numbers and context
        """
        calls = []

        # Pattern: .method_name(
        pattern = rf"\.{method_name}\s*\("

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                calls.append({
                    'line': line_num,
                    'content': line.strip(),
                })

        return calls

    @staticmethod
    def has_pattern(content: str, pattern: str) -> bool:
        """Check if content contains a pattern.

        Args:
            content: File content
            pattern: Pattern to search (e.g., "lancedb.connect")

        Returns:
            True if pattern found
        """
        return pattern in content

    @staticmethod
    def extract_decorators(content: str, function_name: Optional[str] = None) -> List[Dict]:
        """Extract decorator usage.

        Args:
            content: File content
            function_name: Optional function to check decorators for

        Returns:
            List of decorator dicts
        """
        decorators = []

        # Pattern: @decorator or @decorator(args)
        pattern = r"^(\s*)@(\w+(?:\.\w+)*)(?:\s*\(([^)]*)\))?"

        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                decorator_name = match.group(2)
                args = match.group(3)

                # Find the function this decorates
                decorated_func = None
                for j in range(i + 1, min(i + 5, len(lines))):
                    func_match = re.match(r'\s*(?:async\s+)?def\s+(\w+)', lines[j])
                    if func_match:
                        decorated_func = func_match.group(1)
                        break

                if function_name is None or decorated_func == function_name:
                    decorators.append({
                        'name': decorator_name,
                        'args': args,
                        'decorates': decorated_func,
                        'line': i + 1
                    })

        return decorators

    @staticmethod
    def extract_variable_assignments(content: str, var_name: Optional[str] = None) -> List[Dict]:
        """Extract variable assignments.

        Args:
            content: File content
            var_name: Optional specific variable name

        Returns:
            List of assignment dicts
        """
        assignments = []

        # Pattern: var_name = value (at module level or with known indent)
        if var_name:
            pattern = rf"^(\s*)({var_name})\s*(?::\s*[^=]+)?\s*=\s*(.+)$"
        else:
            pattern = r"^(\s*)([a-zA-Z_]\w*)\s*(?::\s*[^=]+)?\s*=\s*(.+)$"

        for match in re.finditer(pattern, content, re.MULTILINE):
            indent = len(match.group(1))
            name = match.group(2)
            value = match.group(3).strip()

            assignments.append({
                'name': name,
                'value': value,
                'indent': indent,
                'line': content[:match.start()].count('\n') + 1
            })

        return assignments

    @staticmethod
    def has_error_handling(content: str) -> bool:
        """Check if content has try-except blocks.

        Args:
            content: File content

        Returns:
            True if error handling found
        """
        return bool(re.search(r'\btry\s*:', content) and re.search(r'\bexcept\b', content))

    @staticmethod
    def has_type_hints(content: str) -> bool:
        """Check if functions have type hints.

        Args:
            content: File content

        Returns:
            True if type hints are used
        """
        # Check for function return type hints
        has_return_hint = bool(re.search(r'def\s+\w+\s*\([^)]*\)\s*->', content))

        # Check for parameter type hints
        has_param_hint = bool(re.search(r'def\s+\w+\s*\([^)]*:\s*\w+', content))

        return has_return_hint or has_param_hint

    @staticmethod
    def extract_string_values(content: str, pattern: str) -> List[str]:
        """Extract string values matching a pattern context.

        Args:
            content: File content
            pattern: Context pattern (e.g., "connect(")

        Returns:
            List of string values found near pattern
        """
        values = []

        # Find pattern and extract nearby strings
        for match in re.finditer(re.escape(pattern), content):
            # Look for strings in the next 100 characters
            context = content[match.start():match.start() + 100]
            strings = re.findall(r'["\']([^"\']+)["\']', context)
            values.extend(strings)

        return values

    @staticmethod
    def count_patterns(content: str, patterns: Dict[str, str]) -> Dict[str, int]:
        """Count occurrences of various patterns.

        Args:
            content: File content
            patterns: Dict mapping pattern names to regex patterns

        Returns:
            Dict mapping pattern names to counts
        """
        counts = {}
        for name, pattern in patterns.items():
            counts[name] = len(re.findall(pattern, content))
        return {k: v for k, v in counts.items() if v > 0}

    @staticmethod
    def extract_docstring(content: str, function_name: Optional[str] = None) -> Optional[str]:
        """Extract docstring from module or function.

        Args:
            content: File content
            function_name: Optional function name

        Returns:
            Docstring content or None
        """
        if function_name:
            # Find function and its docstring
            pattern = rf'def\s+{function_name}\s*\([^)]*\)[^:]*:\s*(?:[\r\n]+\s*)?("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
            match = re.search(pattern, content)
        else:
            # Get module docstring (first triple-quoted string)
            pattern = r'^("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
            match = re.search(pattern, content)

        if match:
            docstring = match.group(1) if function_name else match.group(0)
            # Remove quotes
            return docstring[3:-3].strip()

        return None

    @staticmethod
    def get_sdk_patterns(sdk: str) -> Dict[str, str]:
        """Get SDK-specific patterns to check.

        Args:
            sdk: SDK name (e.g., "lancedb")

        Returns:
            Dict of pattern names to regex patterns
        """
        if sdk == "lancedb":
            return {
                'connect': r'lancedb\.connect\s*\(',
                'create_table': r'\.create_table\s*\(',
                'open_table': r'\.open_table\s*\(',
                'table_names': r'\.table_names\s*\(',
                'search': r'\.search\s*\(',
                'add': r'\.add\s*\(',
                'EmbeddingFunctionRegistry': r'EmbeddingFunctionRegistry',
                'LanceModel': r'LanceModel',
                'SourceField': r'SourceField\s*\(',
                'VectorField': r'VectorField\s*\(',
                'Vector': r'Vector\s*\(',
            }
        return {}
