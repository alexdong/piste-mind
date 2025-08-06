"""Feedback generation agent for tactical epee coaching."""

from loguru import logger
from pydantic_ai import Agent

from piste_mind.agent import MODEL, load_prompt_template, run_agent
from piste_mind.models import Answer, AnswerChoice, Choices, Feedback, Scenario

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


async def generate_feedback(
    scenario: Scenario, options: Choices, answer: Answer
) -> Feedback:
    """Generate coaching feedback for a student's answer using the AI agent."""
    logger.debug(f"Student chose option {answer.choice}: {answer.explanation}")

    # Create a combined object for the template
    problem = {"question": scenario.scenario, "options": options.options}

    # Load and render the prompt template with context
    prompt = load_prompt_template("feedback.j2", problem=problem, user_response=answer)

    # Run the agent and get the feedback
    return await run_agent(
        agent=feedback_agent,
        prompt=prompt,
        expected_type=Feedback,
        operation_name="feedback generation",
    )


if __name__ == "__main__":
    import asyncio

    from piste_mind.session import SessionType, save_session

    async def main() -> None:
        """Generate feedback for a hardcoded question and answer."""
        # Hardcoded scenario
        scenario = Scenario(
            scenario="You're fencing in the direct elimination round, tied 12-12 with 90 seconds remaining. Your opponent is a tall left-hander who has been successfully using a French grip to keep you at maximum distance throughout the bout. They've been scoring primarily with flicks to your wrist and forearm when you attempt to close distance, and they immediately retreat after each action. Your attacks to their body have been falling short, and when you've tried to accelerate your attacks, they've been catching you with stop-hits to the arm. You notice they're starting to breathe heavily and their retreat is becoming slightly slower. How do you adjust your tactics for these final crucial touches?",
        )

        # Hardcoded options
        options = Choices(
            options=[
                "Continue with the same approach but increase your speed and commitment on the attacks, accepting the risk of stop-hits to force them to defend rather than counter-attack",
                "Switch to a more patient game focused on drawing their attack first, then hitting them with counter-attacks to the arm as they come forward, exploiting their fatigue on the recovery",
                "Use false attacks and broken tempo to draw out their stop-hit attempts, then hit them with a second intention action to the arm when they extend",
                "Start making aggressive preparations with the point threatening their arm while advancing slowly, forcing them to either attack first or give up ground until they run out of piste",
            ],
            recommend=3,  # Option D is recommended for this scenario
        )

        # Hardcoded answer
        answer = Answer(
            choice=AnswerChoice.D,
            explanation="I'll use aggressive preparations to threaten their arm while advancing slowly, exploiting their fatigue and forcing them to deal with immediate danger",
        )

        feedback = await generate_feedback(scenario, options, answer)

        # Display scores
        print(f"\n{'=' * 80}\nRUBRIC SCORES:")
        print(f"1. Clock Pressure: {feedback.score_clock_pressure}/10")
        print(f"2. Touch Quality: {feedback.score_touch_quality}/10")
        print(f"3. Initiative: {feedback.score_initiative}/10")
        print(f"4. Opponent Habits: {feedback.score_opponent_habits}/10")
        print(f"5. Skill Alignment: {feedback.score_skill_alignment}/10")
        print(f"6. Piste Geography: {feedback.score_piste_geography}/10")
        print(f"7. External Factors: {feedback.score_external_factors}/10")
        print(f"8. Fatigue Management: {feedback.score_fatigue_management}/10")
        print(f"9. Information Value: {feedback.score_information_value}/10")
        print(f"10. Psychological Momentum: {feedback.score_psychological_momentum}/10")
        total_score = sum(
            [
                feedback.score_clock_pressure,
                feedback.score_touch_quality,
                feedback.score_initiative,
                feedback.score_opponent_habits,
                feedback.score_skill_alignment,
                feedback.score_piste_geography,
                feedback.score_external_factors,
                feedback.score_fatigue_management,
                feedback.score_information_value,
                feedback.score_psychological_momentum,
            ]
        )
        print(f"\nTOTAL SCORE: {total_score}/100")

        print(
            f"\nFEEDBACK:\n\nAcknowledgment: {feedback.acknowledgment}\n\nAnalysis: {feedback.analysis}\n\nAdvanced Concepts: {feedback.advanced_concepts}\n\nBridge to Mastery: {feedback.bridge_to_mastery}\n{'=' * 80}"
        )

        # Save to session
        save_session(scenario, SessionType.QUESTION)
        save_session(answer, SessionType.ANSWER)
        save_session(feedback, SessionType.FEEDBACK)

    asyncio.run(main())
