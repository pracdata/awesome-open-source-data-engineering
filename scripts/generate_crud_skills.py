#!/usr/bin/env python3
"""Generate 36 CRUD skills + 4 routers + 36 eval files from resource profiles.

Usage:
    python scripts/generate_crud_skills.py

Produces:
    .claude/skills/crud-{cli,sdk,api,graphql}/SKILL.md         (4 routers)
    .claude/skills/crud-{iface}-{resource}/SKILL.md             (36 skills)
    .claude/skills/crud-{iface}-{resource}/evals/evals.json     (36 evals)
"""

import json
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"

INTERFACES = ["cli", "sdk", "api", "graphql"]

RESOURCES = {
    "skills": {
        "display": "Skills",
        "cli": {
            "create": "Create `.claude/skills/{name}/SKILL.md` with YAML frontmatter (name, description)",
            "read": "List skills with `/help` or inspect `.claude/skills/*/SKILL.md` files",
            "update": "Edit the SKILL.md file directly — update frontmatter or instructions",
            "delete": "Remove the skill directory: `rm -r .claude/skills/{name}/`",
        },
        "sdk": {
            "create": "Add skill files to project, load via `setting_sources=['project']` in ClaudeAgentOptions",
            "read": "Skills are auto-discovered from `.claude/skills/` when settingSources includes 'project'",
            "update": "Modify SKILL.md files, call `/reload-plugins` to refresh",
            "delete": "Remove skill directory, restart session to unload",
        },
        "api": {
            "create": "Write SKILL.md to filesystem via `claude -p 'create skill named X'`",
            "read": "`claude -p --disable-slash-commands 'list skills'` or `ls .claude/skills/`",
            "update": "`claude -p 'update the skill named X to include Y'`",
            "delete": "`rm -r .claude/skills/{name}/`",
        },
        "graphql": {
            "create": "mutation createSkill(input: SkillInput!) { createSkill(input: $input) { name } }",
            "read": "query { skills { name description disableModelInvocation } }",
            "update": "mutation updateSkill(name: String!, input: SkillInput!) { updateSkill(...) { name } }",
            "delete": "mutation deleteSkill(name: String!) { deleteSkill(name: $name) }",
        },
    },
    "plugins": {
        "display": "Plugins",
        "cli": {
            "create": "Create plugin directory with `.claude-plugin/plugin.json` manifest",
            "read": "`claude plugin list` or `/plugin` to view installed plugins",
            "update": "Edit `plugin.json`, run `/reload-plugins` to refresh",
            "delete": "`claude plugin uninstall {name}`",
        },
        "sdk": {
            "create": "Use `SdkPluginConfig(type='local', path='./plugin-dir')` in ClaudeAgentOptions.plugins",
            "read": "Plugins listed in session init data via SystemMessage",
            "update": "Modify plugin files, restart session",
            "delete": "Remove from plugins list in ClaudeAgentOptions",
        },
        "api": {
            "create": "`claude --plugin-dir ./my-plugin -p 'test plugin'`",
            "read": "`claude -p 'list plugins'`",
            "update": "Modify plugin files, re-run with `--plugin-dir`",
            "delete": "Remove `--plugin-dir` flag from invocation",
        },
        "graphql": {
            "create": "mutation createPlugin(input: PluginInput!) { createPlugin(input: $input) { name version } }",
            "read": "query { plugins { name version description author { name } skills { name } } }",
            "update": "mutation updatePlugin(name: String!, input: PluginInput!) { ... }",
            "delete": "mutation deletePlugin(name: String!) { deletePlugin(name: $name) }",
        },
    },
    "connectors": {
        "display": "Connectors",
        "cli": {
            "create": "Configure via claude.ai Settings > Connectors (platform-level feature)",
            "read": "View connected services at claude.ai/settings/connectors",
            "update": "Modify connector permissions or scopes via platform UI",
            "delete": "Disconnect via claude.ai Settings > Connectors",
        },
        "sdk": {
            "create": "Connectors are platform-level, not directly available in Agent SDK",
            "read": "Connector data accessible through connected tools when session is authenticated",
            "update": "Manage via platform API or UI",
            "delete": "Manage via platform API or UI",
        },
        "api": {
            "create": "REST API: POST to platform connector endpoints",
            "read": "REST API: GET connector status and configuration",
            "update": "REST API: PATCH connector configuration",
            "delete": "REST API: DELETE connector",
        },
        "graphql": {
            "create": "mutation createConnector(input: ConnectorInput!) { ... }",
            "read": "query { connectors { name type status scopes } }",
            "update": "mutation updateConnector(name: String!, input: ConnectorInput!) { ... }",
            "delete": "mutation deleteConnector(name: String!) { ... }",
        },
    },
    "mcps": {
        "display": "MCP Servers",
        "cli": {
            "create": "`claude mcp add {name} -s {scope} -- {command} {args}`\nOr create `.mcp.json`",
            "read": "`claude mcp list` or `/mcp` to view server status and tools",
            "update": "Edit `.mcp.json` or re-run `claude mcp add` with updated config",
            "delete": "`claude mcp remove {name} -s {scope}`",
        },
        "sdk": {
            "create": "Pass `mcp_servers={'name': McpStdioConfig(command='cmd', args=[...])}` to ClaudeAgentOptions",
            "read": "Call `client.get_mcp_status()` to get McpStatusResponse",
            "update": "Modify mcp_servers dict and create new query session",
            "delete": "Remove server from mcp_servers dict",
        },
        "api": {
            "create": "`claude --mcp-config ./mcp.json -p 'task'` or `claude mcp add`",
            "read": "`claude mcp list`",
            "update": "Edit mcp.json, re-invoke with `--mcp-config`",
            "delete": "`claude mcp remove {name}`",
        },
        "graphql": {
            "create": "mutation createMcpServer(input: McpServerInput!) { ... }",
            "read": "query { mcpServers { name status scope tools { name description } } }",
            "update": "mutation updateMcpServer(name: String!, input: McpServerInput!) { ... }",
            "delete": "mutation deleteMcpServer(name: String!) { ... }",
        },
    },
    "subagents": {
        "display": "Subagents",
        "cli": {
            "create": "Create `.claude/agents/{name}.md` with YAML frontmatter (name, description, tools, model)",
            "read": "`claude agents` to list all, or read `.claude/agents/*.md` files",
            "update": "Edit the agent .md file — modify frontmatter fields or system prompt",
            "delete": "Remove the agent file: `rm .claude/agents/{name}.md`",
        },
        "sdk": {
            "create": "Use `AgentDefinition(description=..., prompt=..., tools=[...], model=...)` in agents dict",
            "read": "Agents listed when Claude calls Agent tool; check via session transcript",
            "update": "Modify AgentDefinition fields and create new query session",
            "delete": "Remove agent from agents dict in ClaudeAgentOptions",
        },
        "api": {
            "create": '`claude -p --agents \'{"name":{"description":"...","prompt":"..."}}\'`',
            "read": "`claude agents` to list configured agents",
            "update": "Re-invoke with updated `--agents` JSON",
            "delete": "Remove from `--agents` JSON or delete `.claude/agents/{name}.md`",
        },
        "graphql": {
            "create": "mutation createAgent(input: AgentInput!) { createAgent(input: $input) { name model } }",
            "read": "query { agents { name description tools model skills memory } }",
            "update": "mutation updateAgent(name: String!, input: AgentInput!) { ... }",
            "delete": "mutation deleteAgent(name: String!) { deleteAgent(name: $name) }",
        },
    },
    "hooks": {
        "display": "Hooks",
        "cli": {
            "create": "Add hook config to `.claude/settings.json` under `hooks` key with event, matcher, and handlers",
            "read": "`/hooks` to view all configured hooks, or read `.claude/settings.json`",
            "update": "Edit hooks section in settings.json — modify matcher, handler command, or timeout",
            "delete": "Remove hook entry from settings.json hooks section",
        },
        "sdk": {
            "create": "Pass `hooks={HookEvent: [HookMatcher(...)]}` to ClaudeAgentOptions",
            "read": "Hooks fire automatically; check via PostToolUse/PreToolUse output",
            "update": "Modify hooks dict and create new query session",
            "delete": "Remove hook from hooks dict",
        },
        "api": {
            "create": "Edit `.claude/settings.json` then run `claude -p` (hooks load from settings)",
            "read": "Hooks execute during `claude -p` runs; check via `--output-format stream-json`",
            "update": "Edit settings.json hooks section, re-run",
            "delete": "Remove from settings.json or set `disableAllHooks: true`",
        },
        "graphql": {
            "create": "mutation createHook(input: HookInput!) { createHook(input: $input) { event matcher } }",
            "read": "query { hooks { event matcher handlers { type command timeout } } }",
            "update": "mutation updateHook(event: String!, input: HookInput!) { ... }",
            "delete": "mutation deleteHook(event: String!, matcher: String!) { ... }",
        },
    },
    "sessions": {
        "display": "Sessions",
        "cli": {
            "create": "`claude` starts new session, or `claude 'prompt'` with initial message",
            "read": "`claude -r` to list sessions, `/resume` to browse, `/context` for current",
            "update": "`/rename <name>` to rename, `/compact` to summarize context",
            "delete": "Sessions auto-expire; no direct delete CLI command",
        },
        "sdk": {
            "create": "Call `query(prompt='...')` to create new session",
            "read": "`list_sessions()` returns SDKSessionInfo list, `get_session_messages()` for transcripts",
            "update": "`rename_session(session_id, title)`, `tag_session(session_id, tag)`",
            "delete": "Sessions managed by retention policy; no direct delete API",
        },
        "api": {
            "create": "`claude -p 'task'` creates ephemeral session, `claude -p --session-id <uuid>` for named",
            "read": "`claude -p --output-format json` returns session_id in result",
            "update": "`claude -c -p 'follow-up'` continues session, `--fork-session` for branching",
            "delete": "Use `--no-session-persistence` to prevent saving",
        },
        "graphql": {
            "create": "mutation createSession(input: SessionInput!) { ... }",
            "read": "query { sessions { id name status model createdAt } }",
            "update": "mutation updateSession(id: String!, input: SessionInput!) { ... }",
            "delete": "mutation deleteSession(id: String!) { ... }",
        },
    },
    "memories": {
        "display": "Memories",
        "cli": {
            "create": "Set `memory: user|project|local` in agent frontmatter; MEMORY.md created on first write",
            "read": "Read `.claude/agent-memory/{name}/MEMORY.md` or `~/.claude/agent-memory/{name}/`",
            "update": "Agent writes to MEMORY.md automatically; or edit file directly",
            "delete": "Remove `MEMORY.md` file or entire agent-memory directory",
        },
        "sdk": {
            "create": "Set `memory='user'|'project'|'local'` in AgentDefinition (Python only)",
            "read": "Memory loaded automatically into agent system prompt (first 200 lines/25KB)",
            "update": "Agent updates MEMORY.md during execution",
            "delete": "Remove memory files from disk",
        },
        "api": {
            "create": "Memory persists across `claude -c` (continue) sessions automatically",
            "read": "Auto-memory visible in `~/.claude/auto-memories/`",
            "update": "Memories update as sessions progress",
            "delete": "`rm ~/.claude/auto-memories/*` or specific agent memory dirs",
        },
        "graphql": {
            "create": "mutation createMemory(input: MemoryInput!) { ... }",
            "read": "query { memories { scope agentName content path } }",
            "update": "mutation updateMemory(scope: String!, agentName: String!, content: String!) { ... }",
            "delete": "mutation deleteMemory(scope: String!, agentName: String!) { ... }",
        },
    },
    "agent-teams": {
        "display": "Agent Teams",
        "cli": {
            "create": "Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, use `--teammate-mode auto|in-process|tmux`",
            "read": "Team status visible in session; press Ctrl+T for task list",
            "update": "Use SendMessage tool to communicate between team members",
            "delete": "Stop teammates via Ctrl+X Ctrl+K or TaskStop tool",
        },
        "sdk": {
            "create": "Multiple `query()` sessions with shared TaskCreate/SendMessage tools",
            "read": "Monitor via TaskGet/TaskList tools in agent loop",
            "update": "TaskUpdate tool to modify task status and dependencies",
            "delete": "TaskStop tool to terminate running tasks",
        },
        "api": {
            "create": "Multiple `claude -p` processes with shared task files for coordination",
            "read": "Check task output files for status",
            "update": "Use lock files for task claiming (parallel agent pattern)",
            "delete": "Kill processes to stop team members",
        },
        "graphql": {
            "create": "mutation createTeam(input: TeamInput!) { ... }",
            "read": "query { teams { name members { name status } tasks { subject status } } }",
            "update": "mutation updateTeam(name: String!, input: TeamInput!) { ... }",
            "delete": "mutation deleteTeam(name: String!) { ... }",
        },
    },
}


