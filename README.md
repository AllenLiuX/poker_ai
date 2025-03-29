# Poker AI Agent

A comprehensive AI agent for playing Texas Hold'em poker against multiple online players.

## Features

- Local poker game engine for testing and training
- Extensible architecture for future integration with online poker platforms
- Advanced decision-making based on hand strength and opponent modeling

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run a local poker game simulation
python -m poker_ai.game.runner

# Run tests
pytest
```

## Project Structure

- `poker_ai/`: Main package
  - `engine/`: Core poker game engine
  - `game/`: Game state management
  - `player/`: Player implementations (human, AI)
  - `strategy/`: Strategy implementations
  - `utils/`: Utility functions
