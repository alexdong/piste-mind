"""Scenario generation for tactical epee problems."""

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from agent import MODEL, load_prompt_template, run_agent
from models import Scenario


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


if __name__ == "__main__":
    import asyncio

    from session import SessionType, save_session

    async def main() -> None:
        """Generate tactical scenarios."""
        scenario = await generate_scenario()
        print(f"\n{'=' * 80}\n{scenario.scenario}\n{'=' * 80}")

        # Save to session
        session_path = save_session(scenario, SessionType.QUESTION)
        print(f"\nSaved to: {session_path}")

    asyncio.run(main())
