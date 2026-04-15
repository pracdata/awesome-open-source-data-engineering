# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "httpx>=0.27,<1",
#   "pyyaml>=6.0,<7",
# ]
# ///
"""Generate Tailcall GraphQL configuration from REST/gRPC endpoint definitions.

Tailcall uses .graphql files with custom directives (@server, @upstream, @http)
to define a high-performance GraphQL gateway over REST APIs.

Tailcall docs: https://tailcall.run/docs/
"""

import argparse
import json
import sys
from pathlib import Path

import httpx
import yaml


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tailcall_gen",
        description="Generate Tailcall GraphQL configuration from REST endpoint definitions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/tailcall_gen.py --from-openapi https://petstore3.swagger.io/api/v3/openapi.json --output petstore.graphql
  uv run scripts/tailcall_gen.py --from-openapi openapi.yaml --base-url https://api.example.com --output api.graphql
  uv run scripts/tailcall_gen.py --from-endpoints endpoints.yaml --output gateway.graphql
  uv run scripts/tailcall_gen.py --scaffold --base-url https://api.example.com --output config.graphql

Endpoints YAML format:
  base_url: https://api.example.com
  endpoints:
    - name: users
      path: /api/users
      method: GET
      response_type: "[User]"
      fields:
        - name: id
          type: Int!
        - name: name
          type: String!
        - name: email
          type: String
    - name: user
      path: /api/users/{{.args.id}}
      method: GET
      args:
        - name: id
          type: Int!
      response_type: User

