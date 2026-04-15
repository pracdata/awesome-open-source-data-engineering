"""Channel contract types for MCP channel notifications and permission relay."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class ChannelCapabilities(BaseModel):
    """Server capabilities declaration for channels."""

    channel: dict[str, Any] = Field(default_factory=dict, description="Always {}")
    permission: dict[str, Any] | None = Field(None, description="Enable permission relay")


class ChannelNotification(BaseModel):
    """A notification pushed into a Claude Code session via MCP channel."""

    method: Literal["notifications/claude/channel"] = "notifications/claude/channel"
    content: str
    meta: dict[str, str] | None = None


class ChannelPermissionRequest(BaseModel):
    """Permission relay request from channel to user."""

    method: Literal["notifications/claude/channel/permission_request"] = (
        "notifications/claude/channel/permission_request"
    )
    request_id: str = Field(min_length=5, max_length=5, pattern=r"^[a-km-z]{5}$")
    tool_name: str
    description: str
    input_preview: str = Field(max_length=200)


class ChannelPermissionVerdict(BaseModel):
    """Permission verdict from user back to channel."""

    method: Literal["notifications/claude/channel/permission"] = "notifications/claude/channel/permission"
    request_id: str = Field(min_length=5, max_length=5)
    behavior: Literal["allow", "deny"]


class ChannelReplyTool(BaseModel):
    """A tool exposed by a two-way channel for replies."""

    name: str
    description: str
    input_schema: dict[str, Any] = Field(alias="inputSchema")
