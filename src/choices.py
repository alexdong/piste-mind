"""Strategic choices generation for tactical epee scenarios."""

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from agent import MODEL, load_prompt_template, run_agent
from models import Options, Scenario


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


async def generate_options(
    scenario: Scenario, model: AnthropicModel = MODEL
) -> Options:
    """Generate strategic options for a given scenario."""
    # Create the agent
    options_agent = create_options_agent(model)

    # Load and render the prompt template with the scenario
    prompt = load_prompt_template("choices.j2", scenario=scenario.scenario)

    # Run the agent and get the options
    return await run_agent(
        agent=options_agent,
        prompt=prompt,
        expected_type=Options,
        operation_name="options generation",
    )


if __name__ == "__main__":
    import asyncio
    import json
    from pathlib import Path

    async def main() -> None:
        """Demonstrate generating options for a scenario."""
        logger.info("Starting options generation demonstration")

        # Load a scenario from file (for testing)
        scenario_file = Path("generated_scenario.json")
        if not scenario_file.exists():
            logger.error(
                "No scenario file found. Please run scenario.py first to generate a scenario."
            )
            return

        with scenario_file.open() as f:
            scenario_data = json.load(f)

        scenario = Scenario(**scenario_data)
        logger.info("Loaded scenario from file")

        # Generate options
        logger.info("🎯 Generating strategic options...")
        options = await generate_options(scenario)
        logger.success("Options generated successfully")

        # Display the options
        logger.info("=" * 80)
        logger.info("Strategic Options:")
        for i, option in enumerate(options.options):
            logger.info(f"{chr(65 + i)}. {option}")
        logger.info("=" * 80)

        # Save to JSON
        output_data = {"options": options.options}
        output_path = Path("generated_options.json")
        with output_path.open("w") as f:
            json.dump(output_data, f, indent=2)

        logger.success(f"Options saved to {output_path}")

    # Run the async main function
    logger.info("Launching async main function")
    asyncio.run(main())
    logger.info("Program completed successfully")
