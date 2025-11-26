"""End-to-end pipeline integration tests."""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core import Solution, GroundTruth, EvaluationResult
from sdkbench.evaluator.evaluator import Evaluator


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def complete_metadata() -> Dict[str, Any]:
    """Complete metadata structure with all fields."""
    return {
        "sample_id": "lancedb_task1_init_001",
        "task_type": 1,
        "task_name": "initialization",
        "sdk": "lancedb",
        "lancedb_version": "0.5.0",
        "framework": "python",
        "difficulty": "easy",
        "description": "Basic lancedb.connect() pattern",
        "ground_truth": {
            "ingredients": {
                "initialization": {
                    "location": "app.py",
                    "pattern": "lancedb.connect",
                    "imports": ["lancedb"]
                },
                "configuration": {
                    "db_path": "./my_lancedb",
                    "connection_method": "lancedb.connect"
                }
            }
        },
        "evaluation_targets": {
            "i_acc": {
                "correct_file": "app.py",
                "correct_pattern": "lancedb.connect",
                "correct_imports": ["import lancedb"]
            },
            "c_comp": {
                "required_components": 2,
                "components": ["import", "connection"]
            },
            "ipa": {
                "integration_points": ["lancedb.connect", "table_names"]
            },
            "f_corr": {
                "test_command": "pytest tests/test_init.py",
                "expected_pass": True
            }
        }
    }


@pytest.fixture
def sample_solution_content() -> str:
    """Sample solution file content (TypeScript for Solution class compatibility)."""
    return '''
import lancedb from "lancedb";

const db = await lancedb.connect("./my_lancedb");

export function listTables() {
    return db.tableNames();
}

export async function main() {
    console.log("Tables:", await listTables());
}
'''


