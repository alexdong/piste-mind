"""Data models for the piste-mind tactical training tool."""
# pyright: reportMissingParameterType=false
# mypy: ignore-errors

import random
from dataclasses import dataclass
from enum import IntEnum

from pydantic import BaseModel, Field

# Constants
NUM_OPTIONS = 4


@dataclass
class ProfileOption:
    """A single profile characteristic with its 4 options"""

    category: str
    name: str
    options: list[str]  # [A, B, C, D] in order


# Define all profile options as constants
PROFILE_OPTIONS = [
    # Distance & Mobility
    ProfileOption(
        "distance_mobility", "preferred_distance", ["Very-long", "Long", "Mid", "Short"]
    ),
    ProfileOption(
        "distance_mobility",
        "footwork_rhythm",
        ["Bouncy", "Flat-glide", "Pause-burst", "Mixed/random"],
    ),
    ProfileOption(
        "distance_mobility",
        "advance_style",
        ["Big strides", "Micro-steps", "Hop-bounce", "Glide-pause"],
    ),
    ProfileOption(
        "distance_mobility",
        "retreat_style",
        ["Fast bounce", "Smooth glide", "Slow-parry-retreat", "Sudden stop & counter"],
    ),
    ProfileOption(
        "distance_mobility",
        "acceleration_pattern",
        ["Sudden burst", "Gradual build", "Flat-paced", "Cyclic bursts"],
    ),
    ProfileOption(
        "distance_mobility",
        "distance_attack_trigger",
        ["Shoots from long", "Mid-launch", "Waits close", "Opportunistic/variable"],
    ),
    # Initiative & Attack Construction
    ProfileOption(
        "initiative_attack",
        "opening_action",
        ["Step-lunge", "Fleche", "Slow prep", "Counter-attack"],
    ),
    ProfileOption(
        "initiative_attack",
        "attack_initiative",
        ["Constant aggressor", "Balanced", "Mainly reactive", "Rare-but-explosive"],
    ),
    ProfileOption(
        "initiative_attack",
        "entry_footwork",
        ["Clean step-lunge", "Step-step-lunge", "Fleche/run", "No-prep hit"],
    ),
    ProfileOption(
        "initiative_attack",
        "flick_angled_hits",
        ["Very frequent", "Occasional", "Rare", "Never"],
    ),
    ProfileOption(
        "initiative_attack",
        "point_in_line_use",
        ["Frequent", "Occasional", "Rare", "Never"],
    ),
    ProfileOption(
        "initiative_attack",
        "compound_depth",
        ["Multi-feint chains", "Single feint", "Direct only", "Broken-timing hits"],
    ),
    # Defence & Blade Reaction
    ProfileOption(
        "defence_blade",
        "defensive_reflex",
        ["Parry-riposte", "Distance pull", "Counter-attack", "In-quartata"],
    ),
    ProfileOption(
        "defence_blade",
        "primary_parry_line",
        ["High-outside", "High-inside", "Low-outside", "Low-inside"],
    ),
    ProfileOption(
        "defence_blade",
        "parry_timing",
        ["Early/pre-empt", "On-time", "Late/drag", "Seldom parries"],
    ),
    ProfileOption(
        "defence_blade",
        "riposte_style",
        ["Direct", "Angulated", "Disengage", "Delayed walk-forward"],
    ),
    ProfileOption(
        "defence_blade",
        "remise_redouble",
        [
            "Instant remise",
            "Footwork chase",
            "Rare second action",
            "Multi-phase pursuit",
        ],
    ),
    ProfileOption(
        "defence_blade",
        "reaction_to_beat",
        ["Opens/panics", "Holds strong", "Disengages", "Beats back/counters"],
    ),
    ProfileOption(
        "defence_blade",
        "counter_time_habit",
        ["Very often", "Regular", "Occasional", "Never"],
    ),
    # Adaptability & Tempo
    ProfileOption(
        "adaptability_tempo",
        "setup_vs_direct",
        ["Pure direct", "Simple 2-phase", "Multi-phase 3+", "Unpredictable mix"],
    ),
    ProfileOption(
        "adaptability_tempo",
        "adaptability_speed",
        ["Very slow >4 touches", "Moderate 2-3", "Fast 1", "Constantly shifting"],
    ),
    ProfileOption(
        "adaptability_tempo",
        "tempo_preference",
        ["Slow build", "Medium", "Frenetic", "Variable"],
    ),
    ProfileOption(
        "adaptability_tempo",
        "feint_susceptibility",
        ["Bites easily", "Sometimes", "Rarely", "Reads everything"],
    ),
    # Psychological & Physical
    ProfileOption(
        "psychological_physical",
        "score_pressure",
        [
            "Lead=slow/Trail=rush",
            "Lead=rush/Trail=cautious",
            "Both conservative",
            "Both aggressive",
        ],
    ),
    ProfileOption(
        "psychological_physical",
        "psychological_temperature",
        ["Ice-calm", "Focused", "Nervous/anxious", "Volatile"],
    ),
    ProfileOption(
        "psychological_physical",
        "cardio_recovery",
        ["Winded quickly", "Average", "Fresh late", "Fades gradually"],
    ),
    ProfileOption(
        "psychological_physical",
        "risk_tolerance",
        ["High-risk shooter", "Balanced", "Ultra-safe", "Situational gambler"],
    ),
    # Close-quarters & Strip Craft
    ProfileOption(
        "close_quarters_strip",
        "favorite_line_target",
        ["High-outside", "High-inside", "Low-outside", "Low-inside"],
    ),
    ProfileOption(
        "close_quarters_strip",
        "in_fight_skill",
        ["Dominates grips", "Competent", "Avoids clinch", "Loses clearly"],
    ),
    ProfileOption(
        "close_quarters_strip",
        "edge_of_strip_behavior",
        [
            "Attacks forward",
            "Stops & counters",
            "Flees/steps off",
            "Side-slides along line",
        ],
    ),
    # Discipline & Tells
    ProfileOption(
        "discipline_tells",
        "blade_tell",
        ["Drops tip", "Big circle", "Twitch before lunge", "No obvious tell"],
    ),
    ProfileOption(
        "discipline_tells",
        "penalty_history",
        ["Corps-à-corps", "Covering", "Early start", "None noted"],
    ),
]


