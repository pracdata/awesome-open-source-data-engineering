"""Tool definitions and parameter schemas for Claude Code's 37 built-in tools."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class ToolCategory(str, Enum):
    FILE_OPERATIONS = "file_operations"
    CODE_EXECUTION = "code_execution"
    CODE_SEARCH = "code_search"
    FILE_SEARCH = "file_search"
    WEB_OPERATIONS = "web_operations"
    SUBAGENT_SPAWNING = "subagent_spawning"
    AGENT_TEAMS = "agent_teams"
    TASK_MANAGEMENT = "task_management"
    MCP_INTEGRATION = "mcp_integration"
    CODE_INTELLIGENCE = "code_intelligence"
    SCHEDULING = "scheduling"
    MODE_SWITCHING = "mode_switching"
    USER_INTERACTION = "user_interaction"
    WORKFLOW = "workflow"
    GIT_OPERATIONS = "git_operations"
    BACKGROUND_TASKS = "background_tasks"


class ParamType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NUMBER = "number"


class ToolParameter(BaseModel):
    name: str
    type: ParamType
    required: bool
    description: str
    valid_values: list[str] | None = None
    default: Any | None = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    permission_required: bool
    category: ToolCategory
    parameters: list[ToolParameter] = Field(default_factory=list)


# Per-tool input models


class BashInput(BaseModel):
    command: str
    description: str | None = None
    timeout: int | None = None
    run_in_background: bool | None = None


class EditInput(BaseModel):
    file_path: str
    old_string: str
    new_string: str
    replace_all: bool = False


class WriteInput(BaseModel):
    file_path: str
    content: str


class ReadInput(BaseModel):
    file_path: str
    offset: int | None = None
    limit: int | None = None
    pages: str | None = None


class GlobInput(BaseModel):
    pattern: str
    path: str | None = None


class GrepInput(BaseModel):
    pattern: str
    path: str | None = None
    glob: str | None = None
    output_mode: Literal["content", "files_with_matches", "count"] | None = None
    case_insensitive: bool | None = Field(None, alias="-i")
    multiline: bool | None = None
    context: int | None = None
    head_limit: int | None = None


class AgentToolInput(BaseModel):
    prompt: str
    description: str
    subagent_type: str | None = None
    model: str | None = None
    isolation: Literal["worktree"] | None = None
    run_in_background: bool | None = None


class WebFetchInput(BaseModel):
    url: str
    prompt: str


class WebSearchInput(BaseModel):
    query: str
    allowed_domains: list[str] | None = None
    blocked_domains: list[str] | None = None


class TodoItem(BaseModel):
    content: str
    status: Literal["pending", "in_progress", "completed"]
    active_form: str = Field(alias="activeForm")


class TodoWriteInput(BaseModel):
    todos: list[TodoItem]


class NotebookEditInput(BaseModel):
    notebook_path: str
    cell_index: int
    new_source: str


class SkillToolInput(BaseModel):
    skill: str
    args: str | None = None


class SendMessageInput(BaseModel):
    to: str
    message: str


class TaskCreateInput(BaseModel):
    subject: str
    description: str | None = None
    teammate_name: str | None = None


class AskUserQuestionInput(BaseModel):
    questions: list[dict[str, Any]]


# All 37 tool names as an enum
class ToolName(str, Enum):
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
