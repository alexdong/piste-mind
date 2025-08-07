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
    problem = {
        "question": scenario.scenario,
        "options": options.options,
        "recommendation": chr(65 + options.recommend),  # Convert index to letter
    }

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

    import click

    from piste_mind.fixtures import choices_fixture, scenario_fixture
    from piste_mind.models import Answer, AnswerChoice
    from piste_mind.session import SessionType, save_session

    async def test_aligned_choice() -> None:
        """Test when user's choice aligns with coach's recommendation."""
        print("\n" + "=" * 80)
        print("TESTING ALIGNED CHOICE (User agrees with coach)")
        print("=" * 80)

        # Get test data from fixtures
        scenario = scenario_fixture()
        options = choices_fixture()

        # Create answer that matches coach's recommendation
        answer = Answer(
            choice=AnswerChoice(options.recommend),  # Use coach's recommendation
            explanation="I agree with the false-rhythm preparation approach. By varying my advance speed, I can disrupt their timing and create the opening I need for a successful fleche attack.",
        )

        print(f"\nScenario: {scenario.scenario[:100]}...")
        print(f"Coach recommends: Option {chr(65 + options.recommend)}")
        print(f"User chose: Option {answer.choice}")
        print(f"User's explanation: {answer.explanation}")

        feedback = await generate_feedback(scenario, options, answer)

        # Display feedback
        print(f"\n{'=' * 80}")
        print("GENERATED FEEDBACK:")
        print(f"\nAcknowledgment:\n{feedback.acknowledgment}")
        print(f"\nAnalysis:\n{feedback.analysis}")
        print(f"\nAdvanced Concepts:\n{feedback.advanced_concepts}")
        print(f"\nBridge to Mastery:\n{feedback.bridge_to_mastery}")

    async def test_different_choice() -> None:
        """Test when user's choice differs from coach's recommendation."""
        print("\n\n" + "=" * 80)
        print("TESTING DIFFERENT CHOICE (User disagrees with coach)")
        print("=" * 80)

        # Get test data from fixtures
        scenario = scenario_fixture()
        options = choices_fixture()

        # Create answer that differs from coach's recommendation
        different_choice = (options.recommend + 2) % 4  # Pick a different option
        answer = Answer(
            choice=AnswerChoice(different_choice),
            explanation="I think aggressive marching is the way to go here. With time running out, I need to force the action and create scoring opportunities through relentless pressure.",
        )

        print(f"\nScenario: {scenario.scenario[:100]}...")
        print(f"Coach recommends: Option {chr(65 + options.recommend)}")
        print(f"User chose: Option {answer.choice}")
        print(f"User's explanation: {answer.explanation}")

        feedback = await generate_feedback(scenario, options, answer)

        # Display feedback
        print(f"\n{'=' * 80}")
        print("GENERATED FEEDBACK:")
        print(f"\nAcknowledgment:\n{feedback.acknowledgment}")
        print(f"\nAnalysis:\n{feedback.analysis}")
        print(f"\nAdvanced Concepts:\n{feedback.advanced_concepts}")
        print(f"\nBridge to Mastery:\n{feedback.bridge_to_mastery}")

        logger.debug("Saving feedback to session")
        save_session(feedback, SessionType.FEEDBACK)

    @click.command()
    @click.option(
        "--mode",
        type=click.Choice(["aligned", "different", "both"], case_sensitive=False),
        default="both",
        help="Test mode: aligned (user agrees with coach), different (user disagrees), or both (default)",
    )
    def main(mode: str) -> None:
        """Test feedback generation with different user choices."""

        async def run_tests() -> None:
            if mode in ["aligned", "both"]:
                await test_aligned_choice()

            if mode in ["different", "both"]:
                await test_different_choice()

        asyncio.run(run_tests())

    main()
