"""Claude Code channels: MCP-based message injection and permission relay."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ChannelNotification",
    "ChannelCapabilities",
    "ChannelServerConfig",
    "PermissionRequest",
    "PermissionVerdict",
    "ChannelReplyTool",
]


class ChannelNotification(BaseModel):
    """Payload for notifications/claude/channel events.

    Emitted by the MCP server, received by Claude Code, rendered as
    <channel source="..." attr1="..." attr2="...">content</channel>
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(description="Event body, becomes <channel> tag body")
    meta: dict[str, str] = Field(
        default_factory=dict,
        description="Each entry becomes a <channel> tag attribute. Keys: letters/digits/underscores only.",
    )


class ChannelCapabilities(BaseModel):
    """MCP Server experimental capabilities for channels."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    channel: dict = Field(default_factory=dict, description="Always {} — registers notification listener")
    channel_permission: dict | None = Field(
        default=None,
        alias="claude/channel/permission",
        description="Always {} if present — opts in to permission relay",
    )


class ChannelServerConfig(BaseModel):
    """Configuration for a channel MCP server."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    version: str = "0.0.1"
    instructions: str | None = Field(
        default=None,
        description="Added to Claude's system prompt. Tell Claude what events to expect and how to reply.",
    )
    capabilities_channel: bool = True
    capabilities_tools: bool = Field(default=False, description="True for two-way channels with reply tools")
    capabilities_permission_relay: bool = Field(
        default=False, description="True to receive and relay permission prompts"
    )


class PermissionRequest(BaseModel):
    """Outbound permission request from Claude Code to channel.

    Method: notifications/claude/channel/permission_request
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(description="Five lowercase letters (a-z minus 'l'). Include verbatim in outbound prompt.")
    tool_name: str = Field(description="Tool Claude wants to use (e.g. 'Bash', 'Write')")
    description: str = Field(description="Human-readable summary, same as local terminal dialog")
    input_preview: str = Field(description="Tool args as JSON, truncated to 200 chars")


class PermissionVerdict(BaseModel):
    """Verdict sent back from channel to Claude Code.

    Method: notifications/claude/channel/permission
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(description="Echoed from PermissionRequest")
    behavior: str = Field(description="'allow' or 'deny'")


class ChannelReplyTool(BaseModel):
    """Schema for a channel's reply tool (two-way channels)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = "reply"
    description: str = "Send a message back over this channel"
    input_schema: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "chat_id": {
                    "type": "string",
                    "description": "The conversation to reply in",
                },
                "text": {"type": "string", "description": "The message to send"},
            },
            "required": ["chat_id", "text"],
        }
    )