# Situational options - contexts with score possibilities
SITUATIONAL_CONTEXTS = [
    ProfileOption(
        "situational",
        "pool_bout",
        [
            "leading 4-2",
            "trailing 2-3",
            "tied 3-3",
            "leading 3-1",
            "trailing 1-4",
            "tied 2-2",
            "leading 4-3",
        ],
    ),
    ProfileOption(
        "situational",
        "de_round_32",
        [
            "leading 14-11",
            "trailing 8-12",
            "tied 10-10",
            "leading 9-7",
            "trailing 4-8",
            "tied 13-13",
            "leading 7-5",
            "trailing 11-14",
        ],
    ),
    ProfileOption(
        "situational",
        "de_round_8",
        [
            "leading 14-11",
            "trailing 8-12",
            "tied 10-10",
            "leading 9-7",
            "trailing 4-8",
            "tied 13-13",
            "leading 7-5",
            "trailing 11-14",
        ],
    ),
    ProfileOption(
        "situational",
        "semi_final",
        [
            "leading 14-11",
            "trailing 8-12",
            "tied 10-10",
            "leading 9-7",
            "trailing 4-8",
            "tied 13-13",
            "leading 7-5",
            "trailing 11-14",
        ],
    ),
]


# Helper function to find ProfileOption by name
def find_profile_option(
    name: str, options_list: list[ProfileOption]
) -> ProfileOption | None:
    """Find a ProfileOption by its name from a list of options."""
    for option in options_list:
        if option.name == name:
            return option
    return None


# Time remaining - will be generated dynamically
def generate_time_remaining() -> str:
    """Generate dynamic time remaining strings with various formats."""
    # Format choices
    formats = [
        # Full minutes
        "3:00 remaining",
        "2:00 remaining",
        "1:00 remaining",
        # Partial minutes
        "2:45 remaining",
        "2:30 remaining",
        "2:15 remaining",
        "1:45 remaining",
        "1:30 remaining",
        "1:15 remaining",
        # Less than a minute
        "90 seconds left",
        "75 seconds left",
        "60 seconds left",
        "45 seconds left",
        "30 seconds left",
        # Final countdown
        "final 20 seconds",
        "final 15 seconds",
        "final 10 seconds",
        # Critical moments
        "last 45 seconds",
        "under 2 minutes",
        "under 1 minute",
        "clock winding down",
    ]
    return random.choice(formats)


