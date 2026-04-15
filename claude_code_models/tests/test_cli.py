"""Tests for CLI commands, flags, environment variables, and config."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claude_code_models.models.cli import (
    CLICommand,
    CLIConfig,
    CLIFlag,
    EffortLevel,
    EnvironmentVariable,
    OutputFormat,
)


class TestOutputFormat:
    def test_values(self) -> None:
        assert set(OutputFormat) == {
            OutputFormat.TEXT,
            OutputFormat.JSON,
            OutputFormat.STREAM_JSON,
        }

    def test_stream_json(self) -> None:
        assert OutputFormat.STREAM_JSON == "stream-json"


class TestEffortLevel:
    def test_all(self) -> None:
        assert len(EffortLevel) == 5
        assert EffortLevel.AUTO == "auto"
        assert EffortLevel.MAX == "max"


class TestCLICommand:
    def test_basic(self) -> None:
        cmd = CLICommand(name="claude", description="Start interactive session", example="claude")
        assert cmd.name == "claude"

    def test_with_aliases(self) -> None:
        cmd = CLICommand(
            name="claude plugin",
            description="Manage plugins",
            aliases=["claude plugins"],
        )
        assert "claude plugins" in cmd.aliases

    def test_frozen(self) -> None:
        cmd = CLICommand(name="claude", description="Start")
        with pytest.raises(ValidationError):
            cmd.name = "other"  # type: ignore[misc]


class TestCLIFlag:
    def test_with_short(self) -> None:
        flag = CLIFlag(flag="--print", short="-p", description="Print mode")
        assert flag.short == "-p"

    def test_with_dependencies(self) -> None:
        flag = CLIFlag(
            flag="--include-partial-messages",
            description="Include partial events",
            requires=["--print", "--output-format stream-json"],
        )
        assert len(flag.requires) == 2


class TestEnvironmentVariable:
    def test_basic(self) -> None:
        env = EnvironmentVariable(name="ANTHROPIC_API_KEY", description="API key", category="auth")
        assert env.category == "auth"
        assert env.deprecated is False

    def test_deprecated(self) -> None:
        env = EnvironmentVariable(
            name="ANTHROPIC_SMALL_FAST_MODEL",
            description="Haiku model",
            deprecated=True,
            deprecated_by="ANTHROPIC_DEFAULT_HAIKU_MODEL",
        )
        assert env.deprecated is True
        assert env.deprecated_by == "ANTHROPIC_DEFAULT_HAIKU_MODEL"

    def test_with_default(self) -> None:
        env = EnvironmentVariable(
            name="API_TIMEOUT_MS",
            description="Timeout",
            default="600000",
            value_type="int",
        )
        assert env.default == "600000"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        env = EnvironmentVariable(name="CLAUDE_CODE_EFFORT_LEVEL", description="Effort", default="auto")
        data = env.model_dump(mode="json")
        restored = EnvironmentVariable.model_validate(data)
        assert restored.name == env.name


class TestCLIConfig:
    def test_defaults(self) -> None:
        cfg = CLIConfig()
        assert cfg.bare is False
        assert cfg.print_mode is False
        assert cfg.allowed_tools == []

    def test_full_config(self) -> None:
        cfg = CLIConfig(
            model="claude-opus-4-6",
            effort=EffortLevel.HIGH,
            output_format=OutputFormat.JSON,
            max_turns=10,
            max_budget_usd=5.0,
            allowed_tools=["Bash(git *)", "Read"],
            disallowed_tools=["WebSearch"],
            bare=False,
            print_mode=True,
        )
        assert cfg.model == "claude-opus-4-6"
        assert cfg.max_turns == 10
        assert cfg.max_budget_usd == 5.0

    @pytest.mark.validation
    def test_invalid_max_turns(self) -> None:
        with pytest.raises(ValidationError):
            CLIConfig(max_turns=0)

    @pytest.mark.validation
    def test_invalid_budget(self) -> None:
        with pytest.raises(ValidationError):
            CLIConfig(max_budget_usd=-1.0)
