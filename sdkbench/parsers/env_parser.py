"""Environment file parser for extracting variables."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set


class EnvParser:
    """Parser for .env and .env.local files.

    Extracts environment variables and validates SDK-specific patterns.
    """

    @staticmethod
    def parse_env_file(file_path: Path) -> Dict[str, Optional[str]]:
        """Parse .env file and extract variables.

        Args:
            file_path: Path to .env file

        Returns:
            Dict mapping variable names to values (None if no value)
        """
        if not file_path.exists():
            return {}

        env_vars = {}
        content = file_path.read_text()

        # Pattern: VAR_NAME=value or VAR_NAME="value" or just VAR_NAME
        pattern = r'^([A-Z_][A-Z0-9_]*)\s*=?\s*(.*)$'

        for line in content.split('\n'):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            match = re.match(pattern, line)
            if match:
                var_name = match.group(1)
                var_value = match.group(2).strip()

                # Remove quotes if present
                if var_value:
                    var_value = var_value.strip('"').strip("'")
                    env_vars[var_name] = var_value if var_value else None
                else:
                    env_vars[var_name] = None

        return env_vars

    @staticmethod
    def extract_from_content(content: str) -> Dict[str, Optional[str]]:
        """Extract environment variables from content string.

        Args:
            content: File content

        Returns:
            Dict mapping variable names to values
        """
        env_vars = {}

        pattern = r'^([A-Z_][A-Z0-9_]*)\s*=?\s*(.*)$'

        for line in content.split('\n'):
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            match = re.match(pattern, line)
            if match:
                var_name = match.group(1)
                var_value = match.group(2).strip()

                if var_value:
                    var_value = var_value.strip('"').strip("'")
                    env_vars[var_name] = var_value if var_value else None
                else:
                    env_vars[var_name] = None

        return env_vars

    @staticmethod
    def has_clerk_keys(env_vars: Dict[str, Optional[str]]) -> bool:
        """Check if environment variables contain Clerk keys.

        Args:
            env_vars: Dict of environment variables

        Returns:
            True if Clerk keys found
        """
        clerk_patterns = [
            'NEXT_PUBLIC_CLERK_',
            'CLERK_SECRET_KEY',
            'CLERK_API_KEY',
        ]

        for var_name in env_vars.keys():
            for pattern in clerk_patterns:
                if pattern in var_name:
                    return True

        return False

    @staticmethod
    def extract_clerk_keys(env_vars: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """Extract only Clerk-specific environment variables.

        Args:
            env_vars: Dict of environment variables

        Returns:
            Dict of Clerk-specific variables
        """
        clerk_vars = {}

        clerk_patterns = [
            'NEXT_PUBLIC_CLERK_',
            'CLERK_SECRET_KEY',
            'CLERK_API_KEY',
            'CLERK_WEBHOOK_',
        ]

        for var_name, var_value in env_vars.items():
            for pattern in clerk_patterns:
                if pattern in var_name:
                    clerk_vars[var_name] = var_value
                    break

        return clerk_vars

    @staticmethod
    def get_required_clerk_keys() -> Set[str]:
        """Get set of required Clerk environment variables.

        Returns:
            Set of required variable names
        """
        return {
            'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY',
            'CLERK_SECRET_KEY',
        }

    @staticmethod
    def validate_clerk_keys(env_vars: Dict[str, Optional[str]]) -> Dict[str, bool]:
        """Validate that required Clerk keys are present.

        Args:
            env_vars: Dict of environment variables

        Returns:
            Dict mapping key names to presence status
        """
        required = EnvParser.get_required_clerk_keys()

        validation = {}
        for key in required:
            validation[key] = key in env_vars

        return validation

    @staticmethod
    def find_env_references_in_code(content: str) -> List[str]:
        """Find environment variable references in code.

        Args:
            content: Source code content

        Returns:
            List of referenced environment variable names
        """
        references = []

        # Pattern 1: process.env.VAR_NAME
        pattern1 = r'process\.env\.([A-Z_][A-Z0-9_]*)'
        references.extend(re.findall(pattern1, content))

        # Pattern 2: process.env["VAR_NAME"] or process.env['VAR_NAME']
        pattern2 = r'process\.env\[["\']([A-Z_][A-Z0-9_]*?)["\']\]'
        references.extend(re.findall(pattern2, content))

        # Pattern 3: import.meta.env.VAR_NAME (Vite)
        pattern3 = r'import\.meta\.env\.([A-Z_][A-Z0-9_]*)'
        references.extend(re.findall(pattern3, content))

        return list(set(references))  # Remove duplicates

    @staticmethod
    def check_env_usage_consistency(
        env_file_vars: Dict[str, Optional[str]],
        code_references: List[str]
    ) -> Dict[str, bool]:
        """Check if code references match .env file.

        Args:
            env_file_vars: Variables defined in .env
            code_references: Variables referenced in code

        Returns:
            Dict with 'defined_but_unused' and 'used_but_undefined' lists
        """
        env_vars_set = set(env_file_vars.keys())
        code_refs_set = set(code_references)

        return {
            'all_defined': code_refs_set.issubset(env_vars_set),
            'defined_but_unused': list(env_vars_set - code_refs_set),
            'used_but_undefined': list(code_refs_set - env_vars_set),
        }

    @staticmethod
    def extract_env_example_vars(file_path: Path) -> Set[str]:
        """Extract variable names from .env.example file.

        Args:
            file_path: Path to .env.example

        Returns:
            Set of variable names
        """
        if not file_path.exists():
            return set()

        env_vars = EnvParser.parse_env_file(file_path)
        return set(env_vars.keys())

    @staticmethod
    def compare_env_files(
        env_path: Path,
        env_example_path: Path
    ) -> Dict[str, any]:
        """Compare .env with .env.example.

        Args:
            env_path: Path to .env
            env_example_path: Path to .env.example

        Returns:
            Dict with comparison results
        """
        env_vars = set(EnvParser.parse_env_file(env_path).keys())
        example_vars = EnvParser.extract_env_example_vars(env_example_path)

        return {
            'in_both': list(env_vars.intersection(example_vars)),
            'only_in_env': list(env_vars - example_vars),
            'only_in_example': list(example_vars - env_vars),
            'env_matches_example': env_vars == example_vars,
        }
