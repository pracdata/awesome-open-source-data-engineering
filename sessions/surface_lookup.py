"""Deterministic device / surface lookup table.

Maps environment signals to Kimball dimension values for DimDevice and
DimUserSurface. Used by ``SessionTemplate.auto_populate()`` to fill in
the active session's device and surface metadata without manual input.

Usage::

    from sessions.surface_lookup import detect_device, detect_surface
    device  = detect_device()   # -> DeviceInfo(os_name="Linux", ...)
    surface = detect_surface()  # -> SurfaceInfo(surface_type="Web", ...)
"""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Device detection
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DeviceInfo:
    """Mirrors DimDevice from kimball_dimensions.ts."""

    os_name: str  # Linux | macOS | Windows
    os_version: str | None
    arch: str  # x86_64, arm64, aarch64
    shell: str | None
    terminal: str | None
    node_version: str | None
    claude_code_version: str


def detect_device(claude_code_version: str = "2.1.109") -> DeviceInfo:
    """Auto-detect device attributes from the runtime environment."""
    os_name_raw = platform.system()
    os_name_map = {"Linux": "Linux", "Darwin": "macOS", "Windows": "Windows"}

    return DeviceInfo(
        os_name=os_name_map.get(os_name_raw, os_name_raw),
        os_version=platform.release() or None,
        arch=platform.machine(),
        shell=os.environ.get("SHELL") or os.environ.get("COMSPEC"),
        terminal=os.environ.get("TERM_PROGRAM") or os.environ.get("TERM"),
        node_version=os.environ.get("NODE_VERSION"),
        claude_code_version=claude_code_version,
    )


# ---------------------------------------------------------------------------
# Surface detection — deterministic lookup table
# ---------------------------------------------------------------------------

# Priority-ordered rules. First match wins.
# Each rule: (env_var, pattern, surface_type, hints)
_SURFACE_RULES: list[tuple[str, str | None, str, dict[str, str | None]]] = [
    # CI / automation surfaces
    ("GITHUB_ACTIONS", "true", "GitHubAction", {"ide_name": None, "is_remote": True, "is_headless": True}),
    ("GITLAB_CI", "true", "GitLabCI", {"ide_name": None, "is_remote": True, "is_headless": True}),
    # IDE surfaces (checked via env vars set by extensions)
    ("VSCODE_PID", None, "VSCode", {"ide_name": "VSCode", "is_remote": False, "is_headless": False}),
    ("VSCODE_IPC_HOOK_CLI", None, "VSCode", {"ide_name": "VSCode", "is_remote": False, "is_headless": False}),
    ("JETBRAINS_IDE", None, "JetBrains", {"ide_name": "JetBrains", "is_remote": False, "is_headless": False}),
    # Desktop app
    ("CLAUDE_DESKTOP", "true", "Desktop", {"ide_name": None, "is_remote": False, "is_headless": False}),
    # Web / mobile (claude.ai/code)
    ("CLAUDE_CODE_SURFACE", "web", "Web", {"ide_name": None, "is_remote": True, "is_headless": False}),
    ("CLAUDE_CODE_SURFACE", "mobile", "Mobile", {"ide_name": None, "is_remote": True, "is_headless": False}),
    # SDK (programmatic)
    ("CLAUDE_CODE_SURFACE", "sdk", "SDK", {"ide_name": None, "is_remote": False, "is_headless": True}),
    # Slack
    ("CLAUDE_CODE_SURFACE", "slack", "Slack", {"ide_name": None, "is_remote": True, "is_headless": True}),
]


@dataclass(frozen=True)
class SurfaceInfo:
    """Mirrors DimUserSurface from kimball_dimensions.ts."""

    surface_type: str  # CLI | VSCode | JetBrains | Desktop | Web | Mobile | ...
    surface_version: str | None = None
    ide_name: str | None = None
    ide_version: str | None = None
    is_remote: bool = False
    is_headless: bool = False


def detect_surface() -> SurfaceInfo:
    """Walk the lookup table and return the first matching surface."""
    for env_var, expected, surface_type, hints in _SURFACE_RULES:
        val = os.environ.get(env_var)
        if val is None:
            continue
        if expected is None or val.lower() == expected.lower():
            return SurfaceInfo(
                surface_type=surface_type,
                surface_version=os.environ.get("CLAUDE_CODE_VERSION"),
                ide_name=hints.get("ide_name"),
                ide_version=os.environ.get("IDE_VERSION"),
                is_remote=bool(hints.get("is_remote", False)),
                is_headless=bool(hints.get("is_headless", False)),
            )

    # Default: CLI
    return SurfaceInfo(
        surface_type="CLI",
        surface_version=os.environ.get("CLAUDE_CODE_VERSION"),
        is_remote=False,
        is_headless=False,
    )


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    d = detect_device()
    s = detect_surface()
    print(f"Device:  {d}")
    print(f"Surface: {s}")
