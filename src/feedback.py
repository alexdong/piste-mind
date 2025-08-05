"""Feedback generation agent for tactical epee coaching."""

import json
from pathlib import Path

from loguru import logger
from pydantic_ai import Agent

from agent import MODEL, load_prompt_template, run_agent
from models import Answer, AnswerChoice, Feedback, Question

# Create agent for generating coaching feedback
logger.info("Creating feedback agent with temperature=0.3")
feedback_agent = Agent(
    model=MODEL,
    output_type=Feedback,
    system_prompt="You are an expert epee fencing coach providing detailed tactical feedback.",
    model_settings={
        "temperature": 0.3
    },  # Lower temperature for more consistent feedback
)
logger.debug("Feedback agent initialized successfully")


async def generate_feedback(question: Question, answer: Answer) -> Feedback:
    """Generate coaching feedback for a student's answer using the AI agent."""
    logger.debug(f"Student chose option {answer.choice}: {answer.explanation}")

    # Load and render the prompt template with context
    prompt = load_prompt_template("feedback.j2", problem=question, user_response=answer)

    # Run the agent and get the feedback
    return await run_agent(
        agent=feedback_agent,
        prompt=prompt,
        expected_type=Feedback,
        operation_name="feedback generation",
    )


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Demonstrate feedback generation with sample data."""
        logger.info("Starting piste-mind feedback generation demonstration")

        # Load question and answer from JSON files
        question_path = Path("question.json")
        answer_path = Path("answer.json")

        assert question_path.exists(), (
            f"Question file not found at {question_path}. "
            f"Please create question.json with sample data."
        )
        assert answer_path.exists(), (
            f"Answer file not found at {answer_path}. "
            f"Please create answer.json with sample data."
        )

        # Load question data
        with question_path.open() as f:
            question_data = json.load(f)

        question = Question(**question_data)
        logger.info("✅ Loaded question from question.json")

        # Load answer data
        with answer_path.open() as f:
            answer_data = json.load(f)

        # Convert choice letter to AnswerChoice enum
        choice_letter = answer_data["choice"]
        answer = Answer(
            choice=AnswerChoice[choice_letter], explanation=answer_data["explanation"]
        )
        logger.info(f"✅ Loaded answer: {answer.choice} - {answer.explanation}")

        # Generate feedback
        logger.info("🎯 Generating coaching feedback...")
        feedback = await generate_feedback(question, answer)
        logger.success("Feedback generated successfully")

        # Display the feedback
        logger.info("=" * 80)
        logger.info("Coaching Feedback:")
        logger.info(f"\n📌 Acknowledgment:\n{feedback.acknowledgment}")
        logger.info(f"\n🔍 Analysis:\n{feedback.analysis}")
        logger.info(f"\n📚 Advanced Concepts:\n{feedback.advanced_concepts}")
        logger.info(f"\n🏆 Bridge to Mastery:\n{feedback.bridge_to_mastery}")
        logger.info("=" * 80)

        # Save feedback to JSON
        feedback_data = {
            "acknowledgment": feedback.acknowledgment,
            "analysis": feedback.analysis,
            "advanced_concepts": feedback.advanced_concepts,
            "bridge_to_mastery": feedback.bridge_to_mastery,
        }

        output_path = Path("generated_feedback.json")
        with output_path.open("w") as f:
            json.dump(feedback_data, f, indent=2)

        logger.success(f"Feedback saved to {output_path}")

    # Run the async main function
    logger.info("Launching async main function")
    asyncio.run(main())
    logger.info("Program completed successfully")
