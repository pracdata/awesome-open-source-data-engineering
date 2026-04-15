# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Run a single eval test case and capture outputs.

Executes the CRUD operation specified by the eval ID, captures the output,
timing data, and stores results in the workspace directory following the
agentskills.io eval structure.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_eval",
        description="Run a single eval test case and capture outputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  uv run scripts/run_eval.py --eval-id cli-sessions-create --workspace workspace/iteration-1
  uv run scripts/run_eval.py --eval-id api-agents-read --workspace workspace/iteration-1 --mode without_skill
  uv run scripts/run_eval.py --evals-file evals/evals.json --eval-id cli-sessions-create --workspace workspace/iteration-1
  uv run scripts/run_eval.py --eval-id sdk-agents-list --workspace workspace/iteration-1 --dry-run""",
    )
    p.add_argument("--eval-id", required=True, help="Eval test case ID (e.g. cli-sessions-create)")
    p.add_argument("--evals-file", default="evals/evals.json", help="Path to evals.json")
    p.add_argument("--workspace", required=True, help="Workspace directory for this iteration")
    p.add_argument(
        "--mode", choices=["with_skill", "without_skill"], default="with_skill", help="Run mode (default: with_skill)"
    )
    p.add_argument("--dry-run", action="store_true", help="Show what would be executed")
    return p


def find_eval(evals_file: str, eval_id: str) -> dict | None:
    try:
        data = json.loads(Path(evals_file).read_text())
        for e in data.get("evals", []):
            if e["id"] == eval_id:
                return e
    except FileNotFoundError:
        print(f"Error: Evals file not found: {evals_file}", file=sys.stderr)
        print("Run: uv run scripts/generate_eval_matrix.py --output evals/evals.json", file=sys.stderr)
        sys.exit(1)
    return None


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    eval_case = find_eval(args.evals_file, args.eval_id)
    if not eval_case:
        print(f"Error: Eval '{args.eval_id}' not found in {args.evals_file}", file=sys.stderr)
        sys.exit(1)

    # Setup output directory
    eval_dir = Path(args.workspace) / f"eval-{args.eval_id}" / args.mode
    outputs_dir = eval_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    interface = eval_case["interface"]
    entity = eval_case["entity"]
    operation = eval_case["operation"]
    test_data = eval_case.get("test_data", {})

    # Build the crud_operations command
    cmd = [
        sys.executable,
        "-m",
        "scripts.crud_operations" if False else str(Path(__file__).parent / "crud_operations.py"),
        "--interface",
        interface,
        "--entity",
        entity,
        "--operation",
        operation,
    ]

    if operation in ("create", "update") and test_data:
        cmd.extend(["--params", json.dumps(test_data)])

    if args.dry_run:
        cmd.append("--dry-run")

    # Execute and time it
    print(f"Running: {args.eval_id} [{interface}/{entity}/{operation}] mode={args.mode}", file=sys.stderr)
    start = time.monotonic()

    try:
        result = subprocess.run(
            ["uv", "run"] + cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Save output
        output_file = outputs_dir / "result.json"
        output_file.write_text(result.stdout or "{}")

        if result.stderr:
            (outputs_dir / "stderr.txt").write_text(result.stderr)

        # Save timing
        timing = {
            "duration_ms": elapsed_ms,
            "exit_code": result.returncode,
            "eval_id": args.eval_id,
            "mode": args.mode,
            "interface": interface,
            "entity": entity,
            "operation": operation,
        }
        (eval_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")

        # Save the eval metadata for grading
        (eval_dir / "eval_case.json").write_text(json.dumps(eval_case, indent=2) + "\n")

        print(
            json.dumps(
                {
                    "status": "completed",
                    "eval_id": args.eval_id,
                    "mode": args.mode,
                    "duration_ms": elapsed_ms,
                    "exit_code": result.returncode,
                    "output_dir": str(eval_dir),
                },
                indent=2,
            )
        )

    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        timing = {"duration_ms": elapsed_ms, "exit_code": -1, "error": "timeout"}
        (eval_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")
        print(json.dumps({"status": "timeout", "eval_id": args.eval_id, "duration_ms": elapsed_ms}, indent=2))
        sys.exit(2)


if __name__ == "__main__":
    main()
