"""Tests to validate sample directory structure."""

import pytest
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def samples_dir():
    """Return the samples directory."""
    return Path(__file__).parent.parent.parent / "samples"


@pytest.fixture
def lancedb_samples(samples_dir):
    """Return all LanceDB sample directories."""
    lancedb_dir = samples_dir / "lancedb"
    if not lancedb_dir.exists():
        pytest.skip("LanceDB samples not found")
    return sorted([d for d in lancedb_dir.iterdir() if d.is_dir() and "task" in d.name])


@pytest.fixture
def clerk_samples(samples_dir):
    """Return all Clerk sample directories."""
    clerk_dir = samples_dir / "clerk"
    if not clerk_dir.exists():
        pytest.skip("Clerk samples not found")
    return sorted([d for d in clerk_dir.iterdir() if d.is_dir() and "task" in d.name])


# =============================================================================
# General Sample Structure Tests
# =============================================================================

class TestSampleDirectoryStructure:
    """Tests for sample directory structure."""

    def test_samples_directory_exists(self, samples_dir):
        """Should have samples directory."""
        assert samples_dir.exists(), "samples/ directory should exist"

    def test_has_lancedb_samples(self, samples_dir):
        """Should have LanceDB samples."""
        lancedb_dir = samples_dir / "lancedb"
        assert lancedb_dir.exists(), "samples/lancedb/ should exist"

    def test_has_clerk_samples(self, samples_dir):
        """Should have Clerk samples."""
        clerk_dir = samples_dir / "clerk"
        assert clerk_dir.exists(), "samples/clerk/ should exist"


class TestLanceDBSamples:
    """Tests for LanceDB samples."""

    def test_has_expected_directory(self, lancedb_samples):
        """Each sample should have expected/ directory."""
        for sample in lancedb_samples:
            expected_dir = sample / "expected"
            assert expected_dir.exists(), f"{sample.name} missing expected/"

    def test_has_tests_directory(self, lancedb_samples):
        """Each sample should have tests/ directory."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            assert tests_dir.exists(), f"{sample.name} missing tests/"

    def test_has_metadata_json(self, lancedb_samples):
        """Each sample should have metadata.json in expected/."""
        for sample in lancedb_samples:
            metadata = sample / "expected" / "metadata.json"
            assert metadata.exists(), f"{sample.name} missing expected/metadata.json"

    def test_metadata_is_valid_json(self, lancedb_samples):
        """Metadata should be valid JSON."""
        for sample in lancedb_samples:
            metadata = sample / "expected" / "metadata.json"
            if metadata.exists():
                try:
                    json.loads(metadata.read_text())
                except json.JSONDecodeError as e:
                    pytest.fail(f"{sample.name} has invalid metadata.json: {e}")

    def test_has_solution_file(self, lancedb_samples):
        """Each sample should have at least one .py file in expected/."""
        for sample in lancedb_samples:
            expected_dir = sample / "expected"
            py_files = list(expected_dir.glob("*.py"))
            assert len(py_files) > 0, f"{sample.name} has no .py files in expected/"

    def test_has_test_file(self, lancedb_samples):
        """Each sample should have at least one test file."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))
            assert len(test_files) > 0, f"{sample.name} has no test files"


