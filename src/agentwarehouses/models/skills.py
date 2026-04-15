"""Skill definition types for .claude/skills/{name}/SKILL.md files."""

from __future__ import annotations

from pydantic import Field, field_validator

from agentwarehouses.models.base import BaseModel


class SkillFrontmatter(BaseModel):
    """YAML frontmatter for SKILL.md files (AgentSkills.io spec)."""

    name: str = Field(max_length=64, pattern=r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
    description: str = Field(max_length=1536, min_length=1)
    disable_model_invocation: bool | None = Field(None, alias="disable-model-invocation")
    license: str | None = None
    compatibility: str | None = Field(None, max_length=500)
    metadata: dict[str, str] | None = None
    allowed_tools: str | None = Field(None, alias="allowed-tools")


class SkillFile(BaseModel):
    """Complete skill file representation (frontmatter + instructions)."""

    frontmatter: SkillFrontmatter
    instructions: str
    file_path: str | None = None


class SkillEvalAssertion(BaseModel):
    """A single assertion in a skill eval test case."""

    text: str = Field(min_length=1)


class SkillEvalCase(BaseModel):
    """A single eval test case following AgentSkills.io spec."""

    id: int
    prompt: str = Field(min_length=10)
    expected_output: str
    files: list[str] = Field(default_factory=list)
    assertions: list[str] = Field(min_length=1)

    @field_validator("assertions")
    @classmethod
    def assertions_not_empty(cls, v: list[str]) -> list[str]:
        for a in v:
            if not a.strip():
                raise ValueError("Assertions must be non-empty strings")
        return v


class SkillEvalSuite(BaseModel):
    """Complete eval suite for a skill (evals.json)."""

    skill_name: str
    evals: list[SkillEvalCase] = Field(min_length=1)

    @field_validator("evals")
    @classmethod
    def unique_ids(cls, v: list[SkillEvalCase]) -> list[SkillEvalCase]:
        ids = [e.id for e in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Eval IDs must be unique within a skill")
        return v
