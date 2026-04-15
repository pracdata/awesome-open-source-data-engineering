"""Transcript handling for conversation history."""

import logging
from datetime import datetime
from pathlib import Path


def setup_session() -> tuple[Path, Path]:
    """Setup session directory and transcript file.

    Creates a session folder in logs/ with timestamp, containing both
    transcript and detailed tool call logs.

    Returns:
        Tuple of (transcript_file_path, session_dir_path)
    """
    # Create session directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path("logs") / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)

    # Transcript file in session directory
    transcript_file = session_dir / "transcript.txt"

    # Suppress noisy HTTP debug logs from urllib3
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    return transcript_file, session_dir


class TranscriptWriter:
    """Helper to write output to both console and transcript file."""

    def __init__(self, transcript_file: Path) -> None:
        self.file = open(transcript_file, "w", encoding="utf-8")  # noqa: SIM115

    def write(self, text: str, end: str = "", flush: bool = True) -> None:
        """Write text to both console and transcript."""
        print(text, end=end, flush=flush)
        self.file.write(text + end)
        if flush:
            self.file.flush()

    def write_to_file(self, text: str, flush: bool = True) -> None:
        """Write text to transcript file only (not console)."""
        self.file.write(text)
        if flush:
            self.file.flush()

    def close(self) -> None:
        """Close the transcript file."""
        self.file.close()

    def __enter__(self) -> "TranscriptWriter":
        return self

    def __exit__(self, *_args: object) -> bool:
        self.close()
        return False
