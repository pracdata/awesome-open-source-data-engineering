# Contributing to agentwarehouses

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Install dependencies

```bash
cd claude_code_models
uv sync --dev
```

Or with pip:

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
# Full suite with coverage (parallel across available CPUs)
uv run pytest --cov=claude_code_models --cov-report=term-missing --cov-branch -n auto

# Single marker (e.g. hooks, mcp, semver, tools, cli, plugins, channels, agents, skills, sessions)
uv run pytest -m hooks -v

# Fast run excluding slow tests
uv run pytest -m "not slow" -n auto

# Specific test file
uv run pytest tests/test_version.py -v
```

Coverage must stay at or above **90%** (configured in `pyproject.toml`). Current coverage: **100%**.

### Lint and type check

```bash
uv run ruff check .
uv run mypy claude_code_models/
```

## Commit Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/) with [release-please](https://github.com/googleapis/release-please) for automated versioning.

### Commit message format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use | Version bump |
|---|---|---|
| `feat` | New feature or model | MINOR |
| `fix` | Bug fix | PATCH |
| `deps` | Upstream dependency update (anthropic SDK, MCP SDK) | MINOR |
| `docs` | Documentation only | none |
| `test` | Adding or updating tests | none |
| `refactor` | Code change that neither fixes nor adds | none |
| `chore` | Maintenance, CI, tooling | none |

### Breaking changes

Append `!` after the type/scope, or add a `BREAKING CHANGE:` footer:

```
feat(hooks)!: rename SessionStart matcher values

BREAKING CHANGE: "startup" is now "start", "resume" is now "continue"
```

Breaking changes bump the MAJOR version (once past 1.0.0).

### Upstream dependency bumps

When `anthropic` SDK or `mcp` SDK publishes a new version:

```
deps(anthropic-sdk): bump to 0.53.0
deps(mcp-sdk): bump to 1.10.0
```

These trigger a MINOR version bump via release-please.

## Adding or Updating Models

### Where models live

```
claude_code_models/claude_code_models/models/
├── version.py      # SemVer, ConventionalCommit, UpstreamDependency
├── tools.py        # ToolName enum, ToolDefinition, PermissionMode
├── cli.py          # CLICommand, CLIFlag, EnvironmentVariable
├── hooks.py        # HookEventName, handlers, matchers, config
├── plugins.py      # PluginManifest, LSPServerConfig, marketplace
├── channels.py     # ChannelNotification, PermissionRequest/Verdict
├── checkpoints.py  # Checkpoint, RewindAction
├── sessions.py     # Session, SessionEvent
├── skills.py       # SkillFrontmatter, SlashCommand
├── mcp.py          # MCPServerConfig, MCPToolDefinition
└── agents.py       # SubAgentFrontmatter, AgentTeam
```

### Pydantic patterns (2.0, prepared for 3.0)

Follow these patterns in all models:

```python
from __future__ import annotations          # Required: deferred eval for 3.0

from pydantic import BaseModel, ConfigDict, Field

class MyModel(BaseModel):
    model_config = ConfigDict(              # Not inner Config class
        str_strip_whitespace=True,
        populate_by_name=True,              # Allow both alias and field name
    )

    my_field: str | None = None             # PEP 604 unions, not Optional
    camel_field: str = Field(alias="camelField")  # JSON alias
```

Key rules:

- Use `from __future__ import annotations` in every module
- Use `ConfigDict(...)` on class body, never inner `Config` class
- Use `str | None` not `Optional[str]`
- Use `StrEnum` not `str, Enum`
- Use `Field(alias="...")` with `populate_by_name=True` for camelCase JSON
- Use `field_validator` / `model_validator` decorators, not `validator`
- Add return type annotations to every function/method
- Export public names via `__all__`

### Adding a new model

1. Create or edit the appropriate module in `models/`
2. Add to `__all__` in the module
3. Add import in `claude_code_models/__init__.py`
4. Write tests in `tests/test_<module>.py` with:
   - Construction tests (minimal and full)
   - Validation error tests (marked `@pytest.mark.validation`)
   - JSON roundtrip tests (marked `@pytest.mark.serialization`)
   - Frozen/immutable tests where applicable
5. Run tests and verify coverage stays above 90%

### Adding a new tool to ToolName enum

When Claude Code adds a new built-in tool:

1. Add the entry to `ToolName` in `models/tools.py`
2. Update the count assertion in `tests/test_tools.py::TestToolName::test_all_tools_enumerated`
3. Commit: `feat(tools): add NewToolName tool`

### Adding a new hook event

When Claude Code adds a new lifecycle event:

1. Add the entry to `HookEventName` in `models/hooks.py`
2. Update the count assertion in `tests/test_hooks.py::TestHookEventName::test_count`
3. Add relevant tests for the event's input/output shapes
4. Commit: `feat(hooks): add NewEvent lifecycle event`

## Skills Development

### graphql-tools skill

The `graphql-tools` skill lives at `.claude/skills/graphql-tools/`. Scripts are self-contained Python with PEP 723 inline dependencies:

```bash
uv run .claude/skills/graphql-tools/scripts/<script>.py --help
```

### crud-eval skill

The `crud-eval` skill at `.claude/skills/crud-eval/` follows the [agentskills.io evaluation spec](https://agentskills.io/skill-creation/evaluating-skills):

```bash
# Generate eval matrix
uv run .claude/skills/crud-eval/scripts/generate_eval_matrix.py --output evals/evals.json

# Run an eval
uv run .claude/skills/crud-eval/scripts/run_eval.py --eval-id cli-sessions-create --workspace workspace/iteration-1
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make changes following the patterns above
3. Run the full test suite with coverage
4. Commit using conventional commit messages
5. Push and create a PR

All PRs should:
- Pass tests with >= 90% coverage
- Follow conventional commit messages
- Have clear return types on all functions
- Include tests for new code

## Session History

Development session transcripts are stored in `.claude/sessions/` for reference and reproducibility.
