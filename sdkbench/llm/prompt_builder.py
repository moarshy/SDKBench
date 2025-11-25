"""Prompt builder for SDK instrumentation tasks."""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


# SDK-specific context information
SDK_CONTEXTS = {
    "clerk": """
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
""",
    "lancedb": """
LanceDB is a developer-friendly, serverless vector database for AI applications.

Key Concepts:
1. Connection: lancedb.connect() to create or open a database
2. Tables: Schema-defined collections storing vectors and metadata
3. Search: Vector similarity search, full-text search, and hybrid search
4. Embeddings: Integration with embedding models for vectorization

LanceDB Patterns:
- Connection: db = lancedb.connect("./my_lancedb")
- Create table: db.create_table("name", data)
- Open table: table = db.open_table("name")
- Vector search: table.search(query_vector).limit(k).to_pandas()
- Hybrid search: table.search(query_type="hybrid").vector(vec).text(text)
- Full-text search: table.create_fts_index("column"), table.search(text)

Common integrations:
- sentence-transformers for embeddings
- pandas for data manipulation
- pyarrow for efficient data types
""",
}

# SDK-specific task instructions
SDK_TASK_INSTRUCTIONS = {
    "clerk": {
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
""",
    },
    "lancedb": {
        1: """
For this initialization task:
1. Import lancedb library
2. Create database connection with lancedb.connect()
3. Handle connection path appropriately
4. Verify connection is working
""",
        2: """
For this data operations task:
1. Create or open tables with proper schema
2. Add data with correct vector dimensions
3. Handle embeddings appropriately
4. Implement proper error handling
""",
        3: """
For this search task:
1. Implement vector similarity search
2. Use appropriate search parameters (limit, filter)
3. Handle hybrid search if needed
4. Return results in proper format
""",
        4: """
For this pipeline integration task:
1. Build complete data pipeline
2. Integrate embedding model
3. Handle batch operations efficiently
4. Implement proper indexing
""",
        5: """
For this migration/upgrade task:
1. Update to new LanceDB API patterns
2. Handle schema changes
3. Migrate existing data
4. Update search patterns
""",
    },
}

# Task type names by SDK
TASK_TYPE_NAMES = {
    "clerk": {
        1: "Initialization",
        2: "Middleware Configuration",
        3: "Hooks Integration",
        4: "Complete Integration",
        5: "Migration",
    },
    "lancedb": {
        1: "Initialization",
        2: "Data Operations",
        3: "Search",
        4: "Pipeline Integration",
        5: "Migration",
    },
}


class PromptBuilder:
    """Build prompts for SDK instrumentation tasks."""

    def __init__(self):
        """Initialize prompt builder."""
        pass

    def _get_sdk_context(self, sdk: str) -> str:
        """Get SDK-specific context information."""
        return SDK_CONTEXTS.get(sdk, f"SDK: {sdk}")

    def _get_task_instructions(self, sdk: str, task_type: int) -> str:
        """Get task-specific instructions for an SDK."""
        sdk_instructions = SDK_TASK_INSTRUCTIONS.get(sdk, {})
        return sdk_instructions.get(task_type, "")

    def _get_task_name(self, sdk: str, task_type: int) -> str:
        """Get human-readable task name."""
        sdk_names = TASK_TYPE_NAMES.get(sdk, {})
        return sdk_names.get(task_type, f"Task {task_type}")

    def build_prompt(
        self,
        sdk: str,
        task_type: int,
        description: str,
        framework: str,
        sdk_version: str,
        input_files: Dict[str, str],
        additional_context: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Build prompt for SDK instrumentation task.

        Args:
            sdk: SDK name (clerk, lancedb, etc.)
            task_type: Type of task (1-5)
            description: Task description
            framework: Framework being used (nextjs, python, etc.)
            sdk_version: SDK version to use
            input_files: Dict of file paths to content
            additional_context: Optional additional context

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = self._build_system_prompt(sdk, framework, sdk_version)
        user_prompt = self._build_user_prompt(
            sdk, task_type, description, input_files, additional_context
        )

        return system_prompt, user_prompt

    def _build_system_prompt(self, sdk: str, framework: str, sdk_version: str) -> str:
        """Build system prompt with context."""
        sdk_context = self._get_sdk_context(sdk)

        return f"""You are an expert developer specializing in {sdk} integration.
You are helping integrate {sdk} (version {sdk_version}) into a {framework} application.

{sdk_context}

Your responses should:
1. Provide working code that follows best practices
2. Include all necessary imports
3. Add appropriate error handling
4. Follow the framework's conventions
5. Be production-ready

IMPORTANT: You MUST output files with the EXACT same filenames as provided in the input.
- If the input has "app.py", your output must also be named "app.py"
- If the input has "middleware.ts", your output must also be named "middleware.ts"
- Do NOT create new filenames - modify the existing files

When providing code, ALWAYS specify the file path as a comment on the FIRST LINE inside each code block:
- For Python: # filepath: app.py
- For JavaScript/TypeScript: // filepath: middleware.ts
- For other files: # filepath: requirements.txt

Example format:
```python
# filepath: app.py
import lancedb
# rest of code...
```
"""

    def _build_user_prompt(
        self,
        sdk: str,
        task_type: int,
        description: str,
        input_files: Dict[str, str],
        additional_context: Optional[str] = None,
    ) -> str:
        """Build user prompt for the task."""
        task_name = self._get_task_name(sdk, task_type)

        prompt = f"""Task: {task_name}
{description}

Current project files:

"""

        # Add input files
        for filepath, content in input_files.items():
            prompt += f"=== {filepath} ===\n```\n{content}\n```\n\n"

        # Add task-specific instructions
        prompt += self._get_task_instructions(sdk, task_type)

        # Add additional context if provided
        if additional_context:
            prompt += f"\nAdditional Context:\n{additional_context}\n"

        # List the files that need to be output
        file_list = ", ".join(input_files.keys()) if input_files else "the required files"

        prompt += f"""
Please provide the complete solution by modifying the input files above.
Files to output: {file_list}

CRITICAL: Each code block MUST start with a filepath comment on the first line:
- Python: # filepath: filename.py
- JavaScript/TypeScript: // filepath: filename.ts
- Other: # filepath: filename.ext
"""

        return prompt

    def build_from_metadata(
        self, metadata_path: Path, input_dir: Path
    ) -> Tuple[str, str]:
        """Build prompt from metadata.json and input files.

        Args:
            metadata_path: Path to metadata.json
            input_dir: Directory containing input files

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Load metadata
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Determine SDK from metadata
        sdk = metadata.get("sdk", "clerk")  # Default to clerk for backward compatibility

        # Load input files
        input_files = {}
        if input_dir.exists():
            for file_path in input_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(input_dir)
                    try:
                        with open(file_path, "r") as f:
                            input_files[str(relative_path)] = f.read()
                    except Exception:
                        # Skip binary files
                        pass

        # Handle migration tasks (task_type 5)
        if metadata["task_type"] == 5:
            sdk_version = metadata.get(f"{sdk}_version_to", metadata.get("sdk_version_to", "latest"))
            version_from = metadata.get(f"{sdk}_version_from", metadata.get("sdk_version_from", "previous"))
            additional_context = f"Migrating from {sdk} {version_from} to {sdk_version}"
        else:
            # Try SDK-specific version field, then generic, then default
            sdk_version = metadata.get(
                f"{sdk}_version", metadata.get("sdk_version", "latest")
            )
            additional_context = None

        return self.build_prompt(
            sdk=sdk,
            task_type=metadata["task_type"],
            description=metadata["description"],
            framework=metadata["framework"],
            sdk_version=sdk_version,
            input_files=input_files,
            additional_context=additional_context,
        )
