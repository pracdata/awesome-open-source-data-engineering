"""Shared fixtures and configuration for claude-code-models tests.

Optimized for CPU-parallel execution via pytest-xdist.
All tests are pure unit tests — no I/O, no network, no disk.
"""

from __future__ import annotations

import multiprocessing
import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Auto-detect optimal parallelism for available CPUs."""
    # If xdist is available and user didn't set -n, suggest optimal workers
    workers = config.getoption("numprocesses", default=None)
    if workers is None:
        cpu_count = multiprocessing.cpu_count()
        # Use 75% of CPUs for test workers, minimum 1
        optimal = max(1, int(cpu_count * 0.75))
        os.environ.setdefault("PYTEST_XDIST_AUTO_NUM_WORKERS", str(optimal))


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark tests based on module name."""
    marker_map: dict[str, str] = {
        "test_version": "semver",
        "test_tools": "tools",
        "test_cli": "cli",
        "test_hooks": "hooks",
        "test_plugins": "plugins",
        "test_channels": "channels",
        "test_checkpoints": "sessions",
        "test_sessions": "sessions",
        "test_skills": "skills",
        "test_mcp": "mcp",
        "test_agents": "agents",
    }
    for item in items:
        module_name = item.module.__name__.rsplit(".", 1)[-1] if item.module else ""
        if module_name in marker_map:
            item.add_marker(getattr(pytest.mark, marker_map[module_name]))
        # All tests in this suite are unit tests
        item.add_marker(pytest.mark.unit)
