"""Tests for Pydantic data models — instantiation, validation, serialization."""

import pytest
from pydantic import ValidationError

from agentwarehouses.models import (
    UPSTREAM_DEPS,
    AgentDefinitionSDK,
    AgentFrontmatter,
    BashInput,
    CheckpointAction,
    CheckpointActionType,
    ClaudeAgentOptions,
    CommandDefinition,
    CommandHookHandler,
    ConnectorConfig,
    ConnectorType,
    EditInput,
    EnvVarCategory,
    EnvVarDefinition,
    EnvVarType,
    HookConfig,
    HookEvent,
    HookMatcher,
    McpStdioConfig,
    MemoryScope,
    ModelTier,
    OtelConfig,
    PermissionMode,
    PluginManifest,
    PreCompactInput,
    ResultMessage,
    SemVer,
    SessionCLIFlags,
    SessionInfo,
    SettingSource,
    SkillEvalCase,
    SkillEvalSuite,
    SkillFrontmatter,
    TeamTask,
    TextBlock,
    ThinkingBlock,
    ToolCategory,
    ToolDefinition,
    ToolName,
    ToolParameter,
    __version__,
)


class TestSemVer:
    def test_create(self):
        sv = SemVer(major=0, minor=2, patch=0)
        assert str(sv) == "0.2.0"

    def test_prerelease(self):
        sv = SemVer(major=1, minor=0, patch=0, prerelease="beta.1")
        assert str(sv) == "1.0.0-beta.1"

    def test_bump_patch(self):
        sv = SemVer(major=0, minor=2, patch=0)
        bumped = sv.bump_patch()
        assert str(bumped) == "0.2.1"

    def test_bump_minor(self):
        sv = SemVer(major=0, minor=2, patch=3)
        bumped = sv.bump_minor()
        assert str(bumped) == "0.3.0"

    def test_bump_major(self):
        sv = SemVer(major=0, minor=2, patch=3)
        bumped = sv.bump_major()
        assert str(bumped) == "1.0.0"

    def test_rejects_negative(self):
        with pytest.raises(ValidationError):
            SemVer(major=-1, minor=0, patch=0)


class TestVersion:
    def test_version_is_string(self):
        assert isinstance(__version__, str)
        parts = __version__.split(".")
        assert len(parts) == 3

    def test_upstream_deps(self):
        assert "claude-agent-sdk" in UPSTREAM_DEPS
        assert "mcp" in UPSTREAM_DEPS


class TestToolModels:
    def test_tool_definition(self):
        td = ToolDefinition(
            name="Bash",
            description="Execute commands",
            permission_required=True,
            category=ToolCategory.CODE_EXECUTION,
        )
        assert td.name == "Bash"
        assert td.permission_required is True

    def test_tool_parameter(self):
        tp = ToolParameter(name="command", type="string", required=True, description="The command to run")
        assert tp.required is True

    def test_bash_input(self):
        bi = BashInput(command="ls -la")
        assert bi.command == "ls -la"
        assert bi.timeout is None

    def test_edit_input(self):
        ei = EditInput(file_path="/tmp/test.py", old_string="foo", new_string="bar")
        assert ei.replace_all is False

    def test_tool_name_enum(self):
        assert ToolName.BASH.value == "Bash"
        assert ToolName.AGENT.value == "Agent"
        assert len(ToolName) >= 35


class TestHookModels:
    def test_hook_event_enum(self):
        assert HookEvent.SESSION_START.value == "SessionStart"
        assert HookEvent.PRE_TOOL_USE.value == "PreToolUse"
        assert len(HookEvent) >= 25

    def test_command_hook_handler(self):
        h = CommandHookHandler(type="command", command="ruff check --fix $FILE_PATH")
        assert h.type == "command"

    def test_hook_matcher(self):
        hm = HookMatcher(
            matcher="Edit|Write",
            hooks=[CommandHookHandler(type="command", command="echo test")],
        )
        assert hm.matcher == "Edit|Write"
        assert len(hm.hooks) == 1

    def test_hook_config(self):
        hc = HookConfig(
            hooks={
                "PostToolUse": [
                    HookMatcher(
                        matcher="Edit",
                        hooks=[
                            CommandHookHandler(type="command", command="ruff check"),
                        ],
                    )
                ]
            }
        )
        assert "PostToolUse" in hc.hooks

    def test_pre_compact_input(self):
        pci = PreCompactInput(
            session_id="s1",
            transcript_path="/tmp/t.json",
            cwd="/home/user",
            hook_event_name="PreCompact",
        )
        assert pci.hook_event_name == "PreCompact"
        assert pci.summary is None

    def test_pre_compact_input_with_summary(self):
        pci = PreCompactInput(
            session_id="s1",
            transcript_path="/tmp/t.json",
            cwd="/home/user",
            summary="Context about to be compacted",
        )
        assert pci.summary == "Context about to be compacted"


