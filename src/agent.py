"""AI agent for generating tactical epee scenarios using pydantic-ai."""

import json
from pathlib import Path

from jinja2 import Template
from pydantic import ValidationError
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from models import Question

# Configure the AI model
model = AnthropicModel("claude-opus-4-20250514")

# Create agent for generating tactical questions
# Temperature 0.7 provides good balance between creativity and consistency
question_agent = Agent(
    model=model,
    result_type=Question,
    system_prompt="You are an expert epee fencing coach creating tactical scenarios.",
    model_settings={"temperature": 0.7},
)


def load_initial_prompt() -> str:
    """Load and render the initial.j2 template for question generation."""
    template_path = Path(__file__).parent / "prompts" / "initial.j2"

    with template_path.open() as f:
        template_content = f.read()

    # The initial template doesn't need any variables
    template = Template(template_content)
    return template.render()


async def generate_question() -> Question:
    """Generate a new tactical epee question using the AI agent."""
    prompt = load_initial_prompt()

    # Get the AI to generate a question
    result = await question_agent.run(prompt)

    return result.data


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Demonstrate generating a new tactical question."""
        print("🤺 Generating a new tactical epee scenario...\n")

        try:
            question = await generate_question()

            print("Generated Question:")
            print("=" * 80)
            print(f"\n{question.question}\n")
            print("Options:")
            for i, option in enumerate(question.options, 1):
                print(f"\n{i}. {option}")
            print("\n" + "=" * 80)

            # Also save to a JSON file for reference
            output_data = {"question": question.question, "options": question.options}

            output_path = Path("generated_question.json")
            with output_path.open("w") as f:
                json.dump(output_data, f, indent=2)

            print("\n✅ Question saved to generated_question.json")

        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error generating question: {e}")

    # Run the async main function
    asyncio.run(main())