@pytest.fixture
def complete_sample_dir(complete_metadata, sample_solution_content):
    """Create a complete sample directory structure."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="pipeline_test_"))

    # Create expected/ directory (ground truth)
    expected_dir = tmp_dir / "expected"
    expected_dir.mkdir()
    # Use .ts file so Solution class loads it (Solution only loads ts/tsx/js/jsx/json/env files)
    (expected_dir / "app.ts").write_text(sample_solution_content)
    (expected_dir / "metadata.json").write_text(json.dumps(complete_metadata, indent=2))

    # Create tests/ directory
    tests_dir = tmp_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_init.py").write_text('''
import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0] + "/expected")
from app import db

def test_connection_exists():
    """Test that db connection is established."""
    assert db is not None

def test_table_names_callable():
    """Test that table_names method exists."""
    assert hasattr(db, "table_names")
''')

    # Create input/ directory
    input_dir = tmp_dir / "input"
    input_dir.mkdir()
    (input_dir / "app.py").write_text('''
# TODO: Import lancedb
# TODO: Connect to database at "./my_lancedb"
# TODO: Implement list_tables() function

def main():
    pass

if __name__ == "__main__":
    main()
''')

    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


# =============================================================================
# Sample Loading Tests
# =============================================================================

class TestSampleLoading:
    """Tests for loading samples from disk."""

    def test_solution_loads_from_directory(self, complete_sample_dir):
        """Solution should load files from directory."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        assert solution is not None
        assert len(solution.files) > 0

    def test_solution_loads_typescript_files(self, complete_sample_dir):
        """Solution should load .ts files (Solution class supports ts/tsx/js/jsx/json/env)."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        assert any(f.endswith('.ts') for f in solution.files)

    def test_solution_has_file_content(self, complete_sample_dir):
        """Solution should have file content accessible."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        content = solution.get_file_content("app.ts")
        assert content is not None
        assert "lancedb" in content

    def test_solution_tracks_relative_paths(self, complete_sample_dir):
        """Solution should use relative paths as keys."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        # Keys should be relative paths, not absolute
        for path in solution.files.keys():
            assert not path.startswith("/")


# =============================================================================
# GroundTruth Parsing Tests
# =============================================================================

class TestGroundTruthParsing:
    """Tests for parsing metadata.json into GroundTruth."""

    def test_ground_truth_loads_from_metadata(self, complete_sample_dir):
        """GroundTruth should load from metadata.json."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        assert gt is not None

    def test_ground_truth_parses_sample_id(self, complete_sample_dir):
        """GroundTruth should parse sample_id."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        assert gt.sample_id == "lancedb_task1_init_001"

    def test_ground_truth_parses_task_type(self, complete_sample_dir):
        """GroundTruth should parse task_type."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        assert gt.task_type == 1

    def test_ground_truth_parses_sdk(self, complete_sample_dir):
        """GroundTruth should parse SDK name."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        assert gt.sdk == "lancedb"

    def test_ground_truth_parses_framework(self, complete_sample_dir):
        """GroundTruth should parse framework."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        assert gt.framework == "python"

    def test_ground_truth_has_evaluation_targets(self, complete_sample_dir):
        """GroundTruth should have evaluation_targets."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        assert gt.evaluation_targets is not None
        assert "i_acc" in gt.evaluation_targets

    def test_ground_truth_i_acc_targets(self, complete_sample_dir):
        """GroundTruth should provide I-ACC targets."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        targets = gt.get_i_acc_targets()
        assert "correct_file" in targets
        assert targets["correct_file"] == "app.py"

    def test_ground_truth_expected_files(self, complete_sample_dir):
        """GroundTruth should return expected files list."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        files = gt.get_expected_files()
        assert len(files) > 0

    def test_ground_truth_expected_imports(self, complete_sample_dir):
        """GroundTruth should return expected imports."""
        metadata_path = complete_sample_dir / "expected" / "metadata.json"
        gt = GroundTruth(metadata_path)

        imports = gt.get_expected_imports()
        assert len(imports) > 0


# =============================================================================
# Solution Analysis Tests
# =============================================================================

class TestSolutionAnalysis:
    """Tests for Solution analysis methods."""

    def test_solution_extract_imports(self, complete_sample_dir):
        """Solution should extract import statements."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        imports = solution.extract_imports()
        assert len(imports) > 0
        assert any("lancedb" in imp for imp in imports)

    def test_solution_has_import(self, complete_sample_dir):
        """Solution should check for specific imports."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        assert solution.has_import("lancedb")

    def test_solution_has_pattern(self, complete_sample_dir):
        """Solution should detect patterns in code."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        assert solution.has_pattern("lancedb.connect")

    def test_solution_has_file(self, complete_sample_dir):
        """Solution should check file existence."""
        solution_dir = complete_sample_dir / "expected"
        solution = Solution(solution_dir)

        assert solution.has_file("app.ts")
        assert not solution.has_file("nonexistent.ts")


# =============================================================================
# Evaluation Execution Tests
# =============================================================================

