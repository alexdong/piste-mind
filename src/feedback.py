"""Feedback generation agent for tactical epee coaching."""

from loguru import logger
from pydantic_ai import Agent

from agent import MODEL, load_prompt_template, run_agent
from models import Answer, AnswerChoice, Feedback, Question

# Create agent for generating coaching feedback
logger.info("Creating feedback agent with temperature=0.3")
feedback_agent = Agent(
    model=MODEL,
    output_type=Feedback,
    system_prompt="You are an expert epee fencing coach providing detailed tactical feedback.",
    model_settings={
        "temperature": 0.3
    },  # Lower temperature for more consistent feedback
)
logger.debug("Feedback agent initialized successfully")


async def generate_feedback(question: Question, answer: Answer) -> Feedback:
    """Generate coaching feedback for a student's answer using the AI agent."""
    logger.debug(f"Student chose option {answer.choice}: {answer.explanation}")

    # Load and render the prompt template with context
    prompt = load_prompt_template("feedback.j2", problem=question, user_response=answer)

    # Run the agent and get the feedback
    return await run_agent(
        agent=feedback_agent,
        prompt=prompt,
        expected_type=Feedback,
        operation_name="feedback generation",
    )


if __name__ == "__main__":
    import asyncio

    from session import SessionType, save_session

    async def main() -> None:
        """Generate feedback for a hardcoded question and answer."""
        # Hardcoded question
        question = Question(
            question="You're fencing in the direct elimination round, tied 12-12 with 90 seconds remaining. Your opponent is a tall left-hander who has been successfully using a French grip to keep you at maximum distance throughout the bout. They've been scoring primarily with flicks to your wrist and forearm when you attempt to close distance, and they immediately retreat after each action. Your attacks to their body have been falling short, and when you've tried to accelerate your attacks, they've been catching you with stop-hits to the arm. You notice they're starting to breathe heavily and their retreat is becoming slightly slower. How do you adjust your tactics for these final crucial touches?",
            options=[
                "Continue with the same approach but increase your speed and commitment on the attacks, accepting the risk of stop-hits to force them to defend rather than counter-attack",
                "Switch to a more patient game focused on drawing their attack first, then hitting them with counter-attacks to the arm as they come forward, exploiting their fatigue on the recovery",
                "Use false attacks and broken tempo to draw out their stop-hit attempts, then hit them with a second intention action to the arm when they extend",
                "Start making aggressive preparations with the point threatening their arm while advancing slowly, forcing them to either attack first or give up ground until they run out of piste",
            ],
        )

        # Hardcoded answer
        answer = Answer(
            choice=AnswerChoice.D,
            explanation="I'll use aggressive preparations to threaten their arm while advancing slowly, exploiting their fatigue and forcing them to deal with immediate danger",
        )

        feedback = await generate_feedback(question, answer)
        print(
            f"\n{'=' * 80}\nFEEDBACK:\n\nAcknowledgment: {feedback.acknowledgment}\n\nAnalysis: {feedback.analysis}\n\nAdvanced Concepts: {feedback.advanced_concepts}\n\nBridge to Mastery: {feedback.bridge_to_mastery}\n{'=' * 80}"
        )

        # Save to session
        save_session(question, SessionType.QUESTION)
        save_session(answer, SessionType.ANSWER)
        save_session(feedback, SessionType.FEEDBACK)

    asyncio.run(main())
