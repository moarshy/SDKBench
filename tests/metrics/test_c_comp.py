"""Unit tests for C-COMP (Config Completeness) metric."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdkbench.core.result import CCompResult


class TestCCompResult:
    """Tests for CCompResult model."""

    def test_default_values(self):
        """Should have correct default values."""
        result = CCompResult()

        assert result.score == 0.0
        assert result.env_vars_score == 0.0
        assert result.provider_props_score == 0.0
        assert result.middleware_config_score == 0.0
        assert result.missing_env_vars == []
        assert result.missing_provider_props == []
        assert result.missing_middleware_config == []

    def test_score_calculation(self):
        """Should calculate score from component scores (0-1 scale inputs)."""
        # Component scores are on 0-1 scale
        result = CCompResult(
            env_vars_score=0.8,  # 80%
            provider_props_score=1.0,  # 100%
            middleware_config_score=0.6,  # 60%
        )

        # Formula: (env_vars * 0.5 + provider_props * 0.3 + middleware * 0.2) * 100
        expected = (0.8 * 0.5 + 1.0 * 0.3 + 0.6 * 0.2) * 100
        assert abs(result.score - expected) < 0.01

    def test_perfect_score(self):
        """Should return 100 for complete config."""
        result = CCompResult(
            env_vars_score=1.0,
            provider_props_score=1.0,
            middleware_config_score=1.0,
        )

        # (1.0 * 0.5 + 1.0 * 0.3 + 1.0 * 0.2) * 100 = 100
        assert result.score == 100.0

    def test_zero_score(self):
        """Should return 0 for missing config."""
        result = CCompResult(
            env_vars_score=0.0,
            provider_props_score=0.0,
            middleware_config_score=0.0,
        )

        assert result.score == 0.0


class TestCCompMissingItems:
    """Tests for tracking missing configuration items."""

    def test_missing_env_vars(self):
        """Should track missing environment variables."""
        result = CCompResult(
            env_vars_score=0.5,  # 50% on 0-1 scale
            missing_env_vars=[
                "CLERK_SECRET_KEY",
                "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
            ],
        )

        assert len(result.missing_env_vars) == 2
        assert "CLERK_SECRET_KEY" in result.missing_env_vars

    def test_missing_provider_props(self):
        """Should track missing provider properties."""
        result = CCompResult(
            provider_props_score=0.75,  # 75% on 0-1 scale
            missing_provider_props=["afterSignInUrl"],
        )

        assert len(result.missing_provider_props) == 1
        assert "afterSignInUrl" in result.missing_provider_props

    def test_missing_middleware_config(self):
        """Should track missing middleware configuration."""
        result = CCompResult(
            middleware_config_score=0.0,
            missing_middleware_config=[
                "publicRoutes",
                "ignoredRoutes",
            ],
        )

        assert len(result.missing_middleware_config) == 2

    def test_no_missing_items(self):
        """Should have empty lists when config is complete."""
        result = CCompResult(
            env_vars_score=1.0,
            provider_props_score=1.0,
            middleware_config_score=1.0,
            missing_env_vars=[],
            missing_provider_props=[],
            missing_middleware_config=[],
        )

        assert result.missing_env_vars == []
        assert result.missing_provider_props == []
        assert result.missing_middleware_config == []


class TestCCompPartialScores:
    """Tests for partial configuration scores."""

    def test_partial_env_vars(self):
        """Should calculate partial score for env vars."""
        # 2 out of 4 env vars present = 50%
        result = CCompResult(
            env_vars_score=0.5,  # 0-1 scale
            missing_env_vars=["VAR_A", "VAR_B"],
        )

        assert result.env_vars_score == 0.5
        assert len(result.missing_env_vars) == 2

    def test_partial_provider_props(self):
        """Should calculate partial score for provider props."""
        # 3 out of 4 props present = 75%
        result = CCompResult(
            provider_props_score=0.75,
            missing_provider_props=["prop1"],
        )

        assert result.provider_props_score == 0.75

    def test_one_component_complete(self):
        """Should handle one component being complete."""
        result = CCompResult(
            env_vars_score=1.0,  # 100%
            provider_props_score=0.5,  # 50%
            middleware_config_score=0.0,  # 0%
        )

        # (1.0 * 0.5 + 0.5 * 0.3 + 0.0 * 0.2) * 100 = 65
        expected = (1.0 * 0.5 + 0.5 * 0.3 + 0.0 * 0.2) * 100
        assert abs(result.score - expected) < 0.01

    def test_weighted_scoring(self):
        """Should weight components according to formula."""
        # env_vars * 0.5 + provider_props * 0.3 + middleware * 0.2
        result = CCompResult(
            env_vars_score=1.0,
            provider_props_score=0.0,
            middleware_config_score=0.0,
        )

        # Only env vars (weight 0.5) * 100 = 50
        assert result.score == 50.0