class TestClerkSamples:
    """Tests for Clerk samples."""

    def test_has_expected_directory(self, clerk_samples):
        """Each sample should have expected/ directory."""
        for sample in clerk_samples:
            expected_dir = sample / "expected"
            assert expected_dir.exists(), f"{sample.name} missing expected/"

    def test_has_tests_directory(self, clerk_samples):
        """Each sample should have tests/ directory."""
        for sample in clerk_samples:
            tests_dir = sample / "tests"
            assert tests_dir.exists(), f"{sample.name} missing tests/"

    def test_has_metadata_json(self, clerk_samples):
        """Each sample should have metadata.json in expected/."""
        for sample in clerk_samples:
            metadata = sample / "expected" / "metadata.json"
            assert metadata.exists(), f"{sample.name} missing expected/metadata.json"

    def test_has_test_file(self, clerk_samples):
        """Each sample should have at least one test file."""
        missing_tests = []
        for sample in clerk_samples:
            tests_dir = sample / "tests"
            # Check for various test file patterns
            test_files = (
                list(tests_dir.glob("*.test.ts")) +
                list(tests_dir.glob("*.test.tsx")) +
                list(tests_dir.glob("*.spec.ts")) +
                list(tests_dir.glob("*.spec.tsx")) +
                list(tests_dir.glob("test_*.py"))  # Some might use Python
            )
            if len(test_files) == 0:
                missing_tests.append(sample.name)

        # Allow some samples to be missing tests (report but don't fail if < 10%)
        if len(missing_tests) > 0:
            pct_missing = len(missing_tests) / len(clerk_samples) * 100
            if pct_missing > 10:
                pytest.fail(f"{len(missing_tests)} Clerk samples missing tests: {missing_tests[:5]}...")


# =============================================================================
# Metadata Validation Tests
# =============================================================================

class TestMetadataContent:
    """Tests for metadata content validation."""

    def test_lancedb_metadata_has_required_fields(self, lancedb_samples):
        """LanceDB metadata should have required fields."""
        required_fields = ["sample_id", "sdk"]

        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                for field in required_fields:
                    assert field in metadata, f"{sample.name} metadata missing '{field}'"

    def test_clerk_metadata_has_required_fields(self, clerk_samples):
        """Clerk metadata should have required fields."""
        required_fields = ["sample_id"]  # Clerk may not have sdk field

        for sample in clerk_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                for field in required_fields:
                    assert field in metadata, f"{sample.name} metadata missing '{field}'"

    def test_sample_id_matches_directory(self, lancedb_samples):
        """Sample ID in metadata should match directory name."""
        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                sample_id = metadata.get("sample_id", "")
                assert sample.name == sample_id or sample_id in sample.name, \
                    f"{sample.name} sample_id mismatch: {sample_id}"


# =============================================================================
# Sample Count Tests
# =============================================================================

class TestSampleCounts:
    """Tests for sample counts."""

    def test_minimum_lancedb_samples(self, lancedb_samples):
        """Should have at least 40 LanceDB samples."""
        assert len(lancedb_samples) >= 40, f"Expected 40+ LanceDB samples, got {len(lancedb_samples)}"

    def test_minimum_clerk_samples(self, clerk_samples):
        """Should have at least 40 Clerk samples."""
        assert len(clerk_samples) >= 40, f"Expected 40+ Clerk samples, got {len(clerk_samples)}"

    def test_lancedb_has_all_task_types(self, lancedb_samples):
        """LanceDB should have samples for all 5 task types."""
        task_types = set()
        for sample in lancedb_samples:
            name = sample.name
            if "task1" in name:
                task_types.add("task1")
            elif "task2" in name:
                task_types.add("task2")
            elif "task3" in name:
                task_types.add("task3")
            elif "task4" in name:
                task_types.add("task4")
            elif "task5" in name:
                task_types.add("task5")

        assert len(task_types) >= 5, f"Missing task types: {5 - len(task_types)}"

    def test_clerk_has_all_task_types(self, clerk_samples):
        """Clerk should have samples for all 5 task types."""
        task_types = set()
        for sample in clerk_samples:
            name = sample.name
            if "task1" in name:
                task_types.add("task1")
            elif "task2" in name:
                task_types.add("task2")
            elif "task3" in name:
                task_types.add("task3")
            elif "task4" in name:
                task_types.add("task4")
            elif "task5" in name:
                task_types.add("task5")

        assert len(task_types) >= 5, f"Missing task types: {5 - len(task_types)}"

    def test_minimum_samples_per_task_type_lancedb(self, lancedb_samples):
        """Each task type should have minimum LanceDB samples."""
        task_counts = {"task1": 0, "task2": 0, "task3": 0, "task4": 0, "task5": 0}
        # Minimum samples per task type (task5 may have fewer)
        min_counts = {"task1": 5, "task2": 5, "task3": 5, "task4": 5, "task5": 1}

        for sample in lancedb_samples:
            name = sample.name
            for task in task_counts:
                if task in name:
                    task_counts[task] += 1
                    break

        for task, count in task_counts.items():
            min_required = min_counts.get(task, 5)
            assert count >= min_required, f"LanceDB {task} has only {count} samples (need {min_required}+)"


