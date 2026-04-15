"""Memory scope types for Claude Code agent memory and auto-memory."""

from __future__ import annotations

from enum import Enum

from agentwarehouses.models.base import BaseModel


class MemoryScope(str, Enum):
    USER = "user"
    PROJECT = "project"
    LOCAL = "local"


class MemoryConfig(BaseModel):
    """Agent memory configuration from agent frontmatter."""

    scope: MemoryScope
    agent_name: str
    memory_path: str | None = None


class MemoryFile(BaseModel):
    """Represents a MEMORY.md file for an agent."""

    scope: MemoryScope
    agent_name: str
    content: str
    path: str

    @property
    def base_dir(self) -> str:
        dirs = {
            MemoryScope.USER: "~/.claude/agent-memory/{agent_name}/",
            MemoryScope.PROJECT: ".claude/agent-memory/{agent_name}/",
            MemoryScope.LOCAL: ".claude/agent-memory-local/{agent_name}/",
        }
        return dirs[self.scope].format(agent_name=self.agent_name)


class AutoMemory(BaseModel):
    """Auto-memory entry stored in ~/.claude/auto-memories/."""

    content: str
    source: str | None = None
    created_at: str | None = None
