"""Hook events, handlers, and input/output schemas for Claude Code's 25 hook events."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import Field

from agentwarehouses.models.base import BaseModel, LenientModel
from agentwarehouses.models.permissions import PermissionDecision


class HookEvent(str, Enum):
    SESSION_START = "SessionStart"
    SESSION_END = "SessionEnd"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    POST_TOOL_USE_FAILURE = "PostToolUseFailure"
    PERMISSION_REQUEST = "PermissionRequest"
    PERMISSION_DENIED = "PermissionDenied"
    STOP = "Stop"
    STOP_FAILURE = "StopFailure"
    NOTIFICATION = "Notification"
    SUBAGENT_START = "SubagentStart"
    SUBAGENT_STOP = "SubagentStop"
    TASK_CREATED = "TaskCreated"
    TASK_COMPLETED = "TaskCompleted"
    TEAMMATE_IDLE = "TeammateIdle"
    INSTRUCTIONS_LOADED = "InstructionsLoaded"
    CONFIG_CHANGE = "ConfigChange"
    CWD_CHANGED = "CwdChanged"
    FILE_CHANGED = "FileChanged"
    WORKTREE_CREATE = "WorktreeCreate"
    WORKTREE_REMOVE = "WorktreeRemove"
    PRE_COMPACT = "PreCompact"
    POST_COMPACT = "PostCompact"
    ELICITATION = "Elicitation"
    ELICITATION_RESULT = "ElicitationResult"


class HookHandlerType(str, Enum):
    COMMAND = "command"
    HTTP = "http"
    PROMPT = "prompt"
    AGENT = "agent"


class CommandHookHandler(BaseModel):
    type: Literal["command"]
    command: str
    timeout: int | None = None
    status_message: str | None = Field(None, alias="statusMessage")
    async_: bool | None = Field(None, alias="async")
    shell: Literal["bash", "powershell"] | None = None
    once: bool | None = None
    if_: str | None = Field(None, alias="if")


class HttpHookHandler(BaseModel):
    type: Literal["http"]
    url: str
    headers: dict[str, str] | None = None
    allowed_env_vars: list[str] | None = Field(None, alias="allowedEnvVars")
    timeout: int | None = None
    status_message: str | None = Field(None, alias="statusMessage")
    if_: str | None = Field(None, alias="if")


class PromptHookHandler(BaseModel):
    type: Literal["prompt"]
    prompt: str
    model: str | None = None
    timeout: int | None = None
    status_message: str | None = Field(None, alias="statusMessage")
    if_: str | None = Field(None, alias="if")


class AgentHookHandler(BaseModel):
    type: Literal["agent"]
    prompt: str
    timeout: int | None = None
    status_message: str | None = Field(None, alias="statusMessage")
    if_: str | None = Field(None, alias="if")


HookHandler = CommandHookHandler | HttpHookHandler | PromptHookHandler | AgentHookHandler


class HookMatcher(BaseModel):
    matcher: str | None = None
    hooks: list[HookHandler]


class HookConfig(BaseModel):
    """Full hooks section of .claude/settings.json."""

    hooks: dict[str, list[HookMatcher]] = Field(default_factory=dict)
    disable_all_hooks: bool | None = Field(None, alias="disableAllHooks")


# Hook input models


class BaseHookInput(LenientModel):
    session_id: str
    transcript_path: str
    cwd: str
    permission_mode: str | None = None
    hook_event_name: str
    agent_id: str | None = None
    agent_type: str | None = None


class PreToolUseInput(BaseHookInput):
    hook_event_name: Literal["PreToolUse"] = "PreToolUse"
    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str


class PostToolUseInput(BaseHookInput):
    hook_event_name: Literal["PostToolUse"] = "PostToolUse"
    tool_name: str
    tool_input: dict[str, Any]
    tool_response: Any
    tool_use_id: str


class PostToolUseFailureInput(BaseHookInput):
    hook_event_name: Literal["PostToolUseFailure"] = "PostToolUseFailure"
    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str
    error: str
    is_interrupt: bool | None = None


class UserPromptSubmitInput(BaseHookInput):
    hook_event_name: Literal["UserPromptSubmit"] = "UserPromptSubmit"
    prompt: str


class SessionStartInput(BaseHookInput):
    hook_event_name: Literal["SessionStart"] = "SessionStart"
    source: Literal["startup", "resume", "clear", "compact"]
    model: str | None = None


class StopInput(BaseHookInput):
    hook_event_name: Literal["Stop"] = "Stop"
    stop_hook_active: bool


class SubagentStopInput(BaseHookInput):
    hook_event_name: Literal["SubagentStop"] = "SubagentStop"
    stop_hook_active: bool
    agent_transcript_path: str
    last_assistant_message: str | None = None


class PreCompactInput(BaseHookInput):
    """Input for PreCompact hooks. Exit code 2 or {"decision":"block"} blocks compaction."""

    hook_event_name: Literal["PreCompact"] = "PreCompact"
    summary: str | None = None


class NotificationInput(BaseHookInput):
    hook_event_name: Literal["Notification"] = "Notification"
    message: str
    title: str | None = None
    notification_type: str


# Hook output model


class HookSpecificOutput(LenientModel):
    hook_event_name: str = Field(alias="hookEventName")
    additional_context: str | None = Field(None, alias="additionalContext")
    permission_decision: PermissionDecision | None = Field(None, alias="permissionDecision")
    permission_decision_reason: str | None = Field(None, alias="permissionDecisionReason")
    updated_input: dict[str, Any] | None = Field(None, alias="updatedInput")


class HookOutput(LenientModel):
    continue_: bool | None = Field(True, alias="continue")
    stop_reason: str | None = Field(None, alias="stopReason")
    suppress_output: bool | None = Field(None, alias="suppressOutput")
    system_message: str | None = Field(None, alias="systemMessage")
    decision: str | None = None
    reason: str | None = None
    hook_specific_output: HookSpecificOutput | None = Field(None, alias="hookSpecificOutput")
    additional_context: str | None = Field(None, alias="additionalContext")
