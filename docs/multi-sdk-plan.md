# Multi-SDK Extension Plan for SDKBench

## Executive Summary

This document outlines the plan to extend SDKBench from supporting a single SDK (Clerk) to multiple SDKs, starting with LanceDB as the second SDK. The approach strictly follows the POC methodology inspired by LogBench, maintaining all existing functionality while enabling SDK extensibility.

## 1. Current State

### 1.1 What We Have (Clerk SDK)
- **50 samples** across 5 task types
- **6 evaluation metrics**: I-ACC, C-COMP, IPA, F-CORR, CQ, SEM-SIM
- **Complete pipeline**: GitHub mining → Pattern extraction → Sample generation → Evaluation
- **83-86% accuracy** achieved with GPT-5.1 and Claude models

### 1.2 POC Process (To Be Replicated)
1. **GitHub Mining** (`search_repos.py`): Find repositories using SDK
2. **Repository Analysis** (`mine_repos.py`): Clone and analyze code patterns
3. **Pattern Extraction** (`extract_patterns.py`): Extract usage patterns
4. **Sample Generation** (`build_samples.py`): Create evaluation samples
5. **Evaluation**: Use existing metrics to evaluate LLM-generated code

## 2. Multi-SDK Architecture

### 2.1 Core Principle
**Minimal changes, maximum compatibility**. We extend, not replace.

### 2.2 SDK Identification
Each sample's `metadata.json` includes SDK identification:
```json
{
  "sample_id": "lancedb_task1_init_001",
  "sdk": "lancedb",  // NEW: SDK identifier
  "sdk_version": "0.5.0",
  "language": "python",  // NEW: Language specification
  "framework": "python",
  "task_type": 1,
  ...
}
```

### 2.3 Directory Structure
```
SDKBench/
├── samples/
│   ├── task1_init_001/         # Existing Clerk samples (unchanged)
│   ├── task2_middleware_016/   # Existing Clerk samples (unchanged)
│   ├── ...
│   ├── lancedb_task1_init_001/ # New LanceDB samples
│   ├── lancedb_task2_ops_016/  # New LanceDB samples
│   └── ...
├── data/
│   ├── repositories.json        # Clerk repositories
│   ├── patterns.json           # Clerk patterns
│   ├── lancedb_repositories.json  # LanceDB repositories
│   └── lancedb_patterns.json     # LanceDB patterns
```

## 3. LanceDB Integration Plan

### 3.1 Task Type Mapping

| Task Type | Clerk Context | LanceDB Context |
|-----------|--------------|-----------------|
| **Type 1** | Initialization (ClerkProvider) | Initialization (lancedb.connect) |
| **Type 2** | Middleware (authMiddleware) | Data Operations (create_table, add) |
| **Type 3** | Hooks (useAuth, useUser) | Vector Search (search, query) |
| **Type 4** | Complete Integration | Complete RAG Pipeline |
| **Type 5** | Migration (v4→v5) | Schema Migration |

### 3.2 Sample Distribution (50 samples)
- **Task 1 - Initialization**: 15 samples
- **Task 2 - Data Operations**: 15 samples
- **Task 3 - Vector Search**: 10 samples
- **Task 4 - Complete Pipeline**: 7 samples
- **Task 5 - Migration**: 3 samples

### 3.3 LanceDB-Specific Patterns

#### Pattern 1: Initialization
```python
import lancedb
db = lancedb.connect("./my_database")
```

#### Pattern 2: Table Operations
```python
table = db.create_table("documents", data=df)
table.add(new_documents)
```

#### Pattern 3: Vector Search
```python
results = table.search(query_vector).limit(10).to_pandas()
```

#### Pattern 4: Embedding Integration
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)
```

## 4. Implementation Steps

### 4.1 Phase 1: GitHub Mining for LanceDB

#### Step 1.1: Adapt search_repos.py
```python
# Modifications needed:
SEARCH_QUERIES = [
    "lancedb language:python",
    "import lancedb language:python",
    "lancedb.connect language:python",
    "from lancedb import language:python"
]

LANGUAGE_FILTER = "python"  # Changed from TypeScript/JavaScript
MIN_STARS = 2
```

#### Step 1.2: Update mine_repos.py
```python
# File categories to search for:
FILE_CATEGORIES = {
    "requirements": ["requirements.txt", "pyproject.toml", "setup.py"],
    "connection_files": "lancedb.connect",
    "table_operations": ["create_table", "open_table"],
    "vector_search": ["search", "query", "vector_search"],
    "embeddings": ["embedding", "encode", "SentenceTransformer"]
}
```

#### Step 1.3: Modify extract_patterns.py
```python
# Patterns to extract:
LANCEDB_PATTERNS = {
    "imports": r"(?:import lancedb|from lancedb import \w+)",
    "connection": r"lancedb\.connect\([^)]+\)",
    "table_ops": r"(?:create_table|open_table|add|search)\([^)]+\)",
    "vectors": r"(?:embedding|vector|encode)\([^)]+\)"
}
```

### 4.2 Phase 2: Sample Generation

#### Step 2.1: Create build_lancedb_samples.py
Based on `build_samples.py` but adapted for Python/LanceDB:
- Generate samples from extracted patterns
- Create input/expected/tests structure
- Generate metadata.json with LanceDB-specific ground truth

#### Step 2.2: Sample Structure
```
lancedb_task1_init_001/
├── input/
│   └── app.py          # Starter code without LanceDB
├── expected/
│   ├── app.py          # Solution with LanceDB
│   └── metadata.json   # Ground truth
└── tests/
    └── test_init.py    # Python tests