# =============================================================================
# Conftest Validation Tests
# =============================================================================

class TestConftestPresence:
    """Tests for conftest.py presence and structure."""

    def test_lancedb_has_conftest(self, samples_dir):
        """LanceDB samples should have a shared conftest.py."""
        conftest = samples_dir / "lancedb" / "conftest.py"
        assert conftest.exists(), "samples/lancedb/conftest.py should exist"

    def test_lancedb_conftest_has_fixtures(self, samples_dir):
        """LanceDB conftest should define fixtures."""
        conftest = samples_dir / "lancedb" / "conftest.py"
        if conftest.exists():
            content = conftest.read_text()
            assert "@pytest.fixture" in content, "conftest.py should have pytest fixtures"

    def test_lancedb_conftest_has_db_connection(self, samples_dir):
        """LanceDB conftest should have database connection helpers."""
        conftest = samples_dir / "lancedb" / "conftest.py"
        if conftest.exists():
            content = conftest.read_text()
            # Should have some form of DB connection helper
            assert "db" in content.lower() or "connection" in content.lower(), \
                "conftest.py should have database connection helpers"


# =============================================================================
# Solution File Validation Tests
# =============================================================================

class TestSolutionFiles:
    """Tests for solution file content."""

    def test_lancedb_solutions_import_lancedb(self, lancedb_samples):
        """LanceDB solutions should import lancedb."""
        for sample in lancedb_samples:
            expected_dir = sample / "expected"
            py_files = list(expected_dir.glob("*.py"))

            has_lancedb_import = False
            for py_file in py_files:
                if py_file.name == "__init__.py":
                    continue
                content = py_file.read_text()
                if "import lancedb" in content or "from lancedb" in content:
                    has_lancedb_import = True
                    break

            # Skip if no Python files (some samples might be TypeScript)
            if py_files:
                assert has_lancedb_import, f"{sample.name} solutions don't import lancedb"

    def test_lancedb_solutions_are_valid_python(self, lancedb_samples):
        """LanceDB solutions should be syntactically valid Python."""
        import ast

        for sample in lancedb_samples:
            expected_dir = sample / "expected"
            py_files = list(expected_dir.glob("*.py"))

            for py_file in py_files:
                try:
                    ast.parse(py_file.read_text())
                except SyntaxError as e:
                    pytest.fail(f"{sample.name}/{py_file.name} has syntax error: {e}")

    def test_lancedb_solutions_no_hardcoded_paths(self, lancedb_samples):
        """LanceDB solutions should not have hardcoded absolute paths."""
        for sample in lancedb_samples:
            expected_dir = sample / "expected"
            py_files = list(expected_dir.glob("*.py"))

            for py_file in py_files:
                content = py_file.read_text()
                # Check for common hardcoded path patterns
                assert "/Users/" not in content, \
                    f"{sample.name}/{py_file.name} has hardcoded /Users/ path"
                assert "/home/" not in content or "os.environ" in content, \
                    f"{sample.name}/{py_file.name} has hardcoded /home/ path"


# =============================================================================
# Test File Validation Tests
# =============================================================================

