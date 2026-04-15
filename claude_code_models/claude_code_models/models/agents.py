"""Claude Code subagent and agent team models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SubAgentType",
    "SubAgentFrontmatter",
    "SubAgentDefinition",
    "AgentTeammate",
    "AgentTeam",
    "TeammateMode",
]


class SubAgentType(StrEnum):
    """Built-in subagent types."""

    GENERAL_PURPOSE = "general-purpose"
    EXPLORE = "Explore"
    PLAN = "Plan"
    CODE_REVIEWER = "code-reviewer"
    STATUSLINE_SETUP = "statusline-setup"
    CLAUDE_CODE_GUIDE = "claude-code-guide"
    CUSTOM = "custom"


class TeammateMode(StrEnum):
    """Agent team teammate display modes."""

    AUTO = "auto"
    IN_PROCESS = "in-process"
    TMUX = "tmux"


class SubAgentFrontmatter(BaseModel):
    """AGENT.md frontmatter for subagent definitions."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    name: str
    description: str
    model: str | None = Field(default=None, description="Model alias or full ID")
    effort: str | None = Field(default=None, description="'low', 'medium', 'high', 'max'")
    max_turns: int | None = Field(default=None, alias="maxTurns", ge=1)
    tools: list[str] | None = None
    disallowed_tools: list[str] | None = Field(default=None, alias="disallowedTools")
    skills: list[str] | None = None
    memory: str | None = Field(default=None, description="Memory instructions or path")
    background: bool | None = None
    isolation: str | None = Field(default=None, description="'worktree' or None")

    # Plugin agents cannot use these (security restriction)
    # hooks: not allowed
    # mcpServers: not allowed
    # permissionMode: not allowed


class SubAgentDefinition(BaseModel):
    """A complete subagent definition."""

    model_config = ConfigDict(str_strip_whitespace=True)

    frontmatter: SubAgentFrontmatter
    prompt: str = Field(description="System prompt / instructions for the agent")
    file_path: str | None = None
    source: str | None = Field(
        default=None,
        description="Where defined: 'project', 'user', 'plugin', 'cli', 'built-in'",
    )


class AgentTeammate(BaseModel):
    """A teammate in an agent team."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    role: str | None = None
    agent: str | None = Field(default=None, description="Agent definition to use")
    model: str | None = None
    cwd: str | None = None


class AgentTeam(BaseModel):
    """An agent team configuration (AGENTS.md or TeamCreate)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = None
    teammates: list[AgentTeammate] = Field(default_factory=list)
    display_mode: TeammateMode = TeammateMode.AUTO
