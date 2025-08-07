"""Command-line interface for piste-mind."""

import asyncio

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from piste_mind.agent import ModelType, get_model
from piste_mind.choices import generate_options
from piste_mind.editor import edit_content
from piste_mind.feedback import generate_feedback
from piste_mind.models import Answer, AnswerChoice, Challenge
from piste_mind.scenario import generate_scenario
from piste_mind.session import SessionType, save_session

console = Console()


def parse_answer_choice(text: str) -> AnswerChoice:
    """Parse user input into an AnswerChoice.

    Raises:
        ValueError: If input is not a valid choice (A, B, C, or D)
    """
    normalized = text.strip().upper()
    if normalized not in ["A", "B", "C", "D"]:
        err = ValueError(f"Invalid answer choice: '{text}'")
        err.add_note("Expected one of: A, B, C, or D (case insensitive)")
        err.add_note(f"Received: '{text}' (normalized to: '{normalized}')")
        raise err
    return AnswerChoice[normalized]


async def get_user_choice(session: PromptSession) -> AnswerChoice:
    """Get and parse user's answer choice."""
    while True:
        answer_input = await session.prompt_async("Your choice (A/B/C/D): ")
        try:
            return parse_answer_choice(answer_input)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            console.print("[yellow]Please enter A, B, C, or D[/yellow]")


@click.command()
@click.option(
    "--model",
    type=click.Choice(["haiku", "sonnet", "opus"], case_sensitive=False),
    default="haiku",
    help="AI model to use (default: haiku)",
)
@click.option(
    "--save",
    "-s",
    is_flag=True,
    help="Save question and feedback to files",
)
def train(model: str, save: bool) -> None:  # noqa: FBT001
    """Interactive tactical training session for epee fencers."""

    async def run_session() -> None:
        # Configure model
        model_type = ModelType[model.upper()]
        selected_model = get_model(model_type)

        # Step 1: Generate and present a scenario with options
        console.print("\n[bold cyan]🤺 Generating tactical scenario...[/bold cyan]\n")

        # Generate scenario and options separately
        scenario = await generate_scenario(selected_model)
        options = await generate_options(scenario, selected_model)

        # Create challenge and edit for better readability
        challenge = Challenge(scenario=scenario, choices=options)
        edited_challenge = await edit_content(challenge, selected_model)

        # Display the edited scenario
        console.print(
            Panel(
                edited_challenge.scenario.scenario,
                title="[bold yellow]Tactical Scenario[/bold yellow]",
                border_style="yellow",
            )
        )

        console.print("\n[bold]Strategic Options:[/bold]")
        for choice, option in zip(
            AnswerChoice, edited_challenge.choices.options, strict=True
        ):
            console.print(f"\n[bold cyan]{choice}.[/bold cyan] {option}")

        console.print("\n" + "─" * 80 + "\n")

        # Step 2: Get user's answer and explanation
        # Create answer completer
        answer_completer = WordCompleter(["A", "B", "C", "D", "a", "b", "c", "d"])

        # Custom style for prompts
        style = Style.from_dict(
            {
                "prompt": "bold cyan",
                "answer": "bold green",
            }
        )

        # Create prompt session for async input
        session = PromptSession(completer=answer_completer, style=style)

        # Get answer choice using parse-don't-validate pattern
        parsed_choice = await get_user_choice(session)

        # Get explanation
        console.print("\n[bold cyan]Explain your tactical reasoning:[/bold cyan]")
        explanation = await session.prompt_async("> ")

        # Create Answer object using the parsed choice
        user_answer = Answer(choice=parsed_choice, explanation=explanation)

        # Step 3: Generate and present feedback
        console.print("\n[bold cyan]🎯 Analyzing your response...[/bold cyan]\n")

        # Use the generate_feedback function from feedback.py with original scenario/options
        feedback = await generate_feedback(scenario, options, user_answer)

        # Edit feedback for better readability
        edited_feedback = await edit_content(feedback, selected_model)

        # Display feedback with rich formatting
        console.print(
            Rule("[bold yellow]Coaching Feedback[/bold yellow]", style="yellow")
        )

        # Display the recommended option (using edited version for display)
        console.print(
            f"\n[bold green]Coach's Recommended Option:[/bold green] {chr(65 + options.recommend)}"
        )
        console.print(
            f"[dim]{edited_challenge.choices.options[options.recommend]}[/dim]\n"
        )

        console.print(
            Panel(
                edited_feedback.acknowledgment,
                title="[green]✓ Acknowledgment[/green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                edited_feedback.analysis,
                title="[blue]🔍 Tactical Analysis[/blue]",
                border_style="blue",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                edited_feedback.advanced_concepts,
                title="[magenta]📚 Advanced Concepts[/magenta]",
                border_style="magenta",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                edited_feedback.bridge_to_mastery,
                title="[yellow]🏆 Bridge to Mastery[/yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )

        # Save if requested
        if save:
            # Save each component separately
            save_session(scenario, SessionType.QUESTION)
            save_session(user_answer, SessionType.ANSWER)
            feedback_path = save_session(feedback, SessionType.FEEDBACK)

            console.print(
                f"\n[green]✅ Session saved to {feedback_path.parent / feedback_path.stem.rsplit('_', 1)[0]}_*[/green]"
            )

        console.print("\n[bold cyan]🎯 Training session complete![/bold cyan]\n")

    # Run the async session
    asyncio.run(run_session())


if __name__ == "__main__":
    train()
