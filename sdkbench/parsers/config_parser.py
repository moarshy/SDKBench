"""Configuration file parser for package.json and middleware configs."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set


class ConfigParser:
    """Parser for configuration files (package.json, middleware, etc.)."""

    @staticmethod
    def parse_package_json(file_path: Path) -> Dict:
        """Parse package.json file.

        Args:
            file_path: Path to package.json

        Returns:
            Dict with package.json contents
        """
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def extract_dependencies(package_json: Dict) -> Dict[str, str]:
        """Extract all dependencies from package.json.

        Args:
            package_json: Parsed package.json dict

        Returns:
            Dict mapping package names to versions
        """
        dependencies = {}

        # Regular dependencies
        if 'dependencies' in package_json:
            dependencies.update(package_json['dependencies'])

        # Dev dependencies
        if 'devDependencies' in package_json:
            dependencies.update(package_json['devDependencies'])

        return dependencies

    @staticmethod
    def has_clerk_dependency(package_json: Dict) -> bool:
        """Check if package.json includes Clerk dependency.

        Args:
            package_json: Parsed package.json dict

        Returns:
            True if Clerk dependency found
        """
        deps = ConfigParser.extract_dependencies(package_json)

        for dep_name in deps.keys():
            if '@clerk/' in dep_name or dep_name == 'clerk':
                return True

        return False

    @staticmethod
    def extract_clerk_dependencies(package_json: Dict) -> Dict[str, str]:
        """Extract only Clerk-related dependencies.

        Args:
            package_json: Parsed package.json dict

        Returns:
            Dict of Clerk dependencies
        """
        all_deps = ConfigParser.extract_dependencies(package_json)
        clerk_deps = {}

        for dep_name, version in all_deps.items():
            if '@clerk/' in dep_name or dep_name == 'clerk':
                clerk_deps[dep_name] = version

        return clerk_deps

    @staticmethod
    def get_clerk_package_for_framework(framework: str) -> str:
        """Get expected Clerk package name for a framework.

        Args:
            framework: Framework name (nextjs, react, remix, etc.)

        Returns:
            Expected Clerk package name
        """
        framework_packages = {
            'nextjs': '@clerk/nextjs',
            'next': '@clerk/nextjs',
            'react': '@clerk/clerk-react',
            'remix': '@clerk/remix',
            'gatsby': '@clerk/gatsby-plugin-clerk',
            'expo': '@clerk/clerk-expo',
        }

        return framework_packages.get(framework.lower(), '@clerk/clerk-react')

    @staticmethod
    def validate_clerk_version(version: str) -> Dict[str, any]:
        """Validate Clerk package version.

        Args:
            version: Version string (e.g., "^5.0.0", "4.29.0")

        Returns:
            Dict with validation info
        """
        # Extract numeric version
        version_match = re.search(r'(\d+)\.(\d+)\.(\d+)', version)

        if not version_match:
            return {
                'is_valid': False,
                'major': None,
                'minor': None,
                'patch': None,
            }

        major = int(version_match.group(1))
        minor = int(version_match.group(2))
        patch = int(version_match.group(3))

        return {
            'is_valid': True,
            'major': major,
            'minor': minor,
            'patch': patch,
            'is_v5': major == 5,
            'is_v4': major == 4,
            'raw_version': version,
        }

    @staticmethod
    def parse_next_config(file_path: Path) -> Dict:
        """Parse next.config.js file.

        Args:
            file_path: Path to next.config.js

        Returns:
            Dict with extracted config
        """
        if not file_path.exists():
            return {}

        content = file_path.read_text()

        config = {
            'has_clerk_middleware': False,
            'has_auth_middleware': False,
            'typescript': False,
        }

        # Check for Clerk middleware references
        if 'clerkMiddleware' in content or 'authMiddleware' in content:
            config['has_clerk_middleware'] = True

        if 'authMiddleware' in content:
            config['has_auth_middleware'] = True

        # Check for TypeScript
        if 'typescript' in content.lower():
            config['typescript'] = True

        return config

    @staticmethod
    def extract_middleware_matcher(content: str) -> Optional[List[str]]:
        """Extract matcher config from middleware.ts.

        Args:
            content: Middleware file content

        Returns:
            List of matcher patterns or None
        """
        # Pattern: matcher: ["pattern1", "pattern2"]
        matcher_pattern = r'matcher\s*:\s*\[(.*?)\]'

        match = re.search(matcher_pattern, content, re.DOTALL)
        if not match:
            return None

        matcher_text = match.group(1)

        # Extract individual patterns
        patterns = re.findall(r'["\']([^"\']+)["\']', matcher_text)

        return patterns if patterns else None

    @staticmethod
    def parse_tsconfig(file_path: Path) -> Dict:
        """Parse tsconfig.json file.

        Args:
            file_path: Path to tsconfig.json

        Returns:
            Dict with TypeScript config
        """
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r') as f:
                # Remove comments (simple approach)
                content = f.read()
                # Remove single-line comments
                content = re.sub(r'//.*', '', content)
                # Remove multi-line comments
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

                return json.loads(content)
        except (json.JSONDecodeError, Exception):
            return {}

    @staticmethod
    def check_typescript_setup(solution_dir: Path) -> Dict[str, bool]:
        """Check if TypeScript is properly set up.

        Args:
            solution_dir: Path to solution directory

        Returns:
            Dict with TypeScript setup status
        """
        return {
            'has_tsconfig': (solution_dir / 'tsconfig.json').exists(),
            'has_ts_files': len(list(solution_dir.rglob('*.ts'))) > 0 or
                           len(list(solution_dir.rglob('*.tsx'))) > 0,
            'has_types_folder': (solution_dir / 'types').exists(),
        }

    @staticmethod
    def extract_scripts(package_json: Dict) -> Dict[str, str]:
        """Extract npm scripts from package.json.

        Args:
            package_json: Parsed package.json dict

        Returns:
            Dict of script names to commands
        """
        return package_json.get('scripts', {})

    @staticmethod
    def has_required_scripts(package_json: Dict, required: List[str]) -> Dict[str, bool]:
        """Check if required scripts are present.

        Args:
            package_json: Parsed package.json dict
            required: List of required script names

        Returns:
            Dict mapping script names to presence
        """
        scripts = ConfigParser.extract_scripts(package_json)

        return {script: script in scripts for script in required}

    @staticmethod
    def parse_eslint_config(file_path: Path) -> Dict:
        """Parse .eslintrc.json or eslint config.

        Args:
            file_path: Path to eslint config

        Returns:
            Dict with eslint config
        """
        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def extract_framework_from_dependencies(package_json: Dict) -> Optional[str]:
        """Detect framework from dependencies.

        Args:
            package_json: Parsed package.json dict

        Returns:
            Framework name or None
        """
        deps = ConfigParser.extract_dependencies(package_json)

        framework_indicators = {
            'next': 'nextjs',
            'react': 'react',
            'remix': 'remix',
            '@remix-run/react': 'remix',
            'gatsby': 'gatsby',
            'expo': 'expo',
            'vue': 'vue',
            'nuxt': 'nuxt',
        }

        for dep_name, framework in framework_indicators.items():
            if dep_name in deps:
                return framework

        return None

    @staticmethod
    def compare_dependency_versions(
        actual: Dict[str, str],
        expected: Dict[str, str]
    ) -> Dict[str, any]:
        """Compare actual vs expected dependencies.

        Args:
            actual: Actual dependencies from solution
            expected: Expected dependencies from ground truth

        Returns:
            Dict with comparison results
        """
        actual_set = set(actual.keys())
        expected_set = set(expected.keys())

        missing = expected_set - actual_set
        extra = actual_set - expected_set
        common = actual_set.intersection(expected_set)

        version_mismatches = []
        for dep in common:
            actual_version = ConfigParser.validate_clerk_version(actual[dep])
            expected_version = ConfigParser.validate_clerk_version(expected[dep])

            if (actual_version['major'] != expected_version['major'] or
                actual_version['minor'] != expected_version['minor']):
                version_mismatches.append({
                    'dependency': dep,
                    'actual': actual[dep],
                    'expected': expected[dep],
                })

        return {
            'missing_dependencies': list(missing),
            'extra_dependencies': list(extra),
            'version_mismatches': version_mismatches,
            'all_match': len(missing) == 0 and len(version_mismatches) == 0,
        }

    @staticmethod
    def extract_git_info(solution_dir: Path) -> Dict[str, any]:
        """Extract git information if available.

        Args:
            solution_dir: Path to solution directory

        Returns:
            Dict with git info
        """
        gitignore_path = solution_dir / '.gitignore'

        return {
            'has_gitignore': gitignore_path.exists(),
            'ignores_env': ConfigParser._check_gitignore_pattern(gitignore_path, '.env'),
            'ignores_node_modules': ConfigParser._check_gitignore_pattern(
                gitignore_path, 'node_modules'
            ),
        }

    @staticmethod
    def _check_gitignore_pattern(gitignore_path: Path, pattern: str) -> bool:
        """Check if pattern exists in .gitignore.

        Args:
            gitignore_path: Path to .gitignore
            pattern: Pattern to check

        Returns:
            True if pattern found
        """
        if not gitignore_path.exists():
            return False

        content = gitignore_path.read_text()
        return pattern in content
