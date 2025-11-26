# LanceDB Benchmark Bug Fixing Plan

Based on findings from `lancedb-evaluation.md`, this document outlines the plan to fix identified issues in the LanceDB benchmark tests.

## Executive Summary

**Current State**: f_corr metric shows 14% pass rate (7/50 samples)
**Estimated True Pass Rate**: ~80%+ after fixes
**Root Cause**: Tests verify implementation structure instead of behavior

---

## Bug Categories

### Category A: Module-Level Variable Coupling (HIGH PRIORITY)
- **Impact**: ~30 samples affected (Tasks 1-3)
- **Severity**: Critical - causes systematic false negatives
- **Pattern**: Tests check `app.db is not None` instead of testing behavior

### Category B: Function Naming Inconsistencies (MEDIUM PRIORITY)
- **Impact**: ~5 samples affected
- **Severity**: Medium - causes sporadic failures
- **Pattern**: Tests check for `get_database` but code has `get_cloud_database`

### Category C: Environmental Dependencies (LOW PRIORITY)
- **Impact**: ~3 samples (S3/cloud scenarios)
- **Severity**: Low - known limitation
- **Pattern**: Tests require AWS credentials not available in test env

---

## Phase 1: Test Refactoring (Tasks 1-3)

### 1.1 Task 1 Tests (Initialization)

**Files to modify**:
```
samples/lancedb/lancedb_task1_init_001/tests/test_init.py
samples/lancedb/lancedb_task1_init_002/tests/test_init.py
samples/lancedb/lancedb_task1_init_003/tests/test_init.py
... (all task1 samples)
```

**Current Pattern** (broken):
```python
def test_database_connection():
    from expected import app
    assert app.db is not None  # Requires module-level db
```

**Fixed Pattern**:
```python
def test_database_connection():
    from expected import app
    # Option 1: Check for any valid connection accessor
    has_db = (
        hasattr(app, 'db') or
        hasattr(app, 'get_database') or
        hasattr(app, 'get_db') or
        hasattr(app, 'connect')
    )
    assert has_db, "No database connection method found"

def test_main_runs_without_error():
    from expected import app
    # Test behavior, not structure
    try:
        app.main()
    except Exception as e:
        pytest.fail(f"main() raised {e}")
```

**Alternative Pattern** (more flexible):
```python
def test_can_get_database_connection():
    from expected import app

    # Try multiple ways to get a connection
    db = None
    if hasattr(app, 'db') and app.db is not None:
        db = app.db
    elif hasattr(app, 'get_database'):
        db = app.get_database()
    elif hasattr(app, 'get_db'):
        db = app.get_db()

    assert db is not None, "Could not obtain database connection"
    assert hasattr(db, 'table_names'), "Connection missing table_names method"
```

### 1.2 Task 2 Tests (Data Operations)

**Files to modify**:
```
samples/lancedb/lancedb_task2_data_ops_*/tests/test_data_ops.py
```

**Current Pattern** (broken):
```python
def test_database_connection():
    from expected import data_ops
    assert data_ops.db is not None
```

**Fixed Pattern**:
```python
def test_table_creation_works():
    from expected import data_ops

    # Run main to ensure table is created
    data_ops.main()

    # Verify table exists by getting connection
    db = _get_connection(data_ops)
    tables = db.table_names()
    assert len(tables) > 0, "No tables created"

def _get_connection(module):
    """Helper to get db connection from various patterns."""
    if hasattr(module, 'db') and module.db is not None:
        return module.db
    if hasattr(module, 'get_database'):
        return module.get_database()
    # Try calling main and checking for returned db
    raise ValueError("Could not find database connection")
```

### 1.3 Task 3 Tests (Search)

**Files to modify**:
```
samples/lancedb/lancedb_task3_search_*/tests/test_search.py
```

**Current Pattern** (mixed):
```python
def test_database_connection():
    from expected import search
    assert search.db is not None  # Module-level check

def test_search_function_exists():
    from expected import search
    has_search = hasattr(search, 'search') or ...  # This is OK
    assert has_search
```

**Fixed Pattern**:
```python
def test_search_function_exists():
    from expected import search
    # Keep this - it's behavioral
    has_search = (
        hasattr(search, 'search') or
        hasattr(search, 'search_similar') or
        hasattr(search, 'hybrid_search') or
        hasattr(search, 'vector_search')
    )
    assert has_search

def test_search_returns_results():
    from expected import search
    # Test actual behavior
    search.main()  # Should populate test data
    # If search function is callable, test it
```

---

## Phase 2: Naming Standardization

### 2.1 Function Name Variants to Accept

Create a standard list of acceptable function names:

| Purpose | Accepted Names |
|---------|----------------|
| Get DB connection | `db`, `get_database`, `get_db`, `connect`, `get_connection` |
| Cloud DB | `get_cloud_database`, `get_s3_database`, `connect_cloud` |
| Search | `search`, `search_similar`, `vector_search`, `hybrid_search` |
| Ingest | `ingest`, `ingest_documents`, `add_documents`, `insert` |

### 2.2 Fix task1_init_007 Specifically

