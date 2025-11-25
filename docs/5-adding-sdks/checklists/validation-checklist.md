# Sample Validation Checklist

> Use this checklist during Phase 5 to validate all generated samples.

## SDK: _______________

**Validation Date**: _______________

---

## Overall Statistics

| Metric | Expected | Actual | Pass |
|--------|----------|--------|------|
| Total Samples | 50 | ___ | [ ] |
| Task 1 Samples | 15 | ___ | [ ] |
| Task 2 Samples | 15 | ___ | [ ] |
| Task 3 Samples | 10 | ___ | [ ] |
| Task 4 Samples | 7 | ___ | [ ] |
| Task 5 Samples | 3 | ___ | [ ] |

### Quick Count Commands

```bash
# Total sample count
ls -d samples/{sdk_name}/{sdk}_task*/ | wc -l

# By task type
ls -d samples/{sdk_name}/{sdk}_task1_*/ | wc -l
ls -d samples/{sdk_name}/{sdk}_task2_*/ | wc -l
ls -d samples/{sdk_name}/{sdk}_task3_*/ | wc -l
ls -d samples/{sdk_name}/{sdk}_task4_*/ | wc -l
ls -d samples/{sdk_name}/{sdk}_task5_*/ | wc -l
```

---

## Structure Validation

### Directory Structure

For each sample, verify:

- [ ] `input/` directory exists
- [ ] `expected/` directory exists
- [ ] `tests/` directory exists
- [ ] `expected/metadata.json` exists

### Batch Check Command

```bash
# Check all samples have required directories
for dir in samples/{sdk_name}/{sdk}_task*/; do
  if [ ! -d "$dir/input" ]; then echo "Missing input/: $dir"; fi
  if [ ! -d "$dir/expected" ]; then echo "Missing expected/: $dir"; fi
  if [ ! -d "$dir/tests" ]; then echo "Missing tests/: $dir"; fi
  if [ ! -f "$dir/expected/metadata.json" ]; then echo "Missing metadata: $dir"; fi
done
```

**Results**:
- [ ] All samples have correct structure
- [ ] Issues found: _______________

---

## Input Files Validation

### Required Checks

For each sample's `input/` directory:

- [ ] Contains source code file(s)
- [ ] Contains TODO comments
- [ ] Does NOT contain SDK imports
- [ ] Has manifest file (package.json/requirements.txt) WITHOUT SDK
- [ ] `.env.example` is empty or has placeholders only

### Batch Check Commands

```bash
# Check for TODO comments in input files
grep -r "TODO" samples/{sdk_name}/*/input/ | head -20

# Check NO SDK imports in input (should return 0 matches)
grep -r "{package}" samples/{sdk_name}/*/input/*.{py,ts,tsx} 2>/dev/null | wc -l

# Check manifest files don't have SDK
grep -l "{package}" samples/{sdk_name}/*/input/package.json 2>/dev/null | wc -l
grep -l "{package}" samples/{sdk_name}/*/input/requirements.txt 2>/dev/null | wc -l
```

**Results**:
- [ ] All inputs have TODO comments
- [ ] No inputs have SDK imports
- [ ] Issues found: _______________

---

## Expected Files Validation

### Required Checks

For each sample's `expected/` directory:

- [ ] Contains complete SDK implementation
- [ ] All required imports present
- [ ] SDK is properly initialized/configured
- [ ] `.env.example` has all required variables
- [ ] Manifest file includes SDK with version

### Batch Check Commands

```bash
# Check SDK imports are present in expected (should match sample count)
grep -r "{package}" samples/{sdk_name}/*/expected/*.{py,ts,tsx} 2>/dev/null | wc -l

# Check .env.example files have SDK variables
grep -l "{SDK_PREFIX}" samples/{sdk_name}/*/expected/.env.example | wc -l

# Check manifest files have SDK
grep -l "{package}" samples/{sdk_name}/*/expected/package.json 2>/dev/null | wc -l
grep -l "{package}" samples/{sdk_name}/*/expected/requirements.txt 2>/dev/null | wc -l
```

**Results**:
- [ ] All expected files have SDK integration
- [ ] All .env.example files configured
- [ ] Issues found: _______________

---

## Metadata Validation

### Required Fields

For each `metadata.json`:

- [ ] `sample_id` - matches directory name
- [ ] `task_type` - is 1-5
- [ ] `task_name` - valid name
- [ ] `sdk` - matches SDK name
- [ ] `framework` - valid framework
- [ ] `difficulty` - easy/medium/hard
- [ ] `ground_truth.ingredients` - has content
- [ ] `evaluation_targets` - has i_acc, c_comp, f_corr

### Batch Check Commands