# Fencer self-evaluation options
SELF_EVALUATION_OPTIONS = [
    ProfileOption(
        "self_state",
        "emotional_arousal",
        [
            "Hot - adrenaline spiking, impulsive actions",
            "Optimal - energised yet calm",
            "Cool - slightly detached, reactions slowed",
            "Flat - emotionally numb, no urgency",
        ],
    ),
    ProfileOption(
        "self_state",
        "physical_energy",
        [
            "Over-charged - muscles jittery, rigid",
            "Primed - loose, springy legs",
            "Lagging - heaviness, slight fatigue",
            "Drained - legs burning, slow recoveries",
        ],
    ),
    ProfileOption(
        "self_state",
        "mental_focus",
        [
            "Scattered - distracted by crowd/score",
            "Sharp - single-task focus on touch",
            "Narrow - locked on weapon tip only",
            "Foggy - mind wandering, late reads",
        ],
    ),
    ProfileOption(
        "self_state",
        "tactical_clarity",
        [
            "Tunnel-visioned - forcing one idea",
            "Dynamic Plan - aware of multiple lines",
            "Reactive-only - waiting to see",
            "Uncertain - no plan or reaction",
        ],
    ),
    ProfileOption(
        "self_state",
        "distance_sense",
        [
            "Too Close - crowding, blade jams",
            "Balanced - can hit/abort at will",
            "Too Far - always just short",
            "Undefined - distance surprises you",
        ],
    ),
    ProfileOption(
        "self_state",
        "tempo_awareness",
        [
            "Rushing - stepping into opponent's rhythm",
            "In-sync - dictating start-stop flow",
            "Lagging Beat - counter-tempo late",
            "Tempo-blind - no feel for rhythm",
        ],
    ),
    ProfileOption(
        "self_state",
        "risk_appetite",
        [
            "Gambling - low-percentage lunges",
            "Calculated - odds assessed every action",
            "Over-cautious - passing on good openings",
            "Frozen - unwilling to commit",
        ],
    ),
    ProfileOption(
        "self_state",
        "confidence_level",
        [
            "Cocky - under-estimating danger",
            "Grounded - belief matched to facts",
            "Doubting - second-guessing choices",
            "Defeatist - expecting to lose",
        ],
    ),
    ProfileOption(
        "self_state",
        "breathing_control",
        [
            "Panting - shallow chest breaths",
            "Controlled - steady diaphragmatic",
            "Irregular - holds breath on attacks",
            "Gasping - breathing dictates pace",
        ],
    ),
    ProfileOption(
        "self_state",
        "visual_focus",
        [
            "Hyper-zoom - staring at point only",
            "Soft-wide - blade, arm, body & piste",
            "Peripheral-loss - see body, not tip",
            "Blurred - eyes tired, focus slips",
        ],
    ),
]


class ProfileChoice(IntEnum):
    """Valid choices for profile characteristics (0-3 for indexing)."""

    A = 0
    B = 1
    C = 2
    D = 3


