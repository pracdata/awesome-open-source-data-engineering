# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "graphql-core>=3.2,<4",
# ]
# ///
"""Validate GraphQL operation files (.graphql) against a schema.

Checks queries, mutations, and subscriptions for syntax errors, unknown fields,
type mismatches, missing required arguments, and undefined variables.
"""

import argparse
import json
import sys
from pathlib import Path

from graphql import build_schema, parse, validate
from graphql.error import GraphQLSyntaxError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="validate_operations",
        description="Validate GraphQL operations against a schema.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/validate_operations.py --schema schema.graphql --operations queries/
  uv run scripts/validate_operations.py --schema schema.graphql --operations query.graphql
  uv run scripts/validate_operations.py --schema schema.graphql --operations queries/ --format json
  uv run scripts/validate_operations.py --schema schema.graphql --operations '{ users { id name } }'

Exit codes:
  0  All operations valid
  1  Client error (bad arguments, file not found)
  2  Schema error
  3  Validation errors found""",
    )
    p.add_argument("--schema", required=True, help="Path to GraphQL schema (.graphql) file")
    p.add_argument(
        "--operations",
        required=True,
        help="Path to operation file, directory of .graphql files, or inline query string",
    )
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    p.add_argument("--output", help="Write output to file instead of stdout")
    return p


def load_schema(path: str):
    try:
        sdl = Path(path).read_text()
    except FileNotFoundError:
        print(f"Error: Schema file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return build_schema(sdl)
    except GraphQLSyntaxError as e:
        print(f"Error: Schema syntax error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: Could not build schema: {e}", file=sys.stderr)
        sys.exit(2)


def collect_operations(source: str) -> list[tuple[str, str]]:
    """Return list of (name, content) tuples."""
    path = Path(source)

    # Inline query string (starts with { or contains query/mutation/subscription keyword)
    if not path.exists():
        stripped = source.strip()
        if stripped.startswith("{") or any(
            stripped.startswith(k) for k in ("query", "mutation", "subscription", "fragment")
        ):
            return [("<inline>", source)]
        print(f"Error: Path not found and does not look like an inline query: {source}", file=sys.stderr)
        sys.exit(1)

    if path.is_file():
        return [(str(path), path.read_text())]

    if path.is_dir():
        ops = []
        for f in sorted(path.rglob("*.graphql")):
            ops.append((str(f), f.read_text()))
        if not ops:
            print(f"Warning: No .graphql files found in {source}", file=sys.stderr)
        return ops

    print(f"Error: {source} is not a file or directory.", file=sys.stderr)
    sys.exit(1)


def validate_operation(schema, name: str, content: str) -> dict:
    try:
        document = parse(content)
    except GraphQLSyntaxError as e:
        return {
            "file": name,
            "valid": False,
            "errors": [{"message": f"Syntax error: {e}", "line": getattr(e, "line", None)}],
        }

    errors = validate(schema, document)
    if errors:
        return {
            "file": name,
            "valid": False,
            "errors": [
                {
                    "message": str(e.message),
                    "locations": [{"line": loc.line, "column": loc.column} for loc in (e.locations or [])],
                }
                for e in errors
            ],
        }

    # Extract operation names
    op_names = []
    for defn in document.definitions:
        if hasattr(defn, "name") and defn.name:
            op_names.append(defn.name.value)
        elif hasattr(defn, "operation"):
            op_names.append(f"<anonymous {defn.operation.value}>")

    return {"file": name, "valid": True, "operations": op_names}


def format_text(results: list[dict]) -> str:
    lines = []
    total = len(results)
    valid = sum(1 for r in results if r["valid"])
    invalid = total - valid

    for r in results:
        if r["valid"]:
            ops = ", ".join(r.get("operations", []))
            lines.append(f"  ok  {r['file']}" + (f" ({ops})" if ops else ""))
        else:
            lines.append(f"  FAIL  {r['file']}")
            for err in r["errors"]:
                loc = ""
                if err.get("locations"):
                    loc = f" (line {err['locations'][0]['line']})"
                elif err.get("line"):
                    loc = f" (line {err['line']})"
                lines.append(f"        {err['message']}{loc}")

    lines.append("")
    lines.append(f"Results: {valid}/{total} valid" + (f", {invalid} with errors" if invalid else ""))
    return "\n".join(lines)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    schema = load_schema(args.schema)
    operations = collect_operations(args.operations)

    results = [validate_operation(schema, name, content) for name, content in operations]

    if args.format == "json":
        output = json.dumps(
            {
                "results": results,
                "summary": {
                    "total": len(results),
                    "valid": sum(1 for r in results if r["valid"]),
                    "invalid": sum(1 for r in results if not r["valid"]),
                },
            },
            indent=2,
        )
    else:
        output = format_text(results)

    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)

    has_errors = any(not r["valid"] for r in results)
    sys.exit(3 if has_errors else 0)


if __name__ == "__main__":
    main()
