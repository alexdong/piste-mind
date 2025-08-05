"""Command-line interface for piste-mind."""

import asyncio

import click
from loguru import logger
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from pydantic_ai import Agent
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from src.agent import ModelType, get_model, load_prompt_template, run_agent
from src.models import Answer, AnswerChoice, Feedback, Question
from src.session import SessionManager

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


def get_user_choice(completer: WordCompleter, style: Style) -> AnswerChoice:
    """Get and parse user's answer choice."""
    while True:
        answer_input = prompt(
            "Your choice (A/B/C/D): ",
            completer=completer,
            style=style,
        )
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

        # Create agents
        logger.info(f"Creating agents with {model_type.name} model")
        question_agent = Agent(
            model=selected_model,
            output_type=Question,
            system_prompt="You are an expert epee fencing coach creating tactical scenarios.",
            model_settings={"temperature": 0.7},
        )

        feedback_agent = Agent(
            model=selected_model,
            output_type=Feedback,
            system_prompt="You are an expert epee fencing coach providing detailed tactical feedback.",
            model_settings={"temperature": 0.3},
        )

        # Step 1: Generate and present a question
        console.print("\n[bold cyan]🤺 Generating tactical scenario...[/bold cyan]\n")

        prompt_text = load_prompt_template("initial.j2")
        question = await run_agent(
            agent=question_agent,  # type: ignore[arg-type]
            prompt=prompt_text,
            expected_type=Question,
            operation_name="question generation",
        )

        # Display the scenario
        console.print(
            Panel(
                question.question,
                title="[bold yellow]Tactical Scenario[/bold yellow]",
                border_style="yellow",
            )
        )

        console.print("\n[bold]Strategic Options:[/bold]")
        for choice, option in zip(AnswerChoice, question.options, strict=True):
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

        # Get answer choice using parse-don't-validate pattern
        parsed_choice = get_user_choice(answer_completer, style)

        # Get explanation
        console.print("\n[bold cyan]Explain your tactical reasoning:[/bold cyan]")
        explanation = prompt("> ", multiline=False, style=style)

        # Create Answer object using the parsed choice
        user_answer = Answer(choice=parsed_choice, explanation=explanation)

        # Step 3: Generate and present feedback
        console.print("\n[bold cyan]🎯 Analyzing your response...[/bold cyan]\n")

        feedback_prompt = load_prompt_template(
            "feedback.j2", problem=question, user_response=user_answer
        )

        feedback = await run_agent(
            agent=feedback_agent,  # type: ignore[arg-type]
            prompt=feedback_prompt,
            expected_type=Feedback,
            operation_name="feedback generation",
        )

        # Display feedback with rich formatting
        console.print(
            Rule("[bold yellow]Coaching Feedback[/bold yellow]", style="yellow")
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
            session_manager = SessionManager()
            timestamp = asyncio.get_event_loop().time()
            session_path = session_manager.save_session(
                timestamp=timestamp,
                question=question,
                answer=user_answer,
                feedback=feedback,
            )
            console.print(f"\n[green]✅ Session saved to {session_path}.*[/green]")

        console.print("\n[bold cyan]🎯 Training session complete![/bold cyan]\n")

    # Run the async session
    asyncio.run(run_session())


if __name__ == "__main__":
    train()
