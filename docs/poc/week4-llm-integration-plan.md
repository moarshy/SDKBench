# Week 4: LLM Integration and Testing Plan

## Overview

This document outlines the plan to integrate LLM providers (OpenRouter, Anthropic, OpenAI) into SDK-Bench to systematically test different language models' ability to generate correct SDK instrumentation code.

**Goal**: Create an automated pipeline that:
1. Takes SDK instrumentation tasks from Week 2 metadata
2. Generates solutions using various LLMs
3. Evaluates solutions using the Week 3 evaluation harness
4. Compares LLM performance across multiple dimensions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Testing Pipeline                          │
└─────────────────────────────────────────────────────────────────┘

Task Metadata (metadata.json)
         │
         ↓
┌────────────────────┐
│  Prompt Builder    │  ← SDK docs context
│                    │  ← Framework info
│                    │  ← Output format spec
└────────┬───────────┘
         ↓
┌────────────────────┐
│  LLM Provider      │  ← OpenRouter/Anthropic/OpenAI
│                    │  ← Model selection (Qwen, Claude, GPT-4)
│  - API calls       │  ← Temperature, max_tokens
│  - Retry logic     │
│  - Cost tracking   │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Response Parser    │
│                    │
│  - Extract code    │
│  - Identify files  │
│  - Validate format │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Solution Generator │
│                    │
│  - Create dirs     │
│  - Write files     │
│  - Save metadata   │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Evaluation Harness │  ← Week 3 pipeline
│                    │
│  - I-ACC           │
│  - C-COMP          │
│  - IPA             │
│  - F-CORR          │
│  - CQ              │
│  - SEM-SIM         │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Results Aggregator │
│                    │
│  - Score tables    │
│  - Comparisons     │
│  - Visualizations  │
└────────────────────┘
```

---

## Phase 1: LLM Integration Layer

### 1.1 Provider Abstraction

**File**: `sdkbench/llm/base.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Response from LLM provider."""

    content: str
    model: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str
    raw_response: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.total_tokens = 0
        self.total_cost = 0.0

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from prompt."""
        pass

    @abstractmethod
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for token usage."""
        pass

    def get_total_cost(self) -> float:
        """Get total cost of all API calls."""
        return self.total_cost

    def get_total_tokens(self) -> int:
        """Get total tokens used."""
        return self.total_tokens
```

**Key Features**:
- Abstract base class for all providers
- Standardized response format
- Token and cost tracking
- Async support for parallel calls

### 1.2 OpenRouter Provider

**File**: `sdkbench/llm/openrouter.py`

```python
import httpx
from typing import Optional
from sdkbench.llm.base import LLMProvider, LLMResponse


class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider supporting multiple models."""

    BASE_URL = "https://openrouter.ai/api/v1"

    # Pricing per 1M tokens (approximate, check openrouter.ai for latest)
    PRICING = {
        "qwen/qwen-2.5-72b-instruct": {"prompt": 0.35, "completion": 0.40},
        "anthropic/claude-3.5-sonnet": {"prompt": 3.0, "completion": 15.0},
        "openai/gpt-4": {"prompt": 30.0, "completion": 60.0},
        "openai/gpt-4o": {"prompt": 2.5, "completion": 10.0},
        "meta-llama/llama-3.1-70b-instruct": {"prompt": 0.35, "completion": 0.40},
    }

    def __init__(
        self,
        api_key: str,
        model: str,
        site_url: Optional[str] = None,
        app_name: Optional[str] = "SDK-Bench",
    ):
        super().__init__(api_key, model)
        self.site_url = site_url
        self.app_name = app_name

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using OpenRouter API."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        # Extract response
        choice = data["choices"][0]
        usage = data["usage"]

        # Track tokens and cost
        prompt_tokens = usage["prompt_tokens"]
        completion_tokens = usage["completion_tokens"]
        total_tokens = usage["total_tokens"]

        cost = self.calculate_cost(prompt_tokens, completion_tokens)
        self.total_tokens += total_tokens
        self.total_cost += cost

        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", self.model),
            tokens_used=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            finish_reason=choice["finish_reason"],
            raw_response=data,
        )

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on token usage."""
        if self.model not in self.PRICING:
            # Unknown model, return 0 or estimate
            return 0.0

        pricing = self.PRICING[self.model]
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]

        return prompt_cost + completion_cost
```

**Supported Models via OpenRouter**:
- `qwen/qwen-2.5-72b-instruct` - Qwen 2.5 72B (Alibaba)
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `openai/gpt-4` - GPT-4
- `openai/gpt-4o` - GPT-4o (optimized)
- `meta-llama/llama-3.1-70b-instruct` - Llama 3.1 70B
- Many more available at openrouter.ai

### 1.3 Direct Provider Implementations

**File**: `sdkbench/llm/anthropic.py` (for native Anthropic API)

```python
from anthropic import AsyncAnthropic
from sdkbench.llm.base import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    """Direct Anthropic API provider."""

    PRICING = {
        "claude-3-5-sonnet-20241022": {"prompt": 3.0, "completion": 15.0},
        "claude-3-opus-20240229": {"prompt": 15.0, "completion": 75.0},
    }

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate using native Anthropic API."""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )

        # Extract and track
        content = response.content[0].text
        prompt_tokens = response.usage.input_tokens
        completion_tokens = response.usage.output_tokens
        total_tokens = prompt_tokens + completion_tokens

        cost = self.calculate_cost(prompt_tokens, completion_tokens)
        self.total_tokens += total_tokens
        self.total_cost += cost

        return LLMResponse(
            content=content,
            model=response.model,
            tokens_used=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            finish_reason=response.stop_reason,
            raw_response=response.model_dump(),
        )

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on Anthropic pricing."""
        if self.model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[self.model]
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]

        return prompt_cost + completion_cost
```

**File**: `sdkbench/llm/openai.py` (similar structure for OpenAI)

### 1.4 Configuration

**File**: `sdkbench/llm/config.py`

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""

    provider: Literal["openrouter", "anthropic", "openai"]
    model: str
    api_key: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=100, le=8000)
    timeout: int = Field(default=120, ge=30, le=600)

    # OpenRouter specific
    site_url: Optional[str] = None
    app_name: Optional[str] = "SDK-Bench"

    # Retry settings
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=2.0, ge=0.1, le=60.0)

    class Config:
        extra = "forbid"


def create_provider(config: LLMConfig):
    """Factory function to create LLM provider from config."""
    if config.provider == "openrouter":
        from sdkbench.llm.openrouter import OpenRouterProvider
        return OpenRouterProvider(
            api_key=config.api_key,
            model=config.model,
            site_url=config.site_url,
            app_name=config.app_name,
        )
    elif config.provider == "anthropic":
        from sdkbench.llm.anthropic import AnthropicProvider
        return AnthropicProvider(
            api_key=config.api_key,
            model=config.model,
        )
    elif config.provider == "openai":
        from sdkbench.llm.openai import OpenAIProvider
        return OpenAIProvider(
            api_key=config.api_key,
            model=config.model,
        )
    else:
        raise ValueError(f"Unknown provider: {config.provider}")
```

---

## Phase 2: Prompt Engineering

### 2.1 Prompt Templates

**Directory**: `sdkbench/prompts/templates/`

#### Template: `init_task.txt`

```
# Task: Initialize {sdk_name} SDK in {framework}

## Context
You are integrating the {sdk_name} SDK into a {framework} application.

## SDK Information
- Package: {package_name} v{version}
- Documentation: {doc_url}

### Key Concepts
{sdk_concepts}

### Installation
{installation_instructions}

## Task Requirements

{task_description}

### Required Changes
{required_changes}

### File Locations
{file_locations}

### Expected Patterns
{expected_patterns}

## Framework Context
- Framework: {framework}
- Version: {framework_version}
- Architecture: {architecture}
{framework_specific_notes}

## Expected Output Format

Provide your solution as a series of file operations in the following format:

'''
FILE: path/to/file1.tsx
---
[complete file content here]
---

FILE: path/to/file2.ts
---
[complete file content here]
---

FILE: .env.local
---
[environment variables here]
---
'''

## Constraints

{constraints}

## Important Notes

- Provide COMPLETE file contents, not just snippets
- Include all necessary imports
- Follow {framework} conventions and best practices
- Use proper TypeScript types
- Include error handling where appropriate
- Do NOT include explanations or comments outside the file blocks
- Each file should be production-ready code
```

#### Template: `config_task.txt`

```
# Task: Configure {sdk_name} SDK in {framework}

## Context
You need to configure the {sdk_name} SDK in an existing {framework} application
where the SDK has already been initialized.

## Current Setup
{current_setup}

## Configuration Requirements

{config_description}

### Environment Variables
{env_vars_description}

### Dependencies
{dependencies_description}

### Configuration Files
{config_files_description}

## Expected Output Format

'''
FILE: path/to/file.ts
---
[complete file content]
---
'''

## Constraints

{constraints}
```

#### Template: `integration_task.txt`

```
# Task: Integrate {sdk_name} SDK Features

## Context
The {sdk_name} SDK is initialized and configured. You need to integrate
specific SDK features into the application.

## Integration Requirements

{integration_description}

### Features to Integrate
{features_list}

### Integration Points
{integration_points}

## Expected Output Format

'''
FILE: path/to/file.tsx
---
[complete file content]
---
'''

## Constraints

{constraints}
```

### 2.2 Prompt Builder

**File**: `sdkbench/prompts/builder.py`

```python
from pathlib import Path
from typing import Dict, Optional
import json


class PromptBuilder:
    """Build prompts for SDK instrumentation tasks."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = Path(templates_dir)
        self._templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load all prompt templates."""
        for template_file in self.templates_dir.glob("*.txt"):
            template_name = template_file.stem
            with open(template_file) as f:
                self._templates[template_name] = f.read()

    def build_prompt(
        self,
        task_metadata: Dict,
        include_docs: bool = True,
        include_examples: bool = False,
    ) -> str:
        """Build prompt from task metadata.

        Args:
            task_metadata: Task metadata from metadata.json
            include_docs: Include SDK documentation snippets
            include_examples: Include few-shot examples

        Returns:
            Complete prompt string
        """
        task_type = task_metadata.get("task_type", "init")

        # Select template
        template_name = self._get_template_name(task_type)
        if template_name not in self._templates:
            raise ValueError(f"Unknown template: {template_name}")

        template = self._templates[template_name]

        # Extract variables
        variables = self._extract_variables(task_metadata, include_docs)

        # Fill template
        prompt = template.format(**variables)

        # Optionally add examples
        if include_examples:
            examples = self._get_few_shot_examples(task_type)
            prompt = f"{prompt}\n\n## Examples\n\n{examples}"

        return prompt

    def _get_template_name(self, task_type: str) -> str:
        """Get template name from task type."""
        if task_type.startswith("task1_init"):
            return "init_task"
        elif task_type.startswith("task2_config"):
            return "config_task"
        elif task_type.startswith("task3_integration"):
            return "integration_task"
        elif task_type.startswith("task4_middleware"):
            return "middleware_task"
        else:
            return "init_task"  # default

    def _extract_variables(
        self,
        task_metadata: Dict,
        include_docs: bool
    ) -> Dict[str, str]:
        """Extract variables for template."""

        variables = {
            "sdk_name": task_metadata.get("sdk", "Clerk"),
            "framework": task_metadata.get("framework", "Next.js"),
            "package_name": "@clerk/nextjs",
            "version": "5.x",
            "task_description": task_metadata.get("description", ""),
        }

        # Add initialization-specific variables
        if "initialization" in task_metadata:
            init_data = task_metadata["initialization"]
            variables["file_locations"] = self._format_file_locations(init_data)
            variables["expected_patterns"] = self._format_patterns(init_data)

        # Add configuration-specific variables
        if "configuration" in task_metadata:
            config_data = task_metadata["configuration"]
            variables["env_vars_description"] = self._format_env_vars(config_data)
            variables["dependencies_description"] = self._format_dependencies(config_data)

        # Add SDK documentation
        if include_docs:
            variables["sdk_concepts"] = self._get_sdk_concepts()
            variables["installation_instructions"] = self._get_installation_instructions()

        # Framework-specific notes
        variables["framework_specific_notes"] = self._get_framework_notes(
            variables["framework"]
        )

        # Constraints
        variables["constraints"] = self._get_constraints(task_metadata)

        return variables

    def _format_file_locations(self, init_data: Dict) -> str:
        """Format file locations for prompt."""
        locations = []
        if "file" in init_data:
            locations.append(f"- Initialize in: {init_data['file']}")
        return "\n".join(locations)

    def _format_patterns(self, init_data: Dict) -> str:
        """Format expected patterns for prompt."""
        patterns = []
        if "pattern" in init_data:
            pattern_data = init_data["pattern"]
            pattern_type = pattern_data.get("type", "")

            if pattern_type == "jsx_component":
                patterns.append("- Use JSX component pattern")
                patterns.append(f"  Component: {pattern_data.get('component', '')}")
            elif pattern_type == "function_call":
                patterns.append("- Use function call pattern")
                patterns.append(f"  Function: {pattern_data.get('function', '')}")

        return "\n".join(patterns)

    def _get_sdk_concepts(self) -> str:
        """Get SDK concepts documentation."""
        # In a real implementation, this would load from a documentation database
        return """