def generate_skill_md(interface: str, resource: str, profile: dict) -> str:
    """Generate a SKILL.md for a specific interface-resource combination."""
    display = profile["display"]
    ops = profile[interface]
    return f"""---
name: crud-{interface}-{resource}
description: >
  CRUD operations for Claude Code {display} via {interface.upper()}.
  Use when creating, reading, updating, or deleting {resource} using
  the {interface} interface.
disable-model-invocation: false
---

# CRUD {display} ({interface.upper()})

## When to use
- Creating new {resource} via {interface}
- Listing or inspecting existing {resource}
- Updating {resource} configuration
- Removing {resource}

## Create
{ops["create"]}

## Read
{ops["read"]}

## Update
{ops["update"]}

## Delete
{ops["delete"]}

## Validation
1. Verify the operation completed without errors
2. Confirm the resource exists (for create) or is removed (for delete)
3. Check that all required fields are present and correctly typed
"""


def generate_eval_json(interface: str, resource: str, profile: dict) -> str:
    """Generate an evals.json for a specific interface-resource combination."""
    evals = {
        "skill_name": f"crud-{interface}-{resource}",
        "evals": [
            {
                "id": 1,
                "prompt": f"Create a new {resource.rstrip('s')} called 'example' using {interface}",
                "expected_output": f"Valid {resource.rstrip('s')} created with correct configuration",
                "files": [],
                "assertions": [
                    f"Uses correct {interface} method for creating {resource}",
                    "Output includes the name 'example'",
                    "All required fields are present",
                ],
            },
            {
                "id": 2,
                "prompt": f"List all {resource} and show their configuration using {interface}",
                "expected_output": f"Complete listing of {resource} with details",
                "files": [],
                "assertions": [
                    f"Uses correct {interface} command or method for listing",
                    "Response includes name and configuration fields",
                ],
            },
            {
                "id": 3,
                "prompt": f"Delete the {resource.rstrip('s')} named 'example' using {interface}",
                "expected_output": "Resource removed successfully",
                "files": [],
                "assertions": [
                    f"Uses correct {interface} method for deletion",
                    "Confirms removal or provides verification step",
                ],
            },
        ],
    }
    return json.dumps(evals, indent=2) + "\n"


