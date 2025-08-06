# piste-mind

An interactive tactical training tool for competitive epee fencers

Develop your real-time bout analysis skills through scenario-based tactical
problems. Each scenario presents a critical moment in a match with multiple
strategic options. Make your choice and receive detailed coaching feedback that
breaks down the tactical principles at play.

## Features

- Rich Tactical Scenarios: Complex bout situations with score, time, and opponent analysis
- Multiple Strategic Paths: 4 distinct tactical approaches per scenario
- Expert Coaching Feedback: Detailed analysis of your choices with advanced tactical insights
- Pattern Recognition Training: Learn to identify and exploit opponent vulnerabilities
- Structured Learning: Progress from recognizing situations to executing counter-strategies

## How It Works

- Read a detailed bout scenario (score, time, opponent tendencies)
- Choose from 4 tactical approaches
- Receive comprehensive coaching feedback
- Understand why certain tactics work and when to apply them
- Review what other fencers chose and why

Perfect for intermediate to advanced fencers looking to develop scenario-based
tactical thinking. Transform your ability to read the strip and make winning
adjustments mid-bout.

Built for fencers who know that touches are won in the mind before they're scored on the strip.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alexdong/piste-mind
   cd piste-mind
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

## Usage

Piste-mind provides an interactive training experience through a single command:

```bash
# Start an interactive training session
piste-mind train

# Use a specific model
piste-mind train --model opus

# Save the session for later review
piste-mind train --save
```

## Tips

1. Take time to think through your answer before responding
2. Be specific in your explanations - the AI provides better feedback with detailed reasoning
3. Try different models to experience varying coaching styles
4. Use `--save` to build a library of scenarios for review