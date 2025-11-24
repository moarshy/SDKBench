"""GroundTruth class for loading sample metadata."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class GroundTruth:
    """Represents ground truth for a sample (loaded from metadata.json).

    The ground truth contains expected patterns, configurations, and
    evaluation targets for measuring LLM solution quality.
    """

    def __init__(self, metadata_path: Path):
        """Load ground truth from metadata.json.

        Args:
            metadata_path: Path to metadata.json file
        """
        self.metadata_path = Path(metadata_path)
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")

        self.metadata = self._load_json()
        self._validate_schema()

        # Core fields
        self.sample_id: str = self.metadata["sample_id"]
        self.task_type: int = self.metadata["task_type"]
        self.task_name: str = self.metadata["task_name"]
        self.framework: str = self.metadata["framework"]
        self.difficulty: str = self.metadata["difficulty"]

        # Handle clerk_version differently for migration tasks
        if self.task_type == 5:
            # For migration tasks, use the target version
            self.clerk_version: str = self.metadata.get("clerk_version_to", "5.0.0")
            self.clerk_version_from: str = self.metadata.get("clerk_version_from", "4.x")
        else:
            self.clerk_version: str = self.metadata["clerk_version"]

        # Ground truth data
        self.ground_truth: Dict = self.metadata["ground_truth"]
        self.ingredients: Dict = self.ground_truth.get("ingredients", {})
        self.evaluation_targets: Dict = self.metadata["evaluation_targets"]

    def _load_json(self) -> Dict:
        """Load JSON file."""
        with open(self.metadata_path, 'r') as f:
            return json.load(f)

    def _validate_schema(self) -> None:
        """Validate that metadata has required fields."""
        required_fields = [
            "sample_id",
            "task_type",
            "task_name",
            "framework",
            "difficulty",
            "ground_truth",
            "evaluation_targets"
        ]

        # Special handling for migration tasks (task_type 5)
        if self.metadata.get("task_type") == 5:
            # Migration tasks have clerk_version_from and clerk_version_to
            if "clerk_version_from" not in self.metadata or "clerk_version_to" not in self.metadata:
                raise ValueError("Migration tasks require clerk_version_from and clerk_version_to fields")
        else:
            # Other tasks require clerk_version
            required_fields.append("clerk_version")

        for field in required_fields:
            if field not in self.metadata:
                raise ValueError(f"Missing required field in metadata: {field}")

    # ==================== Ingredient Access ====================

    def get_initialization(self) -> Optional[Dict]:
        """Get initialization ingredient data.

        Returns:
            Dict with location, pattern, imports, or None
        """
        return self.ingredients.get("initialization")

    def get_configuration(self) -> Optional[Dict]:
        """Get configuration ingredient data.

        Returns:
            Dict with env_vars, provider_props, etc., or None
        """
        return self.ingredients.get("configuration")

    def get_integration_points(self) -> List[Dict]:
        """Get integration points data.

        Returns:
            List of integration point dicts
        """
        return self.ingredients.get("integration_points", [])

    def get_error_handling(self) -> List[Dict]:
        """Get error handling patterns.

        Returns:
            List of error handling patterns
        """
        return self.ingredients.get("error_handling", [])

    # ==================== Evaluation Targets ====================

    def get_i_acc_targets(self) -> Dict:
        """Get I-ACC evaluation targets.

        Returns:
            Dict with correct_file, correct_pattern, correct_imports
        """
        return self.evaluation_targets.get("i_acc", {})

    def get_c_comp_targets(self) -> Dict:
        """Get C-COMP evaluation targets.

        Returns:
            Dict with required_env_vars, optional_env_vars, etc.
        """
        return self.evaluation_targets.get("c_comp", {})

    def get_ipa_targets(self) -> Dict:
        """Get IPA evaluation targets.

        Returns:
            Dict with expected_protection_points, expected_hooks, etc.
        """
        return self.evaluation_targets.get("ipa", {})

    def get_f_corr_targets(self) -> Dict:
        """Get F-CORR evaluation targets.

        Returns:
            Dict with test_command, expected_pass
        """
        return self.evaluation_targets.get("f_corr", {})

    # ==================== Convenience Methods ====================

    def get_expected_files(self) -> List[str]:
        """Get list of files that should be modified.

        Returns:
            List of expected file paths
        """
        files = []

        # From initialization
        init = self.get_initialization()
        if init and "location" in init:
            files.append(init["location"])

        # From integration points
        for point in self.get_integration_points():
            if "location" in point:
                location = point["location"]
                if location not in files:
                    files.append(location)

        # From I-ACC targets
        i_acc = self.get_i_acc_targets()
        if "correct_file" in i_acc:
            file = i_acc["correct_file"]
            if file not in files:
                files.append(file)
        if "correct_files" in i_acc:
            for file in i_acc["correct_files"]:
                if file not in files:
                    files.append(file)

        return files

    def get_expected_imports(self) -> List[str]:
        """Get list of expected imports.

        Returns:
            List of expected import patterns
        """
        imports = []

        # From initialization
        init = self.get_initialization()
        if init and "imports" in init:
            imports.extend(init["imports"])

        # From I-ACC targets
        i_acc = self.get_i_acc_targets()
        if "correct_imports" in i_acc:
            imports.extend(i_acc["correct_imports"])

        return list(set(imports))  # Deduplicate

    def get_expected_env_vars(self) -> List[str]:
        """Get list of expected environment variables.

        Returns:
            List of required env var names
        """
        config = self.get_configuration()
        if config and "env_vars" in config:
            return config["env_vars"]
        return []

    def get_expected_patterns(self) -> List[str]:
        """Get list of expected patterns.

        Returns:
            List of pattern strings to look for
        """
        patterns = []

        # From initialization
        init = self.get_initialization()
        if init and "pattern" in init:
            patterns.append(init["pattern"])

        # From I-ACC targets
        i_acc = self.get_i_acc_targets()
        if "correct_pattern" in i_acc:
            patterns.append(i_acc["correct_pattern"])

        return patterns

    # ==================== String Representation ====================

    def __repr__(self) -> str:
        return (
            f"GroundTruth(sample_id={self.sample_id}, "
            f"task_type={self.task_type}, "
            f"framework={self.framework})"
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary.

        Returns:
            Full metadata dictionary
        """
        return self.metadata.copy()
