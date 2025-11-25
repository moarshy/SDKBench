# Phase 0: SDK Research Prompt

Copy and paste this prompt into Claude Code (or any AI assistant) to research a new SDK before adding it to SDKBench.

---

## Prompt

```
I need to research {SDK_NAME} to understand its integration patterns before adding it to SDKBench, a benchmark for evaluating LLM capabilities in SDK instrumentation tasks.

## Research Tasks

### 1. Find Official Documentation
- Search for "{SDK_NAME} official documentation"
- Identify quickstart/getting started guides
- Find API reference documentation
- Locate migration guides (if any major version changes)

### 2. Understand Core Concepts
Answer these questions:
- What is the primary use case? (auth, database, AI, API client, etc.)
- What programming languages are supported?
- What's the package name on npm/pip/cargo?
- What frameworks have official integrations? (Next.js, FastAPI, etc.)

### 3. Identify Integration Patterns
For each of these categories, find code examples:

**Initialization**
- How is the SDK initialized?
- What's the minimal setup code?
- What configuration is required?

**Configuration**
- What environment variables are needed?
- Are there config files? (SDK-specific configs, not just env vars)
- What are optional vs required settings?

**Core Operations**
- What are the 5-10 most common function calls?
- What parameters do they typically take?
- How is error handling typically done?

**Advanced Features**
- Are there middleware patterns?
- Are there hooks or utility functions?
- Are there streaming/async patterns?

### 4. Version History
- What's the current stable version?
- Were there major breaking changes in recent versions?
- Is there a migration guide from the previous major version?

## Output Format

Create a structured summary with:

### Basic Information
- **Package Name**:
- **Language**:
- **Category**: (auth/database/AI/API/etc.)
- **Current Version**:
- **Documentation URL**:
- **GitHub URL**:

### Initialization Pattern
```{language}
// Minimal initialization code example
```

### Required Configuration
- `{ENV_VAR_1}`: Description
- `{ENV_VAR_2}`: Description

### Common Imports
```{language}
// Most common import patterns
```

### Task Type Definitions for SDKBench
| Task | Name | Count | Description | Difficulty |
|------|------|-------|-------------|------------|
| 1 | init | 15 | ... | easy |
| 2 | {core_op} | 15 | ... | easy-medium |
| 3 | {advanced} | 10 | ... | medium |
| 4 | complete | 7 | ... | hard |
| 5 | migration | 3 | ... | hard |

### Suggested GitHub Search Queries
```
"{package_name}"
"import {package_name}"
"{package_name}" in:file filename:{manifest_file}
```

### Framework-Specific Notes
- **{Framework 1}**: Notes on integration
- **{Framework 2}**: Notes on integration
```

---

## Example Usage

Replace `{SDK_NAME}` with the actual SDK name:

- `{SDK_NAME}` = "Stripe Python SDK"
- `{SDK_NAME}` = "Supabase JavaScript"
- `{SDK_NAME}` = "OpenAI Python"
- `{SDK_NAME}` = "Prisma ORM"

---

## After Research

Once you have the research output:

1. Save it to `docs/sdk-research/{sdk_name}.md`
2. Use the task type definitions to guide Phase 4 sample creation
3. Use the search queries in Phase 1

---

## Tips

- Look for official examples repositories (many SDKs have these)
- Check the SDK's GitHub issues for common integration problems
- Look at the SDK's changelog for breaking changes
- Search for "{SDK_NAME} best practices" for common patterns
