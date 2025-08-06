"""Scenario generation for tactical epee problems."""

import json
from pathlib import Path

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from agent import MODEL, load_prompt_template, run_agent
from choices import generate_options
from models import Question, Scenario


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
        """Demonstrate generating a new tactical scenario."""
        logger.info("Starting piste-mind scenario generation")
        logger.info("🤺 Generating a new tactical epee scenario...")

        # Generate the scenario
        scenario = await generate_scenario()
        logger.success("Scenario generated successfully")

        # Display the scenario
        logger.info("=" * 80)
        logger.info("Generated Scenario:")
        logger.info(scenario.scenario)
        logger.info("=" * 80)

        # Save to a JSON file for reference
        output_data = {"scenario": scenario.scenario}

        output_path = Path("generated_scenario.json")
        logger.info(f"Saving scenario to {output_path}")

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

        logger.success(f"Scenario saved successfully to {output_path}")
        logger.info("✅ Scenario saved to generated_scenario.json")

    # Run the async main function
    logger.info("Launching async main function")
    asyncio.run(main())
    logger.info("Program completed successfully")
