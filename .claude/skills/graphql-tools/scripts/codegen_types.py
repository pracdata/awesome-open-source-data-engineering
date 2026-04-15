# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "graphql-core>=3.2,<4",
# ]
# ///
"""Generate TypeScript or Python types from a GraphQL schema.

Reads a GraphQL schema (SDL file) and generates typed code for object types,
input types, enums, and unions. Similar to GraphQL Code Generator but as a
single self-contained script.
"""

import argparse
import sys
from pathlib import Path

from graphql import build_schema
from graphql.error import GraphQLSyntaxError
from graphql.type import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLUnionType,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="codegen_types",
        description="Generate TypeScript or Python types from a GraphQL schema.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/codegen_types.py --schema schema.graphql --lang typescript
  uv run scripts/codegen_types.py --schema schema.graphql --lang python --output types.py
  uv run scripts/codegen_types.py --schema schema.graphql --lang typescript --output types.ts --no-builtins

Exit codes:
  0  Success
  1  Client error (bad arguments, file not found)
  2  Schema error""",
    )
    p.add_argument("--schema", required=True, help="Path to GraphQL schema (.graphql) file")
    p.add_argument(
        "--lang", required=True, choices=["typescript", "python"], help="Target language for generated types"
    )
    p.add_argument("--output", help="Write output to file instead of stdout")
    p.add_argument("--no-builtins", action="store_true", help="Exclude built-in scalar types from output")
    return p


BUILTIN_TYPE_NAMES = {
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

SCALAR_MAP_TS = {
    "String": "string",
    "Int": "number",
    "Float": "number",
    "Boolean": "boolean",
    "ID": "string",
    "DateTime": "string",
    "Date": "string",
    "JSON": "Record<string, unknown>",
    "BigInt": "string",
}

SCALAR_MAP_PY = {
    "String": "str",
    "Int": "int",
    "Float": "float",
    "Boolean": "bool",
    "ID": "str",
    "DateTime": "str",
    "Date": "str",
    "JSON": "dict[str, Any]",
    "BigInt": "str",
}


def resolve_type_ts(gql_type, nullable: bool = True) -> str:
    name = gql_type.__class__.__name__
    if "NonNull" in name:
        return resolve_type_ts(gql_type.of_type, nullable=False)
    if "List" in name:
        inner = resolve_type_ts(gql_type.of_type, nullable=True)
        base = f"Array<{inner}>"
        return f"{base} | null" if nullable else base
    type_name = gql_type.name
    ts_type = SCALAR_MAP_TS.get(type_name, type_name)
    return f"{ts_type} | null" if nullable else ts_type


def resolve_type_py(gql_type, nullable: bool = True) -> str:
    name = gql_type.__class__.__name__
    if "NonNull" in name:
        return resolve_type_py(gql_type.of_type, nullable=False)
    if "List" in name:
        inner = resolve_type_py(gql_type.of_type, nullable=True)
        base = f"list[{inner}]"
        return f"{base} | None" if nullable else base
    type_name = gql_type.name
    py_type = SCALAR_MAP_PY.get(type_name, type_name)
    return f"{py_type} | None" if nullable else py_type


def generate_typescript(schema, skip_builtins: bool) -> str:
    lines: list[str] = [
        "// Auto-generated TypeScript types from GraphQL schema",
        "// Do not edit manually",
        "",
    ]

    type_map = schema.type_map

    # Custom scalars
    custom_scalars = [
        n for n, t in type_map.items() if isinstance(t, GraphQLScalarType) and n not in BUILTIN_TYPE_NAMES
    ]
    if custom_scalars:
        for name in sorted(custom_scalars):
            ts_type = SCALAR_MAP_TS.get(name, "unknown")
            lines.append(f"export type {name} = {ts_type};")
        lines.append("")

    # Enums
    for name, t in sorted(type_map.items()):
        if not isinstance(t, GraphQLEnumType) or name in BUILTIN_TYPE_NAMES:
            continue
        lines.append(f"export enum {name} {{")
        for val_name in t.values:
            lines.append(f'  {val_name} = "{val_name}",')
        lines.append("}")
        lines.append("")

    # Object types and interfaces
    for name, t in sorted(type_map.items()):
        if not isinstance(t, (GraphQLObjectType, GraphQLInterfaceType)):
            continue
        if name in BUILTIN_TYPE_NAMES or (skip_builtins and name in ("Query", "Mutation", "Subscription")):
            continue

        keyword = "interface"
        interfaces = ""
        if isinstance(t, GraphQLObjectType) and t.interfaces:
            iface_names = [i.name for i in t.interfaces]
            interfaces = f" extends {', '.join(iface_names)}"

        lines.append(f"export {keyword} {name}{interfaces} {{")
        for fname, field in t.fields.items():
            ts_type = resolve_type_ts(field.type)
            lines.append(f"  {fname}: {ts_type};")
        lines.append("}")
        lines.append("")

    # Input types
    for name, t in sorted(type_map.items()):
        if not isinstance(t, GraphQLInputObjectType) or name in BUILTIN_TYPE_NAMES:
            continue
        lines.append(f"export interface {name} {{")
        for fname, field in t.fields.items():
            ts_type = resolve_type_ts(field.type)
            lines.append(f"  {fname}: {ts_type};")
        lines.append("}")
        lines.append("")

    # Union types
    for name, t in sorted(type_map.items()):
        if not isinstance(t, GraphQLUnionType) or name in BUILTIN_TYPE_NAMES:
            continue
        members = " | ".join(m.name for m in t.types)
        lines.append(f"export type {name} = {members};")
        lines.append("")

    return "\n".join(lines)


def generate_python(schema, skip_builtins: bool) -> str:
    lines: list[str] = [
        '"""Auto-generated Python types from GraphQL schema."""',
        "# Do not edit manually",
        "",
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "from enum import Enum",
        "from typing import Any",
        "",
    ]

    type_map = schema.type_map

    # Custom scalars
    custom_scalars = [
        n for n, t in type_map.items() if isinstance(t, GraphQLScalarType) and n not in BUILTIN_TYPE_NAMES
    ]
    if custom_scalars:
        for name in sorted(custom_scalars):
            py_type = SCALAR_MAP_PY.get(name, "Any")
            lines.append(f"{name} = {py_type}")
        lines.append("")

    # Enums
    for name, t in sorted(type_map.items()):
        if not isinstance(t, GraphQLEnumType) or name in BUILTIN_TYPE_NAMES:
            continue
        lines.append(f"class {name}(Enum):")
        for val_name in t.values:
            lines.append(f'    {val_name} = "{val_name}"')
        lines.append("")
        lines.append("")

    # Object types and interfaces
    for name, t in sorted(type_map.items()):
        if not isinstance(t, (GraphQLObjectType, GraphQLInterfaceType)):
            continue
        if name in BUILTIN_TYPE_NAMES or (skip_builtins and name in ("Query", "Mutation", "Subscription")):
            continue

        lines.append("@dataclass")
        lines.append(f"class {name}:")
        if not t.fields:
            lines.append("    pass")
        else:
            for fname, field in t.fields.items():
                py_type = resolve_type_py(field.type)
                lines.append(f"    {fname}: {py_type}")
        lines.append("")
        lines.append("")

    # Input types
    for name, t in sorted(type_map.items()):
        if not isinstance(t, GraphQLInputObjectType) or name in BUILTIN_TYPE_NAMES:
            continue
        lines.append("@dataclass")
        lines.append(f"class {name}:")
        if not t.fields:
            lines.append("    pass")
        else:
            for fname, field in t.fields.items():
                py_type = resolve_type_py(field.type)
                lines.append(f"    {fname}: {py_type}")
        lines.append("")
        lines.append("")

    # Union types
    for name, t in sorted(type_map.items()):
        if not isinstance(t, GraphQLUnionType) or name in BUILTIN_TYPE_NAMES:
            continue
        members = " | ".join(m.name for m in t.types)
        lines.append(f"{name} = {members}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        sdl = Path(args.schema).read_text()
    except FileNotFoundError:
        print(f"Error: Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    try:
        schema = build_schema(sdl)
    except GraphQLSyntaxError as e:
        print(f"Error: Syntax error in schema: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: Could not build schema: {e}", file=sys.stderr)
        sys.exit(2)

    if args.lang == "typescript":
        output = generate_typescript(schema, args.no_builtins)
    else:
        output = generate_python(schema, args.no_builtins)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Types written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
