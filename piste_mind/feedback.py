"""Feedback generation agent for tactical epee coaching."""

from loguru import logger
from pydantic_ai import Agent

from piste_mind.agent import MODEL, load_prompt_template, run_agent
from piste_mind.models import Answer, Choices, Feedback, Scenario

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

    from piste_mind.fixtures import answer_fixture, choices_fixture, scenario_fixture
    from piste_mind.session import SessionType, save_session

    async def main() -> None:
        """Generate feedback for a hardcoded question and answer."""
        # Get test data from fixtures
        scenario = scenario_fixture()
        options = choices_fixture()
        answer = answer_fixture()

        feedback = await generate_feedback(scenario, options, answer)

        # Display feedback
        print(f"\n{'=' * 80}")
        print(
            f"FEEDBACK:\n\nAcknowledgment: {feedback.acknowledgment}\n\nAnalysis: {feedback.analysis}\n\nAdvanced Concepts: {feedback.advanced_concepts}\n\nBridge to Mastery: {feedback.bridge_to_mastery}"
        )
        print("=" * 80)

        logger.debug("Saving feedback to session")
        save_session(feedback, SessionType.FEEDBACK)

    asyncio.run(main())
