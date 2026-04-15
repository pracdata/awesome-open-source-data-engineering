"""Tests for channel notification, permission relay, and reply tool models."""

from __future__ import annotations

import pytest

from claude_code_models.models.channels import (
    ChannelNotification,
    ChannelReplyTool,
    ChannelServerConfig,
    PermissionRequest,
    PermissionVerdict,
)


class TestChannelNotification:
    def test_basic(self) -> None:
        n = ChannelNotification(content="build failed on main")
        assert n.content == "build failed on main"
        assert n.meta == {}

    def test_with_meta(self) -> None:
        n = ChannelNotification(content="alert", meta={"severity": "high", "run_id": "1234"})
        assert n.meta["severity"] == "high"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        n = ChannelNotification(content="test", meta={"key": "val"})
        data = n.model_dump(mode="json")
        restored = ChannelNotification.model_validate(data)
        assert restored.content == "test"
        assert restored.meta == {"key": "val"}


class TestChannelServerConfig:
    def test_one_way(self) -> None:
        cfg = ChannelServerConfig(name="webhook", instructions="Events from webhook channel")
        assert cfg.capabilities_tools is False
        assert cfg.capabilities_permission_relay is False

    def test_two_way(self) -> None:
        cfg = ChannelServerConfig(name="telegram", capabilities_tools=True, capabilities_permission_relay=True)
        assert cfg.capabilities_tools is True
        assert cfg.capabilities_permission_relay is True


class TestPermissionRequest:
    def test_fields(self) -> None:
        pr = PermissionRequest(
            request_id="abcde",
            tool_name="Bash",
            description="Run git push",
            input_preview='{"command": "git push"}',
        )
        assert len(pr.request_id) == 5
        assert pr.tool_name == "Bash"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        pr = PermissionRequest(
            request_id="fghij",
            tool_name="Write",
            description="Write file",
            input_preview="{}",
        )
        data = pr.model_dump(mode="json")
        restored = PermissionRequest.model_validate(data)
        assert restored.request_id == "fghij"


class TestPermissionVerdict:
    def test_allow(self) -> None:
        v = PermissionVerdict(request_id="abcde", behavior="allow")
        assert v.behavior == "allow"

    def test_deny(self) -> None:
        v = PermissionVerdict(request_id="abcde", behavior="deny")
        assert v.behavior == "deny"


class TestChannelReplyTool:
    def test_defaults(self) -> None:
        tool = ChannelReplyTool()
        assert tool.name == "reply"
        assert "chat_id" in tool.input_schema["properties"]
        assert "text" in tool.input_schema["properties"]
        assert tool.input_schema["required"] == ["chat_id", "text"]
