"""Test the context generation and template integration."""

import sys
from pathlib import Path

import jinja2

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from piste_mind.models import generate_full_context


def test_context_generation() -> None:
    """Test that context generation produces valid output."""
    context = generate_full_context()

    # Verify basic structure
    min_context_length = 1000
    assert len(context) > min_context_length  # Should be substantial
    assert "COMPLETE SCENARIO CONTEXT" in context
    assert "SITUATION:" in context
    assert "OPPONENT PROFILE:" in context
    assert "YOUR CURRENT STATE:" in context
    assert "Context:" in context
    assert "Score:" in context
    assert "Time:" in context


def test_template_integration() -> None:
    """Test that the template renders correctly with generated context."""
    context = generate_full_context()

    # Load and render template
    template_dir = Path("piste_mind/prompts")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template("scenario.j2")
    rendered = template.render(context=context)

    # Verify the template rendered successfully
    min_rendered_length = 5000
    assert len(rendered) > min_rendered_length  # Should be substantial with context
    assert "Tactical Epee Problem Generation Prompt" in rendered
    assert "Generated Context for This Scenario:" in rendered
    assert context in rendered  # The full context should be embedded

    # Verify the context is properly positioned in the template
    context_start = rendered.find("## Generated Context for This Scenario:")
    assert context_start > 0

    # The context should appear after the context marker
    embedded_context_start = rendered.find(context, context_start)
    assert embedded_context_start > context_start


def test_context_format() -> None:
    """Test that the context format is consistent and well-structured."""
    context = generate_full_context()

    lines = context.split("\n")

    # Should have section headers
    section_headers = [line for line in lines if line.startswith(("📍", "🤺", "💭"))]
    expected_sections = 3  # SITUATION, OPPONENT PROFILE, YOUR CURRENT STATE
    assert len(section_headers) == expected_sections

    # Should have proper separators
    separator_lines = [line for line in lines if line == "=" * 80]
    expected_separators = 3  # Top, middle (none), and bottom separators
    assert len(separator_lines) == expected_separators
