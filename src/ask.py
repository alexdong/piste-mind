"""Question generation agent for tactical epee scenarios."""

import json
from pathlib import Path

from loguru import logger
from pydantic_ai import Agent

from agent import MODEL, load_prompt_template, run_agent
from models import NUM_OPTIONS, AnswerChoice, Question

# Create agent for generating tactical questions
# Temperature 0.7 provides good balance between creativity and consistency
logger.info("Creating question agent with temperature=0.7")
question_agent = Agent(
    model=MODEL,
    output_type=Question,
    system_prompt="You are an expert epee fencing coach creating tactical scenarios.",
    model_settings={"temperature": 0.7},
)
logger.debug("Question agent initialized successfully")


async def generate_question() -> Question:
    """Generate a new tactical epee question using the AI agent."""
    # Load and render the prompt template
    prompt = load_prompt_template("initial.j2")

    # Run the agent and get the question
    return await run_agent(
        agent=question_agent,
        prompt=prompt,
        expected_type=Question,
        operation_name="question generation",
    )


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Demonstrate generating a new tactical question."""
        logger.info("Starting piste-mind question generation")
        logger.info("🤺 Generating a new tactical epee scenario...")

        question = await generate_question()
        logger.success("Question generated successfully")

        # Display the generated question
        logger.info("Formatting question for display")
        logger.info("=" * 80)
        logger.info(f"Generated Question:\n{question.question}")
        logger.info("Options:")

        assert len(question.options) == len(AnswerChoice), (
            f"Number of options ({len(question.options)}) doesn't match "
            f"AnswerChoice enum count ({len(AnswerChoice)}). "
            f"Expected exactly {NUM_OPTIONS} options."
        )

        for choice, option in zip(AnswerChoice, question.options, strict=True):
            logger.info(f"{choice}. {option}")
        logger.info("=" * 80)

        # Save to a JSON file for reference
        output_data = {"question": question.question, "options": question.options}

        output_path = Path("generated_question.json")
        logger.info(f"Saving question to {output_path}")

        # Ensure parent directory exists
        assert output_path.parent.exists(), (
            f"Output directory {output_path.parent} does not exist. "
            f"Cannot save generated question."
        )

        with output_path.open("w") as f:
            json.dump(output_data, f, indent=2)

        assert output_path.exists(), (
            f"Failed to create output file {output_path}. "
            f"Check file permissions in the current directory."
        )
        assert output_path.stat().st_size > 0, (
            f"Output file {output_path} was created but is empty. "
            f"JSON serialization may have failed."
        )

        logger.success(f"Question saved successfully to {output_path}")
        logger.info("✅ Question saved to generated_question.json")

    # Run the async main function
    logger.info("Launching async main function")
    asyncio.run(main())
    logger.info("Program completed successfully")
