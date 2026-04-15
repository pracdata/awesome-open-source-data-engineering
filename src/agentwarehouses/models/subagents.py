"""Subagent definition types for CLI (.claude/agents/) and SDK (AgentDefinition)."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from agentwarehouses.models.base import BaseModel
from agentwarehouses.models.permissions import PermissionMode


class ModelTier(str, Enum):
    OPUS = "opus"
    SONNET = "sonnet"
    HAIKU = "haiku"
    INHERIT = "inherit"


class MemoryScope(str, Enum):
    USER = "user"
    PROJECT = "project"
    LOCAL = "local"


class ContextMode(str, Enum):
    DEFAULT = "default"
    FORK = "fork"


class AgentFrontmatter(BaseModel):
    """YAML frontmatter for .claude/agents/{name}.md files."""

    name: str
    description: str
    tools: list[str] | None = None
    model: ModelTier | None = None
    skills: list[str] | None = None
    memory: MemoryScope | None = None
    mcp_servers: list[str | dict[str, Any]] | None = Field(None, alias="mcpServers")
    context: ContextMode | None = None
    hooks: dict[str, list[dict[str, Any]]] | None = None
    permission_mode: PermissionMode | None = Field(None, alias="permissionMode")


class AgentDefinitionSDK(BaseModel):
    """SDK AgentDefinition — passed to query() as agents={name: AgentDefinition(...)}."""

    description: str
    prompt: str
    tools: list[str] | None = None
    model: ModelTier | None = None
    skills: list[str] | None = None
    memory: MemoryScope | None = None
    mcp_servers: list[str | dict[str, Any]] | None = Field(None, alias="mcpServers")


class AgentCLIFlags(BaseModel):
    """CLI flags for agent invocation."""

    agent: str | None = Field(None, description="--agent flag: reference .claude/agents/{name}.md")
    agents_json: str | None = Field(None, description="--agents flag: inline JSON agent definitions")


class AgentFile(BaseModel):
    """Complete agent file representation (frontmatter + body)."""

    frontmatter: AgentFrontmatter
    system_prompt: str
    file_path: str | None = None


class AgentGraphQLInput(BaseModel):
    """GraphQL createAgent mutation input."""

    name: str
    description: str
    prompt: str
    tools: list[str] | None = None
    model: ModelTier | None = None
    skills: list[str] | None = None
    memory: MemoryScope | None = None
    emotion_calibration: str | None = None
