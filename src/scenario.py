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
    prompt = load_prompt_template("scenario.j2")

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
    import sys

    async def main() -> None:
        """Interactive scenario generation for prompt iteration."""
        logger.info("Starting piste-mind scenario generation")

        while True:
            logger.info("\n🤺 Generating a new tactical epee scenario...")

            # Generate the scenario
            scenario = await generate_scenario()
            logger.success("Scenario generated successfully")

            # Display the scenario
            print("\n" + "=" * 80)
            print("GENERATED SCENARIO:")
            print("=" * 80)
            print(scenario.scenario)
            print("=" * 80)

            # Save to a JSON file for reference
            output_data = {"scenario": scenario.scenario}
            output_path = Path("generated_scenario.json")

            with output_path.open("w") as f:
                json.dump(output_data, f, indent=2)

            logger.info(f"✅ Scenario saved to {output_path}")

            # Ask if user wants to generate another
            print("\nOptions:")
            print("1. Generate another scenario (press Enter)")
            print("2. Save this scenario with a custom name")
            print("3. Exit (q)")

            choice = input("\nYour choice: ").strip().lower()

            if choice in {"q", "3"}:
                logger.info("Exiting scenario generator")
                break
            if choice == "2":
                custom_name = input("Enter filename (without .json): ").strip()
                if custom_name:
                    custom_path = Path(f"{custom_name}.json")
                    with custom_path.open("w") as f:
                        json.dump(output_data, f, indent=2)
                    logger.success(f"Saved to {custom_path}")
            # Default action (Enter or "1") continues the loop

    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