Clerk is an authentication and user management SDK.

Key concepts:
- ClerkProvider: React component that provides authentication context
- auth(): Server-side function to get authentication state
- currentUser(): Get the current user object
- clerkMiddleware: Middleware for protecting routes
"""

    def _get_installation_instructions(self) -> str:
        """Get installation instructions."""
        return """
```bash
npm install @clerk/nextjs
```
"""

    def _get_framework_notes(self, framework: str) -> str:
        """Get framework-specific notes."""
        notes = {
            "Next.js": """
- Use App Router conventions (app/ directory)
- Server Components by default
- 'use client' directive for Client Components
- Environment variables accessible via process.env
""",
            "React": """
- Standard React component conventions
- Use hooks for state management
- Environment variables via process.env or import.meta.env
"""
        }
        return notes.get(framework, "")

    def _get_constraints(self, task_metadata: Dict) -> str:
        """Get constraints for the task."""
        constraints = []

        # Version-specific constraints
        constraints.append("- Use Clerk v5 syntax (not v4)")
        constraints.append("- Use clerkMiddleware, not authMiddleware")
        constraints.append("- Use auth() function, not getAuth()")

        # File-specific constraints
        if "initialization" in task_metadata:
            init_data = task_metadata["initialization"]
            if "file" in init_data:
                constraints.append(f"- Initialize in {init_data['file']}")

        return "\n".join(constraints)
```

**Key Features**:
- Template-based prompt generation
- Dynamic variable extraction from metadata
- Optional SDK documentation injection
- Framework-specific guidance
- Clear output format specification

---

## Phase 3: Solution Generation

### 3.1 Response Parser

**File**: `sdkbench/generation/parser.py`

```python
import re
from typing import Dict, List, Tuple
from pathlib import Path


class ResponseParser:
    """Parse LLM responses to extract file contents."""

    @staticmethod
    def parse_response(response_text: str) -> Dict[str, str]:
        """Extract file path -> content mappings from LLM response.

        Supports multiple formats:
        1. Markdown with FILE: headers
        2. Code blocks with file paths
        3. XML-style file tags

        Args:
            response_text: Raw LLM response

        Returns:
            Dict mapping file paths to contents
        """
        files = {}

        # Try format 1: FILE: path --- content ---
        files_format1 = ResponseParser._parse_format1(response_text)
        if files_format1:
            files.update(files_format1)

        # Try format 2: ```path ... ```
        files_format2 = ResponseParser._parse_format2(response_text)
        if files_format2:
            files.update(files_format2)

        # Try format 3: <file path="...">...</file>
        files_format3 = ResponseParser._parse_format3(response_text)
        if files_format3:
            files.update(files_format3)

        return files

    @staticmethod
    def _parse_format1(text: str) -> Dict[str, str]:
        """Parse format: FILE: path\\n---\\ncontent\\n---"""
        files = {}

        # Pattern: FILE: path followed by --- content ---
        pattern = r'FILE:\s*([^\n]+)\n---\n(.*?)\n---'
        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            file_path = match.group(1).strip()
            content = match.group(2)
            files[file_path] = content

        return files

    @staticmethod
    def _parse_format2(text: str) -> Dict[str, str]:
        """Parse format: ```path\\ncontent\\n```"""
        files = {}

        # Pattern: ```path or ```typescript path
        pattern = r'```(?:\w+)?\s*([^\n]+\.(?:tsx?|jsx?|json|env.*|md))\n(.*?)```'
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            file_path = match.group(1).strip()
            content = match.group(2)
            files[file_path] = content

        return files

    @staticmethod
    def _parse_format3(text: str) -> Dict[str, str]:
        """Parse format: <file path='...'>content</file>"""
        files = {}

        # Pattern: <file path="..." or path='...'>
        pattern = r'<file\s+path=["\']([^"\']+)["\']\s*>(.*?)</file>'
        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            file_path = match.group(1).strip()
            content = match.group(2)
            files[file_path] = content

        return files

    @staticmethod
    def validate_files(files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate extracted files.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        if not files:
            errors.append("No files extracted from response")

        for file_path, content in files.items():
            # Check path is reasonable
            if ".." in file_path:
                errors.append(f"Invalid path (contains ..): {file_path}")

            if file_path.startswith("/"):
                errors.append(f"Absolute paths not allowed: {file_path}")

            # Check content not empty
            if not content.strip():
                errors.append(f"Empty content for file: {file_path}")

            # Check for common mistakes
            if "```" in content:
                errors.append(f"File contains code fence markers: {file_path}")

        return len(errors) == 0, errors
```

### 3.2 Solution Generator

**File**: `sdkbench/generation/generator.py`

```python
import asyncio
from pathlib import Path
from typing import Dict, Optional
import json
import time
from datetime import datetime

from pydantic import BaseModel

from sdkbench.llm.base import LLMProvider
from sdkbench.prompts.builder import PromptBuilder
from sdkbench.generation.parser import ResponseParser
from sdkbench.core import GroundTruth


class GenerationResult(BaseModel):
    """Result of solution generation."""

    task_id: str
    model: str
    success: bool
    solution_dir: Path
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    generation_time: float
    cost: float
    error: Optional[str] = None
    files_generated: int = 0

    class Config:
        arbitrary_types_allowed = True


class SolutionGenerator:
    """Generate SDK instrumentation solutions using LLMs."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        prompt_builder: PromptBuilder,
        output_base_dir: Path,
    ):
        self.llm_provider = llm_provider
        self.prompt_builder = prompt_builder
        self.output_base_dir = Path(output_base_dir)

    async def generate_solution(
        self,
        task_id: str,
        metadata_path: Path,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> GenerationResult:
        """Generate solution for a single task.

        Args:
            task_id: Task identifier
            metadata_path: Path to metadata.json
            temperature: LLM temperature
            max_tokens: Max tokens for generation

        Returns:
            GenerationResult with details
        """
        start_time = time.time()

        try:
            # Load metadata
            ground_truth = GroundTruth(metadata_path)
            task_metadata = ground_truth.metadata

            # Build prompt
            prompt = self.prompt_builder.build_prompt(
                task_metadata,
                include_docs=True,
                include_examples=False,
            )

            # Generate from LLM
            response = await self.llm_provider.generate(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Parse response
            files = ResponseParser.parse_response(response.content)
            is_valid, errors = ResponseParser.validate_files(files)

            if not is_valid:
                error_msg = "; ".join(errors)
                return GenerationResult(
                    task_id=task_id,
                    model=response.model,
                    success=False,
                    solution_dir=self.output_base_dir / task_id,
                    tokens_used=response.tokens_used,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    generation_time=time.time() - start_time,
                    cost=self.llm_provider.total_cost,
                    error=error_msg,
                )

            # Create solution directory
            solution_dir = self.output_base_dir / task_id
            solution_dir.mkdir(parents=True, exist_ok=True)

            # Write files
            for file_path, content in files.items():
                full_path = solution_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, 'w') as f:
                    f.write(content)

            # Save generation metadata
            gen_metadata = {
                "task_id": task_id,
                "model": response.model,
                "timestamp": datetime.now().isoformat(),
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.tokens_used,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "files_generated": list(files.keys()),
            }

            with open(solution_dir / "generation.json", 'w') as f:
                json.dump(gen_metadata, f, indent=2)

            # Copy metadata.json to solution dir for evaluation
            import shutil
            shutil.copy(metadata_path, solution_dir / "metadata.json")

            generation_time = time.time() - start_time

            return GenerationResult(
                task_id=task_id,
                model=response.model,
                success=True,
                solution_dir=solution_dir,
                tokens_used=response.tokens_used,
                prompt_tokens=response.prompt_tokens,
                completion_tokens=response.completion_tokens,
                generation_time=generation_time,
                cost=self.llm_provider.total_cost,
                files_generated=len(files),
            )

        except Exception as e:
            return GenerationResult(
                task_id=task_id,
                model=self.llm_provider.model,
                success=False,
                solution_dir=self.output_base_dir / task_id,
                tokens_used=0,
                prompt_tokens=0,
                completion_tokens=0,
                generation_time=time.time() - start_time,
                cost=0.0,
                error=str(e),
            )

    async def generate_batch(
        self,
        task_ids: list[str],
        metadata_paths: list[Path],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        max_concurrent: int = 3,
    ) -> list[GenerationResult]:
        """Generate solutions for multiple tasks.

        Args:
            task_ids: List of task identifiers
            metadata_paths: List of metadata paths
            temperature: LLM temperature
            max_tokens: Max tokens per generation
            max_concurrent: Max concurrent API calls

        Returns:
            List of GenerationResults
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_with_semaphore(task_id, metadata_path):
            async with semaphore:
                return await self.generate_solution(
                    task_id,
                    metadata_path,
                    temperature,
                    max_tokens,
                )

        tasks = [
            generate_with_semaphore(task_id, metadata_path)
            for task_id, metadata_path in zip(task_ids, metadata_paths)
        ]

        results = await asyncio.gather(*tasks)
        return results
```

---

## Phase 4: Batch Testing Pipeline

### 4.1 Test Runner

**File**: `sdkbench/testing/runner.py`

```python
import asyncio
from pathlib import Path
from typing import List, Optional, Dict
import yaml
import json
from datetime import datetime

from pydantic import BaseModel

from sdkbench.llm.config import LLMConfig, create_provider
from sdkbench.prompts.builder import PromptBuilder
from sdkbench.generation.generator import SolutionGenerator, GenerationResult
from sdkbench.evaluator import Evaluator
from sdkbench.core import EvaluationResult


class ExperimentConfig(BaseModel):
    """Configuration for an LLM testing experiment."""

    name: str
    description: str
    models: List[LLMConfig]
    tasks: List[str]
    samples_dir: Path
    output_dir: Path
    parallel: bool = True
    max_workers: int = 3
    temperature: float = 0.7
    max_tokens: int = 4000
    run_build: bool = False
    run_tests: bool = False

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_yaml(cls, config_path: Path) -> "ExperimentConfig":
        """Load experiment config from YAML."""
        with open(config_path) as f:
            data = yaml.safe_load(f)

        experiment = data["experiment"]

        # Parse models
        models = [LLMConfig(**model_data) for model_data in data["models"]]

        # Parse options
        options = data.get("options", {})

        return cls(
            name=experiment["name"],
            description=experiment["description"],
            models=models,
            tasks=data["tasks"],
            samples_dir=Path(data.get("samples_dir", "samples")),
            output_dir=Path(data.get("output_dir", "experiments/results")),
            parallel=options.get("parallel", True),
            max_workers=options.get("max_workers", 3),
            temperature=options.get("temperature", 0.7),
            max_tokens=options.get("max_tokens", 4000),
            run_build=options.get("run_build", False),
            run_tests=options.get("run_tests", False),
        )


class ExperimentResult(BaseModel):
    """Results from an experiment run."""

    experiment_name: str
    timestamp: str
    models_tested: int
    tasks_tested: int
    total_generations: int
    successful_generations: int
    total_evaluations: int
    successful_evaluations: int
    total_cost: float
    total_time: float
    results: Dict[str, Dict[str, Dict]]  # model -> task -> {generation, evaluation}

    class Config:
        arbitrary_types_allowed = True


class LLMTestRunner:
    """Run LLM testing experiments."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.prompt_builder = PromptBuilder(
            Path(__file__).parent.parent / "prompts" / "templates"
        )

    async def run_experiment(self) -> ExperimentResult:
        """Run complete experiment: generate + evaluate for all models and tasks."""

        print(f"Starting experiment: {self.config.name}")
        print(f"Models: {len(self.config.models)}")
        print(f"Tasks: {len(self.config.tasks)}")
        print("=" * 60)

        start_time = asyncio.get_event_loop().time()

        # Create output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Save experiment metadata
        self._save_experiment_metadata()

        # Run for each model
        all_results = {}
        total_cost = 0.0
        successful_generations = 0
        successful_evaluations = 0

        for i, model_config in enumerate(self.config.models, 1):
            print(f"\n[{i}/{len(self.config.models)}] Testing model: {model_config.model}")
            print("-" * 60)

            model_results = await self._test_model(model_config)
            all_results[model_config.model] = model_results

            # Aggregate stats
            for task_result in model_results.values():
                if task_result["generation"]["success"]:
                    successful_generations += 1
                    total_cost += task_result["generation"]["cost"]

                if task_result["evaluation"] and task_result["evaluation"]["success"]:
                    successful_evaluations += 1

        total_time = asyncio.get_event_loop().time() - start_time

        # Create experiment result
        experiment_result = ExperimentResult(
            experiment_name=self.config.name,
            timestamp=datetime.now().isoformat(),
            models_tested=len(self.config.models),
            tasks_tested=len(self.config.tasks),
            total_generations=len(self.config.models) * len(self.config.tasks),
            successful_generations=successful_generations,
            total_evaluations=successful_generations,  # Only evaluate successful generations
            successful_evaluations=successful_evaluations,
            total_cost=total_cost,
            total_time=total_time,
            results=all_results,
        )

        # Save results
        self._save_results(experiment_result)

        print("\n" + "=" * 60)
        print("Experiment Complete!")
        print(f"Successful generations: {successful_generations}/{experiment_result.total_generations}")
        print(f"Successful evaluations: {successful_evaluations}/{successful_generations}")
        print(f"Total cost: ${total_cost:.2f}")
        print(f"Total time: {total_time:.1f}s")

        return experiment_result

    async def _test_model(self, model_config: LLMConfig) -> Dict[str, Dict]:
        """Test a single model on all tasks."""

        # Create provider
        provider = create_provider(model_config)

        # Create output directory for this model
        model_output_dir = self.config.output_dir / model_config.model.replace("/", "_")
        model_output_dir.mkdir(parents=True, exist_ok=True)

        # Create generator
        generator = SolutionGenerator(
            llm_provider=provider,
            prompt_builder=self.prompt_builder,
            output_base_dir=model_output_dir,
        )

        # Prepare task metadata paths
        metadata_paths = [
            self.config.samples_dir / task_id / "expected" / "metadata.json"
            for task_id in self.config.tasks
        ]

        # Generate solutions (possibly in parallel)
        if self.config.parallel:
            generation_results = await generator.generate_batch(
                task_ids=self.config.tasks,
                metadata_paths=metadata_paths,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                max_concurrent=self.config.max_workers,
            )
        else:
            generation_results = []
            for task_id, metadata_path in zip(self.config.tasks, metadata_paths):
                result = await generator.generate_solution(
                    task_id,
                    metadata_path,
                    self.config.temperature,
                    self.config.max_tokens,
                )
                generation_results.append(result)

        # Evaluate successful generations
        model_results = {}

        for gen_result in generation_results:
            print(f"  {gen_result.task_id}: ", end="")

            if not gen_result.success:
                print(f"❌ Generation failed: {gen_result.error}")
                model_results[gen_result.task_id] = {
                    "generation": gen_result.model_dump(),
                    "evaluation": None,
                }
                continue

            print(f"✅ Generated ({gen_result.files_generated} files, {gen_result.tokens_used} tokens, ${gen_result.cost:.3f})")

            # Evaluate
            try:
                evaluator = Evaluator(gen_result.solution_dir)

                if self.config.run_build or self.config.run_tests:
                    eval_result = evaluator.evaluate(
                        run_build=self.config.run_build,
                        run_tests=self.config.run_tests,
                    )
                else:
                    eval_result = evaluator.evaluate_quick()

                print(f"     Evaluation: {eval_result.overall_score:.1f}%")

                model_results[gen_result.task_id] = {
                    "generation": gen_result.model_dump(),
                    "evaluation": {
                        "success": True,
                        "overall_score": eval_result.overall_score,
                        "i_acc": eval_result.i_acc.score if eval_result.i_acc else None,
                        "c_comp": eval_result.c_comp.score if eval_result.c_comp else None,
                        "ipa": eval_result.ipa.f1_score * 100 if eval_result.ipa else None,
                        "f_corr": eval_result.f_corr.score if eval_result.f_corr else None,
                        "cq": eval_result.cq.score if eval_result.cq else None,
                        "sem_sim": eval_result.sem_sim.score * 100 if eval_result.sem_sim else None,
                    }
                }

                # Save detailed evaluation
                evaluator.save_results(
                    gen_result.solution_dir / "evaluation.json",
                    detailed=True,
                )

            except Exception as e:
                print(f"     ❌ Evaluation failed: {e}")
                model_results[gen_result.task_id] = {
                    "generation": gen_result.model_dump(),
                    "evaluation": {"success": False, "error": str(e)},
                }

        return model_results

    def _save_experiment_metadata(self):
        """Save experiment configuration."""
        metadata = {
            "name": self.config.name,
            "description": self.config.description,
            "timestamp": datetime.now().isoformat(),
            "models": [
                {
                    "provider": m.provider,
                    "model": m.model,
                    "temperature": m.temperature,
                    "max_tokens": m.max_tokens,
                }
                for m in self.config.models
            ],
            "tasks": self.config.tasks,
            "options": {
                "parallel": self.config.parallel,
                "max_workers": self.config.max_workers,
                "run_build": self.config.run_build,
                "run_tests": self.config.run_tests,
            }
        }

        with open(self.config.output_dir / "experiment.json", 'w') as f:
            json.dump(metadata, f, indent=2)

    def _save_results(self, experiment_result: ExperimentResult):
        """Save experiment results."""
        with open(self.config.output_dir / "results.json", 'w') as f:
            json.dump(experiment_result.model_dump(), f, indent=2, default=str)
