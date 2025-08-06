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
    import textwrap

    from piste_mind.session import SessionType, save_session

    async def main() -> None:
        """Generate feedback for a hardcoded question and answer."""
        # Hardcoded scenario
        scenario = Scenario(
            scenario=textwrap.dedent("""
            The bout has reached a critical moment in the DE round of 8.

            You're trailing 8-12 with only 20 seconds remaining, and the psychological weight of potential elimination is crushing.

            Your opponent, a technically disciplined fencer with a very-long distance preference, has been methodically controlling the bout's rhythm through calculated glide-pause advances and smooth retreats.

            Your current state is precarious: physically drained with burning legs, mentally foggy, and oscillating between desperation and resignation.
            The strip feels compressed, your visual focus blurred, and your breathing shallow and erratic. Your opponent's conservative approach has systematically dismantled your earlier aggressive strategy,
            leaving you reactive and uncertain.

            The tactical challenge now centers on breaking your opponent's distance control without falling into their predictable counter-time traps. Their defensive reflex of distance pulling combined with an occasional instant remise means any direct attack risks immediate counteraction. You must find a way to disrupt their carefully maintained spatial rhythm - not through pure aggression, but through subtle tempo manipulation that creates momentary vulnerabilities in their defensive structure.

            The critical question becomes: Can you reset the bout's momentum by creating a deceptive spatial engagement that forces your opponent out of their meticulously constructed defensive comfort zone, all while managing your rapidly depleting physical and mental resources?
            """).strip(),
        )

        # Hardcoded options
        options = Choices(
            options=[
                "Execute a false-rhythm preparation with deliberately slower advances, then explosively accelerate with a fleche attack when opponent adjusts to the deceptive tempo, targeting their anticipatory distance pull.",
                "Launch immediate aggressive attacks with multiple feints and changes of line, attempting to overwhelm opponent's defensive system through sheer pressure and determination.",
                "Employ stop-hits during opponent's glide-pause advances, timing the counter-attack to exploit the brief hesitation in their forward movement pattern.",
                "Retreat deliberately to invite pursuit, then execute a second-intention attack utilizing their forward momentum against their preferred long-distance game.",
            ],
            recommend=0,  # Option A is recommended for this scenario
        )

        # Hardcoded answer
        answer = Answer(
            choice=AnswerChoice.A,
            explanation="B is suicidal; C is technically too challenging; D is unrealistic because they are leading by 4 points and they have no need to chase me. I have to take the initiative.",
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
        save_session(feedback, SessionType.FEEDBACK)

    asyncio.run(main())
