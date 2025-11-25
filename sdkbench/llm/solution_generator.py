"""Solution generator from LLM responses."""

import re
from pathlib import Path
from typing import Dict, List, Optional
import json
import shutil
from datetime import datetime


class SolutionGenerator:
    """Generate solution directories from LLM responses."""

    def __init__(self):
        """Initialize solution generator."""
        pass

    def generate_solution(
        self,
        llm_response: str,
        output_dir: Path,
        sample_id: str,
        model_name: str,
        copy_input: Optional[Path] = None
    ) -> Path:
        """Generate solution directory from LLM response.

        Args:
            llm_response: Raw LLM response content
            output_dir: Base output directory
            sample_id: Sample identifier
            model_name: Model that generated the solution
            copy_input: Optional input directory to copy as base

        Returns:
            Path to generated solution directory
        """
        # Create solution directory
        solution_dir = output_dir / sample_id / model_name.replace('/', '_')
        solution_dir.mkdir(parents=True, exist_ok=True)

        # Copy input files if provided
        if copy_input and copy_input.exists():
            self._copy_input_files(copy_input, solution_dir)

        # Extract files from response
        files = self._extract_files_from_response(llm_response)

        # Write files to solution directory
        for filepath, content in files.items():
            self._write_file(solution_dir, filepath, content)

        # Save generation metadata
        self._save_metadata(solution_dir, sample_id, model_name, llm_response)

        return solution_dir

    def _extract_files_from_response(self, content: str) -> Dict[str, str]:
        """Extract file paths and contents from LLM response.

        Args:
            content: LLM response content

        Returns:
            Dict mapping file paths to their content
        """
        files = {}

        # Pattern 1: Look for explicit file markers
        # // filepath: path/to/file.ext
        # // path/to/file.ext
        # File: path/to/file.ext

        # Split content into sections
        sections = re.split(r'\n(?=(?://\s*filepath:|//\s*\w+[/.]|File:\s*))', content)

        for section in sections:
            lines = section.split('\n')
            if not lines:
                continue

            first_line = lines[0].strip()
            filepath = None

            # Check for file path patterns
            if first_line.startswith('// filepath:'):
                filepath = first_line[12:].strip()
            elif first_line.startswith('//') and ('/' in first_line or '.' in first_line):
                potential_path = first_line[2:].strip()
                # Validate it looks like a path
                if self._is_valid_path(potential_path):
                    filepath = potential_path
            elif first_line.startswith('File:'):
                filepath = first_line[5:].strip()

            if filepath:
                # Extract content after the file marker
                content_lines = []
                in_code_block = False

                for line in lines[1:]:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        if not in_code_block:
                            # End of code block for this file
                            break
                        continue
                    elif in_code_block or not line.strip().startswith('```'):
                        content_lines.append(line)

                if content_lines:
                    files[filepath] = '\n'.join(content_lines).strip()

        # Pattern 2: If no explicit files found, look for code blocks with language hints
        if not files:
            files = self._extract_from_code_blocks(content)

        return files

    def _extract_from_code_blocks(self, content: str) -> Dict[str, str]:
        """Extract files from code blocks when no explicit paths given.

        Args:
            content: LLM response content

        Returns:
            Dict mapping inferred file paths to content
        """
        files = {}
        code_blocks = []

        # Find all code blocks
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        for lang, code in matches:
            code_blocks.append({'language': lang, 'code': code.strip()})

        # Try to infer file names from content and language
        for i, block in enumerate(code_blocks):
            lang = block['language']
            code = block['code']

            # Try to extract filename from comments in code
            filename = self._infer_filename_from_code(code, lang)

            if filename:
                files[filename] = code
            elif lang:
                # Use generic filename based on language
                ext = self._get_extension_for_language(lang)
                files[f"file_{i + 1}.{ext}"] = code

        return files

    def _infer_filename_from_code(self, code: str, language: str) -> Optional[str]:
        """Try to infer filename from code content.

        Args:
            code: Code content
            language: Language hint

        Returns:
            Inferred filename or None
        """
        lines = code.split('\n')

        # Check first few lines for explicit filepath comments
        for line in lines[:5]:
            line_stripped = line.strip()

            # Check for "# filepath: xxx" or "// filepath: xxx" format
            filepath_match = re.search(r'(?:#|//)\s*filepath:\s*(.+)', line_stripped, re.IGNORECASE)
            if filepath_match:
                potential_path = filepath_match.group(1).strip()
                # Clean up any trailing comments or noise
                potential_path = potential_path.split()[0] if potential_path else ""
                if potential_path and self._is_valid_path(potential_path):
                    return potential_path

            # Check for filename in comments (legacy patterns)
            if '//' in line or '#' in line or '/*' in line:
                # Look for paths
                path_match = re.search(r'([a-zA-Z0-9_\-/.]+\.\w+)', line)
                if path_match:
                    potential_path = path_match.group(1)
                    if self._is_valid_path(potential_path):
                        return potential_path

        # Check for React component names
        if language in ['jsx', 'tsx', 'javascript', 'typescript']:
            component_match = re.search(r'export\s+(?:default\s+)?(?:function|const)\s+(\w+)', code)
            if component_match:
                name = component_match.group(1)
                ext = 'tsx' if language in ['tsx', 'typescript'] else 'jsx'
                return f"{name}.{ext}"

        return None

    def _get_extension_for_language(self, language: str) -> str:
        """Get file extension for language.

        Args:
            language: Language identifier

        Returns:
            File extension
        """
        extensions = {
            'javascript': 'js',
            'typescript': 'ts',
            'jsx': 'jsx',
            'tsx': 'tsx',
            'json': 'json',
            'python': 'py',
            'bash': 'sh',
            'shell': 'sh',
            'env': 'env',
            'yaml': 'yaml',
            'yml': 'yml',
            'html': 'html',
            'css': 'css',
        }

        return extensions.get(language.lower(), 'txt')

    def _is_valid_path(self, path: str) -> bool:
        """Check if string looks like a valid file path.

        Args:
            path: Potential file path

        Returns:
            True if valid path pattern
        """
        # Must have an extension
        if '.' not in path:
            return False

        # Must not be a URL
        if path.startswith('http://') or path.startswith('https://'):
            return False

        # Must not have invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in path for char in invalid_chars):
            return False

        # Should have a reasonable extension
        ext = path.split('.')[-1]
        valid_extensions = [
            'js', 'jsx', 'ts', 'tsx', 'json', 'md', 'env', 'local',
            'css', 'scss', 'html', 'yml', 'yaml', 'toml', 'txt', 'sh',
            'py', 'pyc', 'pyx', 'pyi',  # Python
        ]

        return ext.lower() in valid_extensions

    def _copy_input_files(self, input_dir: Path, output_dir: Path) -> None:
        """Copy input files to output directory.

        Args:
            input_dir: Source directory
            output_dir: Destination directory
        """
        for item in input_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, output_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, output_dir / item.name, dirs_exist_ok=True)

    def _write_file(self, base_dir: Path, filepath: str, content: str) -> None:
        """Write file to solution directory.

        Args:
            base_dir: Base directory for solution
            filepath: Relative file path
            content: File content
        """
        # Clean up the filepath
        filepath = filepath.strip()
        if filepath.startswith('/'):
            filepath = filepath[1:]

        file_path = base_dir / filepath
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)

    def _save_metadata(
        self,
        solution_dir: Path,
        sample_id: str,
        model_name: str,
        llm_response: str
    ) -> None:
        """Save generation metadata.

        Args:
            solution_dir: Solution directory
            sample_id: Sample identifier
            model_name: Model name
            llm_response: Raw LLM response
        """
        metadata = {
            'sample_id': sample_id,
            'model': model_name,
            'generated_at': datetime.now().isoformat(),
            'files_generated': [
                str(f.relative_to(solution_dir))
                for f in solution_dir.rglob('*')
                if f.is_file() and f.name != 'generation_metadata.json'
            ]
        }

        with open(solution_dir / 'generation_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save raw response
        with open(solution_dir / 'llm_response.txt', 'w') as f:
            f.write(llm_response)