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

        if len(question.options) != len(AnswerChoice):
            err = ValueError(
                f"Number of options ({len(question.options)}) doesn't match AnswerChoice enum count ({len(AnswerChoice)})"
            )
            err.add_note(f"Expected exactly {NUM_OPTIONS} options")
            err.add_note(f"Options provided: {question.options}")
            raise err

        for choice, option in zip(AnswerChoice, question.options, strict=True):
            logger.info(f"{choice}. {option}")
        logger.info("=" * 80)

        # Save to a JSON file for reference
        output_data = {"question": question.question, "options": question.options}

        output_path = Path("generated_question.json")
        logger.info(f"Saving question to {output_path}")

        # Ensure parent directory exists
        if not output_path.parent.exists():
            err = FileNotFoundError(
                f"Output directory does not exist: {output_path.parent}"
            )
            err.add_note("Cannot save generated question")
            err.add_note(f"Current working directory: {Path.cwd()}")
            raise err

        with output_path.open("w") as f:
            json.dump(output_data, f, indent=2)

        if not output_path.exists():
            err = OSError(f"Failed to create output file: {output_path}")
            err.add_note("Check file permissions in the current directory")
            err.add_note(
                f"Directory permissions: {oct(output_path.parent.stat().st_mode)[-3:]}"
            )
            raise err

        if output_path.stat().st_size == 0:
            err = OSError(f"Output file was created but is empty: {output_path}")
            err.add_note("JSON serialization may have failed")
            err.add_note(f"Data attempted to write: {output_data}")
            raise err

        logger.success(f"Question saved successfully to {output_path}")
        logger.info("✅ Question saved to generated_question.json")

    # Run the async main function
    logger.info("Launching async main function")
    asyncio.run(main())
    logger.info("Program completed successfully")