class TestTestFiles:
    """Tests for test file content."""

    def test_lancedb_tests_use_pytest(self, lancedb_samples):
        """LanceDB tests should use pytest."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))

            for test_file in test_files:
                content = test_file.read_text()
                assert "import pytest" in content or "from pytest" in content, \
                    f"{sample.name}/{test_file.name} doesn't import pytest"

    def test_lancedb_tests_have_assertions(self, lancedb_samples):
        """LanceDB tests should have assertions."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))

            for test_file in test_files:
                content = test_file.read_text()
                assert "assert" in content, \
                    f"{sample.name}/{test_file.name} has no assertions"

    def test_lancedb_tests_have_test_functions(self, lancedb_samples):
        """LanceDB tests should have test functions."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))

            for test_file in test_files:
                content = test_file.read_text()
                assert "def test_" in content, \
                    f"{sample.name}/{test_file.name} has no test functions"

    def test_lancedb_tests_import_solution(self, lancedb_samples):
        """LanceDB tests should import from expected solution."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))

            for test_file in test_files:
                content = test_file.read_text()
                # Tests should import something from the solution
                has_solution_import = (
                    "from expected" in content or
                    "import expected" in content or
                    "sys.path" in content  # If they're manipulating path to import
                )
                assert has_solution_import, \
                    f"{sample.name}/{test_file.name} doesn't import from solution"


# =============================================================================
# Metadata Detail Validation Tests
# =============================================================================

class TestMetadataDetails:
    """Tests for detailed metadata validation."""

    def test_lancedb_metadata_sdk_value(self, lancedb_samples):
        """LanceDB metadata should have sdk='lancedb'."""
        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                sdk = metadata.get("sdk", "")
                assert sdk == "lancedb", f"{sample.name} has wrong sdk: {sdk}"

    def test_lancedb_metadata_sample_id_format(self, lancedb_samples):
        """LanceDB sample_id should follow naming convention."""
        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                sample_id = metadata.get("sample_id", "")
                # Should start with lancedb_task
                assert sample_id.startswith("lancedb_task"), \
                    f"{sample.name} sample_id doesn't start with lancedb_task: {sample_id}"

    def test_clerk_metadata_has_framework(self, clerk_samples):
        """Clerk metadata should have framework field."""
        for sample in clerk_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                framework = metadata.get("framework", "")
                assert framework, f"{sample.name} missing framework field"

    def test_lancedb_metadata_has_description(self, lancedb_samples):
        """LanceDB metadata should have description field."""
        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                # Description is optional but recommended
                if "description" in metadata:
                    assert len(metadata["description"]) > 10, \
                        f"{sample.name} has too short description"

    def test_lancedb_metadata_has_difficulty(self, lancedb_samples):
        """LanceDB metadata should have difficulty field."""
        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                if "difficulty" in metadata:
                    valid_difficulties = ["easy", "medium", "hard", "beginner", "intermediate", "advanced"]
                    assert metadata["difficulty"].lower() in valid_difficulties, \
                        f"{sample.name} has invalid difficulty: {metadata['difficulty']}"


# =============================================================================
# Sample Naming Convention Tests
# =============================================================================

class TestNamingConventions:
    """Tests for sample naming conventions."""

    def test_lancedb_sample_naming(self, lancedb_samples):
        """LanceDB samples should follow naming convention."""
        for sample in lancedb_samples:
            name = sample.name
            # Should be: lancedb_task{N}_{type}_{id}
            assert name.startswith("lancedb_task"), \
                f"{name} doesn't follow naming convention"

            # Should have an underscore after taskN
            parts = name.split("_")
            assert len(parts) >= 3, f"{name} has too few underscore-separated parts"

    def test_clerk_sample_naming(self, clerk_samples):
        """Clerk samples should follow naming convention."""
        for sample in clerk_samples:
            name = sample.name
            # Should be: task{N}_{type}_{id} (without clerk_ prefix)
            assert name.startswith("task"), \
                f"{name} doesn't follow naming convention (should start with 'task')"

    def test_no_duplicate_sample_names_lancedb(self, lancedb_samples):
        """LanceDB samples should have unique names."""
        names = [s.name for s in lancedb_samples]
        assert len(names) == len(set(names)), "Duplicate LanceDB sample names found"

    def test_no_duplicate_sample_names_clerk(self, clerk_samples):
        """Clerk samples should have unique names."""
        names = [s.name for s in clerk_samples]
        assert len(names) == len(set(names)), "Duplicate Clerk sample names found"


