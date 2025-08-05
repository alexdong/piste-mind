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

### Interactive Training Session

Start an interactive tactical training session:

```bash
uv run python -m src.cli
```

Options:
- `--model`: Choose AI model (haiku, sonnet, or opus). Default: haiku
- `--save`: Save session data to files for later review

Examples:
```bash
# Basic training session with default model (haiku)
uv run python -m src.cli

# Use a more advanced model for richer feedback
uv run python -m src.cli --model sonnet

# Save session for later review
uv run python -m src.cli --save
```

### Standalone Tools

Generate individual questions or feedback:

```bash
# Generate a new tactical question
uv run python -m src.ask

# Generate feedback (requires question.json and answer.json files)
uv run python -m src.feedback
```

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `PISTE_MIND_MODEL`: Default model to use (HAIKU, SONNET, or OPUS)

## Tech Stack

- **Modern Python tooling**: uv, ruff, pytest, pydantic
- **Comprehensive documentation**: Ready-to-use guides for common Python packages
- **GitHub Pages ready**: The `docs/` folder can be directly hosted as a static documentation site
- **Best practices**: Pre-configured with Python coding standards and project structure

## Project Structure

```
./
├── docs/                   # Documentation (GitHub Pages ready)
├── src/                    # Application code
├── tests/                  # Test files
├── logs/                   # Implementation logs
├── llms/                   # LLM-friendly documentation
├── Makefile               # Task automation
├── pyproject.toml         # Project configuration
├── Python.md              # Python coding standards
└── CLAUDE.md              # AI assistant instructions
```