```

### 4.2 Experiment Configuration

**File**: `experiments/config.yaml`

```yaml
experiment:
  name: "clerk-sdk-instrumentation-v1"
  description: "Evaluate LLM performance on Clerk SDK instrumentation tasks"

# Samples directory (where Week 2 tasks are stored)
samples_dir: "samples"

# Output directory for experiment results
output_dir: "experiments/results/clerk-v1"

# Models to test
models:
  - provider: "openrouter"
    model: "qwen/qwen-2.5-72b-instruct"
    api_key: "${OPENROUTER_API_KEY}"
    temperature: 0.7
    max_tokens: 4000
    max_retries: 3

  - provider: "openrouter"
    model: "anthropic/claude-3.5-sonnet"
    api_key: "${OPENROUTER_API_KEY}"
    temperature: 0.7
    max_tokens: 4000

  - provider: "openrouter"
    model: "openai/gpt-4"
    api_key: "${OPENROUTER_API_KEY}"
    temperature: 0.7
    max_tokens: 4000

  - provider: "openrouter"
    model: "meta-llama/llama-3.1-70b-instruct"
    api_key: "${OPENROUTER_API_KEY}"
    temperature: 0.7
    max_tokens: 4000

# Tasks to evaluate (task IDs from Week 2)
tasks:
  - "task1_init_001"
  - "task1_init_002"
  - "task2_config_001"
  - "task2_config_002"
  - "task3_integration_001"
  - "task4_middleware_001"

