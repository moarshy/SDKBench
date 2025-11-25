# Phase 5: Sample Validation Prompt

Copy and paste this prompt into Claude Code to perform QA validation on generated samples.

---

## Prompt

```
Review all samples in `samples/{sdk_name}/` to verify correctness and consistency for SDKBench.

## Context

I've generated 50 samples for {SDK_NAME} across 5 task types. I need to validate that all samples are correct, complete, and consistent before running evaluations.

## Validation Tasks

### 1. Structure Validation

For each sample directory, verify:

```bash
# Check structure
ls -la samples/{sdk_name}/{sdk}_task*_*/

# Each should have:
# - input/
# - expected/
# - tests/
# - expected/metadata.json
```

**Check:**
- [ ] `input/` directory exists with starter code
- [ ] `expected/` directory exists with solution
- [ ] `tests/` directory exists with test file(s)
- [ ] `expected/metadata.json` exists

### 2. Input Files Validation

For each sample's `input/` directory:

**Check:**
- [ ] Contains TODO comments indicating work needed
- [ ] Does NOT contain SDK imports (e.g., no `import {package}`)
- [ ] Has valid project structure for the framework
- [ ] `.env.example` is empty or has placeholder values only
- [ ] Manifest file (package.json/requirements.txt) does NOT include SDK

**Example TODO patterns to look for:**
```
# TODO: Add {SDK} initialization
# TODO: Configure {SDK} connection
/* TODO: Add {SDK} provider */
```

### 3. Expected Files Validation

For each sample's `expected/` directory:

**Check:**
- [ ] Contains complete, working SDK integration
- [ ] All required imports are present
- [ ] SDK is properly initialized
- [ ] `.env.example` has all required environment variables
- [ ] Manifest file includes SDK dependency with version
- [ ] Code follows SDK best practices (from Phase 3 patterns)

**Verify SDK patterns:**
```bash
# Check for SDK imports
grep -r "import.*{package}" samples/{sdk_name}/*/expected/
grep -r "from {package}" samples/{sdk_name}/*/expected/

# Check for initialization
grep -r "{init_pattern}" samples/{sdk_name}/*/expected/
```

### 4. Metadata Validation

For each `expected/metadata.json`:

**Required fields:**
- [ ] `sample_id` - matches directory name
- [ ] `task_type` - is 1-5
- [ ] `task_name` - matches task type name
- [ ] `sdk` - is "{sdk_name}"
- [ ] `{sdk}_version` - valid version string
- [ ] `framework` - valid framework name
- [ ] `difficulty` - is "easy", "medium", or "hard"
- [ ] `ground_truth.ingredients` - has initialization/configuration/integration_points
- [ ] `evaluation_targets` - has i_acc, c_comp, f_corr at minimum

**Verify with:**
```bash
# Check all metadata files exist
ls samples/{sdk_name}/*/expected/metadata.json | wc -l
# Should be 50

# Sample check
cat samples/{sdk_name}/{sdk}_task1_init_001/expected/metadata.json | jq '.sample_id, .task_type, .sdk'
```

### 5. Test Files Validation

For each sample's `tests/` directory:

**Check:**
- [ ] Test file exists with correct extension (.test.ts, test_.py, etc.)
- [ ] Tests reference `expected/` files (not `input/`)
- [ ] Tests check for key SDK patterns
- [ ] Test syntax is valid for the test framework
- [ ] Tests would pass with the expected solution

**Verify test patterns:**
```bash
# Check test files exist
ls samples/{sdk_name}/*/tests/

# Check tests reference expected/
grep -r "expected" samples/{sdk_name}/*/tests/
```

### 6. Consistency Validation

**Across all samples:**
- [ ] Naming follows convention: `{sdk}_task{N}_{name}_{sequential_id}`
- [ ] Sequential IDs are correct (001-015 for task1, 016-030 for task2, etc.)
- [ ] Similar task types follow same patterns
- [ ] Same SDK version used consistently (or intentionally varied)
- [ ] Same test framework used throughout

**Task distribution:**
- Task 1 (init): 15 samples (001-015)
- Task 2: 15 samples (016-030)
- Task 3: 10 samples (031-040)
- Task 4: 7 samples (041-047)
- Task 5: 3 samples (048-050)

### 7. Diff Validation

For each sample, verify input vs expected shows only SDK additions:

```bash
# Compare input and expected (should show SDK additions only)
diff -r samples/{sdk_name}/{sdk}_task1_init_001/input/ samples/{sdk_name}/{sdk}_task1_init_001/expected/
```

**Check:**
- [ ] Expected adds SDK imports
- [ ] Expected adds SDK initialization
- [ ] Expected adds SDK configuration
- [ ] No unrelated changes between input and expected

## Output Format

Report any issues found in this format:

```markdown
## Validation Report: {SDK_NAME}

### Summary
- Total samples: 50
- Passed: {N}
- Issues found: {N}

### Issues

#### Sample: {sdk}_task{N}_{name}_{id}
- **Issue**: [description of the problem]
- **Location**: [file path]
- **Severity**: [critical/warning/minor]
- **Fix**: [suggested fix]

#### Sample: {sdk}_task{N}_{name}_{id}
...

### Patterns to Fix

If multiple samples have the same issue:

**Issue Pattern**: [description]
**Affected Samples**: {sdk}_task1_init_001, {sdk}_task1_init_002, ...
**Bulk Fix**: [command or approach to fix all]
```

## Common Issues to Watch For

1. **Missing SDK import** - Expected file doesn't import the SDK
2. **Wrong version** - SDK version in metadata doesn't match package file
3. **Incomplete TODO** - Input file has TODO but expected doesn't resolve it
4. **Wrong test path** - Test references input/ instead of expected/
5. **Missing env var** - Required env var not in .env.example
6. **Metadata mismatch** - sample_id doesn't match directory name
7. **Inconsistent framework** - Different frameworks in same task type
8. **Missing ground_truth** - Metadata missing ground_truth fields
```

---

## Quick Validation Commands

```bash
# Count samples
ls -d samples/{sdk_name}/{sdk}_task*/ | wc -l

# Check all have metadata
ls samples/{sdk_name}/*/expected/metadata.json | wc -l

# Check all have tests
ls samples/{sdk_name}/*/tests/*.{test.ts,test_.py} 2>/dev/null | wc -l

# Validate metadata JSON
for f in samples/{sdk_name}/*/expected/metadata.json; do
  jq . "$f" > /dev/null || echo "Invalid JSON: $f"
done

# Check for SDK in expected (should find matches)
grep -l "{package}" samples/{sdk_name}/*/expected/*.{py,ts,tsx} | wc -l

# Check for SDK in input (should find 0 matches)
grep -l "{package}" samples/{sdk_name}/*/input/*.{py,ts,tsx} | wc -l
```

---

## After Validation

1. Fix all critical issues before proceeding
2. Document any intentional variations (e.g., different frameworks)
3. Re-run validation to confirm all fixes
4. Proceed to Phase 6 (Integration) only when all checks pass