class TestSubagentModels:
    def test_agent_frontmatter(self):
        af = AgentFrontmatter(
            name="test-agent",
            description="A test agent",
            tools=["Read", "Grep"],
            model=ModelTier.OPUS,
        )
        assert af.name == "test-agent"
        assert af.model == ModelTier.OPUS

    def test_agent_definition_sdk(self):
        ad = AgentDefinitionSDK(
            description="Reviewer",
            prompt="You are a code reviewer.",
            tools=["Read", "Grep", "Glob"],
            model=ModelTier.SONNET,
        )
        assert ad.description == "Reviewer"
        assert ad.model == ModelTier.SONNET


class TestMcpModels:
    def test_stdio_config(self):
        mc = McpStdioConfig(command="npx", args=["-y", "@modelcontextprotocol/server-github"])
        assert mc.command == "npx"
        assert len(mc.args) == 2


class TestSkillModels:
    def test_skill_frontmatter(self):
        sf = SkillFrontmatter(name="my-skill", description="Does something useful")
        assert sf.name == "my-skill"

    def test_skill_description_max_length_1536(self):
        long_desc = "a" * 1536
        sf = SkillFrontmatter(name="long-desc", description=long_desc)
        assert len(sf.description) == 1536

    def test_skill_description_exceeds_1536(self):
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="too-long", description="a" * 1537)

    def test_skill_name_validation(self):
        with pytest.raises(ValidationError):
            SkillFrontmatter(name="Invalid Name", description="bad")

    def test_eval_case(self):
        ec = SkillEvalCase(
            id=1,
            prompt="Create a test agent",
            expected_output="Agent file created",
            assertions=["File exists", "Frontmatter valid"],
        )
        assert len(ec.assertions) == 2

    def test_eval_suite_unique_ids(self):
        with pytest.raises(ValidationError):
            SkillEvalSuite(
                skill_name="test",
                evals=[
                    SkillEvalCase(id=1, prompt="test prompt one", expected_output="out", assertions=["a"]),
                    SkillEvalCase(id=1, prompt="test prompt two", expected_output="out", assertions=["b"]),
                ],
            )

    def test_eval_suite_valid(self):
        es = SkillEvalSuite(
            skill_name="crud-cli-subagents",
            evals=[
                SkillEvalCase(id=1, prompt="Create an agent", expected_output="Agent file", assertions=["File exists"]),
                SkillEvalCase(id=2, prompt="List agents", expected_output="Agent list", assertions=["Output shown"]),
            ],
        )
        assert es.skill_name == "crud-cli-subagents"
        assert len(es.evals) == 2


class TestPluginModels:
    def test_plugin_manifest(self):
        pm = PluginManifest(name="my-plugin", version="1.0.0", description="A test plugin")
        assert pm.name == "my-plugin"

    def test_plugin_manifest_with_monitors(self):
        pm = PluginManifest(name="my-plugin", version="1.0.0", monitors=["health-check"])
        assert pm.monitors == ["health-check"]

    def test_plugin_manifest_monitors_dict(self):
        pm = PluginManifest(name="my-plugin", monitors={"check": {"interval": 60}})
        assert isinstance(pm.monitors, dict)

    def test_plugin_manifest_serialization(self):
        pm = PluginManifest(name="test", version="1.0.0")
        data = pm.model_dump(exclude_none=True)
        assert data["name"] == "test"
        assert "description" not in data
        assert "monitors" not in data


class TestSessionModels:
    def test_session_info(self):
        si = SessionInfo(session_id="abc123", summary="Test session", last_modified=1234567890)
        assert si.session_id == "abc123"

    def test_session_cli_flags_recap(self):
        flags = SessionCLIFlags(recap=True)
        assert flags.recap is True

    def test_session_cli_flags_recap_default(self):
        flags = SessionCLIFlags()
        assert flags.recap is None


class TestOtelModels:
    def test_otel_config_defaults(self):
        oc = OtelConfig()
        assert oc.enable_telemetry is False
        assert oc.metric_export_interval_ms == 60000

    def test_otel_config_custom(self):
        oc = OtelConfig(enable_telemetry=True, endpoint="http://collector:4317")
        assert oc.enable_telemetry is True


class TestSdkModels:
    def test_claude_agent_options(self):
        opts = ClaudeAgentOptions(
            model="opus",
            permission_mode=PermissionMode.PLAN,
            max_turns=10,
        )
        assert opts.model == "opus"
        assert opts.max_turns == 10

    def test_text_block(self):
        tb = TextBlock(text="Hello world")
        assert tb.text == "Hello world"

    def test_result_message(self):
        rm = ResultMessage(
            subtype="success",
            duration_ms=1000,
            duration_api_ms=800,
            is_error=False,
            num_turns=3,
            session_id="test-session",
            total_cost_usd=0.05,
        )
        assert rm.total_cost_usd == 0.05

    def test_thinking_block_progress_hint(self):
        tb = ThinkingBlock(thinking="reasoning...", signature="sig123", progress_hint="Analyzing code")
        assert tb.progress_hint == "Analyzing code"

    def test_thinking_block_no_hint(self):
        tb = ThinkingBlock(thinking="reasoning...", signature="sig123")
        assert tb.progress_hint is None


