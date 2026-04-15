"""Session management types for Claude Code sessions."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class SessionInfo(BaseModel):
    """Session metadata as returned by list_sessions() / claude -r."""

    session_id: str
    summary: str
    last_modified: int
    file_size: int | None = None
    custom_title: str | None = None
    first_prompt: str | None = None
    git_branch: str | None = None
    cwd: str | None = None
    tag: str | None = None
    created_at: int | None = None


class SessionMessage(BaseModel):
    """A single message in a session transcript."""

    type: Literal["user", "assistant"]
    uuid: str
    session_id: str
    message: Any
    parent_tool_use_id: str | None = None


class SessionCLIFlags(BaseModel):
    """CLI flags for session management."""

    continue_: bool | None = Field(None, alias="continue", description="-c flag")
    resume: str | None = Field(None, description="-r <id|name>")
    session_id: str | None = Field(None, description="--session-id <uuid>")
    fork_session: bool | None = Field(None, description="--fork-session")
    teleport: bool | None = None
    remote: str | None = None
    name: str | None = Field(None, description="-n <name>")
    recap: bool | None = Field(None, description="Show recap on resume (2.1.108+)")
