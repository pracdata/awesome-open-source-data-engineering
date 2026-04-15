"""Reusable colored logger for Scrapy spiders and pipelines.

Wraps Python's logging with colorlog for terminal readability and
Scrapy-compatible log format. Mirrors the LOG_LEVEL and LOG_FORMAT
from settings.py so all output is consistent.

Usage:
    from agentwarehouses.log import get_logger
    logger = get_logger(__name__)
    logger.info("Crawling %s", url)
"""

import logging
import os
from typing import Any

import colorlog

# Match Scrapy's LOG_LEVEL from settings.py, overridable via env
_DEFAULT_LEVEL = os.environ.get("SCRAPY_LOG_LEVEL", "INFO").upper()

# OTEL-aware resource attributes (Claude Code 2.1.109 telemetry)
OTEL_RESOURCE_ATTRS = {
    "service.name": "agentwarehouses",
    "service.version": "0.1.0",
    "bot.name": "Claudebot",
    "bot.version": "2.1.109",
}

# Color scheme: severity -> color
_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

_SECONDARY_COLORS = {
    "message": {
        "DEBUG": "white",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
}

_FORMAT = "%(log_color)s%(asctime)s [%(name)s] %(levelname)s:%(reset)s %(message_log_color)s%(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized_loggers: set[str] = set()


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Get a colored logger compatible with Scrapy's logging system.

    Args:
        name: Logger name (typically __name__).
        level: Override log level. Defaults to SCRAPY_LOG_LEVEL env var or INFO.

    Returns:
        A configured logging.Logger with color output.
    """
    logger = logging.getLogger(name)

    if name in _initialized_loggers:
        return logger

    effective_level = getattr(logging, (level or _DEFAULT_LEVEL).upper(), logging.INFO)
    logger.setLevel(effective_level)

    # Only add handler if none exist (avoid duplicates with Scrapy's own handlers)
    if not logger.handlers:
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                _FORMAT,
                datefmt=_DATE_FORMAT,
                log_colors=_COLORS,
                secondary_log_colors=_SECONDARY_COLORS,
            )
        )
        handler.setLevel(effective_level)
        logger.addHandler(handler)

    _initialized_loggers.add(name)
    return logger


def get_otel_config() -> dict[str, Any]:
    """Return OTEL environment configuration for Claude Code 2.1.109 telemetry.

    These settings mirror the Claude Code monitoring docs and can be
    set as environment variables or passed to an OTEL collector config.

    Reference: https://code.claude.com/docs/en/monitoring-usage
    """
    return {
        # Required to enable
        "CLAUDE_CODE_ENABLE_TELEMETRY": os.environ.get("CLAUDE_CODE_ENABLE_TELEMETRY", "0"),
        # Exporter config
        "OTEL_METRICS_EXPORTER": os.environ.get("OTEL_METRICS_EXPORTER", "console"),
        "OTEL_LOGS_EXPORTER": os.environ.get("OTEL_LOGS_EXPORTER", "console"),
        "OTEL_TRACES_EXPORTER": os.environ.get("OTEL_TRACES_EXPORTER", "none"),
        # Protocol and endpoint
        "OTEL_EXPORTER_OTLP_PROTOCOL": os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc"),
        "OTEL_EXPORTER_OTLP_ENDPOINT": os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        # Export intervals (ms)
        "OTEL_METRIC_EXPORT_INTERVAL": os.environ.get("OTEL_METRIC_EXPORT_INTERVAL", "60000"),
        "OTEL_LOGS_EXPORT_INTERVAL": os.environ.get("OTEL_LOGS_EXPORT_INTERVAL", "5000"),
        "OTEL_TRACES_EXPORT_INTERVAL": os.environ.get("OTEL_TRACES_EXPORT_INTERVAL", "5000"),
        # Privacy controls
        "OTEL_LOG_USER_PROMPTS": os.environ.get("OTEL_LOG_USER_PROMPTS", "0"),
        "OTEL_LOG_TOOL_DETAILS": os.environ.get("OTEL_LOG_TOOL_DETAILS", "0"),
        "OTEL_LOG_TOOL_CONTENT": os.environ.get("OTEL_LOG_TOOL_CONTENT", "0"),
        # Cardinality control
        "OTEL_METRICS_INCLUDE_SESSION_ID": os.environ.get("OTEL_METRICS_INCLUDE_SESSION_ID", "true"),
        "OTEL_METRICS_INCLUDE_VERSION": os.environ.get("OTEL_METRICS_INCLUDE_VERSION", "false"),
        "OTEL_METRICS_INCLUDE_ACCOUNT_UUID": os.environ.get("OTEL_METRICS_INCLUDE_ACCOUNT_UUID", "true"),
        # Tracing (beta)
        "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": os.environ.get("CLAUDE_CODE_ENHANCED_TELEMETRY_BETA", "0"),
        # Flush/shutdown timeouts
        "CLAUDE_CODE_OTEL_FLUSH_TIMEOUT_MS": os.environ.get("CLAUDE_CODE_OTEL_FLUSH_TIMEOUT_MS", "5000"),
        "CLAUDE_CODE_OTEL_SHUTDOWN_TIMEOUT_MS": os.environ.get("CLAUDE_CODE_OTEL_SHUTDOWN_TIMEOUT_MS", "2000"),
        # Debug logging
        "CLAUDE_CODE_DEBUG_LOG_LEVEL": os.environ.get("CLAUDE_CODE_DEBUG_LOG_LEVEL", "debug"),
        # Resource attributes
        "OTEL_RESOURCE_ATTRIBUTES": ",".join(f"{k}={v}" for k, v in OTEL_RESOURCE_ATTRS.items()),
    }


# Available Claude Code 2.1.109 OTEL metrics for reference
CLAUDE_CODE_METRICS = {
    "claude_code.session.count": "Count of CLI sessions started",
    "claude_code.lines_of_code.count": "Lines of code modified (type: added|removed)",
    "claude_code.pull_request.count": "Pull requests created",
    "claude_code.commit.count": "Git commits created",
    "claude_code.cost.usage": "Session cost in USD (by model)",
    "claude_code.token.usage": "Tokens used (type: input|output|cacheRead|cacheCreation, by model)",
    "claude_code.code_edit_tool.decision": "Code edit permission decisions (tool_name, decision, source, language)",
    "claude_code.active_time.total": "Active time in seconds (type: user|cli)",
}

# Available Claude Code 2.1.109 OTEL events for reference
CLAUDE_CODE_EVENTS = {
    "claude_code.user_prompt": "User submits a prompt (prompt_length, prompt.id)",
    "claude_code.tool_result": "Tool completes (tool_name, success, duration_ms, tool_result_size_bytes)",
    "claude_code.api_request": "API call to Claude (model, cost_usd, duration_ms, tokens, speed)",
    "claude_code.api_error": "API request fails (model, error, status_code, attempt)",
    "claude_code.tool_decision": "Tool permission decision (tool_name, decision, source)",
}

# Standard OTEL attributes attached to all metrics/events
CLAUDE_CODE_STANDARD_ATTRS = [
    "session.id",
    "app.version",
    "organization.id",
    "user.account_uuid",
    "user.account_id",
    "user.id",
    "user.email",
    "terminal.type",
]
