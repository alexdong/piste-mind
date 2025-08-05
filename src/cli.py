"""Command-line interface for piste-mind."""

import asyncio
import json
from pathlib import Path

import click
from loguru import logger
from pydantic_ai import Agent

from agent import ModelType, get_model, load_prompt_template, run_agent
from models import Answer, AnswerChoice, Feedback, Question


@click.group()
def cli() -> None:
    """Piste-mind: Interactive tactical training for epee fencers."""


@cli.command()
@click.option(
    "--model",
    type=click.Choice(["haiku", "sonnet", "opus"], case_sensitive=False),
    default="haiku",
    help="AI model to use (default: haiku)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("generated_question.json"),
    help="Output file path",
)
def ask(model: str, output: Path) -> None:
    """Generate a new tactical scenario."""
    # Configure model
    model_type = ModelType[model.upper()]
    selected_model = get_model(model_type)

    # Create custom agent with selected model
    logger.info(f"Creating question agent with {model_type.name} model")
    question_agent = Agent(
        model=selected_model,
        output_type=Question,
        system_prompt="You are an expert epee fencing coach creating tactical scenarios.",
        model_settings={"temperature": 0.7},
    )

    async def generate() -> None:
        # Load and render the prompt template
        prompt = load_prompt_template("initial.j2")

        # Run the agent
        question = await run_agent(
            agent=question_agent,
            prompt=prompt,
            expected_type=Question,
            operation_name="question generation",
        )

        # Display the question
        click.echo("=" * 80)
        click.echo(f"Generated Question:\n{question.question}")
        click.echo("\nOptions:")
        for choice, option in zip(AnswerChoice, question.options, strict=True):
            click.echo(f"{choice}. {option}")
        click.echo("=" * 80)

        # Save to file
        output_data = {"question": question.question, "options": question.options}
        with output.open("w") as f:
            json.dump(output_data, f, indent=2)

        click.echo(f"\n✅ Question saved to {output}")

    asyncio.run(generate())


@cli.command()
@click.option(
    "--model",
    type=click.Choice(["haiku", "sonnet", "opus"], case_sensitive=False),
    default="haiku",
    help="AI model to use (default: haiku)",
)
@click.option(
    "--question",
    "-q",
    type=click.Path(exists=True, path_type=Path),
    default=Path("question.json"),
    help="Question JSON file",
)
@click.option(
    "--answer",
    "-a",
    type=click.Path(exists=True, path_type=Path),
    default=Path("answer.json"),
    help="Answer JSON file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("generated_feedback.json"),
    help="Output file path",
)
def feedback(model: str, question: Path, answer: Path, output: Path) -> None:
    """Generate coaching feedback for an answer."""
    # Configure model
    model_type = ModelType[model.upper()]
    selected_model = get_model(model_type)

    # Create custom agent with selected model
    logger.info(f"Creating feedback agent with {model_type.name} model")
    feedback_agent = Agent(
        model=selected_model,
        output_type=Feedback,
        system_prompt="You are an expert epee fencing coach providing detailed tactical feedback.",
        model_settings={"temperature": 0.3},
    )

    async def generate() -> None:
        # Load question and answer
        with question.open() as f:
            question_data = json.load(f)
        question_obj = Question(**question_data)

        with answer.open() as f:
            answer_data = json.load(f)
        answer_obj = Answer(
            choice=AnswerChoice[answer_data["choice"]],
            explanation=answer_data["explanation"],
        )

        # Load and render the prompt template
        prompt = load_prompt_template(
            "feedback.j2", problem=question_obj, user_response=answer_obj
        )

        # Run the agent
        feedback_result = await run_agent(
            agent=feedback_agent,
            prompt=prompt,
            expected_type=Feedback,
            operation_name="feedback generation",
        )

        # Display the feedback
        click.echo("=" * 80)
        click.echo("Coaching Feedback:")
        click.echo(f"\n📌 Acknowledgment:\n{feedback_result.acknowledgment}")
        click.echo(f"\n🔍 Analysis:\n{feedback_result.analysis}")
        click.echo(f"\n📚 Advanced Concepts:\n{feedback_result.advanced_concepts}")
        click.echo(f"\n🏆 Bridge to Mastery:\n{feedback_result.bridge_to_mastery}")
        click.echo("=" * 80)

        # Save to file
        feedback_data = {
            "acknowledgment": feedback_result.acknowledgment,
            "analysis": feedback_result.analysis,
            "advanced_concepts": feedback_result.advanced_concepts,
            "bridge_to_mastery": feedback_result.bridge_to_mastery,
        }
        with output.open("w") as f:
            json.dump(feedback_data, f, indent=2)

        click.echo(f"\n✅ Feedback saved to {output}")

    asyncio.run(generate())


if __name__ == "__main__":
    cli()
