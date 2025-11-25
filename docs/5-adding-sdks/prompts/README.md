# Claude Code Prompts for SDK Integration

This folder contains ready-to-use prompts for Claude Code (or other AI assistants) to help with adding new SDKs to SDKBench.

## Available Prompts

| Prompt | Phase | Purpose |
|--------|-------|---------|
| `phase0-research.prompt.md` | 0 | Research SDK documentation and patterns |
| `phase3-patterns.prompt.md` | 3 | Analyze cloned repos to extract patterns |
| `phase5-validation.prompt.md` | 5 | QA validation of generated samples |

## How to Use

### 1. Open the Prompt File

Read the prompt file and understand what it does.

### 2. Replace Placeholders

Each prompt has placeholders like `{SDK_NAME}`, `{sdk_name}`, `{package}`, etc.

Replace them with your actual values:

| Placeholder | Example (LanceDB) | Example (Clerk) |
|-------------|-------------------|-----------------|
| `{SDK_NAME}` | LanceDB | Clerk |
| `{sdk_name}` | lancedb | clerk |
| `{package}` | lancedb | @clerk/nextjs |
| `{ext}` | py | ts, tsx |
| `{SDK_PREFIX}` | LANCEDB_ | CLERK_ |

### 3. Copy to Claude Code

Copy the filled-in prompt and paste it into Claude Code.

### 4. Follow the Output Instructions

Each prompt specifies what output to create and where to save it.

## Prompt Details

### Phase 0: SDK Research

**When to use**: Before any other phase, to understand the SDK

**Input needed**:
- SDK name
- Access to web search

**Output**:
- `docs/sdk-research/{sdk_name}.md`

**Time**: 2-4 hours

### Phase 3: Pattern Extraction

**When to use**: After cloning repositories (Phase 2)

**Input needed**:
- Cloned repos in `data/{sdk_name}/cloned-repos/`
- File extension for the language

**Output**:
- `data/{sdk_name}/patterns.md`
- `data/{sdk_name}/patterns.json`

**Time**: 4-8 hours

### Phase 5: Sample Validation

**When to use**: After generating samples (Phase 4)

**Input needed**:
- Generated samples in `samples/{sdk_name}/`
- 50 samples across 5 task types

**Output**:
- Validation report with issues and fixes
- Updated samples (after fixing issues)

**Time**: 4-8 hours

## Tips for Better Results

1. **Be specific with placeholders** - The more specific you are, the better the results

2. **Provide context** - If you've already done research, include key findings in the prompt

3. **Iterate** - Run the prompt, review output, refine and re-run if needed

4. **Save intermediate results** - Save outputs to files as you go

5. **Use Claude Code features** - Let Claude read files, run grep commands, etc.

## Customizing Prompts

Feel free to modify these prompts for your specific needs:

- Add SDK-specific patterns to look for
- Adjust output formats
- Add additional validation checks
- Include framework-specific instructions

## Example Workflow

```bash
# Phase 0: Research
# Open phase0-research.prompt.md, fill placeholders, paste to Claude Code
# Save output to docs/sdk-research/mysdK.md

# Phase 1-2: Search and Mine (use scripts)
uv run python scripts/data_collection/mysdk/search_repos.py
uv run python scripts/data_collection/mysdk/mine_repos.py

# Phase 3: Pattern Extraction
# Open phase3-patterns.prompt.md, fill placeholders, paste to Claude Code
# Save output to data/mysdk/patterns.md

# Phase 4: Build samples (use script)
uv run python scripts/data_collection/mysdk/build_samples.py

# Phase 5: Validation
# Open phase5-validation.prompt.md, fill placeholders, paste to Claude Code
# Fix any issues found, re-run until all checks pass

# Phase 6: Integration (use evaluation scripts)
uv run python scripts/run_evaluation_multi_sdk.py --sdk mysdk
```
