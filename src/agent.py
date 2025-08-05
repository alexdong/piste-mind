"""AI agent for generating tactical epee scenarios using pydantic-ai."""

import json
from pathlib import Path

from jinja2 import Template
from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from models import NUM_OPTIONS, AnswerChoice, Question

# Configure the AI model
logger.info("Initializing AnthropicModel with claude-opus-4-20250514")
model = AnthropicModel("claude-opus-4-20250514")

# Create agent for generating tactical questions
# Temperature 0.7 provides good balance between creativity and consistency
logger.info("Creating question agent with temperature=0.7")
question_agent = Agent(
    model=model,
    output_type=Question,
    system_prompt="You are an expert epee fencing coach creating tactical scenarios.",
    model_settings={"temperature": 0.7},
)
logger.debug("Question agent initialized successfully")


def load_initial_prompt() -> str:
    """Load and render the initial.j2 template for question generation."""
    template_path = Path(__file__).parent / "prompts" / "initial.j2"
    logger.debug(f"Loading prompt template from: {template_path}")

    assert template_path.exists(), (
        f"Template file not found at {template_path}. "
        f"Ensure 'initial.j2' exists in the prompts directory."
    )
    assert template_path.is_file(), (
        f"Template path {template_path} exists but is not a file. "
        f"Check that 'initial.j2' is a regular file, not a directory."
    )

    with template_path.open() as f:
        template_content = f.read()

    assert template_content.strip(), (
        f"Template file {template_path} is empty or contains only whitespace. "
        f"The template must contain prompt instructions."
    )

    logger.debug(f"Template loaded successfully, length: {len(template_content)} chars")

    # The initial template doesn't need any variables
    template = Template(template_content)
    rendered_prompt = template.render()

    assert rendered_prompt.strip(), (
        "Rendered template resulted in empty content. "
        "Check the Jinja2 template syntax in initial.j2."
    )

    logger.debug(
        f"Template rendered, final prompt length: {len(rendered_prompt)} chars"
    )
    return rendered_prompt


async def generate_question() -> Question:
    """Generate a new tactical epee question using the AI agent."""
    logger.info("Starting question generation process")

    prompt = load_initial_prompt()
    logger.debug("Prompt loaded and ready for AI agent")

    # Get the AI to generate a question
    logger.info("Sending prompt to AI agent")
    result = await question_agent.run(prompt)

    assert result is not None, (
        "AI agent returned None result. "
        "Check API key configuration and network connectivity."
    )
    assert hasattr(result, "output"), (
        f"AI agent result missing 'output' attribute. Got result type: {type(result)}"
    )
    assert isinstance(result.output, Question), (
        f"AI agent output is not a Question instance. Got type: {type(result.output)}"
    )

    logger.success("AI agent returned response successfully")
    logger.debug(f"Generated question length: {len(result.output.question)} chars")
    logger.debug(f"Number of options generated: {len(result.output.options)}")

    return result.output


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Demonstrate generating a new tactical question."""
        logger.info("Starting piste-mind agent demonstration")
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
            logger.debug(f"Option {choice}: {option[:50]}...")
        logger.info("=" * 80)

        # Also save to a JSON file for reference
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