```

### 4.3 Phase 3: Evaluation Adaptation

#### Step 3.1: Minimal Evaluator Changes
```python
# In evaluator.py, detect SDK from metadata:
def __init__(self, solution_dir, metadata_path=None):
    self.ground_truth = GroundTruth(metadata_path)
    self.sdk = self.ground_truth.get("sdk", "clerk")  # Default to clerk
    self.language = self.ground_truth.get("language", "typescript")
```

#### Step 3.2: Metric Adaptations
The existing metrics work as-is, just with different patterns:

| Metric | Clerk Check | LanceDB Check |
|--------|------------|---------------|
| **I-ACC** | ClerkProvider present | lancedb.connect present |
| **C-COMP** | Auth env vars | DB connection string |
| **IPA** | Auth hooks used | Vector operations used |
| **F-CORR** | npm test passes | pytest passes |
| **CQ** | ESLint patterns | pylint patterns |
| **SEM-SIM** | Auth semantics | Vector search semantics |

## 5. Backward Compatibility

### 5.1 Guaranteed Compatibility
- **No changes** to existing Clerk samples
- **No changes** to evaluation metrics
- **No changes** to existing scripts for Clerk
- All existing functionality preserved

### 5.2 Detection Logic
```python
def is_lancedb_sample(sample_id):
    return sample_id.startswith("lancedb_")

def get_sdk_from_metadata(metadata):
    return metadata.get("sdk", "clerk")  # Default to clerk for backward compat
```

## 6. Testing Strategy

### 6.1 Regression Testing
1. Run all existing Clerk samples - must pass unchanged
2. Verify evaluation scores remain consistent
3. Ensure no breaking changes

### 6.2 LanceDB Testing
1. Generate initial 10 samples manually for validation
2. Test evaluation pipeline with Python code
3. Verify metrics calculate correctly

### 6.3 Cross-SDK Testing
1. Compare metric distributions between SDKs
2. Ensure comparable difficulty levels
3. Validate scoring consistency

## 7. Success Criteria

### 7.1 Technical Success
- ✅ All 50 Clerk samples still evaluate correctly
- ✅ 50 LanceDB samples generated from real patterns
- ✅ Both SDKs evaluate with same metrics
- ✅ No breaking changes to existing code

### 7.2 Research Success
- ✅ Can compare LLM performance across SDK types
- ✅ Identified SDK-specific challenges
- ✅ Reproducible evaluation results
- ✅ Extended benchmark coverage

## 8. Timeline

### Week 1: GitHub Mining
- Day 1-2: Adapt mining scripts for LanceDB
- Day 3-4: Run mining and collect repositories
- Day 5: Extract patterns and analyze

### Week 2: Sample Generation
- Day 1-2: Create build_lancedb_samples.py
- Day 3-5: Generate 50 samples

### Week 3: Evaluation Integration
- Day 1-2: Update evaluators for SDK detection
- Day 3-4: Test with both SDKs
- Day 5: Fix any issues

### Week 4: Validation & Documentation
- Day 1-2: Comprehensive testing
- Day 3-4: Documentation updates
- Day 5: Final validation

## 9. File Changes Summary

### 9.1 New Files
```
scripts/search_lancedb_repos.py    # LanceDB repository search
scripts/mine_lancedb_repos.py      # LanceDB repository mining
scripts/extract_lancedb_patterns.py # LanceDB pattern extraction
scripts/build_lancedb_samples.py   # LanceDB sample generation
data/lancedb_repositories.json     # Found repositories
data/lancedb_patterns.json         # Extracted patterns
samples/lancedb_task*/             # 50 new samples
```

### 9.2 Modified Files
```
sdkbench/evaluator/evaluator.py    # Add SDK detection
sdkbench/core/ground_truth.py      # Handle sdk field
README.md                           # Document multi-SDK support
```

### 9.3 Unchanged Files
All existing Clerk-related files remain unchanged.

## 10. Risk Mitigation

### 10.1 Risk: Breaking Clerk Functionality
**Mitigation**: Make no changes to existing samples or core evaluation logic

### 10.2 Risk: Incompatible Metrics
**Mitigation**: Use same metrics, just different patterns

### 10.3 Risk: Insufficient LanceDB Repositories
**Mitigation**: Can supplement with synthetic samples if needed

## 11. Future Extensions

Once this approach is proven with LanceDB, the same process can add:
- **Pinecone**: Another vector database
- **ChromaDB**: Embeddings database
- **Weaviate**: Vector search engine
- **Stripe**: Payment processing
- **Sentry**: Error tracking

Each new SDK follows the same pattern:
1. Mine GitHub for real usage
2. Extract patterns
3. Generate samples
4. Evaluate with existing metrics

## 12. Conclusion

This plan extends SDKBench to multi-SDK support while maintaining the successful POC approach. By following the exact same process used for Clerk (GitHub mining → pattern extraction → sample generation), we ensure consistency and quality. The use of existing evaluation metrics guarantees comparability across SDKs while minimizing implementation complexity.

The key insight is that the evaluation metrics (I-ACC, C-COMP, IPA, F-CORR, CQ, SEM-SIM) are SDK-agnostic - they measure code quality aspects that apply to any SDK integration. This allows us to extend to new SDKs without creating new metrics, maintaining the benchmark's consistency and research value.