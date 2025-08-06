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
    import sys

    async def main() -> None:  # noqa: C901, PLR0912, PLR0915
        """Interactive feedback generation for prompt iteration."""
        logger.info("Starting piste-mind feedback generation tool")

        # Find available question/answer files
        question_files = list(Path().glob("*question*.json"))
        options_files = list(Path().glob("*options*.json"))

        # Try to find files with complete questions (scenario + options)
        complete_files = question_files + options_files

        if not complete_files:
            logger.error(
                "No question files found. Please run scenario.py and choices.py first."
            )
            return None

        # Select question file
        if len(complete_files) == 1:
            question_file = complete_files[0]
        else:
            print("\nAvailable question files:")
            for i, file in enumerate(complete_files):
                print(f"{i + 1}. {file}")

            choice = input("\nSelect question file (number): ").strip()
            try:
                question_file = complete_files[int(choice) - 1]
            except (ValueError, IndexError):
                logger.error("Invalid selection")
                return None

        # Load question data
        with question_file.open() as f:
            data = json.load(f)

        # Handle different file formats
        if "scenario" in data and "options" in data:
            # From choices.py output
            question = Question(question=data["scenario"], options=data["options"])
        elif "question" in data and "options" in data:
            # Standard question format
            question = Question(**data)
        else:
            logger.error("Invalid question file format")
            return None

        logger.info(f"Loaded question from {question_file}")

        # Display the question
        print("\n" + "=" * 80)
        print("TACTICAL SCENARIO:")
        print("=" * 80)
        print(question.question)
        print("\nSTRATEGIC OPTIONS:")
        for i, option in enumerate(question.options):
            print(f"\n{chr(65 + i)}. {option}")
        print("\n" + "=" * 80)

        while True:
            # Get user's answer
            print("\nProvide your answer:")

            # Get choice
            while True:
                choice_input = input("Your choice (A/B/C/D): ").strip().upper()
                if choice_input in ["A", "B", "C", "D"]:
                    choice = AnswerChoice[choice_input]
                    break
                print("Please enter A, B, C, or D")

            # Get explanation
            explanation = input("Your tactical reasoning: ").strip()
            if not explanation:
                explanation = "Testing the feedback generation."

            answer = Answer(choice=choice, explanation=explanation)
            logger.info(f"Answer: {answer.choice} - {answer.explanation}")

            # Generate feedback
            logger.info("\n🎯 Generating coaching feedback...")
            feedback = await generate_feedback(question, answer)
            logger.success("Feedback generated successfully")

            # Display the feedback
            print("\n" + "=" * 80)
            print("COACHING FEEDBACK:")
            print("=" * 80)
            print(f"\n📌 ACKNOWLEDGMENT:\n{feedback.acknowledgment}")
            print(f"\n🔍 TACTICAL ANALYSIS:\n{feedback.analysis}")
            print(f"\n📚 ADVANCED CONCEPTS:\n{feedback.advanced_concepts}")
            print(f"\n🏆 BRIDGE TO MASTERY:\n{feedback.bridge_to_mastery}")
            print("=" * 80)

            # Save complete session
            session_data = {
                "question": question.question,
                "options": question.options,
                "answer": {
                    "choice": answer.choice.value,
                    "explanation": answer.explanation,
                },
                "feedback": {
                    "acknowledgment": feedback.acknowledgment,
                    "analysis": feedback.analysis,
                    "advanced_concepts": feedback.advanced_concepts,
                    "bridge_to_mastery": feedback.bridge_to_mastery,
                },
            }

            output_path = Path("generated_feedback.json")
            with output_path.open("w") as f:
                json.dump(session_data, f, indent=2)

            logger.info(f"✅ Complete session saved to {output_path}")

            # Ask what to do next
            print("\nOptions:")
            print("1. Try a different answer for same question (press Enter)")
            print("2. Save this session with a custom name")
            print("3. Load a different question")
            print("4. Exit (q)")

            choice = input("\nYour choice: ").strip().lower()

            if choice in {"q", "4"}:
                logger.info("Exiting feedback generator")
                break
            if choice == "2":
                custom_name = input("Enter filename (without .json): ").strip()
                if custom_name:
                    custom_path = Path(f"{custom_name}.json")
                    with custom_path.open("w") as f:
                        json.dump(session_data, f, indent=2)
                    logger.success(f"Saved to {custom_path}")
            elif choice == "3":
                # Reload and let user pick a different question
                return await main()
            # Default action (Enter or "1") continues with same question

    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