class OpponentProfile(BaseModel):
    """Complete opponent profile with all 32 tactical characteristics."""

    # Distance & Mobility
    preferred_distance: ProfileChoice
    footwork_rhythm: ProfileChoice
    advance_style: ProfileChoice
    retreat_style: ProfileChoice
    acceleration_pattern: ProfileChoice
    distance_attack_trigger: ProfileChoice

    # Initiative & Attack Construction
    opening_action: ProfileChoice
    attack_initiative: ProfileChoice
    entry_footwork: ProfileChoice
    flick_angled_hits: ProfileChoice
    point_in_line_use: ProfileChoice
    compound_depth: ProfileChoice

    # Defence & Blade Reaction
    defensive_reflex: ProfileChoice
    primary_parry_line: ProfileChoice
    parry_timing: ProfileChoice
    riposte_style: ProfileChoice
    remise_redouble: ProfileChoice
    reaction_to_beat: ProfileChoice
    counter_time_habit: ProfileChoice

    # Adaptability & Tempo
    setup_vs_direct: ProfileChoice
    adaptability_speed: ProfileChoice
    tempo_preference: ProfileChoice
    feint_susceptibility: ProfileChoice

    # Psychological & Physical
    score_pressure: ProfileChoice
    psychological_temperature: ProfileChoice
    cardio_recovery: ProfileChoice
    risk_tolerance: ProfileChoice

    # Close-quarters & Strip Craft
    favorite_line_target: ProfileChoice
    in_fight_skill: ProfileChoice
    edge_of_strip_behavior: ProfileChoice

    # Discipline & Tells
    blade_tell: ProfileChoice
    penalty_history: ProfileChoice


class FencerSelfEvaluation(BaseModel):
    """Fencer's self-state evaluation across 10 dimensions."""

    emotional_arousal: ProfileChoice
    physical_energy: ProfileChoice
    mental_focus: ProfileChoice
    tactical_clarity: ProfileChoice
    distance_sense: ProfileChoice
    tempo_awareness: ProfileChoice
    risk_appetite: ProfileChoice
    confidence_level: ProfileChoice
    breathing_control: ProfileChoice
    visual_focus: ProfileChoice


class SituationalFactors(BaseModel):
    """Random situational factors for scenario generation."""

    context: str
    score: str
    time_remaining: str


class ScenarioContext(BaseModel):
    """Complete context for scenario generation including all tactical factors."""

    opponent_profile: OpponentProfile
    fencer_self_evaluation: FencerSelfEvaluation
    situational_factors: SituationalFactors


class Scenario(BaseModel):
    """A tactical epee scenario without options."""

    scenario: str = Field(
        ...,
        description="Detailed tactical scenario including score, time, and opponent analysis",
        min_length=100,
    )


class Choices(BaseModel):
    """Strategic choices for a tactical scenario."""

    options: list[str] = Field(
        ...,
        description="Four distinct tactical approaches to the scenario",
        min_length=NUM_OPTIONS,
        max_length=NUM_OPTIONS,
    )
    recommend: int = Field(
        ...,
        description="Index (0-3) of the best tactical option for this scenario",
        ge=0,
        le=3,
    )


class AnswerChoice(IntEnum):
    """Valid answer choices for tactical scenarios."""

    A = 0
    B = 1
    C = 2
    D = 3

    def __str__(self) -> str:
        """Return the letter representation."""
        return self.name


class Answer(BaseModel):
    """A student's response to a tactical scenario."""

    choice: AnswerChoice = Field(
        ..., description="The chosen tactical option (A, B, C, or D)"
    )
    explanation: str = Field(
        ...,
        description="Student's reasoning for their tactical choice",
        min_length=20,
    )


class Feedback(BaseModel):
    """Coaching feedback on a student's tactical decision."""

    # Rubric scores (1-10 for each criterion)
    score_clock_pressure: int = Field(
        ...,
        description="Score for clock pressure consideration (1-10)",
        ge=1,
        le=10,
    )
    score_touch_quality: int = Field(
        ...,
        description="Score for touch quality risk assessment (1-10)",
        ge=1,
        le=10,
    )
    score_initiative: int = Field(
        ...,
        description="Score for initiative ownership (1-10)",
        ge=1,
        le=10,
    )
    score_opponent_habits: int = Field(
        ...,
        description="Score for exploiting opponent habits (1-10)",
        ge=1,
        le=10,
    )
    score_skill_alignment: int = Field(
        ...,
        description="Score for alignment with current skills (1-10)",
        ge=1,
        le=10,
    )
    score_piste_geography: int = Field(
        ...,
        description="Score for piste geography advantage (1-10)",
        ge=1,
        le=10,
    )
    score_external_factors: int = Field(
        ...,
        description="Score for considering refereeing/venue conditions (1-10)",
        ge=1,
        le=10,
    )
    score_fatigue_management: int = Field(
        ...,
        description="Score for fatigue and resource management (1-10)",
        ge=1,
        le=10,
    )
    score_information_value: int = Field(
        ...,
        description="Score for information value consideration (1-10)",
        ge=1,
        le=10,
    )
    score_psychological_momentum: int = Field(
        ...,
        description="Score for psychological momentum (1-10)",
        ge=1,
        le=10,
    )

    # Coaching content
    acknowledgment: str = Field(
        ...,
        description="Recognition of what the student correctly identified",
        min_length=50,
    )
    analysis: str = Field(
        ...,
        description="Deep tactical analysis of why the choice works",
        min_length=200,
    )
    advanced_concepts: str = Field(
        ...,
        description="Related tactical concepts and execution details",
        min_length=100,
    )
    bridge_to_mastery: str = Field(
        ...,
        description="Connection to championship-level thinking",
        min_length=100,
    )


