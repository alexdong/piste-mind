# CLI Usage Guide

## Model Selection

Piste-mind now supports three Anthropic models:
- **Haiku** - Fastest and most economical (default)
- **Sonnet** - Balanced performance
- **Opus** - Most capable and creative

## Setting Model via Environment Variable

```bash
# Set default model for all commands
export PISTE_MIND_MODEL=OPUS  # or HAIKU, SONNET

# Run with environment default
piste-mind ask
```

## Setting Model via CLI

```bash
# Generate a question with Opus (most creative)
piste-mind ask --model opus

# Generate a question with Haiku (fastest)
piste-mind ask --model haiku

# Generate feedback with Sonnet
piste-mind feedback --model sonnet
```

## Full Command Examples

### Generate Questions
```bash
# Default (Haiku)
piste-mind ask

# With Opus for maximum variety
piste-mind ask --model opus -o tactical_scenario.json

# With Haiku for quick iteration
piste-mind ask --model haiku
```

### Generate Feedback
```bash
# Default files and model
piste-mind feedback

# Custom files with Opus
piste-mind feedback --model opus -q my_question.json -a my_answer.json -o my_feedback.json

# With Haiku for faster response
piste-mind feedback --model haiku
```

## Model Recommendations

- **For Question Generation**: Use Opus (`--model opus`) for maximum creativity and variety
- **For Feedback Generation**: Sonnet is usually sufficient, but Opus provides deeper analysis
- **For Testing/Development**: Haiku is fast and cost-effective

## Example Workflow

```bash
# 1. Generate a creative scenario with Opus
piste-mind ask --model opus

# 2. Create your answer in answer.json
echo '{"choice": "B", "explanation": "I think option B addresses the distance problem"}' > answer.json

# 3. Get feedback (Sonnet is fine here)
piste-mind feedback

# 4. Try another scenario with different model
export PISTE_MIND_MODEL=HAIKU
piste-mind ask  # Will use Haiku
```