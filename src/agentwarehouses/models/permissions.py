"""Permission modes, rules, and access control types for Claude Code."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from agentwarehouses.models.base import BaseModel


class PermissionMode(str, Enum):
    DEFAULT = "default"
    ACCEPT_EDITS = "acceptEdits"
    PLAN = "plan"
    DONT_ASK = "dontAsk"
    AUTO = "auto"
    BYPASS = "bypassPermissions"


class PermissionBehavior(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


class PermissionUpdateType(str, Enum):
    ADD_RULES = "addRules"
    REPLACE_RULES = "replaceRules"
    REMOVE_RULES = "removeRules"
    SET_MODE = "setMode"
    ADD_DIRECTORIES = "addDirectories"
    REMOVE_DIRECTORIES = "removeDirectories"


class SettingsDestination(str, Enum):
    SESSION = "session"
    LOCAL = "localSettings"
    PROJECT = "projectSettings"
    USER = "userSettings"


class PermissionRule(BaseModel):
    tool_name: str
    rule_content: str | None = None


class PermissionUpdate(BaseModel):
    type: PermissionUpdateType
    rules: list[PermissionRule] | None = None
    behavior: PermissionBehavior | None = None
    mode: PermissionMode | None = None
    directories: list[str] | None = None
    destination: SettingsDestination | None = None


class PermissionResultAllow(BaseModel):
    behavior: Literal["allow"] = "allow"
    updated_input: dict[str, Any] | None = None
    updated_permissions: list[PermissionUpdate] | None = None


class PermissionResultDeny(BaseModel):
    behavior: Literal["deny"] = "deny"
    message: str = ""
    interrupt: bool = False


PermissionResult = PermissionResultAllow | PermissionResultDeny


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"
    DEFER = "defer"
