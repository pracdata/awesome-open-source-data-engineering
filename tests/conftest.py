"""Shared fixtures and marker auto-application for agentwarehouses tests."""

from __future__ import annotations

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Auto-apply markers based on test file location."""
    for item in items:
        path = str(item.fspath)
        if "test_models" in path:
            item.add_marker(pytest.mark.models)
        elif "test_eval_schema" in path:
            item.add_marker(pytest.mark.evals)
        elif "test_spider" in path or "test_pipelines" in path:
            item.add_marker(pytest.mark.integration)
        elif "test_log" in path:
            item.add_marker(pytest.mark.unit)
