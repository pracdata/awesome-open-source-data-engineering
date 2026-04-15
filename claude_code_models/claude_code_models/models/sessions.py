"""Claude Code session models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SessionStatus",
    "SessionSource",
    "Session",
    "SessionEvent",
]


class SessionStatus(StrEnum):
    RUNNING = "running"
    IDLE = "idle"
    STOPPED = "stopped"
    ERRORED = "errored"


class SessionSource(StrEnum):
    """How a session was started (used as SessionStart matcher)."""

    STARTUP = "startup"
    RESUME = "resume"
    CLEAR = "clear"
    COMPACT = "compact"


class Session(BaseModel):
    """A Claude Code session."""

    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: str
    name: str | None = None
    title: str | None = None
    status: SessionStatus = SessionStatus.RUNNING
    model: str | None = None
    cwd: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    parent_session_id: str | None = None
    forked_from: str | None = None
    pr_number: int | None = None
    agent: str | None = None
    total_tokens: int | None = None
    duration_ms: int | None = None


class SessionEvent(BaseModel):
    """An event in a session (user message, assistant message, tool use)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    type: str = Field(description="'user.message', 'assistant.message', 'tool_use', 'tool_result', etc.")
    content: list[dict] | str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str | None = None