# Execution options
options:
  parallel: true          # Run tasks in parallel
  max_workers: 3          # Max concurrent API calls
  temperature: 0.7        # Default temperature
  max_tokens: 4000        # Default max tokens
  run_build: false        # Run builds during evaluation (slower)
  run_tests: false        # Run tests during evaluation (slower)
  retry_failures: true    # Retry failed generations
  save_intermediate: true # Save intermediate results
```

---

## Phase 5: Results Analysis

### 5.1 Results Aggregator

**File**: `sdkbench/analysis/aggregator.py`

```python
from pathlib import Path
from typing import Dict, List, Optional
import json
import pandas as pd
from dataclasses import dataclass


@dataclass
class ModelPerformance:
    """Performance metrics for a single model."""
    model_name: str
    avg_overall_score: float
    avg_i_acc: float
    avg_c_comp: float
    avg_ipa: float
    avg_f_corr: float
    avg_cq: float
    avg_sem_sim: float
    success_rate: float
    total_cost: float
    avg_generation_time: float
    avg_tokens: int


class ResultsAggregator:
    """Aggregate and analyze experiment results."""

    def __init__(self, experiment_dir: Path):
        self.experiment_dir = Path(experiment_dir)
        self.results = self._load_results()
        self.metadata = self._load_metadata()

    def _load_results(self) -> Dict:
        """Load results.json from experiment directory."""
        results_path = self.experiment_dir / "results.json"
        with open(results_path) as f:
            return json.load(f)

    def _load_metadata(self) -> Dict:
        """Load experiment.json metadata."""
        metadata_path = self.experiment_dir / "experiment.json"
        with open(metadata_path) as f:
            return json.load(f)

    def get_model_performance(self, model_name: str) -> ModelPerformance:
        """Calculate performance metrics for a model."""
        model_results = self.results["results"][model_name]

        # Collect scores
        overall_scores = []
        i_acc_scores = []
        c_comp_scores = []
        ipa_scores = []
        f_corr_scores = []
        cq_scores = []
        sem_sim_scores = []

        successful = 0
        total_cost = 0.0
        generation_times = []
        tokens = []

        for task_id, task_result in model_results.items():
            gen = task_result["generation"]
            evalu = task_result["evaluation"]

            if gen["success"]:
                successful += 1
                total_cost += gen["cost"]
                generation_times.append(gen["generation_time"])
                tokens.append(gen["tokens_used"])

            if evalu and evalu.get("success"):
                overall_scores.append(evalu["overall_score"])
                if evalu["i_acc"] is not None:
                    i_acc_scores.append(evalu["i_acc"])
                if evalu["c_comp"] is not None:
                    c_comp_scores.append(evalu["c_comp"])
                if evalu["ipa"] is not None:
                    ipa_scores.append(evalu["ipa"])
                if evalu["f_corr"] is not None:
                    f_corr_scores.append(evalu["f_corr"])
                if evalu["cq"] is not None:
                    cq_scores.append(evalu["cq"])
                if evalu["sem_sim"] is not None:
                    sem_sim_scores.append(evalu["sem_sim"])

        return ModelPerformance(
            model_name=model_name,
            avg_overall_score=sum(overall_scores) / len(overall_scores) if overall_scores else 0.0,
            avg_i_acc=sum(i_acc_scores) / len(i_acc_scores) if i_acc_scores else 0.0,
            avg_c_comp=sum(c_comp_scores) / len(c_comp_scores) if c_comp_scores else 0.0,
            avg_ipa=sum(ipa_scores) / len(ipa_scores) if ipa_scores else 0.0,
            avg_f_corr=sum(f_corr_scores) / len(f_corr_scores) if f_corr_scores else 0.0,
            avg_cq=sum(cq_scores) / len(cq_scores) if cq_scores else 0.0,
            avg_sem_sim=sum(sem_sim_scores) / len(sem_sim_scores) if sem_sim_scores else 0.0,
            success_rate=successful / len(model_results) * 100,
            total_cost=total_cost,
            avg_generation_time=sum(generation_times) / len(generation_times) if generation_times else 0.0,
            avg_tokens=sum(tokens) // len(tokens) if tokens else 0,
        )

    def generate_comparison_table(self) -> pd.DataFrame:
        """Generate comparison table of all models."""

        performances = [
            self.get_model_performance(model_name)
            for model_name in self.results["results"].keys()
        ]

        data = {
            "Model": [p.model_name for p in performances],
            "Overall": [f"{p.avg_overall_score:.1f}%" for p in performances],
            "I-ACC": [f"{p.avg_i_acc:.1f}%" for p in performances],
            "C-COMP": [f"{p.avg_c_comp:.1f}%" for p in performances],
            "IPA": [f"{p.avg_ipa:.1f}%" for p in performances],
            "F-CORR": [f"{p.avg_f_corr:.1f}%" for p in performances],
            "CQ": [f"{p.avg_cq:.1f}%" for p in performances],
            "SEM-SIM": [f"{p.avg_sem_sim:.1f}%" for p in performances],
            "Success": [f"{p.success_rate:.0f}%" for p in performances],
            "Cost": [f"${p.total_cost:.2f}" for p in performances],
            "Time": [f"{p.avg_generation_time:.1f}s" for p in performances],
        }

        return pd.DataFrame(data)

    def generate_summary_report(self) -> str:
        """Generate text summary report."""

        report = []
        report.append("=" * 70)
        report.append(f"Experiment: {self.results['experiment_name']}")
        report.append("=" * 70)
        report.append(f"Timestamp: {self.results['timestamp']}")
        report.append(f"Models tested: {self.results['models_tested']}")
        report.append(f"Tasks tested: {self.results['tasks_tested']}")
        report.append(f"Successful generations: {self.results['successful_generations']}/{self.results['total_generations']}")
        report.append(f"Total cost: ${self.results['total_cost']:.2f}")
        report.append(f"Total time: {self.results['total_time']:.1f}s")
        report.append("")

        # Model comparison table
        df = self.generate_comparison_table()
        report.append("Model Performance Comparison:")
        report.append("-" * 70)
        report.append(df.to_string(index=False))
        report.append("")

        # Best performers
        performances = [
            self.get_model_performance(model_name)
            for model_name in self.results["results"].keys()
        ]

        best_overall = max(performances, key=lambda p: p.avg_overall_score)
        best_cost = min(performances, key=lambda p: p.total_cost)
        best_speed = min(performances, key=lambda p: p.avg_generation_time)

        report.append("Best Performers:")
        report.append(f"  Highest Overall Score: {best_overall.model_name} ({best_overall.avg_overall_score:.1f}%)")
        report.append(f"  Lowest Cost: {best_cost.model_name} (${best_cost.total_cost:.2f})")
        report.append(f"  Fastest: {best_speed.model_name} ({best_speed.avg_generation_time:.1f}s)")
        report.append("")

        return "\n".join(report)

    def identify_failure_patterns(self) -> Dict[str, List[str]]:
        """Identify common failure patterns for each model."""

        failures = {}

        for model_name, model_results in self.results["results"].items():
            model_failures = []

            for task_id, task_result in model_results.items():
                gen = task_result["generation"]
                evalu = task_result["evaluation"]

                if not gen["success"]:
                    model_failures.append({
                        "task": task_id,
                        "phase": "generation",
                        "error": gen.get("error", "Unknown"),
                    })
                elif evalu and not evalu.get("success"):
                    model_failures.append({
                        "task": task_id,
                        "phase": "evaluation",
                        "error": evalu.get("error", "Unknown"),
                    })
                elif evalu and evalu.get("success"):
                    # Check for low scores
                    if evalu["overall_score"] < 50:
                        model_failures.append({
                            "task": task_id,
                            "phase": "quality",
                            "error": f"Low overall score: {evalu['overall_score']:.1f}%",
                        })

            failures[model_name] = model_failures

        return failures

    def export_to_csv(self, output_path: Path):
        """Export results to CSV."""
        df = self.generate_comparison_table()
        df.to_csv(output_path, index=False)
