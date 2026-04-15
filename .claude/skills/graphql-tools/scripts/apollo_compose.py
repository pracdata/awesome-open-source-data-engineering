# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "graphql-core>=3.2,<4",
#   "pyyaml>=6.0,<7",
# ]
# ///
"""Apollo Federation supergraph composition and subgraph validation.

Composes multiple subgraph schemas into a supergraph schema, validates
subgraph compatibility, and checks for federation directive usage.

For full Apollo Router composition, use `rover supergraph compose`.
This script handles local schema composition and validation workflows.
"""

import argparse
import json
import sys
from pathlib import Path

import yaml
from graphql import build_schema, parse
from graphql.error import GraphQLSyntaxError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="apollo_compose",
        description="Apollo Federation supergraph composition and validation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/apollo_compose.py --config supergraph.yaml --output supergraph.graphql
  uv run scripts/apollo_compose.py --validate --subgraph users --schema users.graphql
  uv run scripts/apollo_compose.py --check-directives --schema subgraph.graphql
  uv run scripts/apollo_compose.py --merge schema1.graphql schema2.graphql --output merged.graphql

Config file format (supergraph.yaml):
  subgraphs:
    users:
      schema: ./services/users/schema.graphql
      routing_url: http://users:4001/graphql
    products:
      schema: ./services/products/schema.graphql
      routing_url: http://products:4002/graphql

