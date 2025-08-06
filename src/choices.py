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

    from models import Question
    from session import SessionType, save_session

    async def main() -> None:
        """Generate options for a hardcoded scenario."""
        # Hardcoded scenario
        scenario = Scenario(
            scenario="You're down 8-11 in a DE bout with 45 seconds left. Your opponent is an aggressive attacker who has been dominating with explosive advances and powerful fleches. You've noticed they always attack after exactly two advances, and they're starting to breathe heavily after each action. What's your tactical approach?"
        )

        options = await generate_options(scenario)
        print(f"\n{'=' * 80}\nSCENARIO:\n{scenario.scenario}\n\nOPTIONS:")
        for i, option in enumerate(options.options):
            print(f"\n{chr(65 + i)}. {option}")
        print("=" * 80)

        # Create Question object and save to session
        question = Question.from_parts(scenario, options)
        session_path = save_session(question, SessionType.QUESTION)
        print(f"\nSaved to: {session_path}")

    asyncio.run(main())
