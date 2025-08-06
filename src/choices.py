"""Strategic choices generation for tactical epee scenarios."""

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from agent import MODEL, load_prompt_template, run_agent
from models import Choices, Scenario


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

    from session import SessionType, save_session

    async def main() -> None:
        """Generate options for a hardcoded scenario."""
        scenario = Scenario(
            scenario="""The bout has reached a critical moment in the DE round of 8.
            You're trailing 8-12 with only 20 seconds remaining, and the psychological weight of potential elimination is crushing.
            
            Your opponent, a technically disciplined fencer with a very-long distance preference, has been methodically controlling the bout's rhythm through calculated glide-pause advances and smooth retreats.

            Your current state is precarious: physically drained with burning legs, mentally foggy, and oscillating between desperation and resignation.
            The strip feels compressed, your visual focus blurred, and your breathing shallow and erratic. Your opponent's conservative approach has systematically dismantled your earlier aggressive strategy,
            leaving you reactive and uncertain.

            The tactical challenge now centers on breaking your opponent's distance control without falling into their predictable counter-time traps. Their defensive reflex of distance pulling combined with an occasional instant remise means any direct attack risks immediate counteraction. You must find a way to disrupt their carefully maintained spatial rhythm - not through pure aggression, but through subtle tempo manipulation that creates momentary vulnerabilities in their defensive structure.
            The critical question becomes: Can you reset the bout's momentum by creating a deceptive spatial engagement that forces your opponent out of their meticulously constructed defensive comfort zone, all while managing your rapidly depleting physical and mental resources?
            """
        )

        options = await generate_options(scenario)
        print(f"\n{'=' * 80}\nSCENARIO:\n{scenario.scenario}\n\nOPTIONS:")
        for i, option in enumerate(options.options):
            print(f"\n{chr(65 + i)}. {option}")
        print("=" * 80)

        # Save scenario and options separately
        scenario_path = save_session(scenario, SessionType.CHOICES)
        print(f"\nScenario saved to: {scenario_path}")
        # Note: Options are part of the interaction flow but not saved separately

    asyncio.run(main())
