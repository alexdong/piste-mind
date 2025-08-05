"""Common AI agent utilities for piste-mind."""

import os
from enum import Enum
from pathlib import Path
from typing import TypeVar

from jinja2 import Template
from loguru import logger
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel


class ModelType(Enum):
    """Available Anthropic model types."""

    HAIKU = "claude-3-5-haiku-20241022"
    SONNET = "claude-3-5-sonnet-20241022"
    OPUS = "claude-opus-4-20250514"


def get_model(model_type: ModelType | None = None) -> AnthropicModel:
    """Get the configured AI model.

    Args:
        model_type: The model type to use. If None, uses environment variable
                   PISTE_MIND_MODEL or defaults to HAIKU.

    Returns:
        Configured AnthropicModel instance
    """
    if model_type is None:
        # Check environment variable for model preference
        env_model = os.getenv("PISTE_MIND_MODEL", "HAIKU").upper()
        try:
            model_type = ModelType[env_model]
        except KeyError:
            logger.warning(
                f"Invalid model type '{env_model}' in PISTE_MIND_MODEL. "
                f"Valid options: {[m.name for m in ModelType]}. "
                f"Defaulting to HAIKU."
            )
            model_type = ModelType.HAIKU

    logger.info(f"Initializing AnthropicModel with {model_type.value}")
    return AnthropicModel(model_type.value)


# Configure the default AI model globally
MODEL = get_model()

# Type variable for generic output types
T = TypeVar("T", bound=BaseModel)


def load_prompt_template(template_name: str, **context: BaseModel) -> str:
    """Load and render a Jinja2 template from the prompts directory.

    Args:
        template_name: Name of the template file (e.g., "initial.j2")
        **context: Pydantic models to pass to the template for rendering

    Returns:
        Rendered prompt string
    """
    template_path = Path(__file__).parent / "prompts" / template_name
    logger.debug(f"Loading template from: {template_path}")

    assert template_path.exists(), (
        f"Template file not found at {template_path}. "
        f"Ensure '{template_name}' exists in the prompts directory."
    )
    assert template_path.is_file(), (
        f"Template path {template_path} exists but is not a file. "
        f"Check that '{template_name}' is a regular file, not a directory."
    )

    with template_path.open() as f:
        template_content = f.read()

    assert template_content.strip(), (
        f"Template file {template_path} is empty or contains only whitespace. "
        f"The template must contain prompt instructions."
    )

    logger.debug(f"Template loaded successfully, length: {len(template_content)} chars")

    # Render the template with provided context
    template = Template(template_content)
    rendered_prompt = template.render(**context)

    assert rendered_prompt.strip(), (
        f"Rendered template resulted in empty content. "
        f"Check the Jinja2 template syntax in {template_name}."
    )

    logger.debug(
        f"Template rendered with {len(context)} variables, "
        f"final prompt length: {len(rendered_prompt)} chars"
    )
    return rendered_prompt


async def run_agent(
    agent: Agent[T], prompt: str, expected_type: type[T], operation_name: str
) -> T:
    """Run an AI agent with a prompt and validate the output.

    Args:
        agent: The pydantic-ai Agent to run
        prompt: The prompt to send to the agent
        expected_type: The expected output type for validation
        operation_name: Name of the operation for logging

    Returns:
        The validated output from the agent
    """
    logger.info(f"Starting {operation_name}")
    logger.debug(f"Prompt length: {len(prompt)} chars")

    # Get the AI to generate a response
    logger.info(f"Sending prompt to AI agent for {operation_name}")
    result = await agent.run(prompt)

    assert result is not None, (
        f"AI agent returned None result for {operation_name}. "
        f"Check API key configuration and network connectivity."
    )
    assert hasattr(result, "output"), (
        f"AI agent result missing 'output' attribute for {operation_name}. "
        f"Got result type: {type(result)}"
    )
    assert isinstance(result.output, expected_type), (
        f"AI agent output is not a {expected_type.__name__} instance for {operation_name}. "
        f"Got type: {type(result.output)}"
    )

    logger.success(f"AI agent completed {operation_name} successfully")

    # Log output details based on type
    output = result.output
    if hasattr(output, "__dict__"):
        for field_name, field_value in output.__dict__.items():
            if isinstance(field_value, str):
                logger.debug(f"{field_name} length: {len(field_value)} chars")
            elif isinstance(field_value, list):
                logger.debug(f"{field_name} count: {len(field_value)} items")

    return output
