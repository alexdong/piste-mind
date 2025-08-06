"""Session management for piste-mind training sessions."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path

from loguru import logger
from pydantic import BaseModel


class SessionType(Enum):
    """Types of session data that can be saved."""

    QUESTION = "question"
    ANSWER = "answer"
    FEEDBACK = "feedback"


class SessionManager:
    """Manages saving of training session data."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize session manager.

        Args:
            base_dir: Base directory for saving sessions. Defaults to sessions/ directory.
        """
        self.base_dir = base_dir or Path.cwd() / "sessions"
        self.base_dir.mkdir(exist_ok=True)

    def generate_session_name(self, timestamp: float) -> str:
        """Generate a session name based on timestamp.

        Args:
            timestamp: Unix timestamp

        Returns:
            Session name string with formatted timestamp in local timezone
        """
        # Use local timezone - DTZ006 is intentionally ignored here
        dt = datetime.fromtimestamp(timestamp)  # noqa: DTZ006
        return dt.strftime("%Y%m%d-%H%M%S")

    def save_session(
        self,
        timestamp: float,
        data: BaseModel,
        session_type: SessionType,
    ) -> Path:
        """Save session data to disk.

        Args:
            timestamp: Session timestamp
            data: The data to save (Question, Answer, or Feedback model)
            session_type: Type of session data

        Returns:
            Path to the saved file
        """
        session_name = self.generate_session_name(timestamp)
        file_path = self.base_dir / f"{session_name}_{session_type.value}.json"

        with file_path.open("w") as f:
            json.dump(data.model_dump(), f, indent=2)

        logger.debug(f"Saved {session_type.value} to {file_path}")
        return file_path
