# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
# ]
# ///
"""Execute CRUD operations across GraphQL, API, SDK, and CLI interfaces.

Central dispatcher for CRUD operations against Claude platform entities.
Routes to the correct interface handler based on --interface flag.
"""

import argparse
import json
import os
import subprocess
import sys

import httpx

ANTHROPIC_BASE = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

ENTITY_API_MAP = {
    "skills": "skills",
    "plugins": "plugins",
    "connectors": "connectors",
    "mcps": "mcp-servers",
    "subagents": "agents",
    "hooks": "hooks",
    "sessions": "sessions",
    "memories": "memories",
    "agent-teams": "agent-teams",
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crud_operations",
        description="Execute CRUD operations across GraphQL, API, SDK, and CLI interfaces.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/crud_operations.py --interface cli --entity sessions --operation create --params '{"title": "test"}'
  uv run scripts/crud_operations.py --interface api --entity agents --operation read --id agent_01...
  uv run scripts/crud_operations.py --interface sdk --entity agents --operation list
  uv run scripts/crud_operations.py --interface graphql --entity skills --operation create --params '{"name": "test"}' --endpoint $GRAPHQL_ENDPOINT
  uv run scripts/crud_operations.py --interface cli --entity sessions --operation delete --id session_01...
  uv run scripts/crud_operations.py --dry-run --interface api --entity agents --operation create --params '{"name": "test"}'

Exit codes:
  0  Success
  1  Client error
  2  Execution error
  3  Entity not found (for read/update/delete)""",
    )
    p.add_argument("--interface", required=True, choices=["graphql", "api", "sdk", "cli"])
    p.add_argument("--entity", required=True, choices=list(ENTITY_API_MAP.keys()))
    p.add_argument("--operation", required=True, choices=["create", "read", "update", "delete", "list"])
    p.add_argument("--id", help="Entity ID (for read/update/delete)")
    p.add_argument("--version", type=int, help="Version number (for update)")
    p.add_argument("--params", help="JSON parameters for create/update")
    p.add_argument(
        "--endpoint", default=os.environ.get("GRAPHQL_ENDPOINT"), help="GraphQL endpoint (for graphql interface)"
    )
    p.add_argument("--dry-run", action="store_true", help="Show what would be executed")
    p.add_argument("--output", help="Write result to file")
    return p


def run_cli(
    entity: str, operation: str, entity_id: str | None, version: int | None, params: dict | None, dry_run: bool
) -> dict:
    """Execute via ant CLI."""
    api_entity = ENTITY_API_MAP[entity].replace("-", "_")
    cmd = ["ant", f"beta:{api_entity}"]

    if operation == "create":
        cmd.append("create")
        if params:
            stdin_data = json.dumps(params)
        else:
            stdin_data = None
    elif operation == "read":
        cmd.append("retrieve")
        cmd.extend([f"--{api_entity.rstrip('s')}-id", entity_id or "MISSING"])
    elif operation == "list":
        cmd.append("list")
        stdin_data = None
    elif operation == "update":
        cmd.append("update")
        cmd.extend([f"--{api_entity.rstrip('s')}-id", entity_id or "MISSING"])
        if version:
            cmd.extend(["--version", str(version)])
        stdin_data = json.dumps(params) if params else None
    elif operation == "delete":
        cmd.append("delete")
        cmd.extend([f"--{api_entity.rstrip('s')}-id", entity_id or "MISSING"])
        stdin_data = None

    if dry_run:
        return {"dry_run": True, "command": cmd, "stdin": stdin_data}

    try:
        result = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "exit_code": result.returncode}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw_output": result.stdout.strip()}
    except FileNotFoundError:
        return {"error": "ant CLI not found. Install: brew install anthropics/tap/ant"}
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 30s"}


def run_api(
    entity: str, operation: str, entity_id: str | None, version: int | None, params: dict | None, dry_run: bool
) -> dict:
    """Execute via REST API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and not dry_run:
        return {"error": "ANTHROPIC_API_KEY is required"}

    api_entity = ENTITY_API_MAP[entity]
    base = f"{ANTHROPIC_BASE}/v1/beta/{api_entity}"
    headers = {
        "x-api-key": api_key or "",
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "managed-agents-2026-04-01",
        "content-type": "application/json",
    }

    if operation == "create":
        method, url, body = "POST", base, params
    elif operation == "read":
        method, url, body = "GET", f"{base}/{entity_id}", None
    elif operation == "list":
        method, url, body = "GET", base, None
    elif operation == "update":
        method, url = "PUT", f"{base}/{entity_id}"
        body = {**(params or {}), **({"version": version} if version else {})}
    elif operation == "delete":
        method, url, body = "DELETE", f"{base}/{entity_id}", None
    else:
        return {"error": f"Unknown operation: {operation}"}

    if dry_run:
        return {"dry_run": True, "method": method, "url": url, "body": body}

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.request(method, url, json=body, headers=headers)
            if resp.status_code == 404:
                return {"error": "Not found", "status": 404}
            resp.raise_for_status()
            return resp.json() if resp.text else {"status": resp.status_code}
    except httpx.HTTPStatusError as e:
        try:
            return {"error": e.response.json(), "status": e.response.status_code}
        except Exception:
            return {"error": e.response.text[:500], "status": e.response.status_code}
    except httpx.ConnectError as e:
        return {"error": f"Connection failed: {e}"}


def run_sdk(
    entity: str, operation: str, entity_id: str | None, version: int | None, params: dict | None, dry_run: bool
) -> dict:
    """Execute via Python SDK."""
    api_entity = ENTITY_API_MAP[entity].replace("-", "_")

    # Build the SDK call description
    sdk_call = f"client.beta.{api_entity}"
    if operation == "create":
        sdk_call += f".create(**{json.dumps(params or {})})"
    elif operation == "read":
        sdk_call += f".retrieve({api_entity.rstrip('s')}_id='{entity_id}')"
    elif operation == "list":
        sdk_call += ".list()"
    elif operation == "update":
        update_params = {**(params or {}), **({"version": version} if version else {})}
        sdk_call += f".update({api_entity.rstrip('s')}_id='{entity_id}', **{json.dumps(update_params)})"
    elif operation == "delete":
        sdk_call += f".delete({api_entity.rstrip('s')}_id='{entity_id}')"

    if dry_run:
        return {"dry_run": True, "sdk_call": sdk_call}

    # Execute via subprocess to avoid importing anthropic in this script
    code = f"""
import json, anthropic
client = anthropic.Anthropic()
result = {sdk_call}
if hasattr(result, 'model_dump'):
    print(json.dumps(result.model_dump(), indent=2, default=str))
elif hasattr(result, '__iter__'):
    items = [r.model_dump() if hasattr(r, 'model_dump') else r for r in result]
    print(json.dumps(items, indent=2, default=str))
else:
    print(json.dumps({{"result": str(result)}}))
"""
    try:
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"error": result.stderr.strip()}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "SDK call timed out after 30s"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from SDK", "raw": result.stdout[:500]}


