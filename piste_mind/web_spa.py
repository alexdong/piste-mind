"""Single Page Application for piste-mind using FastHTML."""

import os
from typing import Any
from uuid import uuid4

from fasthtml.common import (
    A,
    Button,
    Div,
    Form,
    H1,
    H2,
    H3,
    Hidden,
    Input,
    Label,
    Link,
    Meta,
    P,
    Script,
    Style,
    Textarea,
    Title,
    fast_app,
)
from loguru import logger

from piste_mind.choices import generate_options
from piste_mind.feedback import generate_feedback
from piste_mind.models import Answer, AnswerChoice
from piste_mind.scenario import generate_scenario

# Create the FastHTML app with SPA configuration
app, rt = fast_app(
    hdrs=(
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
        Link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        Script(src="https://cdn.tailwindcss.com"),
        Script(src="https://unpkg.com/htmx.org@2.0.0"),
        Script(src="https://unpkg.com/htmx.org@2.0.0/dist/ext/preload.js"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Style("""
            /* Base styles */
            body { font-family: 'Inter', sans-serif; }
            
            /* SPA navigation */
            .spa-content { min-height: 100vh; }
            
            /* Page transitions */
            .page-enter {
                animation: pageEnter 0.3s ease-out;
            }
            @keyframes pageEnter {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Loading states */
            .loading-overlay {
                position: fixed;
                inset: 0;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.2s;
            }
            .htmx-request .loading-overlay {
                opacity: 1;
                pointer-events: auto;
            }
            
            /* Spinner */
            .spinner {
                width: 50px;
                height: 50px;
                border: 3px solid #f3f4f6;
                border-top: 3px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Option cards */
            .option-card {
                transition: all 0.2s ease;
                cursor: pointer;
            }
            .option-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            }
            .option-card.selected {
                background-color: #dbeafe;
                border-color: #3b82f6;
            }
            
            /* Feedback sections */
            .feedback-section {
                animation: slideIn 0.5s ease-out;
                animation-fill-mode: both;
            }
            .feedback-section:nth-child(1) { animation-delay: 0.1s; }
            .feedback-section:nth-child(2) { animation-delay: 0.2s; }
            .feedback-section:nth-child(3) { animation-delay: 0.3s; }
            .feedback-section:nth-child(4) { animation-delay: 0.4s; }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            /* Progress indicator */
            .progress-dot {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #e5e7eb;
                transition: all 0.3s;
            }
            .progress-dot.active {
                background: #3b82f6;
                transform: scale(1.2);
            }
            .progress-dot.completed {
                background: #10b981;
            }
            
            /* Responsive adjustments */
            @media (max-width: 640px) {
                .option-card {
                    font-size: 0.875rem;
                }
            }
        """),
    ),
    bodykw={"class": "bg-gray-50", "hx-ext": "preload"},
)


def format_scenario_text(text: str) -> list:
    """Convert scenario text to HTML paragraphs."""
    paragraphs = text.strip().split("\n\n")
    return [
        P(para.strip(), cls="mb-4 text-gray-700 leading-relaxed")
        for para in paragraphs
        if para.strip()
    ]


def create_nav_bar() -> Any:  # noqa: ANN401
    """Create navigation bar component."""
    return Div(
        Div(
            Div(
                H1("🤺 Piste Mind", cls="text-2xl font-bold text-white"),
                P("Tactical Epee Training", cls="text-blue-100 text-sm"),
                cls="flex items-center gap-4",
            ),
            Div(
                A(
                    "New Scenario",
                    href="/",
                    cls="px-4 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors",
                    hx_get="/scenario/new",
                    hx_target="#main-content",
                    hx_push_url="true",
                ),
                A(
                    "About",
                    href="/about",
                    cls="px-4 py-2 text-white hover:bg-blue-700 rounded-lg transition-colors",
                    hx_get="/about",
                    hx_target="#main-content",
                    hx_push_url="true",
                ),
                cls="flex gap-2",
            ),
            cls="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center",
        ),
        cls="bg-blue-600 shadow-lg sticky top-0 z-50",
    )


def create_progress_indicator(step: int) -> Any:  # noqa: ANN401
    """Create progress indicator showing current step."""
    steps = ["Scenario", "Choose", "Explain", "Feedback"]
    return Div(
        Div(
            *[
                Div(
                    Div(
                        cls=f"progress-dot {'active' if i == step else 'completed' if i < step else ''}"
                    ),
                    P(
                        name,
                        cls=f"text-xs mt-1 {'text-blue-600 font-medium' if i == step else 'text-gray-500'}",
                    ),
                    cls="flex flex-col items-center",
                )
                for i, name in enumerate(steps)
            ],
            cls="flex justify-between relative",
        ),
        Div(
            cls="absolute top-1.5 left-0 right-0 h-0.5 bg-gray-200 -z-10",
            style=f"background: linear-gradient(to right, #10b981 {step * 33}%, #e5e7eb {step * 33}%);",
        ),
        cls="max-w-md mx-auto mb-8 relative",
    )


@rt("/")
async def index() -> Any:  # noqa: ANN401
    """Main SPA container."""
    return (
        Title("Piste Mind - Tactical Epee Training"),
        Div(
            create_nav_bar(),
            # Loading overlay
            Div(Div(cls="spinner"), cls="loading-overlay"),
            # Main content area
            Div(
                id="main-content",
                cls="spa-content",
                hx_get="/scenario/new",
                hx_trigger="load",
                hx_swap="innerHTML",
            ),
            cls="min-h-screen bg-gray-50",
        ),
    )


@rt("/scenario/new")
async def new_scenario() -> Any:  # noqa: ANN401
    """Generate and display a new scenario."""
    scenario = await generate_scenario()
    choices = await generate_options(scenario)
    session_id = str(uuid4())

    # Store session data (in production, use a proper session store)
    app.state[session_id] = {
        "scenario": scenario,
        "choices": choices,
        "step": 0,
    }

    return Div(
        Div(
            create_progress_indicator(0),
            # Scenario Card
            Div(
                H2("Tactical Scenario", cls="text-2xl font-bold text-gray-800 mb-6"),
                Div(
                    *format_scenario_text(scenario.scenario),
                    cls="bg-white p-8 rounded-xl shadow-lg",
                ),
                cls="mb-8",
            ),
            # Continue button
            Div(
                Button(
                    "View Options →",
                    cls="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors",
                    hx_get=f"/scenario/{session_id}/options",
                    hx_target="#main-content",
                    hx_swap="innerHTML",
                    hx_push_url="true",
                ),
                cls="text-center",
            ),
            cls="max-w-4xl mx-auto p-6 page-enter",
        ),
        cls="min-h-screen",
    )


@rt("/scenario/{session_id}/options")
async def show_options(session_id: str) -> Any:  # noqa: ANN401
    """Display tactical options."""
    session = app.state.get(session_id)
    if not session:
        return Div(
            P("Session expired. Starting new scenario..."),
            hx_get="/scenario/new",
            hx_trigger="load delay:2s",
            hx_target="#main-content",
        )

    choices = session["choices"]
    session["step"] = 1

    return Div(
        Div(
            create_progress_indicator(1),
            H2("Your Tactical Options", cls="text-2xl font-bold text-gray-800 mb-6"),
            # Options grid
            Div(
                *[
                    Div(
                        Div(
                            Div(
                                f"{chr(65 + i)}",
                                cls="text-xl font-bold text-blue-600",
                            ),
                            cls="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0",
                        ),
                        P(option, cls="text-gray-700 leading-relaxed"),
                        cls="flex gap-4",
                        onclick=f"selectOption('{session_id}', {i}, this)",
                        data_option=str(i),
                        id=f"option-{i}",
                    )
                    for i, option in enumerate(choices.options)
                ],
                cls="space-y-4",
            ),
            # Hidden form for submission
            Form(
                Input(type="hidden", name="choice", id="selected-choice", value=""),
                Button(
                    "Continue to Explanation →",
                    type="submit",
                    id="continue-btn",
                    disabled=True,
                    cls="w-full mt-8 px-8 py-3 bg-gray-400 text-white font-medium rounded-lg transition-colors disabled:cursor-not-allowed",
                    hx_post=f"/scenario/{session_id}/explain",
                    hx_target="#main-content",
                    hx_swap="innerHTML",
                    hx_push_url="true",
                ),
            ),
            cls="max-w-4xl mx-auto p-6 page-enter",
        ),
        # Selection script
        Script("""
            function selectOption(sessionId, index, element) {
                // Remove previous selection
                document.querySelectorAll('.option-card').forEach(card => {
                    card.classList.remove('selected');
                });
                
                // Add selection to clicked option
                element.classList.add('option-card', 'selected');
                
                // Update hidden input
                document.getElementById('selected-choice').value = index;
                
                // Enable continue button
                const btn = document.getElementById('continue-btn');
                btn.disabled = false;
                btn.classList.remove('bg-gray-400');
                btn.classList.add('bg-blue-600', 'hover:bg-blue-700');
            }
            
            // Add option-card class to all options on load
            document.querySelectorAll('[data-option]').forEach(el => {
                el.classList.add('option-card', 'bg-white', 'p-6', 'rounded-xl', 'shadow-lg', 'border-2', 'border-gray-200');
            });
        """),
        cls="min-h-screen",
    )


@rt("/scenario/{session_id}/explain", methods=["POST"])
async def explain_choice(session_id: str, choice: str) -> Any:  # noqa: ANN401
    """Show explanation form."""
    session = app.state.get(session_id)
    if not session:
        return Div(
            P("Session expired. Starting new scenario..."),
            hx_get="/scenario/new",
            hx_trigger="load delay:2s",
            hx_target="#main-content",
        )

    session["choice"] = int(choice)
    session["step"] = 2
    chosen_option = session["choices"].options[int(choice)]

    return Div(
        Div(
            create_progress_indicator(2),
            # Show selected option
            Div(
                H3(
                    f"You selected: Option {chr(65 + int(choice))}",
                    cls="text-lg font-semibold text-gray-700 mb-2",
                ),
                P(chosen_option, cls="text-gray-600"),
                cls="bg-blue-50 p-6 rounded-lg mb-6",
            ),
            # Explanation form
            Div(
                H2(
                    "Explain Your Tactical Reasoning",
                    cls="text-2xl font-bold text-gray-800 mb-4",
                ),
                Form(
                    Textarea(
                        name="explanation",
                        placeholder="Why did you choose this option? What tactical principles guide your decision? Consider the score, time, and opponent's tendencies...",
                        required=True,
                        autofocus=True,
                        rows="6",
                        cls="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none resize-none",
                    ),
                    Button(
                        "Get Feedback →",
                        type="submit",
                        cls="w-full mt-4 px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors",
                        hx_post=f"/scenario/{session_id}/feedback",
                        hx_target="#main-content",
                        hx_swap="innerHTML",
                        hx_push_url="true",
                        hx_indicator=".loading-overlay",
                    ),
                    cls="bg-white p-8 rounded-xl shadow-lg",
                ),
            ),
            cls="max-w-4xl mx-auto p-6 page-enter",
        ),
        cls="min-h-screen",
    )


@rt("/scenario/{session_id}/feedback", methods=["POST"])
async def show_feedback(session_id: str, explanation: str) -> Any:  # noqa: ANN401
    """Generate and display feedback."""
    session = app.state.get(session_id)
    if not session:
        return Div(
            P("Session expired. Starting new scenario..."),
            hx_get="/scenario/new",
            hx_trigger="load delay:2s",
            hx_target="#main-content",
        )

    session["step"] = 3
    scenario = session["scenario"]
    choices = session["choices"]
    choice_index = session["choice"]

    # Create answer and generate feedback
    answer = Answer(choice=AnswerChoice(choice_index), explanation=explanation)
    feedback = await generate_feedback(scenario, choices, answer)

    return Div(
        Div(
            create_progress_indicator(3),
            # Your submission
            Div(
                H3("Your Analysis", cls="text-lg font-semibold text-gray-700 mb-2"),
                P(
                    f"Option {chr(65 + choice_index)}: {choices.options[choice_index]}",
                    cls="font-medium mb-2",
                ),
                P(explanation, cls="text-gray-600 italic"),
                cls="bg-gray-100 p-6 rounded-lg mb-6",
            ),
            # Coach's recommendation
            Div(
                H3(
                    "🎯 Coach's Recommendation",
                    cls="text-lg font-semibold text-green-700 mb-2",
                ),
                P(
                    f"Option {chr(65 + choices.recommend)}: {choices.options[choices.recommend]}",
                    cls="text-green-600",
                ),
                cls="bg-green-50 border-2 border-green-200 p-6 rounded-lg mb-8",
            ),
            # Feedback sections
            Div(
                Div(
                    H3(
                        "✓ Acknowledgment",
                        cls="text-xl font-semibold text-green-700 mb-3",
                    ),
                    P(feedback.acknowledgment, cls="text-gray-700 leading-relaxed"),
                    cls="bg-white p-6 rounded-xl shadow-lg feedback-section",
                ),
                Div(
                    H3(
                        "📊 Tactical Analysis",
                        cls="text-xl font-semibold text-blue-700 mb-3",
                    ),
                    P(
                        feedback.analysis,
                        cls="text-gray-700 leading-relaxed whitespace-pre-wrap",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-lg feedback-section",
                ),
                Div(
                    H3(
                        "🎯 Advanced Concepts",
                        cls="text-xl font-semibold text-purple-700 mb-3",
                    ),
                    P(
                        feedback.advanced_concepts,
                        cls="text-gray-700 leading-relaxed whitespace-pre-wrap",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-lg feedback-section",
                ),
                Div(
                    H3(
                        "🏆 Bridge to Mastery",
                        cls="text-xl font-semibold text-amber-700 mb-3",
                    ),
                    P(
                        feedback.bridge_to_mastery,
                        cls="text-gray-700 leading-relaxed whitespace-pre-wrap",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-lg feedback-section",
                ),
                cls="space-y-6 mb-8",
            ),
            # Action buttons
            Div(
                Button(
                    "Try Another Scenario",
                    cls="px-8 py-3 bg-gray-800 text-white font-medium rounded-lg hover:bg-gray-900 transition-colors",
                    hx_get="/scenario/new",
                    hx_target="#main-content",
                    hx_push_url="/",
                ),
                cls="text-center",
            ),
            cls="max-w-4xl mx-auto p-6 page-enter",
        ),
        cls="min-h-screen",
    )


@rt("/about")
async def about_page() -> Any:  # noqa: ANN401
    """About page."""
    return Div(
        Div(
            H1("About Piste Mind", cls="text-3xl font-bold text-gray-800 mb-6"),
            Div(
                P(
                    "Piste Mind is an interactive tactical training tool designed for competitive epee fencers. "
                    "It helps you develop real-time bout analysis skills through scenario-based tactical problems.",
                    cls="mb-4 text-gray-700 leading-relaxed",
                ),
                P(
                    "Each scenario presents a critical moment in a match with multiple strategic options. "
                    "Make your choice and receive detailed coaching feedback that breaks down the tactical principles at play.",
                    cls="mb-4 text-gray-700 leading-relaxed",
                ),
                H2("Features", cls="text-2xl font-semibold text-gray-800 mt-8 mb-4"),
                Div(
                    P(
                        "• Rich Tactical Scenarios with score, time, and opponent analysis",
                        cls="mb-2",
                    ),
                    P(
                        "• Multiple Strategic Paths with 4 distinct approaches per scenario",
                        cls="mb-2",
                    ),
                    P(
                        "• Expert Coaching Feedback with advanced tactical insights",
                        cls="mb-2",
                    ),
                    P(
                        "• Pattern Recognition Training to identify opponent vulnerabilities",
                        cls="mb-2",
                    ),
                    P(
                        "• Structured Learning from recognition to counter-strategy execution",
                        cls="mb-2",
                    ),
                    cls="text-gray-700 ml-4",
                ),
                H2(
                    "How It Works", cls="text-2xl font-semibold text-gray-800 mt-8 mb-4"
                ),
                Div(
                    P("1. Read a detailed bout scenario", cls="mb-2"),
                    P("2. Choose from 4 tactical approaches", cls="mb-2"),
                    P("3. Explain your reasoning", cls="mb-2"),
                    P("4. Receive comprehensive coaching feedback", cls="mb-2"),
                    P(
                        "5. Learn why certain tactics work and when to apply them",
                        cls="mb-2",
                    ),
                    cls="text-gray-700 ml-4",
                ),
                P(
                    "Built for fencers who know that touches are won in the mind before they're scored on the strip.",
                    cls="mt-6 text-gray-700 font-medium italic",
                ),
                cls="bg-white p-8 rounded-xl shadow-lg",
            ),
            Div(
                Button(
                    "Start Training",
                    cls="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors",
                    hx_get="/scenario/new",
                    hx_target="#main-content",
                    hx_push_url="/",
                ),
                cls="text-center mt-8",
            ),
            cls="max-w-4xl mx-auto p-6 page-enter",
        ),
        cls="min-h-screen",
    )


if __name__ == "__main__":
    import uvicorn

    # Initialize app state for sessions
    app.state = {}

    logger.info("Starting Piste Mind SPA...")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
