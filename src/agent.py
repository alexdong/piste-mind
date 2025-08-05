"""AI agent for generating tactical epee scenarios using pydantic-ai."""

import json
from pathlib import Path

from jinja2 import Template
from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from models import AnswerChoice, Question

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

    try:
        with template_path.open() as f:
            template_content = f.read()
        logger.debug(
            f"Template loaded successfully, length: {len(template_content)} chars"
        )
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        raise

    # The initial template doesn't need any variables
    template = Template(template_content)
    rendered_prompt = template.render()
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
    try:
        result = await question_agent.run(prompt)
        logger.success("AI agent returned response successfully")
        logger.debug(f"Generated question length: {len(result.output.question)} chars")
        logger.debug(f"Number of options generated: {len(result.output.options)}")
    except Exception as e:
        logger.error(f"Error during AI generation: {e}")
        raise

    return result.output


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Demonstrate generating a new tactical question."""
        logger.info("Starting piste-mind agent demonstration")
        print("🤺 Generating a new tactical epee scenario...\n")

        try:
            question = await generate_question()
            logger.success("Question generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate question: {e}")
            raise

        # Display the generated question
        logger.info("Formatting question for display")
        print("Generated Question:")
        print("=" * 80)
        print(f"\n{question.question}\n")
        print("Options:")
        for choice, option in zip(AnswerChoice, question.options, strict=False):
            print(f"\n{choice}. {option}")
            logger.debug(f"Option {choice}: {option[:50]}...")
        print("\n" + "=" * 80)

        # Also save to a JSON file for reference
        output_data = {"question": question.question, "options": question.options}

        output_path = Path("generated_question.json")
        logger.info(f"Saving question to {output_path}")
        try:
            with output_path.open("w") as f:
                json.dump(output_data, f, indent=2)
            logger.success(f"Question saved successfully to {output_path}")
            print("\n✅ Question saved to generated_question.json")
        except Exception as e:
            logger.error(f"Failed to save question to file: {e}")
            raise

    # Run the async main function
    logger.info("Launching async main function")
    asyncio.run(main())
    logger.info("Program completed successfully")