```

---

## Implementation Timeline

### **Week 4: Full Implementation (7 days)**

#### **Day 1-2: LLM Integration Foundation**
- ✅ Create `sdkbench/llm/` module
- ✅ Implement `base.py` with abstract provider
- ✅ Implement `openrouter.py` provider
- ✅ Implement `config.py` for configuration
- ✅ Test basic API calls with Qwen model

#### **Day 3: Prompt Engineering**
- ✅ Create `sdkbench/prompts/` module
- ✅ Write prompt templates (init, config, integration, middleware)
- ✅ Implement `PromptBuilder` class
- ✅ Test prompt generation from metadata

#### **Day 4: Solution Generation**
- ✅ Create `sdkbench/generation/` module
- ✅ Implement `ResponseParser` for multiple formats
- ✅ Implement `SolutionGenerator`
- ✅ Test end-to-end generation on sample task

#### **Day 5-6: Batch Testing Pipeline**
- ✅ Create `sdkbench/testing/` module
- ✅ Implement `LLMTestRunner`
- ✅ Implement experiment configuration (YAML)
- ✅ Add parallel execution support
- ✅ Test complete pipeline on multiple tasks

#### **Day 7: Analysis and CLI**
- ✅ Create `sdkbench/analysis/` module
- ✅ Implement `ResultsAggregator`
- ✅ Create CLI scripts (`generate.py`, `run_experiment.py`, `analyze.py`)
- ✅ Generate sample experiment report
- ✅ Documentation and examples

---

## CLI Usage Examples

### Generate Solution for Single Task

```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Generate solution
uv run generate \
  --task task1_init_001 \
  --model qwen/qwen-2.5-72b-instruct \
  --provider openrouter \
  --output generations/qwen/
