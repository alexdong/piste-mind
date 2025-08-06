"""Session management for piste-mind training sessions."""

import json
import time
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


def save_session(
    data: BaseModel,
    session_type: SessionType,
) -> Path:
    """Save session data to disk.

    Args:
        data: The data to save (Question, Answer, or Feedback model)
        session_type: Type of session data

    Returns:
        Path to the saved file
    """
    # Set up base directory
    base_dir = Path.cwd() / "sessions"
    base_dir.mkdir(exist_ok=True)

    # Generate timestamp and session name
    timestamp = time.time()
    # Use local timezone - DTZ006 is intentionally ignored here
    dt = datetime.fromtimestamp(timestamp)  # noqa: DTZ006
    session_name = dt.strftime("%Y%m%d-%H%M%S")

    # Save file
    file_path = base_dir / f"{session_name}_{session_type.value}.json"
    with file_path.open("w") as f:
        json.dump(data.model_dump(), f, indent=2)

    logger.debug(f"Saved {session_type.value} to {file_path}")
    return file_path
