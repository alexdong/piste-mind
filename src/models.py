"""Data models for the piste-mind tactical training tool."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator

# Constants
NUM_OPTIONS = 4


class AnswerChoice(str, Enum):
    """Valid answer choices for tactical scenarios."""

    A = "a"
    B = "b"
    C = "c"
    D = "d"


class Question(BaseModel):
    """A tactical epee scenario with multiple strategic options."""

    question: str = Field(
        ...,
        description="Detailed tactical scenario including score, time, and opponent analysis",
        min_length=100,
    )
    options: list[str] = Field(
        ...,
        description="Four distinct tactical approaches to the scenario",
        min_length=NUM_OPTIONS,
        max_length=NUM_OPTIONS,
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[str]) -> list[str]:
        """Ensure all options are non-empty strings."""
        if len(v) != NUM_OPTIONS:
            msg = f"Exactly {NUM_OPTIONS} options are required"
            raise ValueError(msg)
        for i, option in enumerate(v):
            if not option or not option.strip():
                raise ValueError(f"Option {i + 1} cannot be empty")
        return v


class Answer(BaseModel):
    """A student's response to a tactical scenario."""

    choice: AnswerChoice = Field(
        ..., description="The chosen tactical option (a, b, c, or d)"
    )
    explanation: str = Field(
        ...,
        description="Student's reasoning for their tactical choice",
        min_length=20,
    )


class Feedback(BaseModel):
    """Coaching feedback on a student's tactical decision."""

    acknowledgment: str = Field(
        ...,
        description="Recognition of what the student correctly identified",
        min_length=50,
    )
    analysis: str = Field(
        ...,
        description="Deep tactical analysis of why the choice works",
        min_length=200,
    )
    advanced_concepts: str = Field(
        ...,
        description="Related tactical concepts and execution details",
        min_length=100,
    )
    bridge_to_mastery: str = Field(
        ...,
        description="Connection to championship-level thinking",
        min_length=100,
    )


if __name__ == "__main__":
    # Exercise all data structures with example data

    # Create a Question from the provided example
    question_data = {
        "question": "You're fencing in the direct elimination round, tied 12-12 with 90 seconds remaining. Your opponent is a tall left-hander who has been successfully using a French grip to keep you at maximum distance throughout the bout. They've been scoring primarily with flicks to your wrist and forearm when you attempt to close distance, and they immediately retreat after each action. Your attacks to their body have been falling short, and when you've tried to accelerate your attacks, they've been catching you with stop-hits to the arm. You notice they're starting to breathe heavily and their retreat is becoming slightly slower. How do you adjust your tactics for these final crucial touches?",
        "options": [
            "Continue with the same approach but increase your speed and commitment on the attacks, accepting the risk of stop-hits to force them to defend rather than counter-attack",
            "Switch to a more patient game focused on drawing their attack first, then hitting them with counter-attacks to the arm as they come forward, exploiting their fatigue on the recovery",
            "Use false attacks and broken tempo to draw out their stop-hit attempts, then hit them with a second intention action to the arm when they extend",
            "Start making aggressive preparations with the point threatening their arm while advancing slowly, forcing them to either attack first or give up ground until they run out of piste",
        ],
    }

    print("1. Creating Question model:")
    question = Question(**question_data)
    print(f"   ✓ Question created with {len(question.options)} options")
    print(f"   ✓ Scenario length: {len(question.question)} characters")

    # Create an Answer from the provided example
    answer_data = {
        "choice": "d",
        "explanation": "Exhaust them so they lost their patient or the pain becomes unbearable. Might be a good idea to follow up with a parry-riposte",
    }

    print("\n2. Creating Answer model:")
    answer = Answer(**answer_data)
    print(f"   ✓ Choice: {answer.choice.value.upper()}")
    print(f"   ✓ Explanation: {answer.explanation[:50]}...")

    # Create sample Feedback
    feedback_data = {
        "acknowledgment": "Your instinct to use aggressive preparations while threatening their arm is spot-on because you've correctly identified that your opponent's fatigue is creating a tactical opportunity that wasn't there earlier in the bout.",
        "analysis": "This tactical adjustment brilliantly exploits multiple factors in the current situation. First, by threatening their arm while advancing slowly, you're reversing the distance game - instead of you trying to close distance against their flicks, you're forcing them to deal with an immediate threat. A tired fencer with a French grip will find it increasingly difficult to maintain the precise point control needed for those wrist flicks while retreating. Second, the slow advance with threatening preparations puts them in a psychological bind: they must either attempt another stop-hit (but now against a prepared threat to their arm rather than a committed attack to their body) or continue retreating. Given their fatigue and the limited piste remaining, this creates mounting pressure that compounds with each step backward. The beauty of this approach is that it forces them out of their successful pattern without requiring you to take excessive risks.",
        "advanced_concepts": "The key to executing this strategy is maintaining what we call 'active pressure' - your point must genuinely threaten their arm throughout the advance, not just gesture at it. Keep your point control tight and be ready to close the line if they attempt to circle under for a low-line flick. Your follow-up idea about parry-riposte preparation is excellent advanced thinking. As they tire and feel the pressure of lost ground, they're likely to eventually attempt a more committed attack to break the pattern. Being mentally prepared for this shift allows you to transition from pressure to defensive actions. Common mistakes to avoid: don't rush the advance even if they retreat quickly - maintain your tempo to keep the threat credible. Also, watch for their attempt to circle-six and flick to your flank as a desperation counter.",
        "bridge_to_mastery": "This type of tactical adjustment separates intermediate from advanced fencers because it demonstrates the ability to read both physical and psychological states in real-time and devise strategies that exploit both simultaneously. Championship-level fencing often comes down to who can force their opponent out of comfort first, and your choice shows understanding of this principle. As the action unfolds, you should be reading whether they're more likely to: (1) attempt a desperate flick anyway, (2) try to launch their own attack, or (3) completely surrender ground. Each requires a different follow-up response, and the ability to anticipate and prepare for all three while maintaining your initial tactical pressure is what defines elite competitive thinking.",
    }

    print("\n3. Creating Feedback model:")
    feedback = Feedback(**feedback_data)
    print(f"   ✓ Acknowledgment: {len(feedback.acknowledgment)} characters")
    print(f"   ✓ Analysis: {len(feedback.analysis)} characters")
    print(f"   ✓ Advanced concepts: {len(feedback.advanced_concepts)} characters")
    print(f"   ✓ Bridge to mastery: {len(feedback.bridge_to_mastery)} characters")
    print("\n✅ All models working correctly!")
