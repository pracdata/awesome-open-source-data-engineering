"""Claude Code CLI commands, flags, and environment variables."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "CLICommand",
    "CLIFlag",
    "OutputFormat",
    "InputFormat",
    "EffortLevel",
    "EnvironmentVariable",
    "CLIConfig",
]


class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


class InputFormat(StrEnum):
    TEXT = "text"
    STREAM_JSON = "stream-json"


class EffortLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"
    AUTO = "auto"


class CLICommand(BaseModel):
    """A Claude Code CLI command."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    name: str = Field(description="Command name (e.g. 'claude', 'claude auth login')")
    description: str
    example: str | None = None
    aliases: list[str] = Field(default_factory=list)


class CLIFlag(BaseModel):
    """A Claude Code CLI flag."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    flag: str = Field(description="Flag name (e.g. '--model', '-p')")
    short: str | None = Field(default=None, description="Short form (e.g. '-p')")
    description: str
    value_type: str | None = Field(default=None, description="Expected value type")
    default: str | None = None
    example: str | None = None
    requires: list[str] = Field(default_factory=list, description="Flags this depends on")


class EnvironmentVariable(BaseModel):
    """A Claude Code environment variable."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    name: str = Field(description="Variable name (e.g. 'ANTHROPIC_API_KEY')")
    description: str
    default: str | None = None
    value_type: str = Field(default="string", description="Expected type: string, int, bool, json")
    category: str | None = Field(
        default=None,
        description="Category: auth, model, api, bash, debug, display, feature, mcp, plugin, agent, etc.",
    )
    deprecated: bool = False
    deprecated_by: str | None = None


class CLIConfig(BaseModel):
    """Full CLI configuration state combining flags, env vars, and settings."""

    model_config = ConfigDict(str_strip_whitespace=True)

    model: str | None = None
    permission_mode: str | None = None
    effort: EffortLevel | None = None
    output_format: OutputFormat | None = None
    input_format: InputFormat | None = None
    max_turns: int | None = Field(default=None, ge=1)
    max_budget_usd: float | None = Field(default=None, gt=0)
    system_prompt: str | None = None
    append_system_prompt: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)
    disallowed_tools: list[str] = Field(default_factory=list)
    tools: str | None = Field(
        default=None,
        description="Restrict tools: '' disables all, 'default' for all, or comma-separated names",
    )
    add_dirs: list[str] = Field(default_factory=list)
    mcp_config: list[str] = Field(default_factory=list)
    betas: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    worktree: str | None = None
    session_id: str | None = None
    name: str | None = None
    agent: str | None = None
    bare: bool = False
    verbose: bool = False
    debug: str | None = None
    chrome: bool | None = None
    print_mode: bool = False
    continue_session: bool = False
    resume: str | None = None
