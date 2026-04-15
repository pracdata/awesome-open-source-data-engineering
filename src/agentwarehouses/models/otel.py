"""OpenTelemetry configuration and metric/event types for Claude Code 2.1.109."""

from __future__ import annotations

from enum import Enum

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class OtelExporterType(str, Enum):
    OTLP = "otlp"
    CONSOLE = "console"
    PROMETHEUS = "prometheus"
    NONE = "none"


class OtelProtocol(str, Enum):
    GRPC = "grpc"
    HTTP_JSON = "http/json"
    HTTP_PROTOBUF = "http/protobuf"


class OtelConfig(BaseModel):
    """All OTEL environment variables as typed fields."""

    enable_telemetry: bool = Field(False, description="CLAUDE_CODE_ENABLE_TELEMETRY")
    metrics_exporter: OtelExporterType = OtelExporterType.CONSOLE
    logs_exporter: OtelExporterType = OtelExporterType.CONSOLE
    traces_exporter: OtelExporterType = OtelExporterType.NONE
    protocol: OtelProtocol = OtelProtocol.GRPC
    endpoint: str = "http://localhost:4317"
    metric_export_interval_ms: int = Field(60000, ge=1000)
    logs_export_interval_ms: int = Field(5000, ge=1000)
    traces_export_interval_ms: int = Field(5000, ge=1000)
    log_user_prompts: bool = False
    log_tool_details: bool = False
    log_tool_content: bool = False
    include_session_id: bool = True
    include_version: bool = False
    include_account_uuid: bool = True
    enhanced_telemetry_beta: bool = False
    flush_timeout_ms: int = 5000
    shutdown_timeout_ms: int = 2000


class MetricDefinition(BaseModel):
    name: str
    description: str
    unit: str


class EventDefinition(BaseModel):
    name: str
    description: str
    attributes: list[str] = Field(default_factory=list)


# All 8 Claude Code metrics
METRICS = [
    MetricDefinition(name="claude_code.session.count", description="CLI sessions started", unit="count"),
    MetricDefinition(name="claude_code.lines_of_code.count", description="Lines modified", unit="count"),
    MetricDefinition(name="claude_code.pull_request.count", description="PRs created", unit="count"),
    MetricDefinition(name="claude_code.commit.count", description="Git commits", unit="count"),
    MetricDefinition(name="claude_code.cost.usage", description="Session cost", unit="USD"),
    MetricDefinition(name="claude_code.token.usage", description="Tokens used", unit="tokens"),
    MetricDefinition(name="claude_code.code_edit_tool.decision", description="Edit decisions", unit="count"),
    MetricDefinition(name="claude_code.active_time.total", description="Active time", unit="s"),
]

# All 5 Claude Code events
EVENTS = [
    EventDefinition(
        name="claude_code.user_prompt", description="User submits prompt", attributes=["prompt_length", "prompt"]
    ),
    EventDefinition(
        name="claude_code.tool_result", description="Tool completes", attributes=["tool_name", "success", "duration_ms"]
    ),
    EventDefinition(
        name="claude_code.api_request",
        description="API call to Claude",
        attributes=["model", "cost_usd", "duration_ms", "input_tokens", "output_tokens"],
    ),
    EventDefinition(
        name="claude_code.api_error",
        description="API request fails",
        attributes=["model", "error", "status_code", "attempt"],
    ),
    EventDefinition(
        name="claude_code.tool_decision",
        description="Tool permission decision",
        attributes=["tool_name", "decision", "source"],
    ),
]

RESOURCE_ATTRS = {
    "service.name": "agentwarehouses",
    "service.version": "0.2.0",
    "bot.name": "Claudebot",
    "bot.version": "2.1.109",
}
