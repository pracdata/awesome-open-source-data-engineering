"""Tests for subagent and agent team models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claude_code_models.models.agents import (
    AgentTeam,
    AgentTeammate,
    SubAgentDefinition,
    SubAgentFrontmatter,
    SubAgentType,
    TeammateMode,
)


class TestSubAgentType:
    def test_built_in_types(self) -> None:
        assert SubAgentType.EXPLORE == "Explore"
        assert SubAgentType.PLAN == "Plan"
        assert SubAgentType.GENERAL_PURPOSE == "general-purpose"

    def test_custom(self) -> None:
        assert SubAgentType.CUSTOM == "custom"


class TestTeammateMode:
    def test_all(self) -> None:
        assert set(TeammateMode) == {"auto", "in-process", "tmux"}


class TestSubAgentFrontmatter:
    def test_minimal(self) -> None:
        sa = SubAgentFrontmatter(name="reviewer", description="Reviews code")
        assert sa.model is None
        assert sa.max_turns is None

    def test_full(self) -> None:
        sa = SubAgentFrontmatter(
            name="security-checker",
            description="Checks for security issues",
            model="sonnet",
            effort="high",
            maxTurns=20,
            tools=["Read", "Grep", "Glob"],
            disallowedTools=["Write", "Edit", "Bash"],
            skills=["security-scan"],
            memory="Remember past findings",
            background=True,
            isolation="worktree",
        )
        assert sa.max_turns == 20
        assert sa.isolation == "worktree"
        assert len(sa.tools or []) == 3
        assert len(sa.disallowed_tools or []) == 3

    @pytest.mark.validation
    def test_max_turns_positive(self) -> None:
        with pytest.raises(ValidationError):
            SubAgentFrontmatter(name="bad", description="Bad", maxTurns=0)

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        sa = SubAgentFrontmatter(name="test", description="Test agent", model="opus", maxTurns=5)
        data = sa.model_dump(mode="json", by_alias=True)
        assert "maxTurns" in data
        restored = SubAgentFrontmatter.model_validate(data)
        assert restored.max_turns == 5


class TestSubAgentDefinition:
    def test_basic(self) -> None:
        sd = SubAgentDefinition(
            frontmatter=SubAgentFrontmatter(name="helper", description="Helps"),
            prompt="You are a helpful assistant.",
        )
        assert sd.prompt.startswith("You are")

    def test_with_source(self) -> None:
        sd = SubAgentDefinition(
            frontmatter=SubAgentFrontmatter(name="built-in", description="Built in"),
            prompt="System prompt",
            source="built-in",
            file_path=".claude/agents/built-in.md",
        )
        assert sd.source == "built-in"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        sd = SubAgentDefinition(
            frontmatter=SubAgentFrontmatter(name="rt", description="RT"),
            prompt="test",
        )
        data = sd.model_dump(mode="json")
        restored = SubAgentDefinition.model_validate(data)
        assert restored.frontmatter.name == "rt"


class TestAgentTeammate:
    def test_basic(self) -> None:
        t = AgentTeammate(name="researcher", role="Information gathering")
        assert t.role == "Information gathering"

    def test_with_agent(self) -> None:
        t = AgentTeammate(name="coder", agent="my-coder-agent", model="opus")
        assert t.agent == "my-coder-agent"


class TestAgentTeam:
    def test_empty(self) -> None:
        team = AgentTeam()
        assert team.teammates == []
        assert team.display_mode == TeammateMode.AUTO

    def test_full(self) -> None:
        team = AgentTeam(
            name="dev-team",
            teammates=[
                AgentTeammate(name="leader", role="coordinator"),
                AgentTeammate(name="coder", role="implementation"),
                AgentTeammate(name="reviewer", role="code review"),
            ],
            display_mode=TeammateMode.TMUX,
        )
        assert len(team.teammates) == 3
        assert team.display_mode == TeammateMode.TMUX

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        team = AgentTeam(
            name="test-team",
            teammates=[AgentTeammate(name="a", role="test")],
        )
        data = team.model_dump(mode="json")
        restored = AgentTeam.model_validate(data)
        assert len(restored.teammates) == 1