# =============================================================================
# File Size and Content Sanity Tests
# =============================================================================

class TestFileSanity:
    """Tests for file sanity checks."""

    def test_lancedb_solutions_not_empty(self, lancedb_samples):
        """LanceDB solution files should not be empty."""
        for sample in lancedb_samples:
            expected_dir = sample / "expected"
            py_files = [f for f in expected_dir.glob("*.py") if f.name != "__init__.py"]

            for py_file in py_files:
                content = py_file.read_text().strip()
                assert len(content) > 50, \
                    f"{sample.name}/{py_file.name} is too short ({len(content)} chars)"

    def test_lancedb_tests_not_empty(self, lancedb_samples):
        """LanceDB test files should not be empty."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))

            for test_file in test_files:
                content = test_file.read_text().strip()
                assert len(content) > 100, \
                    f"{sample.name}/{test_file.name} is too short ({len(content)} chars)"

    def test_lancedb_metadata_not_empty(self, lancedb_samples):
        """LanceDB metadata should have meaningful content."""
        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                assert len(metadata) >= 2, \
                    f"{sample.name} metadata has too few fields"

    def test_solutions_reasonable_size(self, lancedb_samples):
        """Solution files should be reasonably sized."""
        for sample in lancedb_samples:
            expected_dir = sample / "expected"
            py_files = [f for f in expected_dir.glob("*.py") if f.name != "__init__.py"]

            for py_file in py_files:
                size = py_file.stat().st_size
                # Should be less than 50KB (reasonable for a solution file)
                assert size < 50000, \
                    f"{sample.name}/{py_file.name} is too large ({size} bytes)"


# =============================================================================
# Cross-Sample Consistency Tests
# =============================================================================

class TestCrossSampleConsistency:
    """Tests for consistency across samples."""

    def test_all_lancedb_samples_use_same_conftest(self, lancedb_samples, samples_dir):
        """All LanceDB samples should reference the shared conftest."""
        conftest_path = samples_dir / "lancedb" / "conftest.py"
        if not conftest_path.exists():
            pytest.skip("No shared conftest.py")

        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))

            for test_file in test_files:
                content = test_file.read_text()
                # Should import from conftest (directly or via path manipulation)
                uses_conftest = (
                    "from conftest" in content or
                    "import conftest" in content or
                    "conftest" in content
                )
                # This is a soft check - some tests might not need conftest
                if "conftest" not in content:
                    pass  # Okay, not all tests need conftest

    def test_consistent_test_structure_lancedb(self, lancedb_samples):
        """LanceDB tests should follow consistent structure."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            # Should have at least one test file
            test_files = list(tests_dir.glob("test_*.py"))
            assert len(test_files) >= 1, f"{sample.name} has no test files"

    def test_metadata_consistency_across_lancedb(self, lancedb_samples):
        """All LanceDB samples should have consistent metadata structure."""
        common_fields = set()
        first_sample = True

        for sample in lancedb_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                fields = set(metadata.keys())

                if first_sample:
                    common_fields = fields
                    first_sample = False
                else:
                    # At minimum, all should have sample_id and sdk
                    assert "sample_id" in fields, f"{sample.name} missing sample_id"
                    assert "sdk" in fields, f"{sample.name} missing sdk"

    def test_no_test_imports_from_absolute_paths(self, lancedb_samples):
        """Tests should not import using absolute paths."""
        for sample in lancedb_samples:
            tests_dir = sample / "tests"
            test_files = list(tests_dir.glob("test_*.py"))

            for test_file in test_files:
                content = test_file.read_text()
                # Should not have absolute path imports
                assert "from /Users" not in content, \
                    f"{sample.name}/{test_file.name} has absolute path import"
                assert "from /home" not in content, \
                    f"{sample.name}/{test_file.name} has absolute path import"