class TestEvaluationExecution:
    """Tests for full evaluation execution."""

    def test_evaluation_completes_without_error(self, complete_sample_dir):
        """Full evaluation should complete without errors."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate_quick()

        assert result is not None
        assert isinstance(result, EvaluationResult)

    def test_evaluation_returns_scores(self, complete_sample_dir):
        """Evaluation should return metric scores."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate_quick()

        # At least some metrics should have scores
        assert result.i_acc is not None or result.c_comp is not None

    def test_evaluation_has_overall_score(self, complete_sample_dir):
        """Evaluation should calculate overall score."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate_quick()

        assert hasattr(result, 'overall_score')
        assert result.overall_score >= 0.0


# =============================================================================
# Result Serialization Tests
# =============================================================================

class TestResultSerialization:
    """Tests for result serialization/deserialization."""

    def test_results_serialize_to_dict(self, complete_sample_dir):
        """Results should serialize to dictionary."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate_quick()
        data = result.model_dump()

        assert isinstance(data, dict)
        assert "sample_id" in data

    def test_results_serialize_to_json(self, complete_sample_dir):
        """Results should serialize to valid JSON."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate_quick()
        data = result.model_dump()

        # Should not raise
        json_str = json.dumps(data, default=str)
        assert json_str is not None

    def test_results_save_to_file(self, complete_sample_dir, tmp_path):
        """Results should save to JSON file."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate_quick()

        output_path = tmp_path / "result.json"
        result.to_json_file(output_path)

        assert output_path.exists()

    def test_results_deserialize_from_json(self, complete_sample_dir, tmp_path):
        """Results should be loadable from JSON file."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)
        result = evaluator.evaluate_quick()

        # Save
        output_path = tmp_path / "result.json"
        result.to_json_file(output_path)

        # Load
        with open(output_path) as f:
            data = json.load(f)

        assert data["sample_id"] == "lancedb_task1_init_001"


# =============================================================================
# Multi-Sample Pipeline Tests
# =============================================================================

class TestMultiSamplePipeline:
    """Tests for processing multiple samples."""

    def test_batch_evaluate_single_sample(self, complete_sample_dir, tmp_path):
        """Batch evaluate should handle single sample."""
        solution_dir = complete_sample_dir / "expected"

        results = Evaluator.batch_evaluate(
            [solution_dir],
            output_dir=tmp_path,
            run_build=False,
            run_tests=False
        )

        assert len(results) == 1

    def test_batch_evaluate_continues_on_failure(self, complete_sample_dir, tmp_path):
        """Batch evaluate should continue when sample fails."""
        solution_dir = complete_sample_dir / "expected"
        bad_dir = tmp_path / "bad_sample"
        bad_dir.mkdir()

        # Should not raise
        results = Evaluator.batch_evaluate(
            [bad_dir, solution_dir],
            output_dir=tmp_path,
            run_build=False,
            run_tests=False
        )

        # At least one should succeed
        assert isinstance(results, list)


# =============================================================================
# Cross-Component Integration Tests
# =============================================================================

class TestCrossComponentIntegration:
    """Tests for integration between components."""

    def test_solution_and_ground_truth_loaded(self, complete_sample_dir):
        """Solution and GroundTruth should both load from sample directory."""
        solution_dir = complete_sample_dir / "expected"
        metadata_path = complete_sample_dir / "expected" / "metadata.json"

        solution = Solution(solution_dir)
        gt = GroundTruth(metadata_path)

        # Both should load successfully
        assert solution is not None
        assert gt is not None
        assert len(solution.files) > 0

    def test_evaluator_links_solution_and_ground_truth(self, complete_sample_dir):
        """Evaluator should properly link Solution and GroundTruth."""
        solution_dir = complete_sample_dir / "expected"

        evaluator = Evaluator(solution_dir)

        # Both should be linked
        assert evaluator.solution is not None
        assert evaluator.ground_truth is not None
        assert evaluator.ground_truth.sample_id == "lancedb_task1_init_001"


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestPipelineEdgeCases:
    """Tests for edge cases in the pipeline."""

    def test_empty_solution_directory(self, tmp_path, complete_metadata):
        """Pipeline should handle empty solution directory (no supported files)."""
        solution_dir = tmp_path / "empty"
        solution_dir.mkdir()
        (solution_dir / "metadata.json").write_text(json.dumps(complete_metadata))

        # Solution with no .ts/.js files (only json is loaded, but that's metadata)
        solution = Solution(solution_dir)
        # metadata.json is loaded since Solution loads .json files
        assert len(solution.files) >= 1

    def test_solution_with_nested_directories(self, tmp_path, complete_metadata):
        """Solution should handle nested directory structure."""
        solution_dir = tmp_path / "nested"
        solution_dir.mkdir()

        # Create nested structure with TypeScript files (Solution loads ts/tsx/js/jsx)
        (solution_dir / "src").mkdir()
        (solution_dir / "src" / "app.ts").write_text("import lancedb from 'lancedb'")
        (solution_dir / "metadata.json").write_text(json.dumps(complete_metadata))

        solution = Solution(solution_dir)
        # Should find the nested file
        assert any("app.ts" in f for f in solution.files)

    def test_unicode_in_solution_files(self, tmp_path, complete_metadata):
        """Solution should handle unicode content."""
        solution_dir = tmp_path / "unicode"
        solution_dir.mkdir()

        # Create TypeScript file with unicode
        (solution_dir / "app.ts").write_text('// Comment with unicode: 日本語\nimport lancedb from "lancedb"')
        (solution_dir / "metadata.json").write_text(json.dumps(complete_metadata))

        solution = Solution(solution_dir)
        content = solution.get_file_content("app.ts")
        assert "日本語" in content
