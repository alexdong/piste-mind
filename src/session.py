"""Session management for piste-mind training sessions."""

import json
from pathlib import Path
from typing import Any

from loguru import logger

from src.models import Answer, AnswerChoice, Feedback, Question


class SessionManager:
    """Manages saving and loading of training session data."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize session manager.

        Args:
            base_dir: Base directory for saving sessions. Defaults to current directory.
        """
        self.base_dir = base_dir or Path.cwd()

    def generate_session_name(self, timestamp: float) -> str:
        """Generate a session name based on timestamp.

        Args:
            timestamp: Unix timestamp

        Returns:
            Session name string
        """
        return f"session_{int(timestamp)}"

    def save_session(
        self,
        timestamp: float,
        question: Question,
        answer: Answer,
        feedback: Feedback,
    ) -> Path:
        """Save a complete training session to disk.

        Args:
            timestamp: Session timestamp
            question: The generated question
            answer: The user's answer
            feedback: The generated feedback

        Returns:
            Path to the session directory
        """
        session_name = self.generate_session_name(timestamp)
        session_path = self.base_dir / session_name

        # Save question
        question_file = session_path.with_suffix(".question.json")
        self._save_json(
            question_file,
            {"question": question.question, "options": question.options},
        )
        logger.debug(f"Saved question to {question_file}")

        # Save answer
        answer_file = session_path.with_suffix(".answer.json")
        self._save_json(
            answer_file,
            {"choice": answer.choice.value, "explanation": answer.explanation},
        )
        logger.debug(f"Saved answer to {answer_file}")

        # Save feedback
        feedback_file = session_path.with_suffix(".feedback.json")
        self._save_json(
            feedback_file,
            {
                "acknowledgment": feedback.acknowledgment,
                "analysis": feedback.analysis,
                "advanced_concepts": feedback.advanced_concepts,
                "bridge_to_mastery": feedback.bridge_to_mastery,
            },
        )
        logger.debug(f"Saved feedback to {feedback_file}")

        logger.success(f"Session saved to {session_path}.*")
        return session_path

    def _save_json(self, path: Path, data: dict[str, Any]) -> None:
        """Save data to JSON file.

        Args:
            path: File path
            data: Data to save
        """
        with path.open("w") as f:
            json.dump(data, f, indent=2)

    def load_session(self, session_path: Path) -> tuple[Question, Answer, Feedback]:
        """Load a training session from disk.

        Args:
            session_path: Path to session (without extension)

        Returns:
            Tuple of (question, answer, feedback)

        Raises:
            FileNotFoundError: If session files don't exist
            ValueError: If session data is invalid
        """
        # Load question
        question_file = session_path.with_suffix(".question.json")
        if not question_file.exists():
            err = FileNotFoundError(f"Question file not found: {question_file}")
            err.add_note(f"Expected to find {question_file}")
            raise err

        with question_file.open() as f:
            question_data = json.load(f)
        question = Question(**question_data)

        # Load answer
        answer_file = session_path.with_suffix(".answer.json")
        if not answer_file.exists():
            err = FileNotFoundError(f"Answer file not found: {answer_file}")
            err.add_note(f"Expected to find {answer_file}")
            raise err

        with answer_file.open() as f:
            answer_data = json.load(f)

        # Parse answer choice
        try:
            choice = AnswerChoice[answer_data["choice"]]
        except KeyError as e:
            err = ValueError(f"Invalid answer choice: {answer_data['choice']}")
            err.add_note("Expected one of: A, B, C, D")
            raise err from e

        answer = Answer(choice=choice, explanation=answer_data["explanation"])

        # Load feedback
        feedback_file = session_path.with_suffix(".feedback.json")
        if not feedback_file.exists():
            err = FileNotFoundError(f"Feedback file not found: {feedback_file}")
            err.add_note(f"Expected to find {feedback_file}")
            raise err

        with feedback_file.open() as f:
            feedback_data = json.load(f)
        feedback = Feedback(**feedback_data)

        logger.info(f"Loaded session from {session_path}.*")
        return question, answer, feedback

    def list_sessions(self) -> list[Path]:
        """List all saved sessions in the base directory.

        Returns:
            List of session paths (without extensions)
        """
        # Find all question files
        question_files = sorted(self.base_dir.glob("session_*.question.json"))

        # Extract session paths without extensions
        sessions = []
        for qf in question_files:
            # Remove the .question.json suffix to get base session path
            session_path = qf.with_suffix("").with_suffix("")
            sessions.append(session_path)

        return sessions