Exit codes:
  0  Success
  1  Client error (bad arguments, file not found)
  2  Network or processing error""",
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--from-openapi", help="Generate config from OpenAPI spec (URL or file path)")
    mode.add_argument("--from-endpoints", help="Generate config from endpoints YAML definition")
    mode.add_argument("--scaffold", action="store_true", help="Generate a starter Tailcall config")

    p.add_argument("--base-url", help="Base URL for the upstream API")
    p.add_argument("--output", help="Write output to file instead of stdout")
    p.add_argument("--port", type=int, default=8000, help="Tailcall server port (default: 8000)")
    p.add_argument("--hostname", default="0.0.0.0", help="Tailcall server hostname (default: 0.0.0.0)")
    return p


def load_openapi_spec(source: str) -> dict:
    if source.startswith("http://") or source.startswith("https://"):
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(source)
                resp.raise_for_status()
                if "yaml" in source or "yml" in source:
                    return yaml.safe_load(resp.text)
                return resp.json()
        except httpx.HTTPError as e:
            print(f"Error: Could not fetch OpenAPI spec: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        try:
            text = Path(source).read_text()
            if source.endswith((".yaml", ".yml")):
                return yaml.safe_load(text)
            return json.loads(text)
        except FileNotFoundError:
            print(f"Error: File not found: {source}", file=sys.stderr)
            sys.exit(1)


def openapi_type_to_graphql(schema: dict) -> str:
    """Convert OpenAPI schema type to GraphQL type."""
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return ref
    t = schema.get("type", "String")
    fmt = schema.get("format", "")
    if t == "integer":
        return "Int"
    if t == "number":
        return "Float"
    if t == "boolean":
        return "Boolean"
    if t == "string" and fmt == "date-time":
        return "String"
    if t == "array":
        items = schema.get("items", {})
        return f"[{openapi_type_to_graphql(items)}]"
    return "String"


def generate_from_openapi(spec: dict, base_url: str | None, port: int, hostname: str) -> str:
    lines: list[str] = []

    # Determine base URL
    api_base = base_url
    if not api_base:
        servers = spec.get("servers", [])
        api_base = servers[0]["url"] if servers else "https://api.example.com"

    # Server and upstream directives
    lines.append(f'schema @server(port: {port}, hostname: "{hostname}") @upstream(baseURL: "{api_base}") {{')
    lines.append("  query: Query")
    lines.append("}")
    lines.append("")

    # Generate types from components/schemas
    schemas = spec.get("components", {}).get("schemas", {})
    for name, schema in schemas.items():
        if schema.get("type") == "object":
            lines.append(f"type {name} {{")
            for prop_name, prop_schema in schema.get("properties", {}).items():
                gql_type = openapi_type_to_graphql(prop_schema)
                required = prop_name in schema.get("required", [])
                suffix = "!" if required else ""
                lines.append(f"  {prop_name}: {gql_type}{suffix}")
            lines.append("}")
            lines.append("")

    # Generate Query type from paths
    lines.append("type Query {")
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() != "get":
                continue
            op_id = operation.get("operationId", path.replace("/", "_").strip("_"))
            op_id = "".join(c if c.isalnum() else "_" for c in op_id).strip("_")
            # camelCase the operation id
            parts = op_id.split("_")
            op_id = parts[0].lower() + "".join(p.capitalize() for p in parts[1:])

            # Determine return type
            response = operation.get("responses", {}).get("200", {})
            content = response.get("content", {}).get("application/json", {})
            resp_schema = content.get("schema", {})
            return_type = openapi_type_to_graphql(resp_schema)

            # Build args from path parameters
            params = operation.get("parameters", [])
            path_params = [p for p in params if p.get("in") == "path"]

            tailcall_path = path
            args_str = ""
            if path_params:
                arg_parts = []
                for param in path_params:
                    pname = param["name"]
                    ptype = openapi_type_to_graphql(param.get("schema", {"type": "string"}))
                    arg_parts.append(f"{pname}: {ptype}!")
                    tailcall_path = tailcall_path.replace(f"{{{pname}}}", f"{{{{.args.{pname}}}}}")
                args_str = f"({', '.join(arg_parts)})"

            lines.append(f'  {op_id}{args_str}: {return_type} @http(path: "{tailcall_path}")')

    lines.append("}")
    return "\n".join(lines)


def generate_from_endpoints(config_path: str, port: int, hostname: str) -> str:
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    base_url = config.get("base_url", "https://api.example.com")
    endpoints = config.get("endpoints", [])

    lines: list[str] = []
    lines.append(f'schema @server(port: {port}, hostname: "{hostname}") @upstream(baseURL: "{base_url}") {{')
    lines.append("  query: Query")
    lines.append("}")
    lines.append("")

    # Collect and generate types
    defined_types: set[str] = set()
    for ep in endpoints:
        for field in ep.get("fields", []):
            pass  # fields define inline types
        type_name = ep.get("response_type", "").strip("[]")
        if type_name and type_name not in defined_types and ep.get("fields"):
            defined_types.add(type_name)
            lines.append(f"type {type_name} {{")
            for field in ep["fields"]:
                lines.append(f"  {field['name']}: {field['type']}")
            lines.append("}")
            lines.append("")

    # Generate Query
    lines.append("type Query {")
    for ep in endpoints:
        name = ep["name"]
        path = ep["path"]
        response_type = ep.get("response_type", "String")
        args = ep.get("args", [])
        method = ep.get("method", "GET").upper()

        args_str = ""
        if args:
            arg_parts = [f"{a['name']}: {a['type']}" for a in args]
            args_str = f"({', '.join(arg_parts)})"

        method_directive = f', method: "{method}"' if method != "GET" else ""
        lines.append(f'  {name}{args_str}: {response_type} @http(path: "{path}"{method_directive})')

    lines.append("}")
    return "\n".join(lines)


def generate_scaffold(base_url: str | None, port: int, hostname: str) -> str:
    url = base_url or "https://api.example.com"
    return f"""# Tailcall GraphQL Configuration
# Docs: https://tailcall.run/docs/

schema @server(port: {port}, hostname: "{hostname}") @upstream(baseURL: "{url}") {{
  query: Query
}}

type User {{
  id: Int!
  name: String!
  email: String
}}

type Query {{
  users: [User] @http(path: "/api/users")
  user(id: Int!): User @http(path: "/api/users/{{{{.args.id}}}}")
}}"""


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.from_openapi:
        spec = load_openapi_spec(args.from_openapi)
        output = generate_from_openapi(spec, args.base_url, args.port, args.hostname)
    elif args.from_endpoints:
        output = generate_from_endpoints(args.from_endpoints, args.port, args.hostname)
    elif args.scaffold:
        output = generate_scaffold(args.base_url, args.port, args.hostname)
    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"Config written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
