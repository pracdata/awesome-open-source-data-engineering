#!/usr/bin/env python3
"""Fetch all repositories for GitHub organizations using the GraphQL API.

Uses the @octokit/graphql npm package (installed in this project) via a
Node.js subprocess to paginate through all repos with a single GraphQL
query per page. Outputs JSONL to stdout or a file.

Usage:
    python scripts/github_org_repos_graphql.py \
        --orgs anthropics modelcontextprotocol neondatabase safety-research Netflix Netflix-Skunkworks \
        --output output/github_org_manifests.jsonl
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# GraphQL query with cursor-based pagination
GRAPHQL_QUERY = """
query($org: String!, $cursor: String) {
  organization(login: $org) {
    repositories(first: 100, after: $cursor, orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        nameWithOwner
        description
        primaryLanguage { name }
        stargazerCount
        forkCount
        repositoryTopics(first: 10) { nodes { topic { name } } }
        updatedAt
        url
        isArchived
        defaultBranchRef { name }
      }
    }
  }
}
"""

# Node.js script that executes the GraphQL query via @octokit/graphql
NODE_SCRIPT = """
import { graphql } from "@octokit/graphql";

const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";
const org = process.argv[2];
const cursor = process.argv[3] || null;
const query = JSON.parse(process.argv[4]);

const headers = {};
if (token) headers.authorization = `token ${token}`;

try {
  const result = await graphql({
    query,
    org,
    cursor: cursor === "null" ? null : cursor,
    headers,
  });
  console.log(JSON.stringify(result));
} catch (e) {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
}
"""


def fetch_org_repos(org: str) -> list[dict]:
    """Fetch all repos for an org using GraphQL pagination."""
    all_repos: list[dict] = []
    cursor = "null"
    page = 0

    while True:
        page += 1
        result = subprocess.run(
            ["node", "--input-type=module", "-e", NODE_SCRIPT, org, cursor, json.dumps(GRAPHQL_QUERY)],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
        )

        if result.returncode != 0:
            print(f"  ERROR page {page}: {result.stderr.strip()}", file=sys.stderr)
            break

        data = json.loads(result.stdout)
        if "error" in data:
            print(f"  ERROR page {page}: {data['error']}", file=sys.stderr)
            break

        org_data = data.get("organization", {})
        repos_data = org_data.get("repositories", {})
        nodes = repos_data.get("nodes", [])
        total = repos_data.get("totalCount", "?")
        page_info = repos_data.get("pageInfo", {})

        for node in nodes:
            repo = {
                "org": org,
                "name": node["name"],
                "full_name": node["nameWithOwner"],
                "description": node.get("description"),
                "language": node["primaryLanguage"]["name"] if node.get("primaryLanguage") else None,
                "stars": node.get("stargazerCount", 0),
                "forks": node.get("forkCount", 0),
                "topics": [t["topic"]["name"] for t in node.get("repositoryTopics", {}).get("nodes", [])],
                "updated_at": node.get("updatedAt"),
                "url": node.get("url"),
                "archived": node.get("isArchived", False),
                "default_branch": node["defaultBranchRef"]["name"] if node.get("defaultBranchRef") else "main",
            }
            all_repos.append(repo)

        print(f"  {org} page {page}: +{len(nodes)} repos (total={total}, cumulative={len(all_repos)})", file=sys.stderr)

        if not page_info.get("hasNextPage"):
            break
        cursor = page_info["endCursor"]

    return all_repos


def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub org repos via GraphQL")
    parser.add_argument("--orgs", nargs="+", required=True, help="GitHub organization names")
    parser.add_argument("--output", type=str, default="-", help="Output JSONL file (default: stdout)")
    args = parser.parse_args()

    try:
        import orjson

        serialize = lambda obj: orjson.dumps(obj)  # noqa: E731
    except ImportError:
        serialize = lambda obj: json.dumps(obj, ensure_ascii=False).encode()  # noqa: E731

    all_repos: list[dict] = []
    for org in args.orgs:
        print(f"Fetching {org}...", file=sys.stderr)
        repos = fetch_org_repos(org)
        all_repos.extend(repos)
        print(f"  {org}: {len(repos)} repos total", file=sys.stderr)

    # Sort by org, then stars descending
    all_repos.sort(key=lambda r: (r["org"], -r["stars"]))

    if args.output == "-":
        for repo in all_repos:
            sys.stdout.buffer.write(serialize(repo) + b"\n")
    else:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "wb") as f:
            for repo in all_repos:
                f.write(serialize(repo) + b"\n")
        print(f"\nWrote {len(all_repos)} repos to {args.output}", file=sys.stderr)

    # Summary
    from collections import Counter

    orgs = Counter(r["org"] for r in all_repos)
    print(f"\nTotal: {len(all_repos)} repos across {len(orgs)} orgs", file=sys.stderr)
    for org, count in orgs.most_common():
        print(f"  {org:30s} {count:>4d} repos", file=sys.stderr)


if __name__ == "__main__":
    main()
