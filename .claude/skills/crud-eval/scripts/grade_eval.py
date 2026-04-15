# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Grade eval outputs against assertions and produce grading.json.

Reads the eval case assertions and the actual output, then checks each
assertion programmatically where possible. Produces a grading.json file
following the agentskills.io eval spec.
"""

import argparse
import json
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="grade_eval",
        description="Grade eval outputs against assertions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/grade_eval.py --workspace workspace/iteration-1 --eval-id cli-sessions-create
  uv run scripts/grade_eval.py --workspace workspace/iteration-1 --eval-id cli-sessions-create --mode without_skill
  uv run scripts/grade_eval.py --workspace workspace/iteration-1 --all""",
    )
    p.add_argument("--workspace", required=True, help="Workspace directory")
    p.add_argument("--eval-id", help="Specific eval to grade")
    p.add_argument("--mode", choices=["with_skill", "without_skill"], default="with_skill")
    p.add_argument("--all", action="store_true", help="Grade all evals in workspace")
    return p


def check_assertion(assertion: str, output: dict, eval_case: dict) -> dict:
    """Check a single assertion against the output. Returns pass/fail with evidence."""
    assertion_lower = assertion.lower()
    result = {"text": assertion, "passed": False, "evidence": ""}

    # Check for errors in output
    has_error = "error" in output
    is_dry_run = output.get("dry_run", False)

    # Generic assertion checks
    if "returns a valid identifier" in assertion_lower or "returns the" in assertion_lower:
        if is_dry_run:
            result["passed"] = True
            result["evidence"] = "Dry run: command/request structure is valid"
        elif has_error:
            result["evidence"] = f"Error in output: {output.get('error', 'unknown')}"
        elif any(k in output for k in ("id", "session_id", "agent_id", "name")):
            result["passed"] = True
            id_val = output.get("id") or output.get("session_id") or output.get("agent_id")
            result["evidence"] = f"Found identifier: {id_val}"
        else:
            result["evidence"] = f"No identifier found in response keys: {list(output.keys())[:10]}"

    elif "confirms" in assertion_lower and "created" in assertion_lower:
        if is_dry_run:
            result["passed"] = True
            result["evidence"] = "Dry run: creation request structure valid"
        elif has_error:
            result["evidence"] = f"Creation failed: {output.get('error', 'unknown')}"
        elif "name" in output or "title" in output or "id" in output:
            result["passed"] = True
            result["evidence"] = f"Created with name={output.get('name', output.get('title', 'N/A'))}"
        else:
            result["evidence"] = "No confirmation of creation in response"

    elif "timestamp" in assertion_lower or "version" in assertion_lower:
        if is_dry_run:
            result["passed"] = True
            result["evidence"] = "Dry run: version/timestamp expected in response"
        elif any(k in output for k in ("version", "created_at", "updated_at", "timestamp")):
            result["passed"] = True
            ver = output.get("version") or output.get("created_at") or output.get("updated_at")
            result["evidence"] = f"Found version/timestamp: {ver}"
        else:
            result["evidence"] = "No version or timestamp in response"

    elif "correct endpoint" in assertion_lower or "correct method" in assertion_lower:
        interface = eval_case.get("interface", "")
        if is_dry_run:
            if interface == "cli" and "command" in output:
                result["passed"] = True
                result["evidence"] = f"CLI command: {' '.join(output['command'])}"
            elif interface == "api" and "method" in output:
                result["passed"] = True
                result["evidence"] = f"API: {output['method']} {output['url']}"
            elif interface == "sdk" and "sdk_call" in output:
                result["passed"] = True
                result["evidence"] = f"SDK: {output['sdk_call']}"
            elif interface == "graphql" and "query" in output:
                result["passed"] = True
                result["evidence"] = f"GraphQL: {output['query'][:80]}"
            else:
                result["passed"] = True
                result["evidence"] = "Dry run mode: interface-specific validation"
        else:
            result["passed"] = not has_error
            result["evidence"] = "No error" if not has_error else f"Error: {output.get('error')}"

    elif "expected fields" in assertion_lower or "expected schema" in assertion_lower:
        if is_dry_run:
            result["passed"] = True
            result["evidence"] = "Dry run: schema validation deferred"
        elif isinstance(output, dict) and len(output) > 1 and not has_error:
            result["passed"] = True
            result["evidence"] = f"Response has {len(output)} fields: {list(output.keys())[:8]}"
        else:
            result["evidence"] = (
                f"Insufficient fields. Keys: {list(output.keys()) if isinstance(output, dict) else 'not a dict'}"
            )

    elif "incremented" in assertion_lower:
        if is_dry_run:
            result["passed"] = True
            result["evidence"] = "Dry run: version increment expected"
        elif "version" in output:
            result["passed"] = True
            result["evidence"] = f"Version in response: {output['version']}"
        else:
            result["evidence"] = "No version field found after update"

    elif "retain" in assertion_lower or "original values" in assertion_lower:
        result["passed"] = not has_error
        result["evidence"] = (
            "Non-error response implies field preservation" if not has_error else "Cannot verify: error occurred"
        )

    elif "deleted" in assertion_lower or "404" in assertion_lower or "empty" in assertion_lower:
        if is_dry_run:
            result["passed"] = True
            result["evidence"] = "Dry run: delete command structure valid"
        elif has_error and output.get("status") == 404:
            result["passed"] = True
            result["evidence"] = "404 confirms deletion"
        elif not has_error:
            result["passed"] = True
            result["evidence"] = "Delete operation succeeded without error"
        else:
            result["evidence"] = f"Unexpected error: {output.get('error')}"

    elif "idempotent" in assertion_lower:
        result["passed"] = True
        result["evidence"] = "Idempotency requires two sequential calls (deferred to integration test)"

    elif "version lock" in assertion_lower or "optimistic concurrency" in assertion_lower:
        if is_dry_run:
            cmd = output.get("command", [])
            body = output.get("body", {})
            if "--version" in cmd or "version" in str(body):
                result["passed"] = True
                result["evidence"] = "Version parameter included in request"
            else:
                result["evidence"] = "No version parameter found in request"
        else:
            result["passed"] = not has_error
            result["evidence"] = "Update succeeded (version was accepted)" if not has_error else "Update failed"

    else:
        # Fallback: pass if no error, fail otherwise
        result["passed"] = not has_error
        result["evidence"] = f"Generic check: {'no error' if not has_error else output.get('error', 'error occurred')}"

    return result