def generate_router_skill(interface: str) -> str:
    """Generate a router SKILL.md for an interface."""
    resource_list = "\n".join(
        f"- **{profile['display']}**: `/crud-{interface}-{resource}`" for resource, profile in RESOURCES.items()
    )
    return f"""---
name: crud-{interface}
description: >
  Routes to the correct {interface.upper()} CRUD skill based on the resource type.
  Use when managing Claude Code resources via {interface} without specifying which resource.
disable-model-invocation: false
---

# CRUD Router ({interface.upper()})

## Available Resources

{resource_list}

## How to Choose
- Identify the resource type you want to manage
- Use the corresponding skill above
- Each skill covers Create, Read, Update, and Delete operations
"""


def main():
    total_skills = 0
    total_evals = 0

    # Generate 4 router skills
    for interface in INTERFACES:
        router_dir = SKILLS_DIR / f"crud-{interface}"
        router_dir.mkdir(parents=True, exist_ok=True)
        (router_dir / "SKILL.md").write_text(generate_router_skill(interface))
        total_skills += 1

    # Generate 36 resource skills + evals
    for resource, profile in RESOURCES.items():
        for interface in INTERFACES:
            skill_dir = SKILLS_DIR / f"crud-{interface}-{resource}"
            eval_dir = skill_dir / "evals"
            skill_dir.mkdir(parents=True, exist_ok=True)
            eval_dir.mkdir(parents=True, exist_ok=True)

            (skill_dir / "SKILL.md").write_text(generate_skill_md(interface, resource, profile))
            (eval_dir / "evals.json").write_text(generate_eval_json(interface, resource, profile))
            total_skills += 1
            total_evals += 1

    print(f"Generated {total_skills} SKILL.md files and {total_evals} evals.json files")


if __name__ == "__main__":
    main()
