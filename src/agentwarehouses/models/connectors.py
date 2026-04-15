"""Connector types for claude.ai platform connectors (Google Drive, Slack, etc.)."""

from __future__ import annotations

from enum import Enum
from typing import Any

from agentwarehouses.models.base import BaseModel


class ConnectorType(str, Enum):
    GOOGLE_DRIVE = "google_drive"
    SLACK = "slack"
    NOTION = "notion"
    GITHUB = "github"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    CUSTOM = "custom"


class ConnectorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"


class ConnectorConfig(BaseModel):
    """Configuration for a platform connector."""

    name: str
    type: ConnectorType
    status: ConnectorStatus = ConnectorStatus.INACTIVE
    auth_method: str | None = None
    scopes: list[str] | None = None
    config: dict[str, Any] | None = None


class ConnectorCRUD(BaseModel):
    """CRUD operations reference for connectors (platform-level)."""

    create_url: str = "https://claude.ai/settings/connectors"
    list_url: str = "https://claude.ai/settings/connectors"
    api_base: str = "https://api.anthropic.com/v1/connectors"
