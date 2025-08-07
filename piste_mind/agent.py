"""Common AI agent utilities for piste-mind."""

import os
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

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


def get_model(model_type: ModelType) -> AnthropicModel:
    """Get the configured AI model.

    Args:
        model_type: The model type to use.

    Returns:
        Configured AnthropicModel instance
    """
    logger.info(f"Initializing AnthropicModel with {model_type.value}")
    return AnthropicModel(model_type.value)


def parse_model_type_from_env() -> ModelType:
    """Parse model type from PISTE_MIND_MODEL environment variable.

    Returns:
        Parsed ModelType from environment

    Raises:
        ValueError: If PISTE_MIND_MODEL contains invalid model type
    """
    env_model = os.getenv("PISTE_MIND_MODEL", "HAIKU").upper()
    try:
        return ModelType[env_model]
    except KeyError as e:
        err = ValueError(f"Invalid model type in PISTE_MIND_MODEL: '{env_model}'")
        err.add_note(f"Valid options: {', '.join(m.name for m in ModelType)}")
        err.add_note("Set PISTE_MIND_MODEL to one of: HAIKU, SONNET, or OPUS")
        raise err from e


# Configure the default AI model globally
# Parse model type from environment at module initialization
try:
    _default_model_type = parse_model_type_from_env()
except ValueError:
    # Fall back to HAIKU if environment variable is invalid
    logger.warning("Invalid PISTE_MIND_MODEL, using HAIKU as default")
    _default_model_type = ModelType.HAIKU

MODEL = get_model(_default_model_type)

# Type variable for generic output types
T = TypeVar("T", bound=BaseModel)


def load_prompt_template(template_name: str, **context: Any) -> str:  # noqa: ANN401
    """Load and render a Jinja2 template from the prompts directory.

    Args:
        template_name: Name of the template file (e.g., "scenario.j2")
        **context: Variables to pass to the template for rendering

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

    logger.debug("Rendering template with provided context")
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


def _parse_agent_result[T: BaseModel](
    result: object | None, expected_type: type[T], operation_name: str
) -> T:
    """Validate AI agent result and extract output.

    Args:
        result: The result from agent.run()
        expected_type: The expected output type
        operation_name: Name of the operation for error messages

    Returns:
        The validated output

    Raises:
        RuntimeError: If result is None
        AttributeError: If result missing 'output' attribute
        TypeError: If output is not expected type
    """
    if result is None:
        err = RuntimeError(f"AI agent returned None result for {operation_name}")
        err.add_note("Check API key configuration and network connectivity")
        err.add_note("Ensure the AI service is available and responding")
        raise err

    if not hasattr(result, "output"):
        err = AttributeError(
            f"AI agent result missing 'output' attribute for {operation_name}"
        )
        err.add_note(f"Got result type: {type(result)}")
        err.add_note(f"Result attributes: {dir(result)}")
        raise err

    if not isinstance(result.output, expected_type):
        err = TypeError(
            f"AI agent output is not a {expected_type.__name__} instance for {operation_name}"
        )
        err.add_note(f"Expected type: {expected_type.__name__}")
        err.add_note(f"Got type: {type(result.output)}")
        raise err

    return result.output


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

    logger.debug("Getting AI to generate response")
    logger.info(f"Sending prompt to AI agent for {operation_name}")
    result = await agent.run(prompt)

    logger.debug("Validating and extracting agent output")
    output = _parse_agent_result(result, expected_type, operation_name)
    logger.success(f"AI agent completed {operation_name} successfully")

    logger.debug("Logging output details")
    for field_name, field_value in output.__dict__.items():
        if isinstance(field_value, str):
            logger.debug(f"{field_name} length: {len(field_value)} chars")
        elif isinstance(field_value, list):
            logger.debug(f"{field_name} count: {len(field_value)} items")

    return output
