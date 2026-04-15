---
name: research
description: Structured research workflow with scratchpad, web fetching, and blog-style findings
disable-model-invocation: false
---
# Research

Structured research skill using the `sessions/` template system. Creates a
session directory with auto-populated device/surface metadata, a scratchpad
for incremental findings, page archives for web-fetched content, and a
blog-post-style findings document.

## When to use

- Investigating external documentation (transformer-circuits.pub, Anthropic docs)
- Auditing GitHub repositories for patterns, tools, or packages
- Any multi-page research that needs organized output
- When you need a persistent scratchpad across tool calls

## Workflow

### 1. Initialize session

```python
from sessions.session_template import SessionTemplate

session = SessionTemplate.create("topic-name")
# Creates: sessions/session_<id>/
#   metadata.json    — auto-populated device, surface, model
#   scratchpad.md    — timestamped research notes
#   pages/           — archived web pages
```

### 2. Fetch and archive pages

Use WebFetch to retrieve content, then archive it:

```python
session.save_page(
    url="https://transformer-circuits.pub/",
    title="Transformer Circuits Thread",
    content=fetched_markdown,
)
```

### 3. Take scratchpad notes

Append findings as you go — each entry is timestamped:

```python
session.append_scratchpad(
    "Key finding: emotion vectors causally influence agent behavior.",
    heading="Interpretability vectors",
)
```

### 4. Write findings

Produce a blog-post-style summary with YAML frontmatter:

```python
session.write_findings(
    title="Anthropic Interpretability Research Summary",
    summary="Analysis of mechanistic interpretability papers.",
    sections=[
        {"heading": "Background", "body": "Anthropic's interpretability team..."},
        {"heading": "Key Results", "body": "Emotion-concept vectors found..."},
        {"heading": "Implications", "body": "For agent calibration..."},
    ],
    tags=["interpretability", "safety", "anthropic"],
)
```

## Output structure

```
sessions/session_{id}/
  metadata.json              — device, surface, model (auto-populated)
  scratchpad.md              — timestamped research notes
  pages/
    001_page-title.md        — archived web pages with frontmatter
    002_another-page.md
  findings.md                — blog-post-style write-up
```

## Surface lookup table

The session auto-detects the active surface from environment variables:

| Env Var | Value | Surface |
|---------|-------|---------|
| GITHUB_ACTIONS | true | GitHubAction |
| GITLAB_CI | true | GitLabCI |
| VSCODE_PID | any | VSCode |
| JETBRAINS_IDE | any | JetBrains |
| CLAUDE_DESKTOP | true | Desktop |
| CLAUDE_CODE_SURFACE | web | Web |
| CLAUDE_CODE_SURFACE | mobile | Mobile |
| CLAUDE_CODE_SURFACE | sdk | SDK |
| CLAUDE_CODE_SURFACE | slack | Slack |
| *(default)* | | CLI |

## Conventions

- Session directories are gitignored (`sessions/session_*/`)
- Template code is committed (`sessions/*.py`, `sessions/__init__.py`)
- Scratchpad is append-only — never delete entries, only add
- Pages are numbered sequentially (001_, 002_, ...)
- Findings use YAML frontmatter for metadata
- All timestamps are UTC
