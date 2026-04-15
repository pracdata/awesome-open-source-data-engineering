"""Tests for MCP server, tool, and resource models."""

from __future__ import annotations

import pytest

from claude_code_models.models.mcp import (
    MCPConfig,
    MCPResource,
    MCPServerConfig,
    MCPToolAnnotations,
    MCPToolDefinition,
    MCPToolResult,
)


class TestMCPServerConfig:
    def test_stdio(self) -> None:
        cfg = MCPServerConfig(command="node", args=["server.js"])
        assert cfg.command == "node"
        assert cfg.url is None

    def test_http(self) -> None:
        cfg = MCPServerConfig(url="http://localhost:3000/mcp", type="sse")
        assert cfg.url is not None
        assert cfg.command is None

    def test_with_env(self) -> None:
        cfg = MCPServerConfig(command="python", args=["mcp.py"], env={"DB_URL": "postgres://..."})
        assert "DB_URL" in cfg.env

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        cfg = MCPServerConfig(command="npx", args=["@org/server"], cwd="/project")
        data = cfg.model_dump(mode="json")
        restored = MCPServerConfig.model_validate(data)
        assert restored.args == ["@org/server"]


class TestMCPToolAnnotations:
    def test_read_only(self) -> None:
        a = MCPToolAnnotations(readOnlyHint=True)
        assert a.read_only_hint is True

    def test_destructive(self) -> None:
        a = MCPToolAnnotations(destructiveHint=True, idempotentHint=False)
        assert a.destructive_hint is True

    @pytest.mark.serialization
    def test_alias_roundtrip(self) -> None:
        a = MCPToolAnnotations(readOnlyHint=True, openWorldHint=False, title="Test")
        data = a.model_dump(mode="json", by_alias=True)
        assert "readOnlyHint" in data
        restored = MCPToolAnnotations.model_validate(data)
        assert restored.read_only_hint is True


class TestMCPToolDefinition:
    def test_basic(self) -> None:
        td = MCPToolDefinition(
            name="search",
            description="Search docs",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
            },
        )
        assert td.name == "search"

    def test_with_annotations(self) -> None:
        td = MCPToolDefinition(
            name="get_weather",
            description="Get weather",
            annotations=MCPToolAnnotations(readOnlyHint=True),
            server_name="weather",
        )
        assert td.annotations is not None
        assert td.server_name == "weather"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        td = MCPToolDefinition(name="tool1", input_schema={"type": "object"})
        data = td.model_dump(mode="json")
        restored = MCPToolDefinition.model_validate(data)
        assert restored.name == "tool1"


class TestMCPToolResult:
    def test_success(self) -> None:
        r = MCPToolResult(content=[{"type": "text", "text": "result"}])
        assert r.is_error is False

    def test_error(self) -> None:
        r = MCPToolResult(content=[{"type": "text", "text": "failed"}], is_error=True)
        assert r.is_error is True

    def test_multi_content(self) -> None:
        r = MCPToolResult(
            content=[
                {"type": "text", "text": "info"},
                {"type": "image", "data": "base64...", "mimeType": "image/png"},
            ]
        )
        assert len(r.content) == 2


class TestMCPResource:
    def test_basic(self) -> None:
        r = MCPResource(uri="file:///docs/readme.md", name="README", mimeType="text/markdown")
        assert r.mime_type == "text/markdown"

    @pytest.mark.serialization
    def test_alias_roundtrip(self) -> None:
        r = MCPResource(uri="file:///a", name="a", mimeType="text/plain")
        data = r.model_dump(mode="json", by_alias=True)
        assert "mimeType" in data
        restored = MCPResource.model_validate(data)
        assert restored.mime_type == "text/plain"


class TestMCPConfig:
    def test_empty(self) -> None:
        mc = MCPConfig()
        assert mc.mcp_servers == {}

    def test_multi_server(self) -> None:
        mc = MCPConfig(
            mcpServers={
                "github": MCPServerConfig(command="npx", args=["@mcp/github"]),
                "fs": MCPServerConfig(command="npx", args=["@mcp/filesystem", "/home"]),
            }
        )
        assert len(mc.mcp_servers) == 2

    @pytest.mark.serialization
    def test_alias_roundtrip(self) -> None:
        mc = MCPConfig(mcpServers={"s1": MCPServerConfig(command="cmd")})
        data = mc.model_dump(mode="json", by_alias=True)
        assert "mcpServers" in data
        restored = MCPConfig.model_validate(data)
        assert "s1" in restored.mcp_servers