```bash
# Validate all metadata is valid JSON
for f in samples/{sdk_name}/*/expected/metadata.json; do
  jq . "$f" > /dev/null 2>&1 || echo "Invalid JSON: $f"
done

# Check required fields exist
for f in samples/{sdk_name}/*/expected/metadata.json; do
  for field in sample_id task_type sdk ground_truth; do
    jq -e ".$field" "$f" > /dev/null 2>&1 || echo "Missing $field: $f"
  done
done

# Verify sample_id matches directory
for dir in samples/{sdk_name}/{sdk}_task*/; do
  expected_id=$(basename "$dir")
  actual_id=$(jq -r '.sample_id' "$dir/expected/metadata.json" 2>/dev/null)
  if [ "$expected_id" != "$actual_id" ]; then
    echo "ID mismatch: $dir (expected: $expected_id, got: $actual_id)"
  fi
done
```

**Results**:
- [ ] All metadata files are valid JSON
- [ ] All required fields present
- [ ] All sample_ids match directory names
- [ ] Issues found: _______________

---

## Test Files Validation

### Required Checks

For each sample's `tests/` directory:

- [ ] At least one test file exists
- [ ] Test file has correct extension
- [ ] Tests reference `expected/` directory
- [ ] Tests check for SDK patterns
- [ ] Tests are syntactically valid

### Batch Check Commands

```bash
# Check test files exist
ls samples/{sdk_name}/*/tests/*.{test.ts,test_.py,_test.py} 2>/dev/null | wc -l

# Check tests reference expected (not input)
grep -r "expected" samples/{sdk_name}/*/tests/ | wc -l

# Check for SDK pattern assertions
grep -r "{pattern}" samples/{sdk_name}/*/tests/ | head -10
```

**Results**:
- [ ] All samples have test files
- [ ] Tests reference expected/
- [ ] Issues found: _______________

---

## Naming Convention Validation

### Sample ID Format

Expected format: `{sdk}_task{N}_{name}_{sequential_id}`

### Sequence Validation

| Task | Expected Range | Actual | Pass |
|------|----------------|--------|------|
| 1 | 001-015 | ___ | [ ] |
| 2 | 016-030 | ___ | [ ] |
| 3 | 031-040 | ___ | [ ] |
| 4 | 041-047 | ___ | [ ] |
| 5 | 048-050 | ___ | [ ] |

### Check Command

```bash
# List all sample IDs
ls -d samples/{sdk_name}/{sdk}_task*/ | xargs -I{} basename {} | sort
```

**Results**:
- [ ] All IDs follow naming convention
- [ ] Sequences are correct
- [ ] Issues found: _______________

---

## Diff Validation

### Input vs Expected Comparison

For each sample, verify that the diff shows only SDK-related changes:

```bash
# Example diff check
diff -r samples/{sdk_name}/{sdk}_task1_init_001/input/ \
        samples/{sdk_name}/{sdk}_task1_init_001/expected/ \
        --exclude=metadata.json
```

### Expected Changes Only

- [ ] SDK imports added
- [ ] SDK initialization added
- [ ] SDK configuration added
- [ ] No unrelated code changes

**Results**:
- [ ] All diffs show only SDK changes
- [ ] Issues found: _______________

---

## Dataset Manifest Validation

### Check `{sdk}_dataset_manifest.json`

- [ ] File exists at `samples/{sdk_name}/{sdk}_dataset_manifest.json`
- [ ] `total_samples` equals 50
- [ ] `by_task_type` sums to 50
- [ ] All samples listed in `samples` array
- [ ] `sdk` field is correct

### Check Command

```bash
# Validate manifest
cat samples/{sdk_name}/{sdk}_dataset_manifest.json | jq '
  .total_samples,
  .by_task_type,
  (.samples | length)
'
```

**Results**:
- [ ] Manifest is complete and valid
- [ ] Issues found: _______________

---

## Issue Tracking

### Critical Issues (Must Fix)

| Sample | Issue | Status |
|--------|-------|--------|
| ___ | ___ | [ ] Fixed |
| ___ | ___ | [ ] Fixed |
| ___ | ___ | [ ] Fixed |

### Warning Issues (Should Fix)

| Sample | Issue | Status |
|--------|-------|--------|
| ___ | ___ | [ ] Fixed |
| ___ | ___ | [ ] Fixed |

### Minor Issues (Nice to Fix)

| Sample | Issue | Status |
|--------|-------|--------|
| ___ | ___ | [ ] Fixed |
| ___ | ___ | [ ] Fixed |

---

## Final Sign-Off

### All Checks Passed

- [ ] Structure validation complete
- [ ] Input files validation complete
- [ ] Expected files validation complete
- [ ] Metadata validation complete
- [ ] Test files validation complete
- [ ] Naming convention validation complete
- [ ] Diff validation complete
- [ ] Dataset manifest validation complete

### Ready for Phase 6

- [ ] All critical issues resolved
- [ ] All warning issues resolved (or documented)
- [ ] Samples ready for evaluation

**Validator**: _______________

**Date**: _______________

---

## Next Steps

After validation passes:

```bash
# Run test evaluation
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --model claude-sonnet-4-5 \
    --samples 5 \
    --dry-run

# If dry-run succeeds, run full evaluation
uv run python scripts/run_evaluation_multi_sdk.py \
    --sdk {sdk_name} \
    --model claude-sonnet-4-5
```
