"""Agent team coordination types for Claude Code agent teams."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from agentwarehouses.models.base import BaseModel


class TeammateMode(str, Enum):
    AUTO = "auto"
    IN_PROCESS = "in-process"
    TMUX = "tmux"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class TeamTask(BaseModel):
    """A task in an agent team."""

    task_id: str
    subject: str
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    teammate_name: str | None = None
    team_name: str | None = None


class TeamMessage(BaseModel):
    """A message between agent team members."""

    from_agent: str
    to_agent: str
    content: str
    message_id: str | None = None


class AgentTeamConfig(BaseModel):
    """Configuration for an agent team session."""

    enabled: bool = False
    env_var: str = "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"
    teammate_mode: TeammateMode = TeammateMode.AUTO


class TeamMember(BaseModel):
    """A member of an agent team."""

    name: str
    agent_type: str | None = None
    status: Literal["active", "idle", "stopped"] = "idle"
    task_id: str | None = None
