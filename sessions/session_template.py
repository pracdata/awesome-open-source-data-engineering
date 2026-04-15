"""Auto-populating session template.

Creates a ``sessions/session_{id}/`` directory tree with:

- ``metadata.json``   — device, surface, model, timestamps (auto-populated)
- ``scratchpad.md``    — freeform research notes (append-only)
- ``pages/``           — one file per web-fetched page
- ``findings.md``      — blog-post-style write-up (uses BLOG_TEMPLATE)

Usage::

    from sessions.session_template import SessionTemplate

    tpl = SessionTemplate.create("my-research-topic")
    tpl.append_scratchpad("Found interesting pattern in codebase...")
    tpl.save_page("https://example.com/doc", title="Example", content="...")
    tpl.write_findings(title="Research Summary", sections=[...])
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sessions.surface_lookup import detect_device, detect_surface

SESSIONS_ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


@dataclass
class SessionMetadata:
    """Auto-populated metadata for a session directory."""

    session_id: str
    topic: str
    created_at: str
    device: dict[str, Any]
    surface: dict[str, Any]
    model: str = "claude-opus-4-6"
    claude_code_version: str = "2.1.109"
    pages_fetched: int = 0
    scratchpad_entries: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Blog / findings template
# ---------------------------------------------------------------------------

BLOG_TEMPLATE = """\
---
title: "{title}"
date: "{date}"
session_id: "{session_id}"
surface: "{surface_type}"
model: "{model}"
tags: [{tags}]
---

# {title}

## Summary

{summary}

{sections}

---

*Generated during session `{session_id}` on {surface_type} ({date})*
"""

SECTION_TEMPLATE = """\
## {heading}

{body}
"""


# ---------------------------------------------------------------------------
# Page template (for web-fetched content)
# ---------------------------------------------------------------------------

PAGE_TEMPLATE = """\
---
url: "{url}"
title: "{title}"
fetched_at: "{fetched_at}"
session_id: "{session_id}"
---

# {title}

Source: {url}

{content}
"""


# ---------------------------------------------------------------------------
# Session template
# ---------------------------------------------------------------------------


@dataclass
class SessionTemplate:
    """Manages a ``sessions/session_<id>/`` directory."""

    session_id: str
    topic: str
    root: Path
    metadata: SessionMetadata

    @classmethod
    def create(
        cls,
        topic: str,
        session_id: str | None = None,
        model: str = "claude-opus-4-6",
    ) -> SessionTemplate:
        """Create a new session directory with auto-populated metadata."""
        sid = session_id or uuid.uuid4().hex[:12]
        session_dir = SESSIONS_ROOT / f"session_{sid}"
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "pages").mkdir(exist_ok=True)

        device = detect_device()
        surface = detect_surface()

        metadata = SessionMetadata(
            session_id=sid,
            topic=topic,
            created_at=datetime.now(timezone.utc).isoformat(),
            device=asdict(device),
            surface=asdict(surface),
            model=model,
            claude_code_version=device.claude_code_version,
        )

        tpl = cls(session_id=sid, topic=topic, root=session_dir, metadata=metadata)
        tpl._write_metadata()
        tpl._init_scratchpad()
        return tpl

    @classmethod
    def load(cls, session_id: str) -> SessionTemplate:
        """Load an existing session from disk."""
        session_dir = SESSIONS_ROOT / f"session_{session_id}"
        meta_path = session_dir / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"No session found: {session_dir}")

        with open(meta_path) as f:
            data = json.load(f)

        metadata = SessionMetadata(**data)
        return cls(
            session_id=session_id,
            topic=metadata.topic,
            root=session_dir,
            metadata=metadata,
        )

    # -- Scratchpad --------------------------------------------------------

    def append_scratchpad(self, note: str, heading: str | None = None) -> None:
        """Append a timestamped entry to scratchpad.md."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        entry_parts = [f"\n### [{ts}]"]
        if heading:
            entry_parts[0] += f" {heading}"
        entry_parts.append(f"\n{note}\n")

        with open(self.root / "scratchpad.md", "a") as f:
            f.write("\n".join(entry_parts))

        self.metadata.scratchpad_entries += 1
        self._write_metadata()

    # -- Pages -------------------------------------------------------------

    def save_page(
        self,
        url: str,
        title: str,
        content: str,
    ) -> Path:
        """Save a fetched web page using the page template."""
        slug = _slugify(title)[:60]
        filename = f"{self.metadata.pages_fetched + 1:03d}_{slug}.md"
        page_path = self.root / "pages" / filename

        rendered = PAGE_TEMPLATE.format(
            url=url,
            title=title,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            session_id=self.session_id,
            content=content,
        )
        page_path.write_text(rendered)

        self.metadata.pages_fetched += 1
        self._write_metadata()
        return page_path

    # -- Findings (blog-style) --------------------------------------------

    def write_findings(
        self,
        title: str,
        summary: str,
        sections: list[dict[str, str]],
        tags: list[str] | None = None,
    ) -> Path:
        """Write a blog-post-style findings document."""
        sections_text = "\n".join(SECTION_TEMPLATE.format(heading=s["heading"], body=s["body"]) for s in sections)

        rendered = BLOG_TEMPLATE.format(
            title=title,
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            session_id=self.session_id,
            surface_type=self.metadata.surface.get("surface_type", "unknown"),
            model=self.metadata.model,
            tags=", ".join(f'"{t}"' for t in (tags or [])),
            summary=summary,
            sections=sections_text,
        )

        findings_path = self.root / "findings.md"
        findings_path.write_text(rendered)
        return findings_path

    # -- Internal ----------------------------------------------------------

    def _write_metadata(self) -> None:
        meta_path = self.root / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(self.metadata.to_dict(), f, indent=2)
            f.write("\n")

    def _init_scratchpad(self) -> None:
        sp = self.root / "scratchpad.md"
        if not sp.exists():
            sp.write_text(
                f"# Scratchpad — {self.topic}\n\n"
                f"Session: `{self.session_id}`\n"
                f"Created: {self.metadata.created_at}\n\n"
                f"---\n"
            )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")
