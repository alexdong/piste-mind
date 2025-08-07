"""Web interface for piste-mind using FastHTML."""

import os
from typing import Any

from fasthtml.common import (
    H1,
    H2,
    H3,
    Button,
    Div,
    Form,
    Hidden,
    Input,
    Label,
    Meta,
    P,
    Script,
    Style,
    Textarea,
    Title,
    fast_app,
)
from loguru import logger

from piste_mind.agent import ModelType, get_model, parse_model_type_from_env
from piste_mind.db.service import SessionService
from piste_mind.editor import edit_content
from piste_mind.models import AnswerChoice, Challenge

# Initialize session service
session_service = SessionService()

# Get model configuration
try:
    model_type = parse_model_type_from_env()
except ValueError:
    model_type = ModelType.HAIKU
model = get_model(model_type)

# Create the FastHTML app
app, rt = fast_app(
    hdrs=(
        Script(src="https://cdn.tailwindcss.com"),
        Script(src="https://unpkg.com/htmx.org@2.0.0"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Style("""
            [x-cloak] { display: none !important; }
            .htmx-indicator { display: none; }
            .htmx-request .htmx-indicator { display: inline-block; }
            .htmx-request.htmx-indicator { display: inline-block; }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .spinner {
                border: 2px solid #f3f3f3;
                border-top: 2px solid #3498db;
                border-radius: 50%;
                width: 16px;
                height: 16px;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 8px;
                vertical-align: middle;
            }
            @keyframes fade-in {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .animate-fade-in {
                animation: fade-in 0.5s ease-out;
            }
            @keyframes slide-down {
                from {
                    opacity: 0;
                    max-height: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    max-height: 500px;
                    transform: translateY(0);
                }
            }
            .animate-slide-down {
                animation: slide-down 0.3s ease-out;
                overflow: hidden;
            }
            /* Custom radio button styles */
            input[type="radio"]:checked + div .option-circle {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
            input[type="radio"]:checked + div .option-letter {
                color: white;
            }
            /* Progress bar animation */
            @keyframes progress {
                0% { width: 0%; }
                30% { width: 30%; }
                60% { width: 60%; }
                90% { width: 90%; }
                100% { width: 100%; }
            }
            .progress-bar {
                animation: progress 3s ease-in-out infinite;
            }
        """),
    ),
    bodykw={"class": "bg-gray-50"},
)


def format_scenario_text(text: str) -> list:
    """Convert scenario text to HTML paragraphs."""
    # Split by double newlines for paragraphs
    paragraphs = text.strip().split("\n\n")
    return [
        P(para.strip(), cls="mb-4 text-gray-700 leading-relaxed")
        for para in paragraphs
        if para.strip()
    ]


@rt("/")
async def index() -> Any:  # noqa: ANN401
    """Main page - shows scenario and options."""
    logger.info("Creating new training session")

    # Create new session
    session = await session_service.create_session("web", model_type.name.lower())

    # Generate scenario and choices
    logger.debug("Generating scenario and options for web interface")
    session = await session_service.generate_scenario_for_session(session.session_id)

    # Edit for readability
    assert session.scenario is not None, "Scenario should be generated"
    assert session.choices is not None, "Choices should be generated"
    challenge = Challenge(scenario=session.scenario, choices=session.choices)
    edited_challenge = await edit_content(challenge, model)

    return Title("Piste Mind - Tactical Epee Training"), Div(
        Div(
            H1("🤺 Tactical Scenario", cls="text-3xl font-bold text-gray-800 mb-8"),
            # Scenario Card with proper paragraphs
            Div(
                Div(*format_scenario_text(edited_challenge.scenario.scenario)),
                cls="bg-white p-8 rounded-xl shadow-lg mb-8",
            ),
            # Options
            H2("Your Choices", cls="text-2xl font-semibold text-gray-800 mb-6"),
            Div(
                *[
                    Label(
                        Input(
                            type="radio",
                            name="option",
                            value=str(i),
                            id=f"option-{i}",
                            cls="peer sr-only",
                            hx_post=f"/select-option/{session.session_id}",
                            hx_target="#explanation-area",
                            hx_swap="outerHTML",
                            hx_trigger="change",
                            hx_indicator="#loading",
                            hx_include="#explanation-text",
                        ),
                        Div(
                            Div(
                                Div(
                                    f"{chr(65 + i)}",
                                    cls="option-letter text-lg font-bold text-blue-600",
                                ),
                                cls="option-circle flex items-center justify-center w-10 h-10 rounded-full border-2 border-gray-300 transition-all duration-200",
                            ),
                            Div(
                                edited_challenge.choices.options[i],
                                cls="flex-1 text-gray-700",
                            ),
                            cls="flex items-start gap-4",
                        ),
                        for_=f"option-{i}",
                        cls="block mb-4 p-5 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-gray-300 hover:bg-gray-50 has-[:checked]:border-blue-500 has-[:checked]:bg-blue-50 transition-all duration-200",
                    )
                    for i in range(len(edited_challenge.choices.options))
                ],
                cls="bg-white p-8 rounded-xl shadow-lg mb-8",
            ),
            # Loading indicator
            Div(
                "Loading...",
                id="loading",
                cls="htmx-indicator fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg",
            ),
            # Area for explanation form (will be inserted here)
            Div(id="explanation-area"),
            cls="max-w-4xl mx-auto p-6 bg-gray-50 min-h-screen",
        )
    )


@rt("/select-option/{session_id}", methods=["POST"])
async def select_option(session_id: str, option: str, explanation: str = "") -> Any:  # noqa: ANN401
    """Handle option selection and show explanation textarea."""
    # Record the choice
    choice = AnswerChoice(int(option))
    await session_service.record_choice(session_id, choice)

    return Div(
        Div(
            H3(
                "Explain your tactical reasoning",
                cls="text-xl font-semibold text-gray-800 mb-4",
            ),
            Form(
                Textarea(
                    explanation,  # Preserve the content
                    name="explanation",
                    id="explanation-text",
                    placeholder="Why did you choose this option? What tactical principles guide your decision?",
                    required=True,
                    autofocus=bool(not explanation),
                    cls="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none resize-none h-32",
                ),
                Hidden(name="choice_index", value=option),
                Button(
                    Div(cls="spinner htmx-indicator"),
                    "Submit",
                    type="submit",
                    cls="w-full mt-4 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed",
                    hx_disabled_elt="this",
                    onclick="this.disabled = true; this.form.requestSubmit();",
                ),
                hx_post=f"/submit-explanation/{session_id}",
                hx_target="#explanation-area",
                hx_swap="outerHTML",
                hx_trigger="submit",
            ),
            cls="bg-white p-8 rounded-xl shadow-lg animate-slide-down",
        ),
        id="explanation-area",
        cls="mb-8",
    )


@rt("/submit-explanation/{session_id}", methods=["POST"])
async def submit_explanation(session_id: str, explanation: str) -> Any:  # noqa: ANN401
    """Handle explanation submission and show feedback."""
    # Record the explanation
    await session_service.record_explanation(session_id, explanation)

    # Generate feedback
    session = await session_service.generate_feedback_for_session(session_id)

    # Complete the session
    await session_service.complete_session(session_id)

    # Edit feedback for readability
    assert session.feedback is not None, "Feedback should be generated"
    assert session.user_answer is not None, "User answer should exist"
    assert session.choices is not None, "Choices should exist"
    edited_feedback = await edit_content(session.feedback, model)

    # Return the full feedback display
    return Div(
        # Show submitted explanation (read-only) with disabled button
        Div(
            Div(
                H3(
                    f"Your Choice: {session.user_answer.choice}",
                    cls="text-lg font-semibold text-gray-700",
                ),
                P(session.user_answer.explanation, cls="mt-2 text-gray-600 italic"),
                Button(
                    "✓ Submitted",
                    type="button",
                    disabled=True,
                    cls="w-full mt-4 px-6 py-3 bg-gray-400 text-white font-semibold rounded-lg cursor-not-allowed",
                ),
            ),
            cls="bg-white p-8 rounded-xl shadow-lg mb-6",
        ),
        # Feedback section
        Div(
            # Recommendation
            Div(
                H3(
                    f"Coach's Recommendation: {chr(65 + session.choices.recommend)}",
                    cls="text-lg font-semibold text-green-800 mb-2",
                ),
                P(
                    session.choices.options[session.choices.recommend],
                    cls="text-green-700",
                ),
                cls="bg-green-50 border-2 border-green-200 p-6 rounded-lg mb-6",
            ),
            # Feedback cards
            Div(
                H3("✓ Acknowledgment", cls="text-xl font-semibold text-green-700 mb-3"),
                P(edited_feedback.acknowledgment, cls="text-gray-700 leading-relaxed"),
                cls="bg-white p-6 rounded-xl shadow-lg mb-6",
            ),
            Div(
                H3(
                    "📊 Tactical Analysis",
                    cls="text-xl font-semibold text-blue-700 mb-3",
                ),
                P(
                    edited_feedback.analysis,
                    cls="text-gray-700 leading-relaxed whitespace-pre-wrap",
                ),
                cls="bg-white p-6 rounded-xl shadow-lg mb-6",
            ),
            Div(
                H3(
                    "🎯 Advanced Concepts",
                    cls="text-xl font-semibold text-purple-700 mb-3",
                ),
                P(
                    edited_feedback.advanced_concepts,
                    cls="text-gray-700 leading-relaxed whitespace-pre-wrap",
                ),
                cls="bg-white p-6 rounded-xl shadow-lg mb-6",
            ),
            Div(
                H3(
                    "🏆 Bridge to Mastery",
                    cls="text-xl font-semibold text-amber-700 mb-3",
                ),
                P(
                    edited_feedback.bridge_to_mastery,
                    cls="text-gray-700 leading-relaxed whitespace-pre-wrap",
                ),
                cls="bg-white p-6 rounded-xl shadow-lg mb-6",
            ),
            # New scenario button
            Div(
                Button(
                    "Try Another Scenario",
                    onclick="window.location.reload()",
                    cls="px-8 py-3 bg-gray-800 text-white font-semibold rounded-lg hover:bg-gray-900 transition-colors duration-200",
                ),
                cls="text-center mt-8",
            ),
            cls="animate-fade-in",
        ),
        id="explanation-area",
        cls="mb-8",
    )


if __name__ == "__main__":
    import uvicorn

    logger.debug("Setting up logging for web interface")
    logger.info("Starting Piste Mind web interface...")

    logger.debug("Getting port from environment or using default")
    port = int(os.getenv("PORT", "8000"))

    logger.debug(f"Running server on host 0.0.0.0 port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