```

### Run Full Experiment

```bash
# Run experiment with config file
uv run experiment --config experiments/config.yaml

# Quick mode (no build/tests, faster)
uv run experiment --config experiments/config.yaml --quick

# Resume failed experiment
uv run experiment --config experiments/config.yaml --resume
```

### Analyze Results

```bash
# Generate analysis report
uv run analyze experiments/results/clerk-v1/ \
  --report experiments/results/clerk-v1/report.html

# Export to CSV
uv run analyze experiments/results/clerk-v1/ \
  --csv experiments/results/clerk-v1/comparison.csv

# Compare multiple experiments
uv run analyze --compare \
  experiments/results/clerk-v1/ \
  experiments/results/clerk-v2/
```

---

## Expected Results

### Sample Output

```
╔═══════════════════════════════════════════════════════════════════╗
║           Clerk SDK Instrumentation - LLM Performance             ║
╠═══════════════════════════════════════════════════════════════════╣
║ Experiment: clerk-sdk-instrumentation-v1                          ║
║ Tasks: 6 tasks across 4 task types                                ║
║ Models: 4 models tested                                           ║
╚═══════════════════════════════════════════════════════════════════╝

┌────────────────────────────┬─────────┬─────────┬──────────┬───────┐
│ Model                      │ Overall │ Success │ Cost     │ Time  │
├────────────────────────────┼─────────┼─────────┼──────────┼───────┤
│ qwen/qwen-2.5-72b-instruct │  87.3%  │  95%    │  $0.42   │  45s  │
│ anthropic/claude-3.5-sonnet│  92.1%  │  100%   │  $1.23   │  38s  │
│ openai/gpt-4               │  89.5%  │  98%    │  $2.15   │  52s  │
│ meta-llama/llama-3.1-70b   │  84.7%  │  90%    │  $0.38   │  50s  │
└────────────────────────────┴─────────┴─────────┴──────────┴───────┘

