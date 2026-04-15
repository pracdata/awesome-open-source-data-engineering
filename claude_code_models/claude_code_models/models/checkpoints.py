"""Claude Code checkpointing: file state tracking and rewind."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "RewindAction",
    "Checkpoint",
    "CheckpointEntry",
]


class RewindAction(StrEnum):
    """Actions available when rewinding to a checkpoint."""

    RESTORE_CODE_AND_CONVERSATION = "restore_code_and_conversation"
    RESTORE_CONVERSATION = "restore_conversation"
    RESTORE_CODE = "restore_code"
    SUMMARIZE_FROM_HERE = "summarize_from_here"


class CheckpointEntry(BaseModel):
    """A single file state captured in a checkpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    file_path: str
    content_hash: str | None = None
    existed_before: bool = True


class Checkpoint(BaseModel):
    """A checkpoint capturing file state before an edit.

    Created automatically per user prompt. Persists across sessions.
    Cleaned up after 30 days (configurable).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    checkpoint_id: str
    session_id: str
    prompt_text: str | None = Field(default=None, description="The user prompt that triggered this checkpoint")
    files: list[CheckpointEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