def run_graphql(
    entity: str, operation: str, entity_id: str | None, params: dict | None, endpoint: str | None, dry_run: bool
) -> dict:
    """Execute via GraphQL mutations/queries."""
    if not endpoint and not dry_run:
        return {"error": "GRAPHQL_ENDPOINT is required for graphql interface"}

    singular = entity.rstrip("s") if not entity.endswith("ies") else entity[:-3] + "y"
    pascal = "".join(w.capitalize() for w in singular.replace("-", " ").split())

    if operation == "create":
        query = f"mutation {{ create{pascal}(input: $input) {{ id name }} }}"
        variables = {"input": params or {}}
    elif operation == "read":
        query = f'query {{ {singular}(id: "{entity_id}") {{ id name description }} }}'
        variables = {}
    elif operation == "list":
        collection = entity.replace("-", "_") + "Collection"
        query = f"query {{ {collection}(first: 20) {{ edges {{ node {{ id name }} }} }} }}"
        variables = {}
    elif operation == "update":
        query = f'mutation {{ update{pascal}(id: "{entity_id}", input: $input) {{ id name }} }}'
        variables = {"input": params or {}}
    elif operation == "delete":
        query = f'mutation {{ delete{pascal}(id: "{entity_id}") {{ success }} }}'
        variables = {}
    else:
        return {"error": f"Unknown operation: {operation}"}

    if dry_run:
        return {"dry_run": True, "query": query, "variables": variables, "endpoint": endpoint}

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                endpoint or "",
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"},
            )
            return resp.json()
    except Exception as e:
        return {"error": str(e)}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    params = None
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --params: {e}", file=sys.stderr)
            sys.exit(1)

    if args.interface == "cli":
        result = run_cli(args.entity, args.operation, args.id, args.version, params, args.dry_run)
    elif args.interface == "api":
        result = run_api(args.entity, args.operation, args.id, args.version, params, args.dry_run)
    elif args.interface == "sdk":
        result = run_sdk(args.entity, args.operation, args.id, args.version, params, args.dry_run)
    elif args.interface == "graphql":
        result = run_graphql(args.entity, args.operation, args.id, params, args.endpoint, args.dry_run)
    else:
        print(f"Error: Unknown interface: {args.interface}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n")
    else:
        print(output)

    if "error" in result:
        sys.exit(3 if result.get("status") == 404 else 2)


if __name__ == "__main__":
    from pathlib import Path

    main()
