"""Test fixtures for development and testing."""

import textwrap

from piste_mind.models import (
    Answer,
    AnswerChoice,
    Challenge,
    Choices,
    Feedback,
    Scenario,
)


def scenario_fixture() -> Scenario:
    """Return a test scenario for development."""
    return Scenario(
        scenario=textwrap.dedent("""
        The bout has reached a critical moment in the DE round of 8.

        You're trailing 8-12 with only 20 seconds remaining, and the psychological weight of potential elimination is crushing.

        Your opponent, a technically disciplined fencer with a very-long distance preference, has been methodically controlling the bout's rhythm through calculated glide-pause advances and smooth retreats.

        Your current state is precarious: physically drained with burning legs, mentally foggy, and oscillating between desperation and resignation.
        The strip feels compressed, your visual focus blurred, and your breathing shallow and erratic. Your opponent's conservative approach has systematically dismantled your earlier aggressive strategy,
        leaving you reactive and uncertain.

        The tactical challenge now centers on breaking your opponent's distance control without falling into their predictable counter-time traps. Their defensive reflex of distance pulling combined with an occasional instant remise means any direct attack risks immediate counteraction. You must find a way to disrupt their carefully maintained spatial rhythm - not through pure aggression, but through subtle tempo manipulation that creates momentary vulnerabilities in their defensive structure.

        The critical question becomes: Can you reset the bout's momentum by creating a deceptive spatial engagement that forces your opponent out of their meticulously constructed defensive comfort zone, all while managing your rapidly depleting physical and mental resources?
        """).strip(),
    )


def choices_fixture() -> Choices:
    """Return test choices for development."""
    return Choices(
        options=[
            "Execute a false-rhythm preparation with deliberately slower advances, then explosively accelerate with a fleche attack when opponent adjusts to the deceptive tempo, targeting their anticipatory distance pull.",
            "Launch immediate aggressive attacks with multiple feints and changes of line, attempting to overwhelm opponent's defensive system through sheer pressure and determination.",
            "Employ stop-hits during opponent's glide-pause advances, timing the counter-attack to exploit the brief hesitation in their forward movement pattern.",
            "Retreat deliberately to invite pursuit, then execute a second-intention attack utilizing their forward momentum against their preferred long-distance game.",
        ],
        recommend=0,  # Option A is recommended for this scenario
    )


def answer_fixture() -> Answer:
    """Return a test answer for development."""
    return Answer(
        choice=AnswerChoice.A,
        explanation="B is suicidal; C is technically too challenging; D is unrealistic because they are leading by 4 points and they have no need to chase me. I have to take the initiative.",
    )


def challenge_fixture() -> Challenge:
    """Return a complete test challenge for development."""
    return Challenge(scenario=scenario_fixture(), choices=choices_fixture())


def feedback_fixture() -> Feedback:
    """Return test feedback for development."""
    return Feedback(
        acknowledgment="Your choice of the false-rhythm preparation followed by an explosive fleche shows excellent tactical understanding. You've correctly identified that breaking your opponent's defensive rhythm is crucial when trailing by 4 touches with only 20 seconds remaining.",
        analysis="This approach directly addresses the core tactical problem: your opponent's distance control. By deliberately varying your advance rhythm, you create uncertainty in their defensive timing. The subsequent explosive fleche exploits the moment when they're recalibrating to your deceptive tempo. This is particularly effective against fencers who rely heavily on predictable distance patterns.",
        advanced_concepts="The false-rhythm preparation demonstrates mastery of 'tempo manipulation' - a high-level concept where you control not just distance but the perception of time. This creates what master coaches call 'temporal vulnerability' - a moment where your opponent's defensive reflexes are disrupted by conflicting visual information. The fleche, as a commitment attack, capitalizes on this disruption before they can recover their defensive structure.",
        bridge_to_mastery="To elevate this tactic further, consider adding a subtle shoulder feint during the slow advances to amplify the deception. Practice varying not just the speed but also the size of your advances - small-small-large patterns can be devastatingly effective. Remember: at the highest levels, it's not about being faster, but about making your opponent move at the wrong time.",
    )
