"""Slash command definitions for Claude Code (92 commands)."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class CommandType(str, Enum):
    BUILT_IN = "built_in"
    SKILL = "skill"


class CommandAvailability(str, Enum):
    ALL = "all"
    INTERACTIVE = "interactive"
    HEADLESS = "headless"
    WEB = "web"


class CommandArgument(BaseModel):
    name: str
    required: bool
    type: Literal["string", "enum", "number"]
    valid_values: list[str] | None = None
    description: str


class CommandDefinition(BaseModel):
    """A slash command available in Claude Code."""

    name: str = Field(pattern=r"^/[a-z]")
    description: str
    command_type: CommandType
    aliases: list[str] = Field(default_factory=list)
    arguments: list[CommandArgument] = Field(default_factory=list)
    available_in: list[CommandAvailability] = Field(default_factory=lambda: [CommandAvailability.ALL])
    platform: str | None = None


# Key commands as constants

CMD_CLEAR = CommandDefinition(
    name="/clear",
    description="Clear conversation and start fresh",
    command_type=CommandType.BUILT_IN,
    aliases=["/reset", "/new"],
)

CMD_COMPACT = CommandDefinition(
    name="/compact",
    description="Summarize conversation to free context",
    command_type=CommandType.BUILT_IN,
    arguments=[CommandArgument(name="instructions", required=False, type="string", description="Focus for summary")],
)

CMD_AGENTS = CommandDefinition(
    name="/agents",
    description="List all configured subagents",
    command_type=CommandType.BUILT_IN,
)

CMD_MCP = CommandDefinition(
    name="/mcp",
    description="View MCP server status and tools",
    command_type=CommandType.BUILT_IN,
)

CMD_HOOKS = CommandDefinition(
    name="/hooks",
    description="View configured hooks",
    command_type=CommandType.BUILT_IN,
)

CMD_EFFORT = CommandDefinition(
    name="/effort",
    description="Set effort level",
    command_type=CommandType.BUILT_IN,
    arguments=[
        CommandArgument(
            name="level",
            required=False,
            type="enum",
            valid_values=["low", "medium", "high", "max", "auto"],
            description="Effort level",
        )
    ],
)

# Commands added in 2.1.108

CMD_RECAP = CommandDefinition(
    name="/recap",
    description="Show recap of session activity; configurable in /config",
    command_type=CommandType.BUILT_IN,
)

CMD_UNDO = CommandDefinition(
    name="/undo",
    description="Undo last action (alias for /rewind)",
    command_type=CommandType.BUILT_IN,
    aliases=["/rewind"],
)