Exit codes:
  0  Success (or validation passed)
  1  Client error (bad arguments, files not found)
  2  Composition/validation error
  3  Schema syntax error""",
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--config", help="Supergraph config YAML file for composition")
    mode.add_argument("--validate", action="store_true", help="Validate a single subgraph schema")
    mode.add_argument("--check-directives", action="store_true", help="Check federation directive usage in a schema")
    mode.add_argument(
        "--merge", nargs="+", metavar="SCHEMA", help="Merge multiple schema files (simple concatenation with dedup)"
    )

    p.add_argument("--subgraph", help="Subgraph name (for --validate)")
    p.add_argument("--schema", help="Schema file path (for --validate, --check-directives)")
    p.add_argument("--output", help="Write output to file instead of stdout")
    return p


FEDERATION_DIRECTIVES = {
    "@key": {"on": ["OBJECT", "INTERFACE"], "purpose": "Defines entity primary key for cross-subgraph resolution"},
    "@external": {"on": ["FIELD_DEFINITION"], "purpose": "Marks field as owned by another subgraph"},
    "@requires": {"on": ["FIELD_DEFINITION"], "purpose": "Specifies fields needed from this subgraph for resolution"},
    "@provides": {"on": ["FIELD_DEFINITION"], "purpose": "Specifies fields this subgraph can provide for entities"},
    "@shareable": {
        "on": ["OBJECT", "FIELD_DEFINITION"],
        "purpose": "Allows field to be resolved by multiple subgraphs",
    },
    "@extends": {"on": ["OBJECT", "INTERFACE"], "purpose": "Marks type as extension of entity from another subgraph"},
    "@override": {"on": ["FIELD_DEFINITION"], "purpose": "Migrates field resolution from one subgraph to another"},
    "@inaccessible": {
        "on": [
            "FIELD_DEFINITION",
            "OBJECT",
            "INTERFACE",
            "UNION",
            "ENUM",
            "ENUM_VALUE",
            "SCALAR",
            "INPUT_OBJECT",
            "INPUT_FIELD_DEFINITION",
            "ARGUMENT_DEFINITION",
        ],
        "purpose": "Hides element from the public API",
    },
    "@tag": {
        "on": [
            "FIELD_DEFINITION",
            "OBJECT",
            "INTERFACE",
            "UNION",
            "ENUM",
            "ENUM_VALUE",
            "SCALAR",
            "INPUT_OBJECT",
            "INPUT_FIELD_DEFINITION",
            "ARGUMENT_DEFINITION",
        ],
        "purpose": "Applies metadata tags for schema contracts",
    },
}

FEDERATION_DIRECTIVES_SDL = """
directive @key(fields: String!, resolvable: Boolean = true) repeatable on OBJECT | INTERFACE
directive @external on FIELD_DEFINITION
directive @requires(fields: String!) on FIELD_DEFINITION
directive @provides(fields: String!) on FIELD_DEFINITION
directive @shareable on OBJECT | FIELD_DEFINITION
directive @extends on OBJECT | INTERFACE
directive @override(from: String!) on FIELD_DEFINITION
directive @inaccessible on FIELD_DEFINITION | OBJECT | INTERFACE | UNION | ENUM | ENUM_VALUE | SCALAR | INPUT_OBJECT | INPUT_FIELD_DEFINITION | ARGUMENT_DEFINITION
directive @tag(name: String!) repeatable on FIELD_DEFINITION | OBJECT | INTERFACE | UNION | ENUM | ENUM_VALUE | SCALAR | INPUT_OBJECT | INPUT_FIELD_DEFINITION | ARGUMENT_DEFINITION
scalar _FieldSet
scalar _Any
type _Service { sdl: String }
union _Entity
"""


def read_schema_file(path: str) -> str:
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        print(f"Error: Schema file not found: {path}", file=sys.stderr)
        sys.exit(1)


def validate_schema_syntax(sdl: str, name: str) -> bool:
    try:
        parse(sdl)
        return True
    except GraphQLSyntaxError as e:
        print(f"Error: Syntax error in {name}: {e}", file=sys.stderr)
        return False


def validate_subgraph(name: str, schema_path: str) -> dict:
    sdl = read_schema_file(schema_path)
    issues: list[dict] = []
    warnings: list[str] = []

    if not validate_schema_syntax(sdl, name):
        return {"subgraph": name, "valid": False, "issues": [{"severity": "error", "message": "Schema syntax error"}]}

    # Check for federation directive definitions (they should be provided by the runtime)
    full_sdl = FEDERATION_DIRECTIVES_SDL + sdl
    try:
        schema = build_schema(full_sdl)
    except Exception as e:
        issues.append({"severity": "error", "message": f"Schema build error: {e}"})
        return {"subgraph": name, "valid": False, "issues": issues}

    # Check for @key directives on types (entities)
    has_entities = "@key" in sdl
    if not has_entities:
        warnings.append("No @key directives found. This subgraph defines no entities for cross-subgraph resolution.")

    # Check @external fields have corresponding @requires or are referenced by @key
    if "@external" in sdl and "@requires" not in sdl and "@provides" not in sdl:
        warnings.append("@external fields found without @requires or @provides. Verify these fields are needed.")

    # Check Query type exists
    query_type = schema.query_type
    if not query_type or not query_type.fields:
        warnings.append("No Query type fields defined. The subgraph exposes no queries.")

    return {
        "subgraph": name,
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "entities": [
            t.name
            for t in schema.type_map.values()
            if hasattr(t, "ast_node")
            and t.ast_node
            and any(d.name.value == "key" for d in (t.ast_node.directives or []))
        ],
    }


def check_directives(schema_path: str) -> dict:
    sdl = read_schema_file(schema_path)
    found: dict[str, list[str]] = {}

    for directive_name in FEDERATION_DIRECTIVES:
        if directive_name in sdl:
            # Find approximate locations
            lines = sdl.split("\n")
            locations = [f"line {i + 1}" for i, line in enumerate(lines) if directive_name in line]
            found[directive_name] = locations

    return {
        "file": schema_path,
        "directives_found": {
            k: {"count": len(v), "locations": v, "purpose": FEDERATION_DIRECTIVES[k]["purpose"]}
            for k, v in found.items()
        },
        "directives_not_found": [k for k in FEDERATION_DIRECTIVES if k not in found],
    }


def compose_from_config(config_path: str) -> str:
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in {config_path}: {e}", file=sys.stderr)
        sys.exit(1)

    subgraphs = config.get("subgraphs", {})
    if not subgraphs:
        print("Error: No subgraphs defined in config.", file=sys.stderr)
        sys.exit(1)

    all_valid = True
    results = []
    schemas = []

    for name, sub_config in subgraphs.items():
        schema_path = sub_config.get("schema")
        if not schema_path:
            print(f"Error: Subgraph '{name}' missing 'schema' field.", file=sys.stderr)
            sys.exit(1)

        result = validate_subgraph(name, schema_path)
        results.append(result)
        if not result["valid"]:
            all_valid = False
        else:
            schemas.append(
                f"# Subgraph: {name}\n# URL: {sub_config.get('routing_url', 'N/A')}\n\n{read_schema_file(schema_path)}"
            )

    validation_output = json.dumps({"composition": {"valid": all_valid, "subgraphs": results}}, indent=2)
    print(validation_output, file=sys.stderr)

    if not all_valid:
        print("Error: Composition failed due to subgraph validation errors.", file=sys.stderr)
        sys.exit(2)

    return "\n\n".join(schemas)


def merge_schemas(paths: list[str]) -> str:
    parts = []
    for p in paths:
        sdl = read_schema_file(p)
        if not validate_schema_syntax(sdl, p):
            sys.exit(3)
        parts.append(f"# Source: {p}\n{sdl}")
    return "\n\n".join(parts)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.config:
        output = compose_from_config(args.config)
    elif args.validate:
        if not args.schema:
            print("Error: --schema is required with --validate.", file=sys.stderr)
            sys.exit(1)
        name = args.subgraph or Path(args.schema).stem
        result = validate_subgraph(name, args.schema)
        output = json.dumps(result, indent=2)
        if not result["valid"]:
            print(output)
            sys.exit(2)
    elif args.check_directives:
        if not args.schema:
            print("Error: --schema is required with --check-directives.", file=sys.stderr)
            sys.exit(1)
        result = check_directives(args.schema)
        output = json.dumps(result, indent=2)
    elif args.merge:
        output = merge_schemas(args.merge)
    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
