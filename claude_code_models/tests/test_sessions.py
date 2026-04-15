"""Tests for session and checkpoint models."""

from __future__ import annotations

import pytest

from claude_code_models.models.checkpoints import (
    Checkpoint,
    CheckpointEntry,
    RewindAction,
)
from claude_code_models.models.sessions import (
    Session,
    SessionEvent,
    SessionSource,
    SessionStatus,
)


class TestSessionStatus:
    def test_all(self) -> None:
        assert set(SessionStatus) == {"running", "idle", "stopped", "errored"}


class TestSessionSource:
    def test_all(self) -> None:
        assert set(SessionSource) == {"startup", "resume", "clear", "compact"}


class TestSession:
    def test_minimal(self) -> None:
        s = Session(session_id="sess-001")
        assert s.status == SessionStatus.RUNNING
        assert s.name is None

    def test_full(self) -> None:
        s = Session(
            session_id="sess-002",
            name="auth-refactor",
            title="Refactoring auth module",
            model="claude-opus-4-6",
            cwd="/home/user/project",
            pr_number=42,
            agent="my-agent",
            total_tokens=50000,
            duration_ms=120000,
        )
        assert s.pr_number == 42
        assert s.total_tokens == 50000

    def test_forked(self) -> None:
        s = Session(session_id="sess-003", forked_from="sess-001")
        assert s.forked_from == "sess-001"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        s = Session(session_id="sess-004", name="test")
        data = s.model_dump(mode="json")
        restored = Session.model_validate(data)
        assert restored.session_id == "sess-004"


class TestSessionEvent:
    def test_user_message(self) -> None:
        e = SessionEvent(type="user.message", content="Hello Claude")
        assert e.type == "user.message"

    def test_tool_use(self) -> None:
        e = SessionEvent(
            type="tool_use",
            content=[{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}],
        )
        assert isinstance(e.content, list)

    def test_extra_fields(self) -> None:
        e = SessionEvent(type="custom.event", custom_data={"key": "value"})
        assert e.model_extra is not None


class TestRewindAction:
    def test_all(self) -> None:
        actions = set(RewindAction)
        assert "restore_code_and_conversation" in actions
        assert "summarize_from_here" in actions
        assert len(actions) == 4


class TestCheckpointEntry:
    def test_basic(self) -> None:
        entry = CheckpointEntry(file_path="/src/main.py", content_hash="abc123")
        assert entry.existed_before is True

    def test_new_file(self) -> None:
        entry = CheckpointEntry(file_path="/src/new.py", existed_before=False)
        assert entry.existed_before is False


class TestCheckpoint:
    def test_minimal(self) -> None:
        cp = Checkpoint(checkpoint_id="cp-1", session_id="sess-1")
        assert cp.files == []
        assert cp.prompt_text is None

    def test_with_files(self) -> None:
        cp = Checkpoint(
            checkpoint_id="cp-2",
            session_id="sess-1",
            prompt_text="Fix the login bug",
            files=[
                CheckpointEntry(file_path="/src/auth.py", content_hash="aaa"),
                CheckpointEntry(file_path="/src/login.py", content_hash="bbb"),
            ],
        )
        assert len(cp.files) == 2
        assert cp.prompt_text == "Fix the login bug"

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        cp = Checkpoint(
            checkpoint_id="cp-3",
            session_id="sess-2",
            files=[CheckpointEntry(file_path="/a.py")],
        )
        data = cp.model_dump(mode="json")
        restored = Checkpoint.model_validate(data)
        assert len(restored.files) == 1
