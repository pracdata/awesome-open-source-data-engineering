"""Checkpoint and rewind types for Claude Code session state management."""

from __future__ import annotations

from enum import Enum

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class CheckpointActionType(str, Enum):
    RESTORE_CODE_AND_CONVERSATION = "restore_code_and_conversation"
    RESTORE_CONVERSATION_ONLY = "restore_conversation_only"
    RESTORE_CODE_ONLY = "restore_code_only"
    SUMMARIZE_FROM_HERE = "summarize_from_here"


class CheckpointAction(BaseModel):
    action_type: CheckpointActionType
    restore_original_prompt: bool | None = None


class CheckpointMessage(BaseModel):
    """A checkpoint based on a user prompt in the session."""

    prompt_number: int = Field(ge=1)
    user_prompt_text: str
    timestamp: str | None = None
    message_id: str


class CheckpointMetadata(BaseModel):
    session_id: str
    checkpoint_count: int = Field(ge=0)
    last_checkpoint_timestamp: str | None = None
    retention_days: int = 30


class RewindOptions(BaseModel):
    """Available options when accessing the rewind menu (Esc+Esc or /rewind)."""

    checkpoints: list[CheckpointMessage]
    selected_checkpoint: CheckpointMessage | None = None
    available_actions: list[CheckpointAction] = Field(default_factory=list)
