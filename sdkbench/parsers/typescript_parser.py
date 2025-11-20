"""TypeScript/JavaScript parser for extracting code patterns."""

import re
from typing import Dict, List, Optional, Set, Tuple


class TypeScriptParser:
    """Parser for TypeScript/JavaScript/JSX files.

    Uses regex-based parsing for speed and simplicity.
    Can be upgraded to AST-based parsing if needed.
    """

    @staticmethod
    def extract_imports(content: str) -> List[Dict[str, str]]:
        """Extract all import statements from code.

        Args:
            content: File content

        Returns:
            List of import dicts with 'statement', 'names', 'source'
        """
        imports = []

        # Pattern 1: import { X, Y } from "source"
        pattern1 = r"import\s+{([^}]+)}\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern1, content):
            names = [n.strip() for n in match.group(1).split(',')]
            imports.append({
                'statement': match.group(0),
                'names': names,
                'source': match.group(2),
                'type': 'named'
            })

        # Pattern 2: import X from "source"
        pattern2 = r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern2, content):
            # Skip if already captured by pattern 1
            if '{' not in match.group(0):
                imports.append({
                    'statement': match.group(0),
                    'names': [match.group(1)],
                    'source': match.group(2),
                    'type': 'default'
                })

        # Pattern 3: const X = require("source")
        pattern3 = r"const\s+(\w+)\s*=\s*require\(['\"]([^'\"]+)['\"]\)"
        for match in re.finditer(pattern3, content):
            imports.append({
                'statement': match.group(0),
                'names': [match.group(1)],
                'source': match.group(2),
                'type': 'require'
            })

        return imports

    @staticmethod
    def has_clerk_import(content: str, import_name: Optional[str] = None) -> bool:
        """Check if file has Clerk imports.

        Args:
            content: File content
            import_name: Optional specific import to check (e.g., "ClerkProvider")

        Returns:
            True if Clerk import found
        """
        imports = TypeScriptParser.extract_imports(content)

        for imp in imports:
            # Check if from Clerk package
            if '@clerk/' in imp['source']:
                if import_name is None:
                    return True
                # Check specific import name
                if import_name in imp['names']:
                    return True

        return False

    @staticmethod
    def extract_jsx_component_usage(content: str, component_name: str) -> Optional[Dict]:
        """Extract JSX component usage with props.

        Args:
            content: File content
            component_name: Component name (e.g., "ClerkProvider")

        Returns:
            Dict with component info or None if not found
        """
        # Match <ComponentName ...> or <ComponentName>
        pattern = rf"<{component_name}([^/>]*?)(?:>|/>)"

        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return None

        props_text = match.group(1).strip()

        # Extract individual props
        props = TypeScriptParser._extract_props_from_text(props_text)

        return {
            'component': component_name,
            'has_props': len(props) > 0,
            'props': props,
            'props_text': props_text,
            'is_self_closing': '/>' in match.group(0)
        }

    @staticmethod
    def _extract_props_from_text(props_text: str) -> Dict[str, Optional[str]]:
        """Extract prop names and values from JSX props text.

        Args:
            props_text: Text between component name and >

        Returns:
            Dict mapping prop names to values (or None if value unclear)
        """
        props = {}

        # Pattern for prop="value" or prop={value}
        prop_pattern = r'(\w+)(?:=(?:["\']([^"\']*)["\']|{([^}]*)}))?'

        for match in re.finditer(prop_pattern, props_text):
            prop_name = match.group(1)
            # Get value from either quoted string or braces
            prop_value = match.group(2) or match.group(3)
            props[prop_name] = prop_value

        return props

    @staticmethod
    def extract_function_calls(content: str, function_name: str) -> List[Dict]:
        """Extract function call locations and contexts.

        Args:
            content: File content
            function_name: Function to find (e.g., "auth", "currentUser")

        Returns:
            List of dicts with line numbers and context
        """
        calls = []

        # Pattern: functionName() with optional await
        pattern = rf"(?:await\s+)?{function_name}\(\)"

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # Check if it's a destructuring assignment
                is_destructure = bool(re.search(r'const\s+{[^}]+}\s*=', line))

                calls.append({
                    'line': line_num,
                    'content': line.strip(),
                    'has_await': 'await' in line,
                    'is_destructure': is_destructure
                })

        return calls

    @staticmethod
    def extract_hook_usage(content: str, hook_name: str) -> Optional[Dict]:
        """Extract React hook usage details.

        Args:
            content: File content
            hook_name: Hook name (e.g., "useUser", "useAuth")

        Returns:
            Dict with hook usage info or None if not found
        """
        # Pattern: const { ... } = useHook() or const result = useHook()
        pattern = rf"const\s+(?:{{([^}}]+)}}|(\w+))\s*=\s*{hook_name}\(\)"

        match = re.search(pattern, content)
        if not match:
            return None

        # Get destructured properties or variable name
        if match.group(1):  # Destructured
            properties = [p.strip() for p in match.group(1).split(',')]
            return {
                'hook': hook_name,
                'is_destructured': True,
                'properties': properties,
                'variable_name': None
            }
        else:  # Single variable
            return {
                'hook': hook_name,
                'is_destructured': False,
                'properties': [],
                'variable_name': match.group(2)
            }

    @staticmethod
    def has_client_directive(content: str) -> bool:
        """Check if file has 'use client' directive.

        Args:
            content: File content

        Returns:
            True if directive found at top of file
        """
        # Check first few lines for 'use client'
        lines = content.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if line == "'use client'" or line == '"use client"':
                return True
        return False

    @staticmethod
    def has_server_directive(content: str) -> bool:
        """Check if file has 'use server' directive.

        Args:
            content: File content

        Returns:
            True if directive found
        """
        lines = content.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if line == "'use server'" or line == '"use server"':
                return True
        return False

    @staticmethod
    def extract_exported_function(content: str, function_name: str) -> Optional[Dict]:
        """Extract exported function definition.

        Args:
            content: File content
            function_name: Function name to find

        Returns:
            Dict with function info or None if not found
        """
        # Pattern for various function export styles
        patterns = [
            rf"export\s+(?:default\s+)?(?:async\s+)?function\s+{function_name}\s*\([^)]*\)",
            rf"export\s+default\s+(?:async\s+)?{function_name}",
            rf"export\s+const\s+{function_name}\s*=\s*(?:async\s+)?\([^)]*\)\s*=>"
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return {
                    'name': function_name,
                    'is_async': 'async' in match.group(0),
                    'is_default': 'default' in match.group(0),
                    'definition': match.group(0)
                }

        return None

    @staticmethod
    def extract_middleware_config(content: str) -> Dict:
        """Extract authMiddleware or clerkMiddleware configuration.

        Args:
            content: Middleware file content

        Returns:
            Dict with middleware configuration
        """
        config = {
            'type': None,
            'public_routes': [],
            'ignored_routes': [],
            'has_matcher': False
        }

        # Detect middleware type
        if 'authMiddleware' in content:
            config['type'] = 'authMiddleware'
        elif 'clerkMiddleware' in content:
            config['type'] = 'clerkMiddleware'
        else:
            return config

        # Extract publicRoutes array
        public_match = re.search(
            r"publicRoutes\s*:\s*\[(.*?)\]",
            content,
            re.DOTALL
        )
        if public_match:
            routes_text = public_match.group(1)
            config['public_routes'] = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)

        # Extract ignoredRoutes array
        ignored_match = re.search(
            r"ignoredRoutes\s*:\s*\[(.*?)\]",
            content,
            re.DOTALL
        )
        if ignored_match:
            routes_text = ignored_match.group(1)
            config['ignored_routes'] = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)

        # Check for matcher config
        config['has_matcher'] = bool(re.search(r"export\s+const\s+config\s*=", content))

        # Check for createRouteMatcher (v5 pattern)
        config['has_route_matcher'] = 'createRouteMatcher' in content

        return config

    @staticmethod
    def extract_api_route_protection(content: str) -> Dict:
        """Extract API route protection patterns.

        Args:
            content: API route file content

        Returns:
            Dict with protection details
        """
        protection = {
            'uses_auth_helper': False,
            'uses_current_user': False,
            'uses_get_auth': False,  # v4 pattern
            'has_auth_check': False,
            'returns_401': False
        }

        # Check for auth() usage
        if re.search(r"const\s+{[^}]*userId[^}]*}\s*=\s*auth\(\)", content):
            protection['uses_auth_helper'] = True

        # Check for currentUser()
        if 'currentUser()' in content:
            protection['uses_current_user'] = True

        # Check for getAuth (v4)
        if 'getAuth(' in content:
            protection['uses_get_auth'] = True

        # Check for userId check
        if re.search(r"if\s*\(\s*!userId", content):
            protection['has_auth_check'] = True

        # Check for 401 response
        if 'status: 401' in content or 'status(401)' in content:
            protection['returns_401'] = True

        return protection

    @staticmethod
    def count_clerk_patterns(content: str) -> Dict[str, int]:
        """Count occurrences of various Clerk patterns.

        Args:
            content: File content

        Returns:
            Dict mapping pattern names to counts
        """
        patterns = {
            'ClerkProvider': len(re.findall(r'ClerkProvider', content)),
            'auth()': len(re.findall(r'auth\(\)', content)),
            'currentUser()': len(re.findall(r'currentUser\(\)', content)),
            'useUser()': len(re.findall(r'useUser\(\)', content)),
            'useAuth()': len(re.findall(r'useAuth\(\)', content)),
            'useClerk()': len(re.findall(r'useClerk\(\)', content)),
            'authMiddleware': len(re.findall(r'authMiddleware', content)),
            'clerkMiddleware': len(re.findall(r'clerkMiddleware', content)),
            'getAuth(': len(re.findall(r'getAuth\(', content)),  # v4
        }

        return {k: v for k, v in patterns.items() if v > 0}
