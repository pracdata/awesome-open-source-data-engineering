/**
 * Fetch all repositories for a GitHub organization using GraphQL pagination.
 *
 * Usage: node scripts/github_graphql_fetch.mjs <org> [cursor]
 * Output: JSON to stdout with { repos: [...], pageInfo: {...}, totalCount: N }
 */

import { graphql } from "@octokit/graphql";

const QUERY = `
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
}`;

const org = process.argv[2];
const cursor = process.argv[3] === "null" || !process.argv[3] ? null : process.argv[3];

if (!org) {
  console.error("Usage: node github_graphql_fetch.mjs <org> [cursor]");
  process.exit(1);
}

const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";
const headers = {};
if (token) headers.authorization = `token ${token}`;

try {
  const result = await graphql({
    query: QUERY,
    org,
    cursor,
    headers,
  });
  const repoData = result.organization.repositories;
  console.log(JSON.stringify({
    totalCount: repoData.totalCount,
    pageInfo: repoData.pageInfo,
    repos: repoData.nodes,
  }));
} catch (e) {
  console.error(JSON.stringify({ error: e.message, status: e.status }));
  process.exit(1);
}
