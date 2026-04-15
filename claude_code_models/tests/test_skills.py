"""Tests for skill frontmatter, definitions, and slash commands."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claude_code_models.models.skills import (
    SkillDefinition,
    SkillFrontmatter,
    SlashCommand,
)


class TestSkillFrontmatter:
    def test_minimal(self) -> None:
        sf = SkillFrontmatter(name="my-skill", description="Does stuff")
        assert sf.name == "my-skill"
        assert sf.license is None

    def test_full(self) -> None:
        sf = SkillFrontmatter(
            name="pdf-processing",
            description="Extract PDF text, fill forms, merge files",
            license="Apache-2.0",
            compatibility="Requires Python 3.14+ and uv",
            metadata={"author": "org", "version": "1.0"},
            **{"allowed-tools": "Bash(uv:*) Read Write"},  # type: ignore[arg-type]
        )
        assert sf.allowed_tools == "Bash(uv:*) Read Write"
        assert sf.compatibility is not None

    @pytest.mark.validation
    def test_name_max_length(self) -> None:
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="a" * 65, description="Too long name")

    @pytest.mark.validation
    def test_name_no_uppercase(self) -> None:
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="My-Skill", description="Bad")

    @pytest.mark.validation
    def test_name_no_leading_hyphen(self) -> None:
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="-bad", description="Bad")

    @pytest.mark.validation
    def test_name_no_trailing_hyphen(self) -> None:
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="bad-", description="Bad")

    @pytest.mark.validation
    def test_name_no_consecutive_hyphens(self) -> None:
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="bad--name", description="Bad")

    @pytest.mark.validation
    def test_description_required(self) -> None:
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="good", description="")

    @pytest.mark.validation
    def test_description_max_length(self) -> None:
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="good", description="x" * 1025)

    def test_valid_names(self) -> None:
        for name in ["a", "abc", "my-skill", "a1b2c3", "x"]:
            sf = SkillFrontmatter(name=name, description="ok")
            assert sf.name == name


class TestSkillDefinition:
    def test_basic(self) -> None:
        sd = SkillDefinition(
            frontmatter=SkillFrontmatter(name="test", description="Test skill"),
            body="## Instructions\nDo the thing.",
        )
        assert sd.body.startswith("## Instructions")

    def test_with_source(self) -> None:
        sd = SkillDefinition(
            frontmatter=SkillFrontmatter(name="bundled", description="Built-in"),
            body="content",
            source="bundled",
            file_path=".claude/skills/bundled/SKILL.md",
        )
        assert sd.source == "bundled"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        sd = SkillDefinition(
            frontmatter=SkillFrontmatter(name="rt", description="Roundtrip test"),
            body="body",
        )
        data = sd.model_dump(mode="json")
        restored = SkillDefinition.model_validate(data)
        assert restored.frontmatter.name == "rt"


class TestSlashCommand:
    def test_built_in(self) -> None:
        cmd = SlashCommand(name="compact", description="Compact conversation", is_skill=False)
        assert cmd.is_skill is False

    def test_skill_command(self) -> None:
        cmd = SlashCommand(
            name="commit",
            description="Create a git commit",
            is_skill=True,
            arguments="[-m message]",
        )
        assert cmd.is_skill is True
        assert cmd.arguments is not None

    def test_with_aliases(self) -> None:
        cmd = SlashCommand(name="resume", description="Resume session", aliases=["r"])
        assert "r" in cmd.aliases

    def test_frozen(self) -> None:
        cmd = SlashCommand(name="help", description="Show help")
        with pytest.raises(ValidationError):
            cmd.name = "other"  # type: ignore[misc]
