"""Question and options generation agents for tactical epee scenarios."""

import json
from pathlib import Path

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from agent import MODEL, load_prompt_template, run_agent
from models import NUM_OPTIONS, AnswerChoice, Options, Question, Scenario


def create_scenario_agent(model: AnthropicModel = MODEL) -> Agent[Scenario]:
    """Create agent for generating tactical scenarios."""
    logger.info("Creating scenario agent with temperature=0.7")
    agent = Agent(
        model=model,
        output_type=Scenario,
        system_prompt="You are an expert epee fencing coach creating tactical scenarios.",
        model_settings={"temperature": 0.7},
    )
    logger.debug("Scenario agent initialized successfully")
    return agent  # type: ignore[return-value]


def create_options_agent(model: AnthropicModel = MODEL) -> Agent[Options]:
    """Create agent for generating strategic options."""
    logger.info("Creating options agent with temperature=0.5")
    agent = Agent(
        model=model,
        output_type=Options,
        system_prompt="You are an expert epee fencing coach creating strategic options for tactical scenarios.",
        model_settings={"temperature": 0.5},
    )
    logger.debug("Options agent initialized successfully")
    return agent  # type: ignore[return-value]


async def generate_scenario(model: AnthropicModel = MODEL) -> Scenario:
    """Generate a new tactical epee scenario using the AI agent."""
    # Create the agent
    scenario_agent = create_scenario_agent(model)

    # Load and render the prompt template
    prompt = load_prompt_template("initial.j2")

    # Run the agent and get the scenario
    return await run_agent(
        agent=scenario_agent,
        prompt=prompt,
        expected_type=Scenario,
        operation_name="scenario generation",
    )


async def generate_options(
    scenario: Scenario, model: AnthropicModel = MODEL
) -> Options:
    """Generate strategic options for a given scenario."""
    # Create the agent
    options_agent = create_options_agent(model)

    # Load and render the prompt template with the scenario
    prompt = load_prompt_template("options.j2", scenario=scenario.scenario)

    # Run the agent and get the options
    return await run_agent(
        agent=options_agent,
        prompt=prompt,
        expected_type=Options,
        operation_name="options generation",
    )


async def generate_question(model: AnthropicModel = MODEL) -> Question:
    """Generate a complete tactical question (scenario + options)."""
    # Generate the scenario first
    scenario = await generate_scenario(model)
    logger.info("Scenario generated successfully")

    # Generate options for the scenario
    options = await generate_options(scenario, model)
    logger.info("Options generated successfully")

    # Combine into a complete question
    return Question.from_parts(scenario, options)


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Demonstrate generating a new tactical question."""
        logger.info("Starting piste-mind question generation")
        logger.info("🤺 Generating a new tactical epee scenario...")

        # First generate just the scenario
        scenario = await generate_scenario()
        logger.success("Scenario generated successfully")
        logger.info(f"Scenario: {scenario.scenario[:100]}...")

        # Then generate options for that scenario
        logger.info("🎯 Generating strategic options...")
        options = await generate_options(scenario)
        logger.success("Options generated successfully")

        # Combine into a complete question
        question = Question.from_parts(scenario, options)
        logger.success("Complete question assembled")

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
