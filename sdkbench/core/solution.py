"""Solution class for representing LLM-generated code."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set


class Solution:
    """Represents an LLM-generated solution to evaluate.

    A solution is a directory containing source files that implement
    a Clerk SDK integration task.
    """

    def __init__(self, solution_dir: Path):
        """Initialize from a directory containing solution files.

        Args:
            solution_dir: Path to directory with solution files
        """
        self.solution_dir = Path(solution_dir)
        if not self.solution_dir.exists():
            raise FileNotFoundError(f"Solution directory not found: {solution_dir}")

        self.files: Dict[str, str] = {}  # relative_path -> content
        self._load_files()

    def _load_files(self) -> None:
        """Load all files from solution directory into memory."""
        # File extensions to include
        extensions = {'.ts', '.tsx', '.js', '.jsx', '.json', '.env'}

        for file_path in self.solution_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip node_modules and build directories
                if 'node_modules' in file_path.parts or '.next' in file_path.parts:
                    continue

                try:
                    relative_path = file_path.relative_to(self.solution_dir)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        self.files[str(relative_path)] = f.read()
                except Exception as e:
                    print(f"Warning: Failed to read {file_path}: {e}")

    # ==================== File Operations ====================

    def has_file(self, path: str) -> bool:
        """Check if solution contains a file at the given path.

        Args:
            path: Relative path to check (e.g., "app/layout.tsx")

        Returns:
            True if file exists in solution
        """
        # Normalize path separators
        path = path.replace('\\', '/')
        return path in self.files

    def get_file_content(self, path: str) -> Optional[str]:
        """Get content of a file in the solution.

        Args:
            path: Relative path to file

        Returns:
            File content or None if not found
        """
        path = path.replace('\\', '/')
        return self.files.get(path)

    def get_all_files(self) -> Dict[str, str]:
        """Get all files in the solution.

        Returns:
            Dictionary mapping relative paths to file contents
        """
        return self.files.copy()

    # ==================== Import Extraction ====================

    def extract_imports(self, file_path: Optional[str] = None) -> List[str]:
        """Extract import statements from solution files.

        Args:
            file_path: Optional specific file to extract from.
                      If None, extracts from all files.

        Returns:
            List of import statements found
        """
        imports = []

        # Files to check
        files_to_check = {}
        if file_path:
            content = self.get_file_content(file_path)
            if content:
                files_to_check[file_path] = content
        else:
            files_to_check = self.files

        # Import patterns
        patterns = [
            r"import\s+{([^}]+)}\s+from\s+['\"]([^'\"]+)['\"]",  # import { X } from "Y"
            r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]",      # import X from "Y"
            r"const\s+\w+\s*=\s*require\(['\"]([^'\"]+)['\"]\)",  # const X = require("Y")
        ]

        for path, content in files_to_check.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    imports.append(match.group(0))

        return imports

    def has_import(self, import_pattern: str) -> bool:
        """Check if solution has a specific import.

        Args:
            import_pattern: Pattern to search for (e.g., "@clerk/nextjs")

        Returns:
            True if import found
        """
        imports = self.extract_imports()
        return any(import_pattern in imp for imp in imports)

    # ==================== Pattern Detection ====================

    def has_pattern(self, pattern: str, file_path: Optional[str] = None) -> bool:
        """Check if a pattern exists in solution files.

        Args:
            pattern: String pattern to search for
            file_path: Optional specific file to search in

        Returns:
            True if pattern found
        """
        files_to_check = {}
        if file_path:
            content = self.get_file_content(file_path)
            if content:
                files_to_check[file_path] = content
        else:
            files_to_check = self.files

        return any(pattern in content for content in files_to_check.values())

    def extract_jsx_component(self, component_name: str) -> Optional[Dict]:
        """Extract JSX component usage and props.

        Args:
            component_name: Name of component (e.g., "ClerkProvider")

        Returns:
            Dict with props and location, or None if not found
        """
        pattern = rf"<{component_name}([^>]*)>"

        for file_path, content in self.files.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                props_text = match.group(1).strip()
                return {
                    "file": file_path,
                    "props_text": props_text,
                    "has_props": len(props_text) > 0
                }

        return None

    # ==================== Environment Variables ====================

    def extract_env_vars(self) -> List[str]:
        """Extract environment variable names from .env files.

        Returns:
            List of environment variable names
        """
        env_vars = []

        # Find all .env files
        for file_path, content in self.files.items():
            if '.env' in file_path:
                for line in content.split('\n'):
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        if '=' in line:
                            var_name = line.split('=')[0].strip()
                            env_vars.append(var_name)

        return env_vars

    def extract_clerk_env_vars(self) -> List[str]:
        """Extract Clerk-specific environment variables.

        Returns:
            List of Clerk env var names
        """
        all_env_vars = self.extract_env_vars()
        return [
            var for var in all_env_vars
            if var.startswith('CLERK_') or var.startswith('NEXT_PUBLIC_CLERK_')
        ]

    # ==================== Configuration ====================

    def extract_provider_props(self) -> List[str]:
        """Extract ClerkProvider props from solution.

        Returns:
            List of prop names used
        """
        component = self.extract_jsx_component("ClerkProvider")
        if not component or not component["has_props"]:
            return []

        props_text = component["props_text"]
        # Extract prop names: appearance, publishableKey, etc.
        prop_names = re.findall(r'(\w+)=', props_text)
        return prop_names

    def extract_middleware_config(self) -> Dict:
        """Extract authMiddleware configuration.

        Returns:
            Dict with publicRoutes, ignoredRoutes, etc.
        """
        config = {}

        # Find middleware file
        middleware_content = None
        for file_path, content in self.files.items():
            if 'middleware' in file_path:
                middleware_content = content
                break

        if not middleware_content:
            return config

        # Extract publicRoutes
        public_match = re.search(
            r"publicRoutes:\s*\[(.*?)\]",
            middleware_content,
            re.DOTALL
        )
        if public_match:
            routes_text = public_match.group(1)
            routes = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)
            config["publicRoutes"] = routes

        # Extract ignoredRoutes
        ignored_match = re.search(
            r"ignoredRoutes:\s*\[(.*?)\]",
            middleware_content,
            re.DOTALL
        )
        if ignored_match:
            routes_text = ignored_match.group(1)
            routes = re.findall(r"['\"]([^'\"]+)['\"]", routes_text)
            config["ignoredRoutes"] = routes

        return config

    # ==================== Integration Points ====================

    def extract_integration_points(self) -> Set[str]:
        """Extract files that use Clerk authentication.

        Returns:
            Set of file paths with Clerk integration
        """
        integration_files = set()

        # Patterns that indicate Clerk usage
        patterns = [
            r"useUser\(\)",
            r"useAuth\(\)",
            r"useClerk\(\)",
            r"auth\(\)",
            r"currentUser\(\)",
            r"getAuth\(",
            r"authMiddleware",
            r"clerkMiddleware",
        ]

        for file_path, content in self.files.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    integration_files.add(file_path)
                    break

        return integration_files

    def has_client_directive(self, file_path: str) -> bool:
        """Check if file has 'use client' directive.

        Args:
            file_path: Path to check

        Returns:
            True if 'use client' found
        """
        content = self.get_file_content(file_path)
        if not content:
            return False

        return "'use client'" in content or '"use client"' in content

    # ==================== String Representation ====================

    def __repr__(self) -> str:
        return f"Solution(dir={self.solution_dir}, files={len(self.files)})"
