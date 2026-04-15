Never use ANTHROPIC_API_KEY in GitHub Actions workflows, scripts, or configuration.
Always use CLAUDE_CODE_OAUTH_TOKEN for authenticating Claude Code CLI and claude-code-action.
This applies to all workflows under .github/workflows/ and any CI/CD configuration.
