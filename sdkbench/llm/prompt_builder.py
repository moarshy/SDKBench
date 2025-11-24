"""Prompt builder for SDK instrumentation tasks."""

from typing import Dict, List, Optional
from pathlib import Path
import json


class PromptBuilder:
    """Build prompts for SDK instrumentation tasks."""

    def __init__(self):
        """Initialize prompt builder."""
        self.sdk_context = self._load_sdk_context()

    def _load_sdk_context(self) -> str:
        """Load Clerk SDK context information.

        Returns:
            Context string with SDK documentation
        """
        return """
Clerk is a complete authentication and user management solution for modern web applications.

Key Concepts:
1. ClerkProvider: Wraps your React app to provide authentication context
2. Middleware: Protects routes on the server-side
3. Hooks: Access user data and auth state in React components
4. Server-side helpers: Get auth state in server components and API routes

Clerk v5 (Latest):
- Package: @clerk/nextjs
- Middleware: clerkMiddleware()
- Server imports: @clerk/nextjs/server
- Client imports: @clerk/nextjs

Clerk v4 (Legacy):
- Package: @clerk/nextjs@4
- Middleware: authMiddleware()
- Different import paths

Environment Variables:
- NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: Your publishable key
- CLERK_SECRET_KEY: Your secret key
- Optional URL configs for custom sign-in/up pages
"""

    def build_prompt(
        self,
        task_type: int,
        description: str,
        framework: str,
        clerk_version: str,
        input_files: Dict[str, str],
        additional_context: Optional[str] = None
    ) -> tuple[str, str]:
        """Build prompt for SDK instrumentation task.

        Args:
            task_type: Type of task (1-5)
            description: Task description
            framework: Framework being used (nextjs, express, etc.)
            clerk_version: Clerk version to use
            input_files: Dict of file paths to content
            additional_context: Optional additional context

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = self._build_system_prompt(framework, clerk_version)
        user_prompt = self._build_user_prompt(
            task_type,
            description,
            input_files,
            additional_context
        )

        return system_prompt, user_prompt

    def _build_system_prompt(self, framework: str, clerk_version: str) -> str:
        """Build system prompt with context.

        Args:
            framework: Framework being used
            clerk_version: Clerk version

        Returns:
            System prompt string
        """
        return f"""You are an expert developer specializing in authentication integration.
You are helping integrate Clerk authentication (version {clerk_version}) into a {framework} application.

{self.sdk_context}

Your responses should:
1. Provide working code that follows best practices
2. Include all necessary imports
3. Add appropriate error handling
4. Follow the framework's conventions
5. Be production-ready

When providing code, always specify the file path as a comment at the top of each code block.
Format: // filepath: path/to/file.ext
"""

    def _build_user_prompt(
        self,
        task_type: int,
        description: str,
        input_files: Dict[str, str],
        additional_context: Optional[str] = None
    ) -> str:
        """Build user prompt for the task.

        Args:
            task_type: Type of task
            description: Task description
            input_files: Dict of file paths to content
            additional_context: Optional additional context

        Returns:
            User prompt string
        """
        task_type_names = {
            1: "Initialization",
            2: "Middleware Configuration",
            3: "Hooks Integration",
            4: "Complete Integration",
            5: "Migration"
        }

        task_name = task_type_names.get(task_type, "Integration")

        prompt = f"""Task: {task_name}
{description}

Current project files:

"""

        # Add input files
        for filepath, content in input_files.items():
            prompt += f"=== {filepath} ===\n```\n{content}\n```\n\n"

        # Add task-specific instructions
        prompt += self._get_task_instructions(task_type)

        # Add additional context if provided
        if additional_context:
            prompt += f"\nAdditional Context:\n{additional_context}\n"

        prompt += """
Please provide the complete solution with all necessary files and configurations.
Mark each file clearly with its path using the format: // filepath: path/to/file.ext
"""

        return prompt

    def _get_task_instructions(self, task_type: int) -> str:
        """Get task-specific instructions.

        Args:
            task_type: Type of task

        Returns:
            Instructions string
        """
        instructions = {
            1: """
For this initialization task:
1. Add ClerkProvider to wrap the application
2. Import necessary Clerk components
3. Ensure proper placement in component hierarchy
4. Add any required configuration
""",
            2: """
For this middleware configuration task:
1. Create or update middleware configuration
2. Define protected and public routes
3. Add proper middleware exports
4. Ensure middleware runs on correct paths
""",
            3: """
For this hooks integration task:
1. Use appropriate Clerk hooks (useUser, useAuth, etc.)
2. Handle loading and error states
3. Display user information correctly
4. Add proper TypeScript types if applicable
""",
            4: """
For this complete integration task:
1. Set up full authentication flow
2. Add sign-in and sign-up components
3. Protect appropriate routes
4. Handle user sessions
5. Add user profile management
""",
            5: """
For this migration task:
1. Update imports to new version
2. Replace deprecated methods
3. Update middleware configuration
4. Fix any breaking changes
5. Ensure backward compatibility where needed
"""
        }

        return instructions.get(task_type, "")

    def build_from_metadata(self, metadata_path: Path, input_dir: Path) -> tuple[str, str]:
        """Build prompt from metadata.json and input files.

        Args:
            metadata_path: Path to metadata.json
            input_dir: Directory containing input files

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Load input files
        input_files = {}
        if input_dir.exists():
            for file_path in input_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(input_dir)
                    try:
                        with open(file_path, 'r') as f:
                            input_files[str(relative_path)] = f.read()
                    except Exception:
                        # Skip binary files
                        pass

        # Handle migration tasks
        if metadata['task_type'] == 5:
            clerk_version = metadata.get('clerk_version_to', '5.0.0')
            additional_context = f"Migrating from Clerk {metadata.get('clerk_version_from', '4.x')} to {clerk_version}"
        else:
            clerk_version = metadata.get('clerk_version', '5.0.0')
            additional_context = None

        return self.build_prompt(
            task_type=metadata['task_type'],
            description=metadata['description'],
            framework=metadata['framework'],
            clerk_version=clerk_version,
            input_files=input_files,
            additional_context=additional_context
        )