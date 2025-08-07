"""Scenario generation for tactical epee problems."""

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from piste_mind.agent import MODEL, load_prompt_template, run_agent
from piste_mind.models import Scenario, generate_full_context


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
    logger.debug("Returning agent with pydantic-ai typing quirk")
    return agent  # type: ignore[return-value]


async def generate_scenario(model: AnthropicModel = MODEL) -> Scenario:
    """Generate a new tactical epee scenario using the AI agent."""
    logger.debug("Generating full context")
    context_str = generate_full_context()

    logger.debug("Logging generated context")
    logger.info("Generated scenario context:")
    logger.info(f"\n{context_str}")

    logger.debug("Creating scenario agent")
    scenario_agent = create_scenario_agent(model)

    logger.debug("Loading and rendering prompt template with context")
    prompt = load_prompt_template("scenario.j2", context=context_str)

    logger.debug("Running agent to generate scenario")
    return await run_agent(
        agent=scenario_agent,
        prompt=prompt,
        expected_type=Scenario,
        operation_name="scenario generation",
    )


if __name__ == "__main__":
    import asyncio

    from piste_mind.session import SessionType, save_session

    async def main() -> None:
        """Generate tactical scenarios."""
        scenario = await generate_scenario()
        print(f"\n{'=' * 80}\n{scenario.scenario}\n{'=' * 80}")

        logger.debug("Saving scenario to session")
        session_path = save_session(scenario, SessionType.QUESTION)
        print(f"\nSaved to: {session_path}")

    asyncio.run(main())