class TestPermissionModels:
    def test_permission_mode_enum(self):
        assert PermissionMode.DEFAULT.value == "default"
        assert PermissionMode.BYPASS.value == "bypassPermissions"


class TestConnectorModels:
    def test_connector_config(self):
        cc = ConnectorConfig(name="Google Drive", type=ConnectorType.GOOGLE_DRIVE)
        assert cc.name == "Google Drive"


class TestCheckpointModels:
    def test_checkpoint_action(self):
        ca = CheckpointAction(action_type=CheckpointActionType.RESTORE_CODE_AND_CONVERSATION)
        assert ca.action_type == CheckpointActionType.RESTORE_CODE_AND_CONVERSATION


class TestMemoryModels:
    def test_memory_scope(self):
        assert MemoryScope.USER.value == "user"
        assert MemoryScope.PROJECT.value == "project"


class TestAgentTeamModels:
    def test_team_task(self):
        tt = TeamTask(task_id="t1", subject="Fix bug")
        assert tt.subject == "Fix bug"


class TestCommandModels:
    def test_command_definition(self):
        cd = CommandDefinition(name="/clear", description="Clear conversation", command_type="built_in")
        assert cd.name == "/clear"

    def test_recap_command(self):
        from agentwarehouses.models.commands import CMD_RECAP

        assert CMD_RECAP.name == "/recap"
        assert CMD_RECAP.command_type == "built_in"

    def test_undo_command(self):
        from agentwarehouses.models.commands import CMD_UNDO

        assert CMD_UNDO.name == "/undo"
        assert "/rewind" in CMD_UNDO.aliases


class TestSettingSource:
    def test_managed_source(self):
        assert SettingSource.MANAGED.value == "managed"

    def test_all_sources(self):
        assert len(SettingSource) == 4
        sources = {s.value for s in SettingSource}
        assert sources == {"user", "project", "local", "managed"}


class TestEnvVarModels:
    def test_env_var_definition(self):
        ev = EnvVarDefinition(
            name="ANTHROPIC_API_KEY",
            type=EnvVarType.STRING,
            description="API key",
            category=EnvVarCategory.AUTHENTICATION,
        )
        assert ev.name == "ANTHROPIC_API_KEY"

    def test_cloud_env_vars_exist(self):
        from agentwarehouses.models.env_vars import (
            API_TIMEOUT_MS,
            CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC,
            CLAUDE_CODE_EXIT_AFTER_STOP_DELAY,
            CLAUDE_CODE_OAUTH_TOKEN,
            CLAUDE_CODE_SYNC_PLUGIN_INSTALL,
            DISABLE_AUTOUPDATER,
        )

        assert CLAUDE_CODE_OAUTH_TOKEN.category == EnvVarCategory.AUTHENTICATION
        assert CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC.category == EnvVarCategory.TELEMETRY
        assert DISABLE_AUTOUPDATER.category == EnvVarCategory.FEATURES
        assert CLAUDE_CODE_EXIT_AFTER_STOP_DELAY.category == EnvVarCategory.FEATURES
        assert CLAUDE_CODE_SYNC_PLUGIN_INSTALL.category == EnvVarCategory.PLUGINS
        assert API_TIMEOUT_MS.category == EnvVarCategory.NETWORK
        assert API_TIMEOUT_MS.default == "600000"

    def test_prompt_caching_env_vars_exist(self):
        from agentwarehouses.models.env_vars import (
            CLAUDE_CODE_ENABLE_AWAY_SUMMARY,
            CLAUDE_ENV_FILE,
            DISABLE_PROMPT_CACHING,
            ENABLE_PROMPT_CACHING_1H,
            ENABLE_PROMPT_CACHING_1H_BEDROCK,
            FORCE_PROMPT_CACHING_5M,
        )

        assert ENABLE_PROMPT_CACHING_1H.category == EnvVarCategory.FEATURES
        assert ENABLE_PROMPT_CACHING_1H_BEDROCK.category == EnvVarCategory.FEATURES
        assert "Deprecated" in ENABLE_PROMPT_CACHING_1H_BEDROCK.description
        assert FORCE_PROMPT_CACHING_5M.category == EnvVarCategory.FEATURES
        assert DISABLE_PROMPT_CACHING.category == EnvVarCategory.FEATURES
        assert CLAUDE_CODE_ENABLE_AWAY_SUMMARY.category == EnvVarCategory.FEATURES
        assert CLAUDE_ENV_FILE.category == EnvVarCategory.BASH