def generate_random_profile() -> OpponentProfile:
    """Generate a random opponent profile."""
    profile_data = {}
    for option in PROFILE_OPTIONS:
        # Randomly choose A, B, C, or D for each characteristic
        profile_data[option.name] = random.choice(list(ProfileChoice))
    return OpponentProfile(**profile_data)  # ty: ignore[missing-argument]


def generate_random_self_evaluation() -> FencerSelfEvaluation:
    """Generate a random fencer self-evaluation."""
    eval_data = {}
    for option in SELF_EVALUATION_OPTIONS:
        # Randomly choose A, B, C, or D for each dimension
        eval_data[option.name] = random.choice(list(ProfileChoice))
    return FencerSelfEvaluation(**eval_data)  # ty: ignore[missing-argument]


def generate_random_situational_factors() -> SituationalFactors:
    """Generate random situational factors."""
    # Pick a random context
    context_option = random.choice(SITUATIONAL_CONTEXTS)
    context = context_option.name.replace("_", " ")

    # Pick a random score for that context
    score = random.choice(context_option.options)

    # Generate random time
    time_remaining = generate_time_remaining()

    return SituationalFactors(
        context=context, score=score, time_remaining=time_remaining
    )


def construct_context(context: ScenarioContext) -> str:
    """Construct a complete scenario context as a formatted string."""
    lines = []
    lines.append("=" * 80)
    lines.append("COMPLETE SCENARIO CONTEXT")
    lines.append("=" * 80)

    # Situational factors
    lines.append("\n📍 SITUATION:")
    lines.append(f"   Context: {context.situational_factors.context}")
    lines.append(f"   Score: {context.situational_factors.score}")
    lines.append(f"   Time: {context.situational_factors.time_remaining}")

    # Opponent profile
    lines.append("\n🤺 OPPONENT PROFILE:")
    for option in PROFILE_OPTIONS:
        value = getattr(context.opponent_profile, option.name)
        description = option.options[value]
        category = option.category.replace("_", " ").title()
        if option == PROFILE_OPTIONS[0] or (
            PROFILE_OPTIONS.index(option) > 0
            and option.category
            != PROFILE_OPTIONS[PROFILE_OPTIONS.index(option) - 1].category
        ):
            lines.append(f"\n   {category}:")
        lines.append(f"      {option.name.replace('_', ' ').title()}: {description}")

    # Self-evaluation
    lines.append("\n💭 YOUR CURRENT STATE:\n")
    for option in SELF_EVALUATION_OPTIONS:
        value = getattr(context.fencer_self_evaluation, option.name)
        description = option.options[value]
        lines.append(f"   {option.name.replace('_', ' ').title()}: {description}")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def generate_full_context() -> str:
    """Generate a complete random context and return it as a formatted string."""
    # Generate random components
    opponent = generate_random_profile()
    self_eval = generate_random_self_evaluation()
    situational = generate_random_situational_factors()

    # Create full context
    context = ScenarioContext(
        opponent_profile=opponent,
        fencer_self_evaluation=self_eval,
        situational_factors=situational,
    )

    # Construct and return the string representation
    return construct_context(context)


if __name__ == "__main__":
    # Generate a complete random scenario context
    print("Generating random tactical scenario context...")

    # Generate and display full context
    context_str = generate_full_context()
    print("\n" + context_str)
