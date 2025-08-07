"""Content editor for improving readability of scenarios, choices, and feedback.

When run as a module, provides CLI options to test editor functionality:
    python -m piste_mind.editor --mode challenge  # Test only challenge editing
    python -m piste_mind.editor --mode feedback   # Test only feedback editing
    python -m piste_mind.editor --mode both       # Test both (default)
    python -m piste_mind.editor                   # Same as --mode both
"""

from typing import TypeVar

from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from piste_mind.agent import MODEL, load_prompt_template, run_agent

T = TypeVar("T", bound=BaseModel)


def create_editor_agent[T: BaseModel](
    output_type: type[T], model: AnthropicModel = MODEL
) -> Agent[T]:
    """Create a generic editor agent."""
    logger.info("Creating editor agent with temperature=0.3")
    return Agent(
        model=model,
        output_type=output_type,
        system_prompt="You are an expert editor who rewrites fencing content to be clearer and more understandable while preserving all technical accuracy.",
        model_settings={"temperature": 0.3},
    )  # type: ignore[return-value]


async def edit_content[T: BaseModel](
    content: T,
    model: AnthropicModel = MODEL,
) -> T:
    """Edit content for better readability.

    Args:
        content: Either Challenge or Feedback instance to edit
        model: AI model to use

    Returns:
        New instance of the same type with edited content
    """
    content_type = type(content).__name__
    logger.info(f"Editing {content_type} for improved readability")

    logger.debug(f"Creating agent for {content_type} editing")
    agent = create_editor_agent(output_type=type(content), model=model)

    logger.debug(f"Converting {content_type} to dict for template")
    content_dict = content.model_dump()

    logger.debug("Loading and rendering editor prompt template")
    prompt = load_prompt_template("editor.j2", content=content_dict)
    logger.debug(f"Prompt for {content_type} editing: {prompt}")

    logger.debug(f"Running agent to edit {content_type}")
    edited = await run_agent(
        agent=agent,
        prompt=prompt,
        expected_type=type(content),
        operation_name=f"{content_type.lower()} editing",
    )

    logger.info(f"{content_type} editing completed successfully: {edited}")
    return edited


if __name__ == "__main__":
    import asyncio

    import click

    from piste_mind.fixtures import challenge_fixture, feedback_fixture

    async def test_challenge_editing() -> None:
        """Test Challenge editing functionality."""
        print("\n" + "=" * 80)
        print("TESTING CHALLENGE EDITING")
        print("=" * 80)

        challenge = challenge_fixture()

        print("\n[BEFORE] ORIGINAL CHALLENGE:")
        print("-" * 40)
        print(f"Scenario: {challenge.scenario.scenario}")
        print("\nChoices:")
        for i, choice in enumerate(challenge.choices.options):
            print(f"\n{chr(65 + i)}. {choice}")

        logger.debug("Editing challenge for better readability")
        edited_challenge = await edit_content(challenge)

        print("\n\n[AFTER] EDITED CHALLENGE:")
        print("-" * 40)
        print(f"Scenario: {edited_challenge.scenario.scenario}")
        print("\nChoices:")
        for i, choice in enumerate(edited_challenge.choices.options):
            print(f"\n{chr(65 + i)}. {choice}")

    async def test_feedback_editing() -> None:
        """Test Feedback editing functionality."""
        print("\n\n" + "=" * 80)
        print("TESTING FEEDBACK EDITING")
        print("=" * 80)

        feedback = feedback_fixture()

        print("\n[BEFORE] ORIGINAL FEEDBACK:")
        print("-" * 40)
        print(f"\nAcknowledgment:\n{feedback.acknowledgment}")
        print(f"\nAnalysis:\n{feedback.analysis}")
        print(f"\nAdvanced Concepts:\n{feedback.advanced_concepts}")
        print(f"\nBridge to Mastery:\n{feedback.bridge_to_mastery}")

        logger.debug("Editing feedback for better readability")
        edited_feedback = await edit_content(feedback)

        print("\n\n[AFTER] EDITED FEEDBACK:")
        print("-" * 40)
        print(f"\nAcknowledgment:\n{edited_feedback.acknowledgment}")
        print(f"\nAnalysis:\n{edited_feedback.analysis}")
        print(f"\nAdvanced Concepts:\n{edited_feedback.advanced_concepts}")
        print(f"\nBridge to Mastery:\n{edited_feedback.bridge_to_mastery}")

    @click.command()
    @click.option(
        "--mode",
        type=click.Choice(["challenge", "feedback", "both"], case_sensitive=False),
        default="both",
        help="What to test: challenge editing, feedback editing, or both (default)",
    )
    def main(mode: str) -> None:
        """Test the editor functionality with different modes."""

        async def run_tests() -> None:
            if mode in ["challenge", "both"]:
                await test_challenge_editing()

            if mode in ["feedback", "both"]:
                await test_feedback_editing()

        asyncio.run(run_tests())

    main()
