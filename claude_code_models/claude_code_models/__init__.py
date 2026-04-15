"""Claude Code data models — Pydantic 2.0, prepared for Pydantic 3.0.

Typed models for Claude Code CLI, Agent SDK, MCP SDK v2, hooks, plugins,
channels, checkpoints, tools, sessions, skills, subagents, and agent teams.

Version is bumped automatically via release-please when upstream dependencies
(anthropic SDK, MCP SDK v2) publish new releases.
"""

__version__ = "0.1.0"

# Upstream dependency versions this model set targets
ANTHROPIC_SDK_MIN = "0.52.0"  # claude-agent-sdk-python
MCP_SDK_MIN = "1.9.0"  # modelcontextprotocol/python-sdk v2

from claude_code_models.models.agents import *  # noqa: F401,F403,E402
from claude_code_models.models.channels import *  # noqa: F401,F403,E402
from claude_code_models.models.checkpoints import *  # noqa: F401,F403,E402
from claude_code_models.models.cli import *  # noqa: F401,F403,E402
from claude_code_models.models.hooks import *  # noqa: F401,F403,E402
from claude_code_models.models.mcp import *  # noqa: F401,F403,E402
from claude_code_models.models.plugins import *  # noqa: F401,F403,E402
from claude_code_models.models.sessions import *  # noqa: F401,F403,E402
from claude_code_models.models.skills import *  # noqa: F401,F403,E402
from claude_code_models.models.tools import *  # noqa: F401,F403,E402
from claude_code_models.models.version import *  # noqa: F401,F403,E402
