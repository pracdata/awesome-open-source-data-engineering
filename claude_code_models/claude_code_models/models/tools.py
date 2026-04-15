"""Claude Code built-in tools reference models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ToolName",
    "ToolDefinition",
    "ToolPermissionRule",
    "PermissionMode",
    "ToolUseResult",
]


class ToolName(StrEnum):
    """All built-in Claude Code tool names (used in permission rules and hook matchers)."""

    AGENT = "Agent"
    ASK_USER_QUESTION = "AskUserQuestion"
    BASH = "Bash"
    CRON_CREATE = "CronCreate"
    CRON_DELETE = "CronDelete"
    CRON_LIST = "CronList"
    EDIT = "Edit"
    ENTER_PLAN_MODE = "EnterPlanMode"
    ENTER_WORKTREE = "EnterWorktree"
    EXIT_PLAN_MODE = "ExitPlanMode"
    EXIT_WORKTREE = "ExitWorktree"
    GLOB = "Glob"
    GREP = "Grep"
    LIST_MCP_RESOURCES = "ListMcpResourcesTool"
    LSP = "LSP"
    MONITOR = "Monitor"
    NOTEBOOK_EDIT = "NotebookEdit"
    POWERSHELL = "PowerShell"
    READ = "Read"
    READ_MCP_RESOURCE = "ReadMcpResourceTool"
    SEND_MESSAGE = "SendMessage"
    SKILL = "Skill"
    TASK_CREATE = "TaskCreate"
    TASK_GET = "TaskGet"
    TASK_LIST = "TaskList"
    TASK_OUTPUT = "TaskOutput"
    TASK_STOP = "TaskStop"
    TASK_UPDATE = "TaskUpdate"
    TEAM_CREATE = "TeamCreate"
    TEAM_DELETE = "TeamDelete"
    TODO_WRITE = "TodoWrite"
    TOOL_SEARCH = "ToolSearch"
    WEB_FETCH = "WebFetch"
    WEB_SEARCH = "WebSearch"
    WRITE = "Write"


class PermissionMode(StrEnum):
    """Claude Code permission modes."""

    DEFAULT = "default"
    ACCEPT_EDITS = "acceptEdits"
    PLAN = "plan"
    AUTO = "auto"
    DONT_ASK = "dontAsk"
    BYPASS_PERMISSIONS = "bypassPermissions"


class ToolDefinition(BaseModel):
    """A built-in Claude Code tool definition."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    name: ToolName
    description: str
    permission_required: bool = False


class ToolPermissionRule(BaseModel):
    """A tool-specific permission rule (allow/deny pattern).

    Pattern syntax:
    - Exact tool name: 'Bash'
    - Tool with argument pattern: 'Bash(git *)'
    - Path-based: 'Edit(*.ts)'
    - Wildcard: '*'
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    tool_name: str = Field(description="Tool name or pattern")
    rule_content: str | None = Field(default=None, description="Argument pattern")
    behavior: str = Field(description="'allow' or 'deny'")
    destination: str | None = Field(
        default=None,
        description="Where to persist: 'localSettings', 'projectSettings', 'userSettings', 'session'",
    )


class ToolUseResult(BaseModel):
    """Result from a tool execution (used in hooks)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    tool_name: str
    tool_use_id: str
    tool_input: dict = Field(default_factory=dict)
    tool_response: str | None = None
    error: str | None = None
    is_interrupt: bool = False
