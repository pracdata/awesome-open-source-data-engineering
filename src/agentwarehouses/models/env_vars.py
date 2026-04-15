"""Environment variable definitions for Claude Code (120+ variables)."""

from __future__ import annotations

from enum import Enum

from agentwarehouses.models.base import BaseModel


class EnvVarType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    JSON = "json"
    ENUM = "enum"


class EnvVarCategory(str, Enum):
    AUTHENTICATION = "authentication"
    API_ENDPOINTS = "api_endpoints"
    MODEL = "model"
    THINKING = "thinking"
    CONTEXT = "context"
    TOOLS = "tools"
    BASH = "bash"
    MEMORY = "memory"
    TASKS = "tasks"
    SECURITY = "security"
    NETWORK = "network"
    UI = "ui"
    FILES = "files"
    PLUGINS = "plugins"
    IDE = "ide"
    LOGGING = "logging"
    TELEMETRY = "telemetry"
    CLOUD_PROVIDERS = "cloud_providers"
    MTLS = "mtls"
    FEATURES = "features"
    OTEL = "otel"


class EnvVarDefinition(BaseModel):
    """A single Claude Code environment variable."""

    name: str
    type: EnvVarType
    default: str | None = None
    valid_values: list[str] | None = None
    min_value: int | None = None
    max_value: int | None = None
    description: str
    category: EnvVarCategory


# Key environment variable constants

ANTHROPIC_API_KEY = EnvVarDefinition(
    name="ANTHROPIC_API_KEY",
    type=EnvVarType.STRING,
    description="API key for Anthropic API",
    category=EnvVarCategory.AUTHENTICATION,
)

CLAUDE_CODE_ENABLE_TELEMETRY = EnvVarDefinition(
    name="CLAUDE_CODE_ENABLE_TELEMETRY",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Enable OpenTelemetry data collection",
    category=EnvVarCategory.OTEL,
)

CLAUDE_CODE_EFFORT_LEVEL = EnvVarDefinition(
    name="CLAUDE_CODE_EFFORT_LEVEL",
    type=EnvVarType.ENUM,
    default="auto",
    valid_values=["low", "medium", "high", "max", "auto"],
    description="Effort level for model responses",
    category=EnvVarCategory.MODEL,
)

CLAUDE_AUTOCOMPACT_PCT_OVERRIDE = EnvVarDefinition(
    name="CLAUDE_AUTOCOMPACT_PCT_OVERRIDE",
    type=EnvVarType.INTEGER,
    default="95",
    min_value=1,
    max_value=100,
    description="Compaction threshold percentage",
    category=EnvVarCategory.CONTEXT,
)

BASH_DEFAULT_TIMEOUT_MS = EnvVarDefinition(
    name="BASH_DEFAULT_TIMEOUT_MS",
    type=EnvVarType.INTEGER,
    default="120000",
    description="Default timeout for Bash commands in milliseconds",
    category=EnvVarCategory.BASH,
)

CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = EnvVarDefinition(
    name="CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Enable experimental agent teams feature",
    category=EnvVarCategory.FEATURES,
)

# Cloud / headless environment variables (2.1.105+)

CLAUDE_CODE_OAUTH_TOKEN = EnvVarDefinition(
    name="CLAUDE_CODE_OAUTH_TOKEN",
    type=EnvVarType.STRING,
    description="OAuth access token for Claude.ai (preferred over API key in cloud/CI)",
    category=EnvVarCategory.AUTHENTICATION,
)

CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = EnvVarDefinition(
    name="CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Disable telemetry, surveys, auto-updates, and error reporting (scoping fixed in 2.1.105)",
    category=EnvVarCategory.TELEMETRY,
)

DISABLE_AUTOUPDATER = EnvVarDefinition(
    name="DISABLE_AUTOUPDATER",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Disable automatic updates (set to 1 in containerized environments)",
    category=EnvVarCategory.FEATURES,
)

CLAUDE_CODE_EXIT_AFTER_STOP_DELAY = EnvVarDefinition(
    name="CLAUDE_CODE_EXIT_AFTER_STOP_DELAY",
    type=EnvVarType.INTEGER,
    description="Time in ms after idle before auto-exit (for serverless/container cleanup)",
    category=EnvVarCategory.FEATURES,
)

CLAUDE_CODE_SYNC_PLUGIN_INSTALL = EnvVarDefinition(
    name="CLAUDE_CODE_SYNC_PLUGIN_INSTALL",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Wait for plugin installation in headless (-p) mode instead of async",
    category=EnvVarCategory.PLUGINS,
)

CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS = EnvVarDefinition(
    name="CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS",
    type=EnvVarType.INTEGER,
    default="60000",
    description="Timeout in ms for synchronous plugin installation in headless mode",
    category=EnvVarCategory.PLUGINS,
)

API_TIMEOUT_MS = EnvVarDefinition(
    name="API_TIMEOUT_MS",
    type=EnvVarType.INTEGER,
    default="600000",
    description="API request timeout in milliseconds (default 10 min)",
    category=EnvVarCategory.NETWORK,
)

# Prompt caching env vars (2.1.108+)

ENABLE_PROMPT_CACHING_1H = EnvVarDefinition(
    name="ENABLE_PROMPT_CACHING_1H",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Opt into 1-hour prompt cache TTL on API key, Bedrock, Vertex, and Foundry",
    category=EnvVarCategory.FEATURES,
)

ENABLE_PROMPT_CACHING_1H_BEDROCK = EnvVarDefinition(
    name="ENABLE_PROMPT_CACHING_1H_BEDROCK",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Deprecated: use ENABLE_PROMPT_CACHING_1H instead. Still honored for Bedrock.",
    category=EnvVarCategory.FEATURES,
)

FORCE_PROMPT_CACHING_5M = EnvVarDefinition(
    name="FORCE_PROMPT_CACHING_5M",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Force 5-minute prompt cache TTL",
    category=EnvVarCategory.FEATURES,
)

DISABLE_PROMPT_CACHING = EnvVarDefinition(
    name="DISABLE_PROMPT_CACHING",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Disable prompt caching entirely (shows warning at startup when set)",
    category=EnvVarCategory.FEATURES,
)

# Recap / away summary (2.1.108+)

CLAUDE_CODE_ENABLE_AWAY_SUMMARY = EnvVarDefinition(
    name="CLAUDE_CODE_ENABLE_AWAY_SUMMARY",
    type=EnvVarType.BOOLEAN,
    default="0",
    description="Force recap/away-summary on session resume even when telemetry is disabled",
    category=EnvVarCategory.FEATURES,
)

# Bash env file (2.1.108 fix)

CLAUDE_ENV_FILE = EnvVarDefinition(
    name="CLAUDE_ENV_FILE",
    type=EnvVarType.STRING,
    description="Path to env file loaded by Bash tool (e.g. ~/.zprofile)",
    category=EnvVarCategory.BASH,
)
