# CLI Usage Guide

## Interactive Training

Piste-mind provides an interactive training experience through a single command:

```bash
# Start an interactive training session
piste-mind train

# Use a specific model
piste-mind train --model opus

# Save the session for later review
piste-mind train --save
```

### Interactive Flow

1. **Scenario Presentation**: A tactical scenario is displayed with 4 strategic options
2. **Your Input**: 
   - Enter your choice (A, B, C, or D)
   - Explain your tactical reasoning
3. **Coaching Feedback**: Receive detailed analysis of your decision

### Features

- **Auto-completion**: Type 'a', 'b', 'c', or 'd' with tab completion
- **Input validation**: Only accepts valid choices (A-D)
- **Rich formatting**: Color-coded panels for easy reading
- **Session saving**: Use `--save` to keep records of your training

## Model Selection

Piste-mind supports three Anthropic models:
- **Haiku** - Fastest and most economical (default)
- **Sonnet** - Balanced performance
- **Opus** - Most capable and creative

### Setting Model via Environment Variable

```bash
# Set default model for all commands
export PISTE_MIND_MODEL=OPUS  # or HAIKU, SONNET

# Run with environment default
piste-mind train
```

### Setting Model via CLI

```bash
# Train with Opus (most sophisticated feedback)
piste-mind train --model opus

# Train with Haiku (fastest response)
piste-mind train --model haiku
```

## Example Training Session

```bash
$ piste-mind train --model opus

🤺 Generating tactical scenario...

┌─ Tactical Scenario ─────────────────────────────────┐
│ You're trailing 8-12 with 1:30 remaining in a      │
│ semi-final. Your opponent is a defensive counter-   │
│ attacker who has been successfully drawing your     │
│ attacks and scoring with ripostes...                │
└─────────────────────────────────────────────────────┘

Strategic Options:

A. Increase tempo and accept higher risk...
B. Switch to defensive play and force them...
C. Use false attacks to draw their parry...
D. Close distance aggressively to jam...

────────────────────────────────────────────────────

Your choice (A/B/C/D): C

Explain your tactical reasoning:
> Their counter-attacking success shows they're reading my real attacks well. False attacks should disrupt their timing.

🎯 Analyzing your response...

══════════════ Coaching Feedback ═══════════════

┌─ ✓ Acknowledgment ─────────────────────────────┐
│ Your recognition that the opponent is          │
│ successfully reading your attacks shows        │
│ excellent tactical awareness...                │
└────────────────────────────────────────────────┘

[Additional feedback panels follow...]
```

## Model Recommendations

- **For Training**: Use Opus (`--model opus`) for deepest tactical insights
- **For Quick Practice**: Haiku is perfect for rapid iterations
- **For Competition Prep**: Sonnet provides good balance

## Tips

1. Take time to think through your answer before responding
2. Be specific in your explanations - the AI provides better feedback with detailed reasoning
3. Try different models to experience varying coaching styles
4. Use `--save` to build a library of scenarios for review

## Saved Sessions

When using `--save`, three files are created:
- `session_[timestamp].question.json` - The tactical scenario
- `session_[timestamp].answer.json` - Your choice and reasoning
- `session_[timestamp].feedback.json` - The coaching feedback

This allows you to review past training sessions and track your progress.