"""Tests for hook events, handlers, matchers, and configuration."""

from __future__ import annotations

import pytest

from claude_code_models.models.hooks import (
    AgentHook,
    CommandHook,
    HookConfig,
    HookEventName,
    HookInput,
    HookMatcherGroup,
    HookOutput,
    HttpHook,
    PermissionRequestDecision,
    PermissionUpdateEntry,
    PreToolUseDecision,
    PromptHook,
)


class TestHookEventName:
    def test_count(self) -> None:
        assert len(HookEventName) == 26

    def test_session_events(self) -> None:
        assert HookEventName.SESSION_START == "SessionStart"
        assert HookEventName.SESSION_END == "SessionEnd"

    def test_tool_events(self) -> None:
        tool_events = {
            HookEventName.PRE_TOOL_USE,
            HookEventName.POST_TOOL_USE,
            HookEventName.POST_TOOL_USE_FAILURE,
        }
        assert all(e.value.endswith(("Use", "Failure")) for e in tool_events)

    def test_new_events(self) -> None:
        assert HookEventName.PRE_COMPACT == "PreCompact"
        assert HookEventName.POST_COMPACT == "PostCompact"
        assert HookEventName.WORKTREE_CREATE == "WorktreeCreate"
        assert HookEventName.ELICITATION == "Elicitation"
        assert HookEventName.TEAMMATE_IDLE == "TeammateIdle"
        assert HookEventName.INSTRUCTIONS_LOADED == "InstructionsLoaded"


class TestCommandHook:
    def test_basic(self) -> None:
        h = CommandHook(command="echo test")
        assert h.type == "command"
        assert h.timeout == 600
        assert h.shell is None

    def test_with_shell(self) -> None:
        h = CommandHook(command="Get-Process", shell="powershell", timeout=30)
        assert h.shell == "powershell"

    def test_with_if_filter(self) -> None:
        h = CommandHook(command="./check.sh", **{"if": "Bash(rm *)"})  # type: ignore[arg-type]
        assert h.if_ == "Bash(rm *)"

    def test_async(self) -> None:
        h = CommandHook(command="./bg.sh", **{"async": True})  # type: ignore[arg-type]
        assert h.async_ is True

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        h = CommandHook(command="./test.sh", timeout=10)
        data = h.model_dump(mode="json")
        restored = CommandHook.model_validate(data)
        assert restored.command == h.command


class TestHttpHook:
    def test_basic(self) -> None:
        h = HttpHook(url="http://localhost:8080/hook")
        assert h.type == "http"
        assert h.timeout == 30

    def test_with_headers(self) -> None:
        h = HttpHook(
            url="http://localhost:8080/hook",
            headers={"Authorization": "Bearer $TOKEN"},
            allowedEnvVars=["TOKEN"],
        )
        assert "Authorization" in h.headers
        assert "TOKEN" in h.allowed_env_vars


class TestPromptHook:
    def test_basic(self) -> None:
        h = PromptHook(prompt="Should this be allowed?")
        assert h.type == "prompt"
        assert h.model is None

    def test_with_model(self) -> None:
        h = PromptHook(prompt="Check safety", model="fast-model", timeout=15)
        assert h.model == "fast-model"


class TestAgentHook:
    def test_basic(self) -> None:
        h = AgentHook(prompt="Verify this deployment")
        assert h.type == "agent"
        assert h.timeout == 60


class TestHookMatcherGroup:
    def test_wildcard(self) -> None:
        mg = HookMatcherGroup(hooks=[CommandHook(command="echo")])
        assert mg.matcher is None  # matches all

    def test_exact_match(self) -> None:
        mg = HookMatcherGroup(matcher="Bash", hooks=[CommandHook(command="echo")])
        assert mg.matcher == "Bash"

    def test_pipe_separated(self) -> None:
        mg = HookMatcherGroup(matcher="Edit|Write", hooks=[CommandHook(command="lint")])
        assert "|" in (mg.matcher or "")

    def test_regex_pattern(self) -> None:
        mg = HookMatcherGroup(matcher="mcp__memory__.*", hooks=[HttpHook(url="http://localhost/v")])
        assert mg.matcher == "mcp__memory__.*"


class TestHookConfig:
    def test_empty(self) -> None:
        cfg = HookConfig()
        assert cfg.hooks == {}
        assert cfg.disable_all_hooks is False

    def test_multi_event(self) -> None:
        pre = HookMatcherGroup(matcher="Bash", hooks=[CommandHook(command="./pre.sh")])
        post = HookMatcherGroup(matcher="Edit|Write", hooks=[CommandHook(command="./post.sh")])
        cfg = HookConfig(
            hooks={
                HookEventName.PRE_TOOL_USE: [pre],
                HookEventName.POST_TOOL_USE: [post],
            }
        )
        assert len(cfg.hooks) == 2

    def test_disabled(self) -> None:
        cfg = HookConfig(disableAllHooks=True)
        assert cfg.disable_all_hooks is True

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        cfg = HookConfig(
            hooks={
                HookEventName.SESSION_START: [
                    HookMatcherGroup(matcher="startup", hooks=[CommandHook(command="./init.sh")])
                ]
            }
        )
        data = cfg.model_dump(mode="json", by_alias=True)
        restored = HookConfig.model_validate(data)
        assert HookEventName.SESSION_START in restored.hooks


class TestHookInput:
    def test_basic(self) -> None:
        inp = HookInput(
            session_id="abc",
            cwd="/home",
            permission_mode="default",
            hook_event_name="PreToolUse",
        )
        assert inp.session_id == "abc"

    def test_tool_context(self) -> None:
        inp = HookInput(
            session_id="abc",
            cwd="/home",
            permission_mode="default",
            hook_event_name="PreToolUse",
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="tu_1",
        )
        assert inp.tool_name == "Bash"

    def test_extra_fields(self) -> None:
        inp = HookInput(
            session_id="abc",
            cwd="/home",
            permission_mode="default",
            hook_event_name="Stop",
            custom_field="value",
        )
        assert inp.model_extra is not None


class TestPreToolUseDecision:
    def test_allow(self) -> None:
        d = PreToolUseDecision(permissionDecision="allow", permissionDecisionReason="safe command")
        assert d.permission_decision == "allow"

    def test_deny_with_context(self) -> None:
        d = PreToolUseDecision(
            permissionDecision="deny",
            permissionDecisionReason="destructive",
            additionalContext="Blocked rm -rf",
        )
        assert d.additional_context == "Blocked rm -rf"

    def test_updated_input(self) -> None:
        d = PreToolUseDecision(updatedInput={"command": "safe-command"})
        assert d.updated_input == {"command": "safe-command"}


class TestPermissionRequestDecision:
    def test_allow(self) -> None:
        d = PermissionRequestDecision(behavior="allow")
        assert d.behavior == "allow"

    def test_with_updates(self) -> None:
        d = PermissionRequestDecision(
            behavior="allow",
            updatedPermissions=[
                PermissionUpdateEntry(
                    type="addRules",
                    rules=[{"toolName": "Bash", "ruleContent": "git *"}],
                    behavior="allow",
                )
            ],
        )
        assert len(d.updated_permissions) == 1


class TestHookOutput:
    def test_continue(self) -> None:
        out = HookOutput(**{"continue": True})  # type: ignore[arg-type]
        assert out.continue_ is True

    def test_block(self) -> None:
        out = HookOutput(decision="block", reason="Not allowed")
        assert out.decision == "block"

    def test_system_message(self) -> None:
        out = HookOutput(systemMessage="Warning: risky operation")
        assert out.system_message == "Warning: risky operation"
