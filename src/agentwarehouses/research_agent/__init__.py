"""Multi-agent research system using Claude Code CLI and Agent SDK.

Refactored from anthropics/claude-agent-sdk-demos/research-agent to use
the Claude Code CLI for authentication instead of ANTHROPIC_API_KEY.
The claude-code-sdk Python package wraps the CLI, so auth is handled by
whatever credentials the user has configured (OAuth, API key, etc.).

Usage:
    python -m agentwarehouses.research_agent
"""

from agentwarehouses.research_agent.agent import chat

__all__ = ["chat"]
