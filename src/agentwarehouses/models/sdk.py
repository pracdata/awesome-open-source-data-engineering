"""Claude Agent SDK types — query(), ClaudeAgentOptions, message types.

Aligned with claude-agent-sdk Python package.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import Field

from agentwarehouses.models.base import BaseModel, LenientModel
from agentwarehouses.models.mcps import McpServerConfig
from agentwarehouses.models.permissions import PermissionMode
from agentwarehouses.models.subagents import AgentDefinitionSDK


class SettingSource(str, Enum):
    USER = "user"
    PROJECT = "project"
    LOCAL = "local"
    MANAGED = "managed"


class ThinkingConfigAdaptive(BaseModel):
    type: Literal["adaptive"]


class ThinkingConfigEnabled(BaseModel):
    type: Literal["enabled"]
    budget_tokens: int


class ThinkingConfigDisabled(BaseModel):
    type: Literal["disabled"]


ThinkingConfig = ThinkingConfigAdaptive | ThinkingConfigEnabled | ThinkingConfigDisabled


class SystemPromptPreset(BaseModel):
    type: Literal["preset"]
    preset: Literal["claude_code"]
    append: str | None = None


class ClaudeAgentOptions(LenientModel):
    """All options for query() — 40+ fields from the SDK dataclass."""

    tools: list[str] | None = None
    allowed_tools: list[str] = Field(default_factory=list)
    disallowed_tools: list[str] = Field(default_factory=list)
    system_prompt: str | SystemPromptPreset | None = None
    mcp_servers: dict[str, McpServerConfig] | str | None = None
    permission_mode: PermissionMode | None = None
    continue_conversation: bool = False
    resume: str | None = None
    max_turns: int | None = None
    max_budget_usd: float | None = None
    model: str | None = None
    fallback_model: str | None = None
    output_format: dict[str, Any] | None = None
    cwd: str | None = None
    env: dict[str, str] = Field(default_factory=dict)
    agents: dict[str, AgentDefinitionSDK] | None = None
    setting_sources: list[SettingSource] | None = None
    thinking: ThinkingConfig | None = None
    effort: Literal["low", "medium", "high", "max"] | None = None
    enable_file_checkpointing: bool = False
    include_partial_messages: bool = False
    fork_session: bool = False


# Message types


class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ThinkingBlock(BaseModel):
    type: Literal["thinking"] = "thinking"
    thinking: str
    signature: str
    progress_hint: str | None = None


class ToolUseBlock(BaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict[str, Any]


class ToolResultBlock(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str | list[dict[str, Any]] | None = None
    is_error: bool | None = None


ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock


class UserMessage(BaseModel):
    type: Literal["user"] = "user"
    content: str | list[ContentBlock]
    uuid: str | None = None
    parent_tool_use_id: str | None = None


class AssistantMessage(BaseModel):
    type: Literal["assistant"] = "assistant"
    content: list[ContentBlock]
    model: str | None = None
    parent_tool_use_id: str | None = None
    message_id: str | None = None


class ResultMessage(BaseModel):
    type: Literal["result"] = "result"
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    result: str | None = None
    stop_reason: str | None = None
    structured_output: Any = None


class SystemMessage(BaseModel):
    type: Literal["system"] = "system"
    subtype: str
    data: dict[str, Any] = Field(default_factory=dict)


class RateLimitStatus(str, Enum):
    ALLOWED = "allowed"
    ALLOWED_WARNING = "allowed_warning"
    REJECTED = "rejected"


class RateLimitInfo(BaseModel):
    status: RateLimitStatus
    resets_at: int | None = None
    utilization: float | None = None
