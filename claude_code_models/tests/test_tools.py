"""Tests for tool definitions, permission rules, and permission modes."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claude_code_models.models.tools import (
    PermissionMode,
    ToolDefinition,
    ToolName,
    ToolPermissionRule,
    ToolUseResult,
)


class TestToolName:
    def test_all_tools_enumerated(self) -> None:
        assert len(ToolName) == 35

    def test_core_tools_exist(self) -> None:
        core = {"Bash", "Read", "Write", "Edit", "Glob", "Grep", "Agent", "Skill"}
        assert core.issubset({t.value for t in ToolName})

    def test_mcp_tools(self) -> None:
        assert ToolName.LIST_MCP_RESOURCES == "ListMcpResourcesTool"
        assert ToolName.READ_MCP_RESOURCE == "ReadMcpResourceTool"
        assert ToolName.TOOL_SEARCH == "ToolSearch"

    def test_task_tools(self) -> None:
        task_tools = {
            ToolName.TASK_CREATE,
            ToolName.TASK_GET,
            ToolName.TASK_LIST,
            ToolName.TASK_UPDATE,
            ToolName.TASK_STOP,
        }
        assert len(task_tools) == 5

    def test_team_tools(self) -> None:
        assert ToolName.TEAM_CREATE == "TeamCreate"
        assert ToolName.TEAM_DELETE == "TeamDelete"
        assert ToolName.SEND_MESSAGE == "SendMessage"


class TestToolDefinition:
    def test_permission_required(self) -> None:
        bash = ToolDefinition(name=ToolName.BASH, description="Shell commands", permission_required=True)
        assert bash.permission_required is True

    def test_no_permission(self) -> None:
        read = ToolDefinition(name=ToolName.READ, description="Read files", permission_required=False)
        assert read.permission_required is False

    def test_frozen(self) -> None:
        td = ToolDefinition(name=ToolName.EDIT, description="Edit files", permission_required=True)
        with pytest.raises(ValidationError):
            td.name = ToolName.WRITE  # type: ignore[misc]

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        td = ToolDefinition(name=ToolName.WEB_FETCH, description="Fetch URLs", permission_required=True)
        data = td.model_dump(mode="json")
        restored = ToolDefinition.model_validate(data)
        assert restored.name == td.name


class TestPermissionMode:
    def test_all_modes(self) -> None:
        modes = {m.value for m in PermissionMode}
        assert modes == {
            "default",
            "acceptEdits",
            "plan",
            "auto",
            "dontAsk",
            "bypassPermissions",
        }


class TestToolPermissionRule:
    def test_allow_rule(self) -> None:
        rule = ToolPermissionRule(tool_name="Bash", rule_content="git *", behavior="allow")
        assert rule.behavior == "allow"
        assert rule.rule_content == "git *"

    def test_deny_rule(self) -> None:
        rule = ToolPermissionRule(tool_name="Bash", rule_content="rm -rf *", behavior="deny")
        assert rule.behavior == "deny"

    def test_wildcard(self) -> None:
        rule = ToolPermissionRule(tool_name="*", behavior="allow")
        assert rule.tool_name == "*"
        assert rule.rule_content is None

    def test_path_pattern(self) -> None:
        rule = ToolPermissionRule(tool_name="Edit", rule_content="*.ts", behavior="allow")
        assert rule.rule_content == "*.ts"


class TestToolUseResult:
    def test_success(self) -> None:
        r = ToolUseResult(
            tool_name="Bash",
            tool_use_id="tu_123",
            tool_input={"command": "ls"},
            tool_response="file1\nfile2",
        )
        assert r.error is None
        assert r.is_interrupt is False

    def test_error(self) -> None:
        r = ToolUseResult(
            tool_name="Bash",
            tool_use_id="tu_456",
            tool_input={"command": "bad"},
            error="command not found",
        )
        assert r.error == "command not found"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        r = ToolUseResult(
            tool_name="Write",
            tool_use_id="tu_789",
            tool_input={"file_path": "/a.txt", "content": "hi"},
        )
        data = r.model_dump(mode="json")
        restored = ToolUseResult.model_validate(data)
        assert restored.tool_name == "Write"
