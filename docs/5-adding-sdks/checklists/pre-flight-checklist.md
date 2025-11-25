# Pre-Flight Checklist

> Complete this checklist before starting to add a new SDK to SDKBench.

## SDK: _______________

**Date Started**: _______________

---

## Prerequisites

### Environment Setup

- [ ] Python 3.10+ installed
- [ ] `uv` package manager installed
- [ ] SDKBench repository cloned
- [ ] Dependencies installed (`uv sync`)

### API Keys

- [ ] `GITHUB_TOKEN` set in `.env` (for repository search)
- [ ] GitHub token has `repo` scope
- [ ] SDK-specific API keys (if needed for testing)

### Disk Space

- [ ] At least 2GB free (for cloning repositories)
- [ ] `data/{sdk_name}/cloned-repos/` location accessible

---

## Research (Phase 0)

### Documentation Found

- [ ] Official documentation URL identified
- [ ] Quickstart guide located
- [ ] API reference found
- [ ] Migration guide found (if applicable)

### SDK Understanding

- [ ] Primary use case understood
- [ ] Package name identified (npm/pip/cargo)
- [ ] Current stable version known
- [ ] Supported frameworks identified

### Task Types Defined

- [ ] Task 1 (Initialization) defined
- [ ] Task 2 (Core Operation) defined
- [ ] Task 3 (Advanced Feature) defined
- [ ] Task 4 (Complete Integration) defined
- [ ] Task 5 (Migration) defined
- [ ] Total of 50 samples planned (15+15+10+7+3)

### Search Queries Prepared

- [ ] Direct package search queries ready
- [ ] Import pattern search queries ready
- [ ] Manifest file search queries ready
- [ ] At least 5 search variations prepared

---

## Directory Setup

### Create Required Directories

```bash
# Run these commands to set up directories
mkdir -p data/{sdk_name}/cloned-repos
mkdir -p samples/{sdk_name}
mkdir -p scripts/data_collection/{sdk_name}
mkdir -p docs/sdk-research
```

- [ ] `data/{sdk_name}/` created
- [ ] `samples/{sdk_name}/` created
- [ ] `scripts/data_collection/{sdk_name}/` created
- [ ] `docs/sdk-research/` exists

---

## Scripts Preparation

### Copy and Adapt from Reference

Choose reference based on language:
- **Python SDK**: Copy from `scripts/data_collection/lancedb/`
- **TypeScript SDK**: Copy from `scripts/data_collection/clerk/`

```bash
# Example for Python SDK
cp scripts/data_collection/lancedb/search_repos.py scripts/data_collection/{sdk_name}/
cp scripts/data_collection/lancedb/mine_repos.py scripts/data_collection/{sdk_name}/
cp scripts/data_collection/lancedb/extract_patterns.py scripts/data_collection/{sdk_name}/
cp scripts/data_collection/lancedb/build_samples.py scripts/data_collection/{sdk_name}/
```

### Scripts Checklist

- [ ] `search_repos.py` copied
- [ ] `mine_repos.py` copied
- [ ] `extract_patterns.py` copied
- [ ] `build_samples.py` copied
- [ ] All scripts have SDK-specific modifications noted

---

## Research Output

### Save Research Summary

- [ ] `docs/sdk-research/{sdk_name}.md` created
- [ ] Basic information documented
- [ ] Initialization pattern documented
- [ ] Required configuration documented
- [ ] Task types documented
- [ ] Search queries documented

---

## Time Estimation

| Phase | Estimated Time | Actual Time |
|-------|----------------|-------------|
| 0: Research | 2-4 hours | ___ |
| 1: GitHub Search | 1-2 hours | ___ |
| 2: Mining | 2-4 hours | ___ |
| 3: Pattern Extraction | 4-8 hours | ___ |
| 4: Sample Generation | 8-16 hours | ___ |
| 5: Validation | 4-8 hours | ___ |
| 6: Integration | 2-4 hours | ___ |
| **Total** | **23-46 hours** | ___ |

---

## Go/No-Go Decision

### Minimum Requirements Met

- [ ] SDK has sufficient real-world usage (50+ repos on GitHub)
- [ ] Documentation is adequate for sample creation
- [ ] At least 2 frameworks are supported
- [ ] Version migration path exists (for Task 5)
- [ ] No blocking issues identified

### Potential Blockers

List any concerns:
1. _______________
2. _______________
3. _______________

---

## Approval

**Ready to proceed**: [ ] Yes / [ ] No

**Reviewer**: _______________

**Date**: _______________

---

## Quick Start Commands

After completing this checklist:

```bash
# Phase 1: Search for repositories
uv run python scripts/data_collection/{sdk_name}/search_repos.py --max-repos 100

# Phase 2: Mine repositories
uv run python scripts/data_collection/{sdk_name}/mine_repos.py --limit 20

# Phase 3: Extract patterns
uv run python scripts/data_collection/{sdk_name}/extract_patterns.py

# Phase 4: Build samples
uv run python scripts/data_collection/{sdk_name}/build_samples.py

# Phase 6: Test evaluation
uv run python scripts/run_evaluation_multi_sdk.py --sdk {sdk_name} --samples 5 --dry-run
```
