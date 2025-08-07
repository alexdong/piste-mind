"""Database models for session management."""

from datetime import UTC, datetime
from enum import Enum
from typing import ClassVar
from uuid import uuid4

from pydantic import BaseModel, Field

from piste_mind.models import Answer, AnswerChoice, Choices, Feedback, Scenario


class SessionState(Enum):
    """Training session states."""

    CREATED = "created"
    SCENARIO_GENERATED = "scenario_generated"
    OPTION_SELECTED = "option_selected"
    EXPLANATION_PROVIDED = "explanation_provided"
    FEEDBACK_GENERATED = "feedback_generated"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ERROR = "error"


class TrainingSession(BaseModel):
    """Complete training session with all data and state tracking."""

    # Session metadata
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    state: SessionState = SessionState.CREATED
    interface: str  # "web" or "cli"
    model_used: str = "haiku"
    user_id: str | None = None  # Future: user identification

    # Training data
    scenario: Scenario | None = None
    choices: Choices | None = None
    user_answer: Answer | None = None
    feedback: Feedback | None = None

    # Analytics data
    time_to_choice: float | None = None  # seconds from scenario to choice
    time_to_explanation: float | None = None  # seconds from choice to explanation
    total_session_time: float | None = None

    # Error tracking
    error_message: str | None = None
    error_count: int = 0

    class Config:
        """Pydantic configuration."""

        json_encoders: ClassVar[dict] = {
            datetime: lambda v: v.isoformat(),
            Enum: lambda v: v.value,
        }


class SessionSummary(BaseModel):
    """Lightweight session summary for analytics."""

    session_id: str
    created_at: datetime
    state: SessionState
    interface: str
    user_choice: AnswerChoice | None = None
    recommended_choice: int | None = None
    choice_correct: bool | None = None
    total_time: float | None = None


class UserPerformance(BaseModel):
    """Aggregate performance metrics for a user."""

    user_id: str
    total_sessions: int
    completed_sessions: int
    abandoned_sessions: int
    average_session_time: float
    choice_accuracy: float  # percentage of correct choices
    most_common_mistakes: list[str]
    improvement_trend: float  # trend in accuracy over time


class SessionAnalytics(BaseModel):
    """System-wide session analytics."""

    total_sessions: int
    completion_rate: float
    average_session_duration: float
    most_popular_choices: dict[str, int]  # choice letter -> count
    common_abandonment_points: dict[SessionState, int]
