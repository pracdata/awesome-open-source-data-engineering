# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Aggregate grading results into benchmark.json.

Reads all grading.json files in a workspace iteration directory and
computes summary statistics per interface, entity, operation, and mode.
Follows the agentskills.io benchmark.json format.
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="benchmark",
        description="Aggregate grading results into benchmark.json.",
        epilog="""Examples:
  uv run scripts/benchmark.py --workspace workspace/iteration-1
  uv run scripts/benchmark.py --workspace workspace/iteration-1 --by-interface
  uv run scripts/benchmark.py --workspace workspace/iteration-1 --by-entity""",
    )
    p.add_argument("--workspace", required=True, help="Workspace iteration directory")
    p.add_argument("--by-interface", action="store_true", help="Break down by interface")
    p.add_argument("--by-entity", action="store_true", help="Break down by entity")
    p.add_argument("--output", help="Write benchmark to file (default: workspace/benchmark.json)")
    return p


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def collect_gradings(workspace: Path) -> list[dict]:
    gradings = []
    for grading_file in workspace.rglob("grading.json"):
        try:
            g = json.loads(grading_file.read_text())
            # Also try to load timing
            timing_file = grading_file.parent / "timing.json"
            if timing_file.exists():
                g["timing"] = json.loads(timing_file.read_text())
            gradings.append(g)
        except (json.JSONDecodeError, KeyError):
            continue
    return gradings


def compute_stats(gradings: list[dict]) -> dict:
    pass_rates = [g["summary"]["pass_rate"] for g in gradings if "summary" in g]
    durations = [g["timing"]["duration_ms"] for g in gradings if "timing" in g]

    return {
        "count": len(gradings),
        "pass_rate": {"mean": round(mean(pass_rates), 4), "stddev": round(stddev(pass_rates), 4)},
        "duration_ms": {"mean": round(mean(durations), 1), "stddev": round(stddev(durations), 1)}
        if durations
        else None,
    }


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    workspace = Path(args.workspace)

    if not workspace.exists():
        print(f"Error: Workspace not found: {workspace}", file=sys.stderr)
        sys.exit(1)

    gradings = collect_gradings(workspace)
    if not gradings:
        print(f"Error: No grading.json files found in {workspace}", file=sys.stderr)
        sys.exit(1)

    # Split by mode
    with_skill = [g for g in gradings if g.get("mode") == "with_skill"]
    without_skill = [g for g in gradings if g.get("mode") == "without_skill"]

    benchmark: dict = {
        "workspace": str(workspace),
        "total_evals": len(gradings),
        "run_summary": {
            "with_skill": compute_stats(with_skill) if with_skill else None,
            "without_skill": compute_stats(without_skill) if without_skill else None,
        },
    }

    # Compute delta
    if with_skill and without_skill:
        ws = compute_stats(with_skill)
        wos = compute_stats(without_skill)
        benchmark["run_summary"]["delta"] = {
            "pass_rate": round(ws["pass_rate"]["mean"] - wos["pass_rate"]["mean"], 4),
            "duration_ms": round(
                (ws["duration_ms"]["mean"] if ws["duration_ms"] else 0)
                - (wos["duration_ms"]["mean"] if wos["duration_ms"] else 0),
                1,
            ),
        }

    # Breakdowns
    if args.by_interface:
        by_interface = defaultdict(list)
        for g in gradings:
            eval_id = g.get("eval_id", "")
            parts = eval_id.split("-")
            if parts:
                by_interface[parts[0]].append(g)
        benchmark["by_interface"] = {k: compute_stats(v) for k, v in sorted(by_interface.items())}

    if args.by_entity:
        by_entity = defaultdict(list)
        for g in gradings:
            eval_id = g.get("eval_id", "")
            parts = eval_id.split("-")
            if len(parts) >= 2:
                by_entity[parts[1]].append(g)
        benchmark["by_entity"] = {k: compute_stats(v) for k, v in sorted(by_entity.items())}

    output = json.dumps(benchmark, indent=2)
    out_path = args.output or str(workspace / "benchmark.json")
    Path(out_path).write_text(output + "\n")
    print(f"Benchmark written to {out_path}", file=sys.stderr)
    print(output)


if __name__ == "__main__":
    main()
