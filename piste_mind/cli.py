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
from piste_mind.feedback import generate_feedback
from piste_mind.models import Answer, AnswerChoice
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

        # Display the scenario
        console.print(
            Panel(
                scenario.scenario,
                title="[bold yellow]Tactical Scenario[/bold yellow]",
                border_style="yellow",
            )
        )

        console.print("\n[bold]Strategic Options:[/bold]")
        for choice, option in zip(AnswerChoice, options.options, strict=True):
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

        # Use the generate_feedback function from feedback.py
        feedback = await generate_feedback(scenario, options, user_answer)

        # Display feedback with rich formatting
        console.print(
            Rule("[bold yellow]Coaching Feedback[/bold yellow]", style="yellow")
        )

        # Display rubric scores
        score_lines = [
            f"[cyan]1. Clock Pressure:[/cyan] {feedback.score_clock_pressure}/10",
            f"[cyan]2. Touch Quality:[/cyan] {feedback.score_touch_quality}/10",
            f"[cyan]3. Initiative:[/cyan] {feedback.score_initiative}/10",
            f"[cyan]4. Opponent Habits:[/cyan] {feedback.score_opponent_habits}/10",
            f"[cyan]5. Skill Alignment:[/cyan] {feedback.score_skill_alignment}/10",
            f"[cyan]6. Piste Geography:[/cyan] {feedback.score_piste_geography}/10",
            f"[cyan]7. External Factors:[/cyan] {feedback.score_external_factors}/10",
            f"[cyan]8. Fatigue Management:[/cyan] {feedback.score_fatigue_management}/10",
            f"[cyan]9. Information Value:[/cyan] {feedback.score_information_value}/10",
            f"[cyan]10. Psychological Momentum:[/cyan] {feedback.score_psychological_momentum}/10",
        ]

        total_score = sum(
            [
                feedback.score_clock_pressure,
                feedback.score_touch_quality,
                feedback.score_initiative,
                feedback.score_opponent_habits,
                feedback.score_skill_alignment,
                feedback.score_piste_geography,
                feedback.score_external_factors,
                feedback.score_fatigue_management,
                feedback.score_information_value,
                feedback.score_psychological_momentum,
            ]
        )

        scores_text = (
            "\n".join(score_lines)
            + f"\n\n[bold yellow]TOTAL SCORE: {total_score}/100[/bold yellow]"
        )

        console.print(
            Panel(
                scores_text,
                title="[bold red]📊 Rubric Scores[/bold red]",
                border_style="red",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                feedback.acknowledgment,
                title="[green]✓ Acknowledgment[/green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                feedback.analysis,
                title="[blue]🔍 Tactical Analysis[/blue]",
                border_style="blue",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                feedback.advanced_concepts,
                title="[magenta]📚 Advanced Concepts[/magenta]",
                border_style="magenta",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                feedback.bridge_to_mastery,
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