Metric Breakdown:
┌────────────┬──────┬──────┬──────┬──────┬──────┬────────┐
│ Model      │ I-ACC│C-COMP│ IPA  │F-CORR│  CQ  │SEM-SIM │
├────────────┼──────┼──────┼──────┼──────┼──────┼────────┤
│ Qwen 2.5   │ 85.2 │ 91.3 │ 82.1 │ 88.9 │ 86.5 │  89.8  │
│ Claude 3.5 │ 94.1 │ 95.2 │ 88.9 │ 93.4 │ 91.8 │  89.1  │
│ GPT-4      │ 88.7 │ 92.4 │ 85.3 │ 91.2 │ 89.1 │  90.5  │
│ Llama 3.1  │ 82.5 │ 89.1 │ 79.8 │ 85.7 │ 83.9 │  87.2  │
└────────────┴──────┴──────┴──────┴──────┴──────┴────────┘

Best Performers:
  🥇 Highest Score: Claude 3.5 Sonnet (92.1%)
  💰 Best Value: Llama 3.1 70B ($0.38, 84.7%)
  ⚡ Fastest: Claude 3.5 Sonnet (38s avg)

Insights:
  • Claude 3.5 leads in most metrics but costs 3x more than Qwen
  • Qwen 2.5 offers excellent price/performance ratio
  • All models struggle with IPA (integration points) - avg 84%
  • Code quality (CQ) scores are consistently high across all models
