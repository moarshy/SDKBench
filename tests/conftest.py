"""Shared pytest fixtures and configuration for SDKBench tests."""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def samples_dir(project_root) -> Path:
    """Return the samples directory."""
    return project_root / "samples"


@pytest.fixture
def lancedb_samples_dir(samples_dir) -> Path:
    """Return the LanceDB samples directory."""
    return samples_dir / "lancedb"


@pytest.fixture
def clerk_samples_dir(samples_dir) -> Path:
    """Return the Clerk samples directory."""
    return samples_dir / "clerk"


# =============================================================================
# Temp Directory Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory that's cleaned up after the test."""
    tmp = Path(tempfile.mkdtemp(prefix="sdkbench_test_"))
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def temp_python_project(temp_dir) -> Path:
    """Create a temporary Python project structure."""
    # Create basic Python project
    (temp_dir / "app.py").write_text('def main():\n    print("Hello")\n')
    (temp_dir / "requirements.txt").write_text("pytest>=7.0.0\n")

    # Create tests directory
    tests_dir = temp_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text(
        'def test_example():\n    assert True\n'
    )

    return temp_dir


@pytest.fixture
def temp_typescript_project(temp_dir) -> Path:
    """Create a temporary TypeScript project structure."""
    # Create package.json
    (temp_dir / "package.json").write_text('''{
  "name": "test-project",
  "version": "1.0.0",
  "scripts": {
    "test": "jest"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "@types/jest": "^29.0.0",
    "typescript": "^5.0.0"
  }
}''')

    # Create tsconfig.json
    (temp_dir / "tsconfig.json").write_text('''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true
  }
}''')

    # Create source file
    (temp_dir / "app.ts").write_text('export function hello(): string { return "Hello"; }\n')

    # Create test file
    (temp_dir / "app.test.ts").write_text(
        "import { hello } from './app';\n"
        "test('hello returns Hello', () => { expect(hello()).toBe('Hello'); });\n"
    )

    return temp_dir


# =============================================================================
# Sample Fixtures
# =============================================================================

@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """Return a sample metadata structure."""
    return {
        "task_id": "test_task_001",
        "task_type": "init",
        "sdk": "test_sdk",
        "difficulty": "easy",
        "expected_files": ["app.py"],
        "required_imports": ["test_sdk"],
        "required_patterns": ["test_sdk.init()"],
    }


@pytest.fixture
def sample_lancedb_metadata() -> Dict[str, Any]:
    """Return sample LanceDB metadata."""
    return {
        "task_id": "lancedb_task1_init_001",
        "task_type": "init",
        "sdk": "lancedb",
        "difficulty": "easy",
        "expected_files": ["app.py"],
        "required_imports": ["lancedb"],
        "required_patterns": ["lancedb.connect"],
    }


@pytest.fixture
def sample_clerk_metadata() -> Dict[str, Any]:
    """Return sample Clerk metadata."""
    return {
        "task_id": "task1_init_001",
        "task_type": "init",
        "sdk": "clerk",
        "difficulty": "easy",
        "expected_files": ["app/layout.tsx", "package.json"],
        "required_imports": ["@clerk/nextjs"],
        "required_patterns": ["ClerkProvider"],
    }


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_solution(temp_dir) -> Path:
    """Create a mock solution directory."""
    solution_dir = temp_dir / "solution"
    solution_dir.mkdir()

    (solution_dir / "app.py").write_text('''
import lancedb

db = lancedb.connect("./data")

def main():
    print("LanceDB connected")

if __name__ == "__main__":
    main()
''')

    return solution_dir


@pytest.fixture
def mock_ground_truth(temp_dir) -> Path:
    """Create a mock ground truth directory."""
    gt_dir = temp_dir / "expected"
    gt_dir.mkdir()

    (gt_dir / "app.py").write_text('''
import lancedb

db = lancedb.connect("./data")

def main():
    print("LanceDB connected")
''')

    (gt_dir / "metadata.json").write_text('''{
    "task_id": "test_task_001",
    "sdk": "lancedb",
    "expected_files": ["app.py"],
    "required_imports": ["lancedb"],
    "required_patterns": ["lancedb.connect"]
}''')

    return gt_dir


# =============================================================================
# Utility Functions
# =============================================================================

def create_python_file(path: Path, content: str) -> Path:
    """Create a Python file with the given content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def create_test_sample(base_dir: Path, sdk: str, task_id: str) -> Path:
    """Create a complete test sample structure."""
    sample_dir = base_dir / sdk / task_id
    sample_dir.mkdir(parents=True)

    # Create expected directory
    expected_dir = sample_dir / "expected"
    expected_dir.mkdir()
    (expected_dir / "app.py").write_text('def main(): pass\n')
    (expected_dir / "metadata.json").write_text(f'{{"task_id": "{task_id}", "sdk": "{sdk}"}}\n')

    # Create tests directory
    tests_dir = sample_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text('def test_example(): assert True\n')

    # Create input directory
    input_dir = sample_dir / "input"
    input_dir.mkdir()

    return sample_dir
