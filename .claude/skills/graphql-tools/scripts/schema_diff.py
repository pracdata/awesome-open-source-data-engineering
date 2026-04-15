# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "graphql-core>=3.2,<4",
# ]
# ///
"""Compare two GraphQL schemas and detect breaking/non-breaking changes.

Similar to GraphQL Inspector's diff functionality. Compares types, fields,
arguments, directives, and enums between two schema versions.
"""

import argparse
import json
import sys
from pathlib import Path

from graphql import build_schema
from graphql.error import GraphQLSyntaxError
from graphql.type import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLUnionType,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="schema_diff",
        description="Compare two GraphQL schemas and report changes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/schema_diff.py --old schema-v1.graphql --new schema-v2.graphql
  uv run scripts/schema_diff.py --old schema-v1.graphql --new schema-v2.graphql --format json
  uv run scripts/schema_diff.py --old schema-v1.graphql --new schema-v2.graphql --breaking-only

Exit codes:
  0  No breaking changes
  1  Client error (bad arguments, file not found)
  2  Schema syntax error
  3  Breaking changes detected""",
    )
    p.add_argument("--old", required=True, help="Path to the old (base) schema file")
    p.add_argument("--new", required=True, help="Path to the new (target) schema file")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    p.add_argument("--breaking-only", action="store_true", help="Only show breaking changes")
    p.add_argument("--output", help="Write output to file instead of stdout")
    return p


BUILTIN_TYPES = {
    "String",
    "Int",
    "Float",
    "Boolean",
    "ID",
    "__Schema",
    "__Type",
    "__Field",
    "__InputValue",
    "__EnumValue",
    "__Directive",
    "__DirectiveLocation",
}


def load_schema(path: str):
    try:
        sdl = Path(path).read_text()
    except FileNotFoundError:
        print(f"Error: Schema file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return build_schema(sdl)
    except GraphQLSyntaxError as e:
        print(f"Error: Syntax error in {path}: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: Could not build schema from {path}: {e}", file=sys.stderr)
        sys.exit(2)


def get_type_name(gql_type) -> str:
    if hasattr(gql_type, "of_type"):
        inner = get_type_name(gql_type.of_type)
        if hasattr(gql_type, "__class__") and "NonNull" in gql_type.__class__.__name__:
            return f"{inner}!"
        if hasattr(gql_type, "__class__") and "List" in gql_type.__class__.__name__:
            return f"[{inner}]"
        return inner
    return gql_type.name if hasattr(gql_type, "name") else str(gql_type)


def diff_schemas(old_schema, new_schema) -> list[dict]:
    changes: list[dict] = []

    old_types = {n: t for n, t in old_schema.type_map.items() if n not in BUILTIN_TYPES}
    new_types = {n: t for n, t in new_schema.type_map.items() if n not in BUILTIN_TYPES}

    # Removed types (breaking)
    for name in old_types:
        if name not in new_types:
            changes.append(
                {"type": "TYPE_REMOVED", "breaking": True, "path": name, "message": f"Type '{name}' was removed"}
            )

    # Added types (non-breaking)
    for name in new_types:
        if name not in old_types:
            changes.append(
                {"type": "TYPE_ADDED", "breaking": False, "path": name, "message": f"Type '{name}' was added"}
            )

    # Changed types
    for name in old_types:
        if name not in new_types:
            continue
        old_t = old_types[name]
        new_t = new_types[name]

        # Type kind changed (breaking)
        if type(old_t) is not type(new_t):
            changes.append(
                {
                    "type": "TYPE_KIND_CHANGED",
                    "breaking": True,
                    "path": name,
                    "message": f"Type '{name}' changed kind from {old_t.__class__.__name__} to {new_t.__class__.__name__}",
                }
            )
            continue

        # Object/Interface types - check fields
        if isinstance(old_t, (GraphQLObjectType, GraphQLInterfaceType)):
            old_fields = old_t.fields
            new_fields = new_t.fields

            for fname in old_fields:
                if fname not in new_fields:
                    changes.append(
                        {
                            "type": "FIELD_REMOVED",
                            "breaking": True,
                            "path": f"{name}.{fname}",
                            "message": f"Field '{fname}' was removed from type '{name}'",
                        }
                    )
                else:
                    old_ftype = get_type_name(old_fields[fname].type)
                    new_ftype = get_type_name(new_fields[fname].type)
                    if old_ftype != new_ftype:
                        changes.append(
                            {
                                "type": "FIELD_TYPE_CHANGED",
                                "breaking": True,
                                "path": f"{name}.{fname}",
                                "message": f"Field '{name}.{fname}' type changed from '{old_ftype}' to '{new_ftype}'",
                            }
                        )

                    # Check arguments
                    old_args = old_fields[fname].args
                    new_args = new_fields[fname].args

                    for aname in old_args:
                        if aname not in new_args:
                            changes.append(
                                {
                                    "type": "ARG_REMOVED",
                                    "breaking": True,
                                    "path": f"{name}.{fname}({aname})",
                                    "message": f"Argument '{aname}' removed from '{name}.{fname}'",
                                }
                            )

                    for aname in new_args:
                        if aname not in old_args:
                            is_required = "!" in get_type_name(new_args[aname].type)
                            if is_required and new_args[aname].default_value is None:
                                changes.append(
                                    {
                                        "type": "REQUIRED_ARG_ADDED",
                                        "breaking": True,
                                        "path": f"{name}.{fname}({aname})",
                                        "message": f"Required argument '{aname}' added to '{name}.{fname}'",
                                    }
                                )
                            else:
                                changes.append(
                                    {
                                        "type": "OPTIONAL_ARG_ADDED",
                                        "breaking": False,
                                        "path": f"{name}.{fname}({aname})",
                                        "message": f"Optional argument '{aname}' added to '{name}.{fname}'",
                                    }
                                )

            for fname in new_fields:
                if fname not in old_fields:
                    changes.append(
                        {
                            "type": "FIELD_ADDED",
                            "breaking": False,
                            "path": f"{name}.{fname}",
                            "message": f"Field '{fname}' was added to type '{name}'",
                        }
                    )

        # Enum types - check values
        if isinstance(old_t, GraphQLEnumType):
            old_values = set(old_t.values.keys())
            new_values = set(new_t.values.keys())
            for v in old_values - new_values:
                changes.append(
                    {
                        "type": "ENUM_VALUE_REMOVED",
                        "breaking": True,
                        "path": f"{name}.{v}",
                        "message": f"Enum value '{v}' removed from '{name}'",
                    }
                )
            for v in new_values - old_values:
                changes.append(
                    {
                        "type": "ENUM_VALUE_ADDED",
                        "breaking": False,
                        "path": f"{name}.{v}",
                        "message": f"Enum value '{v}' added to '{name}'",
                    }
                )

        # Union types - check members
        if isinstance(old_t, GraphQLUnionType):
            old_members = {m.name for m in old_t.types}
            new_members = {m.name for m in new_t.types}
            for m in old_members - new_members:
                changes.append(
                    {
                        "type": "UNION_MEMBER_REMOVED",
                        "breaking": True,
                        "path": f"{name}.{m}",
                        "message": f"Union member '{m}' removed from '{name}'",
                    }
                )
            for m in new_members - old_members:
                changes.append(
                    {
                        "type": "UNION_MEMBER_ADDED",
                        "breaking": False,
                        "path": f"{name}.{m}",
                        "message": f"Union member '{m}' added to '{name}'",
                    }
                )

        # Input types - check fields
        if isinstance(old_t, GraphQLInputObjectType):
            old_fields = old_t.fields
            new_fields = new_t.fields
            for fname in old_fields:
                if fname not in new_fields:
                    changes.append(
                        {
                            "type": "INPUT_FIELD_REMOVED",
                            "breaking": True,
                            "path": f"{name}.{fname}",
                            "message": f"Input field '{fname}' removed from '{name}'",
                        }
                    )
            for fname in new_fields:
                if fname not in old_fields:
                    is_required = "!" in get_type_name(new_fields[fname].type)
                    if is_required and new_fields[fname].default_value is None:
                        changes.append(
                            {
                                "type": "REQUIRED_INPUT_FIELD_ADDED",
                                "breaking": True,
                                "path": f"{name}.{fname}",
                                "message": f"Required input field '{fname}' added to '{name}'",
                            }
                        )
                    else:
                        changes.append(
                            {
                                "type": "OPTIONAL_INPUT_FIELD_ADDED",
                                "breaking": False,
                                "path": f"{name}.{fname}",
                                "message": f"Optional input field '{fname}' added to '{name}'",
                            }
                        )

    return changes


def format_text(changes: list[dict], breaking_only: bool) -> str:
    if breaking_only:
        changes = [c for c in changes if c["breaking"]]

    if not changes:
        return "No changes detected." if not breaking_only else "No breaking changes detected."

    breaking = [c for c in changes if c["breaking"]]
    non_breaking = [c for c in changes if not c["breaking"]]

    lines = []
    if breaking:
        lines.append(f"Breaking changes ({len(breaking)}):")
        for c in breaking:
            lines.append(f"  x {c['message']}")
    if non_breaking and not breaking_only:
        if lines:
            lines.append("")
        lines.append(f"Non-breaking changes ({len(non_breaking)}):")
        for c in non_breaking:
            lines.append(f"  + {c['message']}")

    lines.append("")
    lines.append(f"Summary: {len(breaking)} breaking, {len(non_breaking)} non-breaking")
    return "\n".join(lines)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    old_schema = load_schema(args.old)
    new_schema = load_schema(args.new)
    changes = diff_schemas(old_schema, new_schema)

    if args.format == "json":
        filtered = [c for c in changes if c["breaking"]] if args.breaking_only else changes
        output = json.dumps(
            {
                "changes": filtered,
                "summary": {
                    "breaking": sum(1 for c in changes if c["breaking"]),
                    "non_breaking": sum(1 for c in changes if not c["breaking"]),
                    "total": len(changes),
                },
            },
            indent=2,
        )
    else:
        output = format_text(changes, args.breaking_only)

    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)

    has_breaking = any(c["breaking"] for c in changes)
    sys.exit(3 if has_breaking else 0)


if __name__ == "__main__":
    main()