```

---

## Key Design Decisions

1. **Async/Await Architecture**: All LLM calls use async for parallel execution
2. **Provider Abstraction**: Easy to add new LLM providers (Gemini, Cohere, etc.)
3. **Multiple Response Formats**: Parser handles various LLM output styles
4. **Cost Tracking**: Track API costs at every level for budget management
5. **Incremental Saving**: Save results as they complete to enable resuming
6. **YAML Configuration**: Human-readable experiment configuration
7. **Detailed Metadata**: Save generation and evaluation metadata for analysis
8. **Flexible Evaluation**: Support both quick (static) and full (build+tests) evaluation

---

## Next Steps After Implementation

1. **Validate Pipeline**: Test on sample tasks with known-good solutions
2. **Tune Prompts**: Iterate on prompt templates based on initial results
3. **Expand Model Coverage**: Add more models (Gemini, Cohere, DeepSeek, etc.)
4. **Optimize Costs**: Implement caching, prompt compression
5. **Add Visualizations**: Create charts and graphs for better analysis
6. **Multi-turn Refinement**: Allow LLMs to iterate on failed attempts
7. **Few-shot Learning**: Add example-based prompts for better performance

---

## Questions & Considerations

### Prompt Strategy
- **Question**: Include few-shot examples?
- **Recommendation**: Start without, add if needed (saves tokens/cost)

### Output Format
- **Question**: Structured (JSON) or natural (Markdown)?
- **Recommendation**: Markdown with clear delimiters (easier for LLMs)

### Validation
- **Question**: Validate syntax before evaluation?
- **Recommendation**: Yes - add basic TypeScript syntax check

### Iteration
- **Question**: Allow multi-turn refinement?
- **Recommendation**: Phase 2 feature - adds complexity

### Budget
- **Question**: Set spending limits?
- **Recommendation**: Yes - add max_cost parameter to config

### Parallelism
- **Question**: How many concurrent calls?
- **Recommendation**: Start with 3, tune based on API rate limits

---

## File Structure Summary

```
sdkbench/
├── llm/
│   ├── __init__.py
│   ├── base.py              # LLMProvider, LLMResponse
│   ├── openrouter.py        # OpenRouter implementation
│   ├── anthropic.py         # Anthropic implementation
│   ├── openai.py            # OpenAI implementation
│   └── config.py            # LLMConfig, create_provider()
│
├── prompts/
│   ├── __init__.py
│   ├── builder.py           # PromptBuilder
│   └── templates/
│       ├── init_task.txt
│       ├── config_task.txt
│       ├── integration_task.txt
│       └── middleware_task.txt
│
├── generation/
│   ├── __init__.py
│   ├── parser.py            # ResponseParser
│   └── generator.py         # SolutionGenerator, GenerationResult
│
├── testing/
│   ├── __init__.py
│   └── runner.py            # LLMTestRunner, ExperimentConfig
│
└── analysis/
    ├── __init__.py
    ├── aggregator.py        # ResultsAggregator, ModelPerformance
    └── visualizer.py        # (future: charts and graphs)

scripts/
├── generate.py              # CLI: generate single solution
├── run_experiment.py        # CLI: run full experiment
└── analyze.py               # CLI: analyze results

experiments/
├── config.yaml              # Experiment configuration
└── results/
    └── clerk-v1/
        ├── experiment.json       # Experiment metadata
        ├── results.json          # Aggregated results
        ├── report.html           # HTML report
        ├── comparison.csv        # CSV export
        └── qwen_qwen-2.5-72b-instruct/
            ├── task1_init_001/
            │   ├── app/
            │   │   └── layout.tsx
            │   ├── .env.local
            │   ├── generation.json    # Generation metadata
            │   ├── evaluation.json    # Evaluation results
            │   └── metadata.json      # Task metadata (copied)
            └── task1_init_002/
                └── ...
```

---

## Success Criteria

Week 4 is successful if:

1. ✅ Can generate solutions using OpenRouter (Qwen, Claude, GPT-4)
2. ✅ Generated solutions are evaluated automatically
3. ✅ Results are aggregated and compared across models
4. ✅ Complete experiment can be run with single command
5. ✅ Total cost is tracked and reasonable (<$10 for full experiment)
6. ✅ Results show clear performance differences between models
7. ✅ Analysis provides actionable insights

---

## Budget Estimate

### Cost Per Task (approximate)

| Model | Prompt Tokens | Completion Tokens | Cost/Task | 6 Tasks |
|-------|---------------|-------------------|-----------|---------|
| Qwen 2.5 72B | 1500 | 2000 | $0.07 | $0.42 |
| Claude 3.5 | 1500 | 2000 | $0.20 | $1.23 |
| GPT-4 | 1500 | 2000 | $0.36 | $2.15 |
| Llama 3.1 70B | 1500 | 2000 | $0.06 | $0.38 |

**Total for 4 models × 6 tasks = ~$4.18**

Very affordable for comprehensive testing!

---

## Conclusion

This plan provides a complete, production-ready system for:
- Testing multiple LLMs on SDK instrumentation tasks
- Generating solutions automatically
- Evaluating with the Week 3 harness
- Comparing performance across models
- Identifying best models for SDK instrumentation

The modular architecture allows easy extension to:
- More LLM providers
- Additional SDKs beyond Clerk
- Different frameworks beyond Next.js
- Custom metrics and analysis

**Ready to implement? Let's start with Phase 1 (LLM Integration Layer)!**
