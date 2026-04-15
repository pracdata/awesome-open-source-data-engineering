"""Tests for plugin manifest, marketplace, LSP server config."""

from __future__ import annotations

import pytest

from claude_code_models.models.plugins import (
    LSPServerConfig,
    MarketplaceConfig,
    MarketplaceEntry,
    PluginAuthor,
    PluginChannelDeclaration,
    PluginInstallation,
    PluginManifest,
    PluginScope,
    PluginUserConfigEntry,
)


class TestPluginScope:
    def test_all_scopes(self) -> None:
        assert set(PluginScope) == {
            PluginScope.USER,
            PluginScope.PROJECT,
            PluginScope.LOCAL,
            PluginScope.MANAGED,
        }


class TestPluginManifest:
    def test_minimal(self) -> None:
        pm = PluginManifest(name="my-plugin")
        assert pm.name == "my-plugin"
        assert pm.version is None

    def test_full(self) -> None:
        pm = PluginManifest(
            name="enterprise-tools",
            version="2.1.0",
            description="Enterprise deployment tools",
            author=PluginAuthor(name="Dev Team", email="dev@co.com"),
            homepage="https://docs.example.com",
            repository="https://github.com/org/plugin",
            license="MIT",
            keywords=["deploy", "ci-cd"],
            skills="./custom/skills/",
            agents="./agents/",
            hooks="./hooks/hooks.json",
            mcpServers={"db": {"command": "node", "args": ["server.js"]}},
            lspServers="./.lsp.json",
            userConfig={
                "api_token": PluginUserConfigEntry(description="API token", sensitive=True),
                "endpoint": PluginUserConfigEntry(description="API endpoint"),
            },
        )
        assert pm.version == "2.1.0"
        assert pm.user_config is not None
        assert pm.user_config["api_token"].sensitive is True
        assert pm.mcp_servers is not None

    def test_with_channels(self) -> None:
        pm = PluginManifest(
            name="chat-bridge",
            channels=[PluginChannelDeclaration(server="telegram")],
        )
        assert pm.channels is not None
        assert len(pm.channels) == 1

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        pm = PluginManifest(name="test", version="1.0.0", keywords=["test"])
        data = pm.model_dump(mode="json", by_alias=True)
        restored = PluginManifest.model_validate(data)
        assert restored.name == pm.name

    def test_extra_fields_allowed(self) -> None:
        pm = PluginManifest(name="ext", custom_field="value")  # type: ignore[call-arg]
        assert pm.model_extra is not None


class TestLSPServerConfig:
    def test_basic(self) -> None:
        lsp = LSPServerConfig(command="gopls", args=["serve"], extensionToLanguage={".go": "go"})
        assert lsp.command == "gopls"
        assert lsp.extension_to_language[".go"] == "go"

    def test_with_options(self) -> None:
        lsp = LSPServerConfig(
            command="pyright-langserver",
            args=["--stdio"],
            extensionToLanguage={".py": "python"},
            transport="stdio",
            restartOnCrash=True,
            maxRestarts=5,
            startupTimeout=10000,
        )
        assert lsp.restart_on_crash is True
        assert lsp.max_restarts == 5

    @pytest.mark.serialization
    def test_alias_roundtrip(self) -> None:
        lsp = LSPServerConfig(command="tsserver", extensionToLanguage={".ts": "typescript"})
        data = lsp.model_dump(mode="json", by_alias=True)
        assert "extensionToLanguage" in data
        restored = LSPServerConfig.model_validate(data)
        assert restored.extension_to_language == lsp.extension_to_language


class TestPluginInstallation:
    def test_basic(self) -> None:
        pi = PluginInstallation(name="formatter", marketplace="official", scope=PluginScope.USER)
        assert pi.enabled is True

    def test_disabled(self) -> None:
        pi = PluginInstallation(name="old-plugin", enabled=False)
        assert pi.enabled is False


class TestMarketplace:
    def test_entry(self) -> None:
        entry = MarketplaceEntry(name="formatter", source="./plugins/formatter", version="1.0.0")
        assert entry.source.startswith("./")

    def test_config(self) -> None:
        mc = MarketplaceConfig(
            name="my-marketplace",
            plugins=[
                MarketplaceEntry(name="tool-a", source="./a"),
                MarketplaceEntry(name="tool-b", source="./b"),
            ],
        )
        assert len(mc.plugins) == 2
