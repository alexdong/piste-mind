"""Strategic choices generation for tactical epee scenarios."""

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from piste_mind.agent import MODEL, load_prompt_template, run_agent
from piste_mind.models import Choices, Scenario


def create_options_agent(model: AnthropicModel = MODEL) -> Agent[Choices]:
    """Create agent for generating strategic options."""
    logger.info("Creating options agent with temperature=0.5")
    agent = Agent(
        model=model,
        output_type=Choices,
        system_prompt="You are an expert epee fencing coach creating strategic options for tactical scenarios.",
        model_settings={"temperature": 0.5},
    )
    logger.debug("Options agent initialized successfully")
    return agent  # type: ignore[return-value]


async def generate_options(
    scenario: Scenario, model: AnthropicModel = MODEL
) -> Choices:
    """Generate strategic options for a given scenario."""
    # Create the agent
    options_agent = create_options_agent(model)

    # Load and render the prompt template with the scenario
    prompt = load_prompt_template("choices.j2", scenario=scenario.scenario)

    # Run the agent and get the options
    return await run_agent(
        agent=options_agent,
        prompt=prompt,
        expected_type=Choices,
        operation_name="options generation",
    )


if __name__ == "__main__":
    import asyncio

    from piste_mind.fixtures import scenario_fixture
    from piste_mind.session import SessionType, save_session

    async def main() -> None:
        """Generate options for a hardcoded scenario."""
        scenario = scenario_fixture()

        choices: Choices = await generate_options(scenario)
        print(f"\n{'=' * 80}\nSCENARIO:\n{scenario.scenario}\n\nOPTIONS:")
        for i, option in enumerate(choices.options):
            print(f"\n{chr(65 + i)}. {option}")
        print(f"\nRECOMMENDED: Option {chr(65 + choices.recommend)}")
        print("=" * 80)

        # Save scenario and options separately
        scenario_path = save_session(scenario, SessionType.CHOICES)
        print(f"\nScenario saved to: {scenario_path}")
        # Note: Options are part of the interaction flow but not saved separately

    asyncio.run(main())
