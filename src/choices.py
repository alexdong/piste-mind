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
    import sys
    from pathlib import Path

    async def main() -> None:  # noqa: C901, PLR0915
        """Interactive options generation for prompt iteration."""
        logger.info("Starting options generation tool")

        # Load or select scenario file
        scenario_files = list(Path().glob("*scenario*.json"))

        if not scenario_files:
            logger.error("No scenario files found. Please run scenario.py first.")
            return None

        # Select scenario file
        if len(scenario_files) == 1:
            scenario_file = scenario_files[0]
        else:
            print("\nAvailable scenario files:")
            for i, file in enumerate(scenario_files):
                print(f"{i + 1}. {file}")

            choice = input("\nSelect scenario file (number): ").strip()
            try:
                scenario_file = scenario_files[int(choice) - 1]
            except (ValueError, IndexError):
                logger.error("Invalid selection")
                return None

        # Load scenario
        with scenario_file.open() as f:
            scenario_data = json.load(f)

        scenario = Scenario(**scenario_data)
        logger.info(f"Loaded scenario from {scenario_file}")

        # Display the scenario for context
        print("\n" + "=" * 80)
        print("SCENARIO:")
        print("=" * 80)
        print(scenario.scenario)
        print("=" * 80)

        while True:
            logger.info("\n🎯 Generating strategic options...")

            # Generate options
            options = await generate_options(scenario)
            logger.success("Options generated successfully")

            # Display the options
            print("\n" + "=" * 80)
            print("STRATEGIC OPTIONS:")
            print("=" * 80)
            for i, option in enumerate(options.options):
                print(f"\n{chr(65 + i)}. {option}")
            print("\n" + "=" * 80)

            # Save to JSON
            output_data = {"scenario": scenario.scenario, "options": options.options}
            output_path = Path("generated_options.json")
            with output_path.open("w") as f:
                json.dump(output_data, f, indent=2)

            logger.info(f"✅ Options saved to {output_path}")

            # Ask what to do next
            print("\nOptions:")
            print("1. Generate new options for same scenario (press Enter)")
            print("2. Save these options with a custom name")
            print("3. Load a different scenario")
            print("4. Exit (q)")

            choice = input("\nYour choice: ").strip().lower()

            if choice in {"q", "4"}:
                logger.info("Exiting options generator")
                break
            if choice == "2":
                custom_name = input("Enter filename (without .json): ").strip()
                if custom_name:
                    custom_path = Path(f"{custom_name}.json")
                    with custom_path.open("w") as f:
                        json.dump(output_data, f, indent=2)
                    logger.success(f"Saved to {custom_path}")
            elif choice == "3":
                # Reload scenario files and let user pick again
                return await main()
            # Default action (Enter or "1") continues the loop

    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
