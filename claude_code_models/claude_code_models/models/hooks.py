"""Claude Code hooks: lifecycle events, handlers, matchers, and configuration."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "HookEventName",
    "HookHandlerType",
    "HookHandler",
    "CommandHook",
    "HttpHook",
    "PromptHook",
    "AgentHook",
    "HookMatcherGroup",
    "HookConfig",
    "HookInput",
    "HookOutput",
    "PreToolUseDecision",
    "PermissionRequestDecision",
    "PermissionUpdateEntry",
]


class HookEventName(StrEnum):
    """All Claude Code hook lifecycle events."""

    SESSION_START = "SessionStart"
    SESSION_END = "SessionEnd"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    STOP = "Stop"
    STOP_FAILURE = "StopFailure"
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    POST_TOOL_USE_FAILURE = "PostToolUseFailure"
    PERMISSION_REQUEST = "PermissionRequest"
    PERMISSION_DENIED = "PermissionDenied"
    SUBAGENT_START = "SubagentStart"
    SUBAGENT_STOP = "SubagentStop"
    TASK_CREATED = "TaskCreated"
    TASK_COMPLETED = "TaskCompleted"
    TEAMMATE_IDLE = "TeammateIdle"
    INSTRUCTIONS_LOADED = "InstructionsLoaded"
    CONFIG_CHANGE = "ConfigChange"
    FILE_CHANGED = "FileChanged"
    CWD_CHANGED = "CwdChanged"
    PRE_COMPACT = "PreCompact"
    POST_COMPACT = "PostCompact"
    WORKTREE_CREATE = "WorktreeCreate"
    WORKTREE_REMOVE = "WorktreeRemove"
    ELICITATION = "Elicitation"
    ELICITATION_RESULT = "ElicitationResult"
    NOTIFICATION = "Notification"


class HookHandlerType(StrEnum):
    COMMAND = "command"
    HTTP = "http"
    PROMPT = "prompt"
    AGENT = "agent"


class CommandHook(BaseModel):
    """Shell command hook handler."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: str = Field(default="command", pattern="^command$")
    command: str
    shell: str | None = Field(default=None, description="'bash' (default) or 'powershell'")
    async_: bool = Field(default=False, alias="async")
    timeout: int = Field(default=600, ge=1, description="Seconds before cancel")
    if_: str | None = Field(
        default=None,
        alias="if",
        description="Permission rule filter (e.g. 'Bash(git *)')",
    )
    status_message: str | None = Field(default=None, alias="statusMessage")
    once: bool | None = Field(default=None, description="Skills only: run once per session")


class HttpHook(BaseModel):
    """HTTP POST hook handler."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: str = Field(default="http", pattern="^http$")
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    allowed_env_vars: list[str] = Field(default_factory=list, alias="allowedEnvVars")
    timeout: int = Field(default=30, ge=1)
    if_: str | None = Field(default=None, alias="if")
    status_message: str | None = Field(default=None, alias="statusMessage")


class PromptHook(BaseModel):
    """LLM prompt hook handler."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: str = Field(default="prompt", pattern="^prompt$")
    prompt: str
    model: str | None = None
    timeout: int = Field(default=30, ge=1)
    if_: str | None = Field(default=None, alias="if")
    status_message: str | None = Field(default=None, alias="statusMessage")


class AgentHook(BaseModel):
    """Subagent verifier hook handler."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: str = Field(default="agent", pattern="^agent$")
    prompt: str
    timeout: int = Field(default=60, ge=1)
    if_: str | None = Field(default=None, alias="if")
    status_message: str | None = Field(default=None, alias="statusMessage")


HookHandler = CommandHook | HttpHook | PromptHook | AgentHook


class HookMatcherGroup(BaseModel):
    """A matcher group containing hooks that fire when the matcher matches.

    Matcher values:
    - '*', '', or omitted: match all
    - Letters/digits/_/|: exact string or pipe-separated list
    - Other characters: JavaScript regex
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    matcher: str | None = Field(default=None, description="Pattern to filter when hooks fire")
    hooks: list[HookHandler]


class HookConfig(BaseModel):
    """Full hooks configuration mapping event names to matcher groups."""

    model_config = ConfigDict(str_strip_whitespace=True)

    hooks: dict[HookEventName, list[HookMatcherGroup]] = Field(default_factory=dict)
    disable_all_hooks: bool = Field(default=False, alias="disableAllHooks")


class HookInput(BaseModel):
    """Common input fields passed to all hooks via stdin/POST body."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    session_id: str
    transcript_path: str | None = None
    cwd: str
    permission_mode: str
    hook_event_name: str
    agent_id: str | None = None
    agent_type: str | None = None
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    tool_use_id: str | None = None
    tool_response: str | None = None
    error: str | None = None
    prompt: str | None = None
    source: str | None = None


class PreToolUseDecision(BaseModel):
    """Decision output for PreToolUse hooks."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    hook_event_name: str = Field(default="PreToolUse", alias="hookEventName")
    permission_decision: str | None = Field(
        default=None,
        alias="permissionDecision",
        description="'allow', 'deny', 'ask', or 'defer'",
    )
    permission_decision_reason: str | None = Field(default=None, alias="permissionDecisionReason")
    updated_input: dict[str, Any] | None = Field(default=None, alias="updatedInput")
    additional_context: str | None = Field(default=None, alias="additionalContext")


class PermissionRequestDecision(BaseModel):
    """Decision output for PermissionRequest hooks."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    behavior: str = Field(description="'allow' or 'deny'")
    updated_input: dict[str, Any] | None = Field(default=None, alias="updatedInput")
    updated_permissions: list[PermissionUpdateEntry] = Field(default_factory=list, alias="updatedPermissions")


class PermissionUpdateEntry(BaseModel):
    """A permission update entry used in PermissionRequest hook output."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    type: str = Field(description="'addRules', 'setMode', or 'addDirectories'")
    rules: list[dict[str, str]] | None = None
    behavior: str | None = None
    mode: str | None = None
    directories: list[str] | None = None
    destination: str | None = None


class HookOutput(BaseModel):
    """Universal hook output format."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True, extra="allow")

    continue_: bool | None = Field(default=None, alias="continue")
    stop_reason: str | None = Field(default=None, alias="stopReason")
    suppress_output: bool | None = Field(default=None, alias="suppressOutput")
    system_message: str | None = Field(default=None, alias="systemMessage")
    decision: str | None = None
    reason: str | None = None
    hook_specific_output: dict[str, Any] | None = Field(default=None, alias="hookSpecificOutput")
