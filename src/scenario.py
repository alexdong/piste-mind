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

    async def main() -> None:
        """Generate tactical scenarios."""
        while True:
            scenario = await generate_scenario()
            print(f"\n{'=' * 80}\n{scenario.scenario}\n{'=' * 80}")

            with Path("scenario.json").open("w") as f:
                json.dump({"scenario": scenario.scenario}, f, indent=2)

            if input("\nPress Enter for another, 'q' to quit: ").strip().lower() == "q":
                break

    asyncio.run(main())
