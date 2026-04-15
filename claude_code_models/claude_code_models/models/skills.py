"""Claude Code skill models (Agent Skills spec)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

__all__ = [
    "SkillFrontmatter",
    "SkillDefinition",
    "SlashCommand",
]

SKILL_NAME_RE = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"


class SkillFrontmatter(BaseModel):
    """YAML frontmatter from a SKILL.md file (Agent Skills spec)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    name: str = Field(max_length=64, pattern=SKILL_NAME_RE)
    description: str = Field(max_length=1024, min_length=1)
    license: str | None = None
    compatibility: str | None = Field(default=None, max_length=500)
    metadata: dict[str, str] | None = None
    allowed_tools: str | None = Field(
        default=None,
        alias="allowed-tools",
        description="Space-separated string of pre-approved tools (experimental)",
    )

    # Claude Code extensions
    argument_hint: str | None = Field(default=None, alias="argument-hint")
    disable_model_invocation: bool | None = Field(default=None, alias="disable-model-invocation")
    shell: str | None = Field(default=None, description="'bash' or 'powershell'")
    context: str | None = Field(default=None, description="'fork' to run in subagent context")

    @field_validator("name")
    @classmethod
    def no_consecutive_hyphens(cls, v: str) -> str:
        if "--" in v:
            raise ValueError("Skill name must not contain consecutive hyphens")
        return v


class SkillDefinition(BaseModel):
    """A complete skill including frontmatter and body."""

    model_config = ConfigDict(str_strip_whitespace=True)

    frontmatter: SkillFrontmatter
    body: str = Field(description="Markdown instructions after frontmatter")
    file_path: str | None = None
    source: str | None = Field(
        default=None,
        description="Where the skill comes from: 'project', 'user', 'plugin', 'bundled'",
    )


class SlashCommand(BaseModel):
    """A Claude Code slash command (built-in or skill-based)."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    name: str = Field(description="Command name without leading /")
    description: str
    is_skill: bool = Field(default=False, description="True if this is a bundled skill, not a built-in")
    arguments: str | None = Field(default=None, description="Argument syntax: '<arg>' required, '[arg]' optional")
    aliases: list[str] = Field(default_factory=list)
