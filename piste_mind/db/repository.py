"""Repository pattern implementation for session data access."""

from datetime import UTC, datetime

from loguru import logger

from piste_mind.db.connection import get_async_connection
from piste_mind.db.models import (
    SessionAnalytics,
    SessionState,
    SessionSummary,
    TrainingSession,
    UserPerformance,
)
from piste_mind.models import Answer, Choices, Feedback, Scenario


class SessionRepository:
    """Data access layer for session management."""

    @staticmethod
    def _serialize_model(model: object | None) -> str | None:
        """Serialize a Pydantic model to JSON."""
        if model is None:
            return None
        assert hasattr(model, "model_dump_json"), "Model must be a Pydantic model"
        return model.model_dump_json()  # type: ignore[attr-defined]

    @staticmethod
    def _deserialize_scenario(data: str | None) -> Scenario | None:
        """Deserialize JSON to Scenario model."""
        if data is None:
            return None
        return Scenario.model_validate_json(data)

    @staticmethod
    def _deserialize_choices(data: str | None) -> Choices | None:
        """Deserialize JSON to Choices model."""
        if data is None:
            return None
        return Choices.model_validate_json(data)

    @staticmethod
    def _deserialize_answer(data: str | None) -> Answer | None:
        """Deserialize JSON to Answer model."""
        if data is None:
            return None
        return Answer.model_validate_json(data)

    @staticmethod
    def _deserialize_feedback(data: str | None) -> Feedback | None:
        """Deserialize JSON to Feedback model."""
        if data is None:
            return None
        return Feedback.model_validate_json(data)

    def _row_to_summary(self, data: dict) -> SessionSummary:
        """Convert database row to SessionSummary."""
        # Extract user choice from answer if available
        user_choice = None
        if data["user_answer"]:
            answer = self._deserialize_answer(data["user_answer"])
            user_choice = answer.choice if answer else None

        # Extract recommended choice from choices if available
        recommended_choice = None
        choice_correct = None
        if data["choices"]:
            choices = self._deserialize_choices(data["choices"])
            if choices:
                recommended_choice = choices.recommend
                if user_choice is not None:
                    choice_correct = user_choice.value == recommended_choice

        return SessionSummary(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            state=SessionState(data["state"]),
            interface=data["interface"],
            user_choice=user_choice,
            recommended_choice=recommended_choice,
            choice_correct=choice_correct,
            total_time=data["total_session_time"],
        )

    async def create_session(self, session: TrainingSession) -> TrainingSession:
        """Create a new session."""
        logger.debug(f"Creating session {session.session_id}")

        async with get_async_connection() as conn:
            await conn.execute(
                """
                INSERT INTO sessions (
                    session_id, created_at, updated_at, state, interface,
                    model_used, user_id, scenario, choices, user_answer,
                    feedback, time_to_choice, time_to_explanation,
                    total_session_time, error_message, error_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                    session.state.value,
                    session.interface,
                    session.model_used,
                    session.user_id,
                    self._serialize_model(session.scenario),
                    self._serialize_model(session.choices),
                    self._serialize_model(session.user_answer),
                    self._serialize_model(session.feedback),
                    session.time_to_choice,
                    session.time_to_explanation,
                    session.total_session_time,
                    session.error_message,
                    session.error_count,
                ),
            )
            await conn.commit()

        logger.info(f"Session {session.session_id} created successfully")
        return session

    async def get_session(self, session_id: str) -> TrainingSession | None:
        """Retrieve session by ID."""
        logger.debug(f"Retrieving session {session_id}")

        async with get_async_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            )
            row = await cursor.fetchone()

        if row is None:
            logger.warning(f"Session {session_id} not found")
            return None

        # Convert row to dict
        data = dict(row)

        # Deserialize complex fields
        session = TrainingSession(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            state=SessionState(data["state"]),
            interface=data["interface"],
            model_used=data["model_used"],
            user_id=data["user_id"],
            scenario=self._deserialize_scenario(data["scenario"]),
            choices=self._deserialize_choices(data["choices"]),
            user_answer=self._deserialize_answer(data["user_answer"]),
            feedback=self._deserialize_feedback(data["feedback"]),
            time_to_choice=data["time_to_choice"],
            time_to_explanation=data["time_to_explanation"],
            total_session_time=data["total_session_time"],
            error_message=data["error_message"],
            error_count=data["error_count"],
        )

        logger.debug(f"Session {session_id} retrieved successfully")
        return session

    async def update_session(self, session: TrainingSession) -> TrainingSession:
        """Update existing session."""
        logger.debug(f"Updating session {session.session_id}")

        session.updated_at = datetime.now(UTC)

        async with get_async_connection() as conn:
            await conn.execute(
                """
                UPDATE sessions SET
                    updated_at = ?, state = ?, scenario = ?, choices = ?,
                    user_answer = ?, feedback = ?, time_to_choice = ?,
                    time_to_explanation = ?, total_session_time = ?,
                    error_message = ?, error_count = ?
                WHERE session_id = ?
                """,
                (
                    session.updated_at.isoformat(),
                    session.state.value,
                    self._serialize_model(session.scenario),
                    self._serialize_model(session.choices),
                    self._serialize_model(session.user_answer),
                    self._serialize_model(session.feedback),
                    session.time_to_choice,
                    session.time_to_explanation,
                    session.total_session_time,
                    session.error_message,
                    session.error_count,
                    session.session_id,
                ),
            )
            await conn.commit()

        logger.info(f"Session {session.session_id} updated successfully")
        return session

    async def list_sessions(
        self,
        user_id: str | None = None,
        state: SessionState | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SessionSummary]:
        """List sessions with filtering."""
        logger.debug("Listing sessions with filters")

        query = "SELECT * FROM sessions WHERE 1=1"
        params = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)

        if state is not None:
            query += " AND state = ?"
            params.append(state.value)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with get_async_connection() as conn:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()

        summaries = []
        for row in rows:
            summary = self._row_to_summary(dict(row))
            summaries.append(summary)

        logger.debug(f"Retrieved {len(summaries)} session summaries")
        return summaries

    async def get_user_performance(self, user_id: str) -> UserPerformance | None:
        """Get performance analytics for a user."""
        logger.debug(f"Getting performance analytics for user {user_id}")

        async with get_async_connection() as conn:
            # Get basic session counts
            cursor = await conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN state = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN state = 'abandoned' THEN 1 END) as abandoned,
                    AVG(CASE WHEN state = 'completed' THEN total_session_time END) as avg_time
                FROM sessions WHERE user_id = ?
                """,
                (user_id,),
            )
            stats = await cursor.fetchone()

            if stats["total"] == 0:
                return None

            # Get choice accuracy
            cursor = await conn.execute(
                """
                SELECT
                    user_answer, choices
                FROM sessions
                WHERE user_id = ? AND state = 'completed'
                    AND user_answer IS NOT NULL AND choices IS NOT NULL
                """,
                (user_id,),
            )
            choices_data = await cursor.fetchall()

        # Calculate accuracy
        correct_choices = 0
        total_choices = 0
        for row in choices_data:
            answer = self._deserialize_answer(row["user_answer"])
            choices = self._deserialize_choices(row["choices"])
            if answer and choices:
                total_choices += 1
                if answer.choice.value == choices.recommend:
                    correct_choices += 1

        accuracy = correct_choices / total_choices if total_choices > 0 else 0.0

        return UserPerformance(
            user_id=user_id,
            total_sessions=stats["total"],
            completed_sessions=stats["completed"],
            abandoned_sessions=stats["abandoned"],
            average_session_time=stats["avg_time"] or 0.0,
            choice_accuracy=accuracy,
            most_common_mistakes=[],  # TODO: Implement mistake tracking
            improvement_trend=0.0,  # TODO: Implement trend calculation
        )

    async def get_system_analytics(self) -> SessionAnalytics:
        """Get system-wide analytics."""
        logger.debug("Getting system-wide analytics")

        async with get_async_connection() as conn:
            # Get basic stats
            cursor = await conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN state = 'completed' THEN 1 END) as completed,
                    AVG(CASE WHEN state = 'completed' THEN total_session_time END) as avg_duration
                FROM sessions
                """
            )
            stats = await cursor.fetchone()

            # Get abandonment points
            cursor = await conn.execute(
                """
                SELECT state, COUNT(*) as count
                FROM sessions
                WHERE state IN ('created', 'scenario_generated', 'option_selected', 'abandoned')
                GROUP BY state
                """
            )
            abandonment_rows = await cursor.fetchall()

        total_sessions = stats["total"] or 0
        completed_sessions = stats["completed"] or 0
        completion_rate = (
            completed_sessions / total_sessions if total_sessions > 0 else 0.0
        )

        abandonment_points = {
            SessionState(row["state"]): row["count"] for row in abandonment_rows
        }

        return SessionAnalytics(
            total_sessions=total_sessions,
            completion_rate=completion_rate,
            average_session_duration=stats["avg_duration"] or 0.0,
            most_popular_choices={},  # TODO: Implement choice tracking
            common_abandonment_points=abandonment_points,
        )

    async def cleanup_abandoned_sessions(self, older_than_hours: int = 24) -> int:
        """Clean up old abandoned sessions."""
        logger.debug(f"Cleaning up sessions older than {older_than_hours} hours")

        async with get_async_connection() as conn:
            cursor = await conn.execute(
                """
                UPDATE sessions
                SET state = 'abandoned', error_message = 'Session timed out'
                WHERE state NOT IN ('completed', 'abandoned', 'error')
                AND datetime(updated_at) < datetime('now', '-' || ? || ' hours')
                """,
                (older_than_hours,),
            )
            await conn.commit()

            rows_affected = cursor.rowcount

        logger.info(f"Marked {rows_affected} sessions as abandoned")
        return rows_affected