**File**: `samples/lancedb/lancedb_task1_init_007/tests/test_init.py`

**Current** (bug):
```python
def test_lancedb_connection():
    from expected import app
    assert hasattr(app, "db") or hasattr(app, "get_database")  # Wrong name!
```

**Fixed**:
```python
def test_lancedb_connection():
    from expected import app
    assert hasattr(app, "db") or hasattr(app, "get_database") or hasattr(app, "get_cloud_database")
```

---

## Phase 3: Test Helper Utilities

### 3.1 Create Shared Test Utilities

**New file**: `samples/lancedb/conftest.py`

```python
"""Shared test utilities for LanceDB samples."""

import pytest

def get_db_connection(module):
    """Get database connection from module using various patterns.

    Supports:
    - module.db (module-level variable)
    - module.get_database() (factory function)
    - module.get_db() (short factory)
    - module.connect() (direct connect)
    """
    # Module-level variable
    if hasattr(module, 'db') and module.db is not None:
        return module.db

    # Factory functions
    for func_name in ['get_database', 'get_db', 'get_connection', 'connect', 'get_cloud_database']:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                try:
                    return func()
                except Exception:
                    continue

    return None

def has_search_capability(module):
    """Check if module has any search function."""
    search_names = ['search', 'search_similar', 'vector_search', 'hybrid_search', 'full_text_search']
    return any(hasattr(module, name) and callable(getattr(module, name)) for name in search_names)

def has_ingest_capability(module):
    """Check if module has any ingest function."""
    ingest_names = ['ingest', 'ingest_documents', 'add_documents', 'insert', 'add']
    return any(hasattr(module, name) and callable(getattr(module, name)) for name in ingest_names)

@pytest.fixture
def skip_without_credentials():
    """Skip test if required credentials are missing."""
    import os
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        pytest.skip("AWS credentials not configured")
```

### 3.2 Update Tests to Use Helpers

**Example updated test**:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import get_db_connection

def test_database_connection():
    from expected import app
    db = get_db_connection(app)
    assert db is not None, "Could not obtain database connection via any method"

def test_main_executes():
    from expected import app
    app.main()  # Should not raise
```

---

## Phase 4: Environmental Test Handling

### 4.1 S3/Cloud Tests

**Strategy**: Skip tests that require external credentials rather than fail them.

**Files affected**:
```
samples/lancedb/lancedb_task1_init_007/tests/test_init.py  (S3)
samples/lancedb/lancedb_task1_init_008/tests/test_init.py  (if exists, cloud)
```

**Pattern**:
```python
import pytest
import os

@pytest.fixture
def requires_aws():
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        pytest.skip("AWS credentials required")

def test_s3_connection(requires_aws):
    from expected import app
    app.main()
```

### 4.2 OpenAI/Embedding Tests

**Files affected**: Task 1 samples using OpenAI embeddings

**Pattern**:
```python
@pytest.fixture
def requires_openai():
    import os
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("OpenAI API key required")
```

---

## Implementation Order

### Step 1: Create Test Utilities (1 file)
- [ ] Create `samples/lancedb/conftest.py` with helper functions

### Step 2: Fix Task 1 Tests (15 files)
- [ ] `lancedb_task1_init_001` - basic_connection
- [ ] `lancedb_task1_init_002` - memory_storage
- [ ] `lancedb_task1_init_003` - file_storage
- [ ] `lancedb_task1_init_004` - registry_openai (already works, verify)
- [ ] `lancedb_task1_init_005` - registry_sentence_transformers
- [ ] `lancedb_task1_init_006` - custom_embedding
- [ ] `lancedb_task1_init_007` - cloud_s3
- [ ] `lancedb_task1_init_008` through _015

### Step 3: Fix Task 2 Tests (15 files)
- [ ] `lancedb_task2_data_ops_016` through `_030`

### Step 4: Fix Task 3 Tests (10 files)
- [ ] `lancedb_task3_search_031` through `_040`

### Step 5: Verify Task 4-5 Tests (10 files)
- [ ] Verify Task 4 tests work (should be OK)
- [ ] Verify Task 5 tests work (should be OK)

### Step 6: Re-run Benchmark
- [ ] Run full benchmark with fixed tests
- [ ] Compare f_corr scores before/after
- [ ] Document improvement

---

## Validation Checklist

After fixes, verify:

- [ ] All tests pass against their `expected/` solutions
- [ ] Tests are architecture-agnostic (accept multiple valid patterns)
- [ ] Environmental tests skip gracefully without credentials
- [ ] No false negatives on functionally correct code
- [ ] f_corr metric accurately reflects functional correctness

---

## Expected Outcomes

| Metric | Before Fix | After Fix (Est.) |
|--------|------------|------------------|
| f_corr Pass Rate | 14% (7/50) | 80%+ (40+/50) |
| False Negatives | ~35 samples | ~5 samples |
| Test Quality | Structural | Behavioral |

---

## Notes

- Do NOT change expected solutions - only fix tests
- Preserve backward compatibility with module-level patterns
- Tests should pass for BOTH module-level and function-scoped implementations
- Document any samples that fail for legitimate reasons (actual bugs in LLM output)