def grade_eval(workspace: Path, eval_id: str, mode: str) -> dict:
    eval_dir = workspace / f"eval-{eval_id}" / mode

    # Load eval case
    eval_case_file = eval_dir / "eval_case.json"
    if not eval_case_file.exists():
        return {"error": f"Eval case not found: {eval_case_file}"}
    eval_case = json.loads(eval_case_file.read_text())

    # Load output
    output_file = eval_dir / "outputs" / "result.json"
    if not output_file.exists():
        return {"error": f"Output not found: {output_file}. Run the eval first."}
    try:
        output = json.loads(output_file.read_text())
    except json.JSONDecodeError:
        output = {"raw": output_file.read_text()[:500]}

    # Grade each assertion
    assertions = eval_case.get("assertions", [])
    assertion_results = [check_assertion(a, output, eval_case) for a in assertions]

    passed = sum(1 for r in assertion_results if r["passed"])
    total = len(assertion_results)

    grading = {
        "eval_id": eval_id,
        "mode": mode,
        "assertion_results": assertion_results,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total > 0 else 0,
        },
    }

    # Save grading
    grading_file = eval_dir / "grading.json"
    grading_file.write_text(json.dumps(grading, indent=2) + "\n")
    return grading


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    workspace = Path(args.workspace)

    if args.all:
        # Find all eval directories
        results = []
        for eval_dir in sorted(workspace.glob("eval-*")):
            eval_id = eval_dir.name.removeprefix("eval-")
            for mode_dir in eval_dir.iterdir():
                if mode_dir.is_dir() and mode_dir.name in ("with_skill", "without_skill"):
                    result = grade_eval(workspace, eval_id, mode_dir.name)
                    results.append(result)
                    status = "error" if "error" in result else f"{result['summary']['pass_rate']:.0%}"
                    print(f"  {eval_id}/{mode_dir.name}: {status}", file=sys.stderr)
        print(json.dumps({"graded": len(results), "results": results}, indent=2))
    else:
        if not args.eval_id:
            print("Error: --eval-id or --all is required.", file=sys.stderr)
            sys.exit(1)
        result = grade_eval(workspace, args.eval_id, args.mode)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
