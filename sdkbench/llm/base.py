"""Base LLM provider abstraction for SDK-Bench."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from pathlib import Path
import json
import time


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    model: str
    temperature: float = 0.1
    max_tokens: int = 4000
    top_p: float = 0.95
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    retry_count: int = 3
    retry_delay: float = 1.0


class LLMResponse(BaseModel):
    """Response from LLM provider."""

    content: str
    model: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str
    cost: Optional[float] = None
    latency_ms: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        """Initialize provider with configuration.

        Args:
            config: LLM configuration
        """
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate provider configuration."""
        if not self.config.api_key:
            raise ValueError(f"API key required for {self.__class__.__name__}")

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context

        Returns:
            LLMResponse object with generation details
        """
        pass

    @abstractmethod
    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        validation_fn: Optional[callable] = None
    ) -> LLMResponse:
        """Generate with retry logic and optional validation.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            validation_fn: Optional function to validate response

        Returns:
            LLMResponse object
        """
        pass

    def extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from LLM response.

        Args:
            content: LLM response content

        Returns:
            List of dicts with 'language' and 'code' keys
        """
        blocks = []
        lines = content.split('\n')
        in_block = False
        current_block = []
        language = None

        for line in lines:
            if line.startswith('```'):
                if in_block:
                    # End of block
                    blocks.append({
                        'language': language or 'plaintext',
                        'code': '\n'.join(current_block)
                    })
                    in_block = False
                    current_block = []
                    language = None
                else:
                    # Start of block
                    in_block = True
                    # Extract language if specified
                    lang_spec = line[3:].strip()
                    if lang_spec:
                        language = lang_spec.split()[0]
            elif in_block:
                current_block.append(line)

        return blocks

    def extract_files_from_response(self, content: str) -> Dict[str, str]:
        """Extract file paths and contents from LLM response.

        Looks for patterns like:
        - File: path/to/file.ext
        - // path/to/file.ext
        - <!-- path/to/file.ext -->

        Args:
            content: LLM response content

        Returns:
            Dict mapping file paths to their content
        """
        files = {}
        lines = content.split('\n')
        current_file = None
        current_content = []

        for i, line in enumerate(lines):
            # Check for file markers
            if line.startswith('File:') or line.startswith('// ') or line.startswith('<!-- '):
                # Save previous file if exists
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)

                # Extract new file path
                if line.startswith('File:'):
                    current_file = line[5:].strip()
                elif line.startswith('// '):
                    potential_path = line[3:].strip()
                    if '/' in potential_path or '.' in potential_path:
                        current_file = potential_path
                elif line.startswith('<!-- ') and line.endswith(' -->'):
                    current_file = line[5:-4].strip()

                current_content = []

                # Check if next line is a code block
                if i + 1 < len(lines) and lines[i + 1].startswith('```'):
                    # Skip to code block handling
                    continue
            elif current_file is not None:
                # Accumulate content for current file
                if line.startswith('```'):
                    # Toggle code block state but don't include markers
                    continue
                current_content.append(line)

        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)

        return files

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on token usage.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Cost in USD
        """
        # Override in subclasses with model-specific pricing
        return 0.0

    def save_response(self, response: LLMResponse, output_path: Path) -> None:
        """Save LLM response to file.

        Args:
            response: LLM response to save
            output_path: Path to save response
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(response.model_dump(), f, indent=2)

    def load_response(self, response_path: Path) -> LLMResponse:
        """Load LLM response from file.

        Args:
            response_path: Path to response file

        Returns:
            LLMResponse object
        """
        with open(response_path, 'r') as f:
            data = json.load(f)

        return LLMResponse(**data)