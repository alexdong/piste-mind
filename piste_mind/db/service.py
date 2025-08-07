"""Session service for business logic."""

from datetime import UTC, datetime

from loguru import logger

from piste_mind.choices import generate_options
from piste_mind.db.models import SessionState, TrainingSession
from piste_mind.db.repository import SessionRepository
from piste_mind.feedback import generate_feedback
from piste_mind.models import Answer, AnswerChoice
from piste_mind.scenario import generate_scenario


class SessionError(Exception):
    """Session-related errors."""


class SessionService:
    """Business logic for session management."""

    def __init__(self, repository: SessionRepository | None = None) -> None:
        """Initialize with repository instance."""
        self.repository = repository or SessionRepository()

    async def create_session(
        self, interface: str, model: str = "haiku", user_id: str | None = None
    ) -> TrainingSession:
        """Create a new training session."""
        logger.info(f"Creating new {interface} session with {model} model")

        session = TrainingSession(
            interface=interface,
            model_used=model,
            user_id=user_id,
            state=SessionState.CREATED,
        )

        return await self.repository.create_session(session)

    async def generate_scenario_for_session(self, session_id: str) -> TrainingSession:
        """Generate scenario and choices for a session."""
        logger.debug(f"Generating scenario for session {session_id}")

        session = await self.repository.get_session(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")

        if session.state != SessionState.CREATED:
            raise SessionError(
                f"Invalid session state for scenario generation: {session.state}"
            )

        try:
            # Generate scenario and choices
            logger.debug("Generating scenario")
            scenario = await generate_scenario()

            logger.debug("Generating choices for scenario")
            choices = await generate_options(scenario)

            # Update session
            session.scenario = scenario
            session.choices = choices
            session.state = SessionState.SCENARIO_GENERATED

            return await self.repository.update_session(session)

        except Exception as e:
            logger.error(f"Error generating scenario: {e}")
            session.state = SessionState.ERROR
            session.error_message = str(e)
            session.error_count += 1
            await self.repository.update_session(session)
            raise SessionError(f"Failed to generate scenario: {e}") from e

    async def record_choice(
        self, session_id: str, choice: AnswerChoice
    ) -> TrainingSession:
        """Record user's choice selection."""
        logger.debug(f"Recording choice {choice} for session {session_id}")

        session = await self.repository.get_session(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")

        if session.state != SessionState.SCENARIO_GENERATED:
            raise SessionError(
                f"Invalid session state for choice recording: {session.state}"
            )

        # Calculate time to choice
        time_elapsed = (datetime.now(UTC) - session.updated_at).total_seconds()

        # Create or update answer
        if session.user_answer:
            session.user_answer.choice = choice
        else:
            session.user_answer = Answer(choice=choice, explanation="")

        session.time_to_choice = time_elapsed
        session.state = SessionState.OPTION_SELECTED

        return await self.repository.update_session(session)

    async def record_explanation(
        self, session_id: str, explanation: str
    ) -> TrainingSession:
        """Record user's explanation."""
        logger.debug(f"Recording explanation for session {session_id}")

        session = await self.repository.get_session(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")

        if session.state != SessionState.OPTION_SELECTED:
            raise SessionError(
                f"Invalid session state for explanation recording: {session.state}"
            )

        if not session.user_answer:
            msg = "No choice recorded for this session"
            raise SessionError(msg)

        # Calculate time to explanation
        time_elapsed = (datetime.now(UTC) - session.updated_at).total_seconds()

        # Update answer with explanation
        session.user_answer.explanation = explanation
        session.time_to_explanation = time_elapsed
        session.state = SessionState.EXPLANATION_PROVIDED

        return await self.repository.update_session(session)

    async def generate_feedback_for_session(self, session_id: str) -> TrainingSession:
        """Generate feedback for a session."""
        logger.debug(f"Generating feedback for session {session_id}")

        session = await self.repository.get_session(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")

        if session.state != SessionState.EXPLANATION_PROVIDED:
            raise SessionError(
                f"Invalid session state for feedback generation: {session.state}"
            )

        if not all([session.scenario, session.choices, session.user_answer]):
            msg = "Missing required data for feedback generation"
            raise SessionError(msg)

        try:
            # Generate feedback
            logger.debug("Calling feedback generation")
            feedback = await generate_feedback(
                session.scenario, session.choices, session.user_answer
            )

            # Update session
            session.feedback = feedback
            session.state = SessionState.FEEDBACK_GENERATED
            session.total_session_time = (session.time_to_choice or 0) + (
                session.time_to_explanation or 0
            )

            return await self.repository.update_session(session)

        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            session.state = SessionState.ERROR
            session.error_message = str(e)
            session.error_count += 1
            await self.repository.update_session(session)
            raise SessionError(f"Failed to generate feedback: {e}") from e

    async def complete_session(self, session_id: str) -> TrainingSession:
        """Mark session as completed."""
        logger.debug(f"Completing session {session_id}")

        session = await self.repository.get_session(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")

        if session.state != SessionState.FEEDBACK_GENERATED:
            logger.warning(f"Completing session {session_id} in state {session.state}")

        session.state = SessionState.COMPLETED
        logger.info(
            f"Session {session_id} completed in {session.total_session_time:.1f}s"
        )

        return await self.repository.update_session(session)

    async def abandon_session(
        self, session_id: str, reason: str = "User abandoned"
    ) -> TrainingSession:
        """Mark session as abandoned."""
        logger.debug(f"Abandoning session {session_id}: {reason}")

        session = await self.repository.get_session(session_id)
        if not session:
            raise SessionError(f"Session {session_id} not found")

        session.state = SessionState.ABANDONED
        session.error_message = reason

        return await self.repository.update_session(session)

    async def get_or_create_session(
        self, session_id: str | None, interface: str, model: str = "haiku"
    ) -> TrainingSession:
        """Get existing session or create new one."""
        if session_id:
            session = await self.repository.get_session(session_id)
            if session:
                return session

        # Create new session if not found
        return await self.create_session(interface, model)