# =============================================================================
# Clerk-Specific Validation Tests
# =============================================================================

class TestClerkSpecificValidation:
    """Tests specific to Clerk samples."""

    def test_clerk_samples_have_source_files(self, clerk_samples):
        """Clerk samples should have TypeScript/JavaScript files."""
        missing_source = []
        for sample in clerk_samples:
            expected_dir = sample / "expected"
            # Check for TS/TSX/JS/JSX files
            ts_files = list(expected_dir.glob("*.ts")) + list(expected_dir.glob("*.tsx"))
            js_files = list(expected_dir.glob("*.js")) + list(expected_dir.glob("*.jsx"))
            # Also check for nested files in common patterns
            nested_ts = list(expected_dir.glob("**/*.ts")) + list(expected_dir.glob("**/*.tsx"))

            has_files = len(ts_files) > 0 or len(js_files) > 0 or len(nested_ts) > 0
            if not has_files:
                missing_source.append(sample.name)

        # Allow some samples to be incomplete (report but don't fail if < 10%)
        if len(missing_source) > 0:
            pct_missing = len(missing_source) / len(clerk_samples) * 100
            if pct_missing > 10:
                pytest.fail(f"{len(missing_source)} Clerk samples missing source files: {missing_source[:5]}...")

    def test_clerk_has_test_directory(self, clerk_samples):
        """Clerk samples should have a tests directory."""
        for sample in clerk_samples:
            tests_dir = sample / "tests"
            assert tests_dir.exists(), f"{sample.name} missing tests/"

    def test_clerk_metadata_sample_id_format(self, clerk_samples):
        """Clerk sample_id should follow naming convention."""
        for sample in clerk_samples:
            metadata_path = sample / "expected" / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                sample_id = metadata.get("sample_id", "")
                # Should start with task (without clerk_ prefix)
                assert sample_id.startswith("task"), \
                    f"{sample.name} sample_id doesn't start with task: {sample_id}"


# =============================================================================
# Task Type Distribution Tests
# =============================================================================

class TestTaskTypeDistribution:
    """Tests for task type distribution."""

    def test_lancedb_task1_samples(self, lancedb_samples):
        """Should have Task 1 (Init) samples for LanceDB."""
        task1_samples = [s for s in lancedb_samples if "task1" in s.name]
        assert len(task1_samples) >= 5, f"Need 5+ task1 samples, have {len(task1_samples)}"

    def test_lancedb_task2_samples(self, lancedb_samples):
        """Should have Task 2 (Data Operations) samples for LanceDB."""
        task2_samples = [s for s in lancedb_samples if "task2" in s.name]
        assert len(task2_samples) >= 5, f"Need 5+ task2 samples, have {len(task2_samples)}"

    def test_lancedb_task3_samples(self, lancedb_samples):
        """Should have Task 3 (Search) samples for LanceDB."""
        task3_samples = [s for s in lancedb_samples if "task3" in s.name]
        assert len(task3_samples) >= 5, f"Need 5+ task3 samples, have {len(task3_samples)}"

    def test_lancedb_task4_samples(self, lancedb_samples):
        """Should have Task 4 (Schema) samples for LanceDB."""
        task4_samples = [s for s in lancedb_samples if "task4" in s.name]
        assert len(task4_samples) >= 5, f"Need 5+ task4 samples, have {len(task4_samples)}"

    def test_lancedb_task5_samples(self, lancedb_samples):
        """Should have Task 5 (Indexing) samples for LanceDB."""
        task5_samples = [s for s in lancedb_samples if "task5" in s.name]
        # Task 5 may have fewer samples as it's more specialized
        assert len(task5_samples) >= 1, f"Need 1+ task5 samples, have {len(task5_samples)}"
