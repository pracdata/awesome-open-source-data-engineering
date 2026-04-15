import logging

from agentwarehouses.log import (
    CLAUDE_CODE_EVENTS,
    CLAUDE_CODE_METRICS,
    CLAUDE_CODE_STANDARD_ATTRS,
    OTEL_RESOURCE_ATTRS,
    get_logger,
    get_otel_config,
)


class TestGetLogger:
    def test_returns_logger(self):
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_default_level_is_info(self):
        logger = get_logger("test.level.default")
        assert logger.level == logging.INFO

    def test_custom_level(self):
        logger = get_logger("test.level.debug", level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_has_handler(self):
        logger = get_logger("test.handler")
        assert len(logger.handlers) >= 1

    def test_idempotent(self):
        logger1 = get_logger("test.idempotent")
        handler_count = len(logger1.handlers)
        logger2 = get_logger("test.idempotent")
        assert logger1 is logger2
        assert len(logger2.handlers) == handler_count


class TestOtelConfig:
    def test_returns_dict(self):
        config = get_otel_config()
        assert isinstance(config, dict)

    def test_contains_required_keys(self):
        config = get_otel_config()
        assert "CLAUDE_CODE_ENABLE_TELEMETRY" in config
        assert "OTEL_METRICS_EXPORTER" in config
        assert "OTEL_LOGS_EXPORTER" in config
        assert "OTEL_EXPORTER_OTLP_PROTOCOL" in config
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in config
        assert "OTEL_RESOURCE_ATTRIBUTES" in config

    def test_default_telemetry_disabled(self):
        config = get_otel_config()
        assert config["CLAUDE_CODE_ENABLE_TELEMETRY"] == "0"

    def test_resource_attributes_format(self):
        config = get_otel_config()
        attrs = config["OTEL_RESOURCE_ATTRIBUTES"]
        assert "service.name=agentwarehouses" in attrs
        assert "bot.name=Claudebot" in attrs
        assert "bot.version=2.1.109" in attrs

    def test_privacy_defaults_disabled(self):
        config = get_otel_config()
        assert config["OTEL_LOG_USER_PROMPTS"] == "0"
        assert config["OTEL_LOG_TOOL_DETAILS"] == "0"
        assert config["OTEL_LOG_TOOL_CONTENT"] == "0"


class TestOtelReferences:
    def test_metrics_catalog(self):
        assert "claude_code.session.count" in CLAUDE_CODE_METRICS
        assert "claude_code.token.usage" in CLAUDE_CODE_METRICS
        assert "claude_code.cost.usage" in CLAUDE_CODE_METRICS
        assert len(CLAUDE_CODE_METRICS) == 8

    def test_events_catalog(self):
        assert "claude_code.user_prompt" in CLAUDE_CODE_EVENTS
        assert "claude_code.tool_result" in CLAUDE_CODE_EVENTS
        assert "claude_code.api_request" in CLAUDE_CODE_EVENTS
        assert "claude_code.api_error" in CLAUDE_CODE_EVENTS
        assert len(CLAUDE_CODE_EVENTS) == 5

    def test_standard_attrs(self):
        assert "session.id" in CLAUDE_CODE_STANDARD_ATTRS
        assert "user.id" in CLAUDE_CODE_STANDARD_ATTRS

    def test_resource_attrs(self):
        assert OTEL_RESOURCE_ATTRS["service.name"] == "agentwarehouses"
        assert OTEL_RESOURCE_ATTRS["bot.version"] == "2.1.109"
