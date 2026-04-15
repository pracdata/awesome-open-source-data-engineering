# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate the full CRUD eval matrix as evals.json.

Creates test cases for all combinations of:
- 4 interfaces (graphql, api, sdk, cli)
- 9 entities (skills, plugins, connectors, mcps, subagents, hooks, sessions, memories, agent-teams)
- 4 operations (create, read, update, delete)
"""

import argparse
import json
import sys
from pathlib import Path

INTERFACES = ["graphql", "api", "sdk", "cli"]

ENTITIES = [
    "skills",
    "plugins",
    "connectors",
    "mcps",
    "subagents",
    "hooks",
    "sessions",
    "memories",
    "agent-teams",
]

OPERATIONS = ["create", "read", "update", "delete"]

# Interface-specific command patterns
INTERFACE_PATTERNS = {
    "graphql": {
        "create": "mutation {{ create{Entity}(input: $input) {{ id name }} }}",
        "read": "query {{ {entity}(id: $id) {{ id name description }} }}",
        "update": "mutation {{ update{Entity}(id: $id, input: $input) {{ id name }} }}",
        "delete": "mutation {{ delete{Entity}(id: $id) {{ success }} }}",
    },
    "api": {
        "create": "POST /v1/beta/{entity_plural}",
        "read": "GET /v1/beta/{entity_plural}/{{id}}",
        "update": "PUT /v1/beta/{entity_plural}/{{id}}",
        "delete": "DELETE /v1/beta/{entity_plural}/{{id}}",
    },
    "sdk": {
        "create": "client.beta.{entity_plural}.create(**params)",
        "read": "client.beta.{entity_plural}.retrieve({entity}_id=id)",
        "update": "client.beta.{entity_plural}.update({entity}_id=id, **params)",
        "delete": "client.beta.{entity_plural}.delete({entity}_id=id)",
    },
    "cli": {
        "create": "ant beta:{entity_plural} create [< config.yaml]",
        "read": "ant beta:{entity_plural} retrieve --{entity}-id <id>",
        "update": "ant beta:{entity_plural} update --{entity}-id <id> --version <v>",
        "delete": "ant beta:{entity_plural} delete --{entity}-id <id>",
    },
}

# Entity-specific test data
ENTITY_TEST_DATA = {
    "skills": {"name": "test-analyzer", "description": "Analyzes test data"},
    "plugins": {"name": "test-plugin", "type": "tool", "description": "A test plugin"},
    "connectors": {"name": "test-connector", "type": "mcp", "config": {"command": "echo"}},
    "mcps": {"name": "test-mcp", "command": "npx", "args": ["@test/server"]},
    "subagents": {"name": "test-subagent", "model": {"id": "claude-sonnet-4-6"}, "system": "You are a test helper."},
    "hooks": {"event": "PreToolUse", "command": "echo pre-hook", "matcher": "Bash"},
    "sessions": {"title": "test-session", "agent": "agent_placeholder", "environment": "env_placeholder"},
    "memories": {"key": "test-memory", "content": "This is a test memory entry."},
    "agent-teams": {"name": "test-team", "agents": [{"name": "leader", "role": "coordinator"}]},
}

# Per-operation assertion templates
ASSERTION_TEMPLATES = {
    "create": [
        "The operation returns a valid identifier for the created {entity}",
        "The response confirms the {entity} was created with the provided name/title",
        "The response includes a timestamp or version number",
        "The {interface} call uses the correct endpoint/method for creation",
    ],
    "read": [
        "The operation returns the {entity} data matching the requested ID",
        "The response includes all expected fields (id, name, description or equivalent)",
        "The {interface} call uses the correct endpoint/method for retrieval",
        "The response format matches the expected schema for {entity}",
    ],
    "update": [
        "The operation returns the updated {entity} with changed fields",
        "The version/timestamp is incremented after update",
        "The {interface} call includes the version lock for optimistic concurrency",
        "Unchanged fields retain their original values",
    ],
    "delete": [
        "The operation confirms the {entity} was deleted",
        "A subsequent read of the same ID returns 404 or empty result",
        "The {interface} call uses the correct endpoint/method for deletion",
        "The operation is idempotent (re-deleting does not error fatally)",
    ],
}

# Prompt templates per operation
PROMPT_TEMPLATES = {
    "create": "Create a new {entity_singular} via the {interface} interface with name '{test_name}' and verify it was created successfully.",
    "read": "Retrieve the {entity_singular} with ID '{{id}}' via the {interface} interface and display all its fields.",
    "update": "Update the {entity_singular} with ID '{{id}}' via the {interface} interface to change its description to 'Updated by eval', then verify the change.",
    "delete": "Delete the {entity_singular} with ID '{{id}}' via the {interface} interface and confirm it no longer exists.",
}


def entity_singular(entity: str) -> str:
    """Convert plural entity name to singular."""
    if entity == "memories":
        return "memory"
    if entity.endswith("ies"):
        return entity[:-3] + "y"
    if entity.endswith("s"):
        return entity[:-1]
    return entity


def entity_pascal(entity: str) -> str:
    """Convert entity name to PascalCase."""
    return "".join(word.capitalize() for word in entity_singular(entity).replace("-", " ").split())


def generate_eval(interface: str, entity: str, operation: str) -> dict:
    eval_id = f"{interface}-{entity}-{operation}"
    singular = entity_singular(entity)
    pascal = entity_pascal(entity)
    test_data = ENTITY_TEST_DATA.get(entity, {})
    test_name = test_data.get("name", test_data.get("title", f"test-{singular}"))

    prompt = PROMPT_TEMPLATES[operation].format(
        entity_singular=singular,
        interface=interface,
        test_name=test_name,
    )

    expected = f"A successful {operation} of a {singular} via {interface}, returning the appropriate response."

    assertions = [a.format(entity=singular, interface=interface) for a in ASSERTION_TEMPLATES[operation]]

    pattern = INTERFACE_PATTERNS[interface][operation]
    command_hint = pattern.format(
        Entity=pascal,
        entity=singular,
        entity_plural=entity.replace("-", "_"),
    )

    return {
        "id": eval_id,
        "interface": interface,
        "entity": entity,
        "operation": operation,
        "prompt": prompt,
        "expected_output": expected,
        "command_hint": command_hint,
        "test_data": test_data,
        "assertions": assertions,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate_eval_matrix",
        description="Generate the full CRUD eval matrix.",
        epilog="""Examples:
  uv run scripts/generate_eval_matrix.py --output evals/evals.json
  uv run scripts/generate_eval_matrix.py --interface cli --entity sessions
  uv run scripts/generate_eval_matrix.py --list-ids""",
    )
    p.add_argument("--output", help="Write evals to file (default: stdout)")
    p.add_argument("--interface", choices=INTERFACES, help="Filter to one interface")
    p.add_argument("--entity", choices=ENTITIES, help="Filter to one entity")
    p.add_argument("--operation", choices=OPERATIONS, help="Filter to one operation")
    p.add_argument("--list-ids", action="store_true", help="Print only eval IDs")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    interfaces = [args.interface] if args.interface else INTERFACES
    entities = [args.entity] if args.entity else ENTITIES
    operations = [args.operation] if args.operation else OPERATIONS

    evals = []
    for interface in interfaces:
        for entity in entities:
            for operation in operations:
                evals.append(generate_eval(interface, entity, operation))

    if args.list_ids:
        for e in evals:
            print(e["id"])
        return

    result = {
        "skill_name": "crud-eval",
        "matrix": {
            "interfaces": interfaces,
            "entities": entities,
            "operations": operations,
        },
        "total_evals": len(evals),
        "evals": evals,
    }

    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output + "\n")
        print(f"Generated {len(evals)} eval test cases to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
