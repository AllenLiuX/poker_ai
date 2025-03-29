# Poker AI Web Interface

This web interface allows you to play Texas Hold'em poker against AI agents using a modern web interface. The system uses Flask for the backend API and React for the frontend UI.

## Features

- Play Texas Hold'em poker against multiple AI opponents
- Configure game parameters (number of AI players, starting stack, blinds, etc.)
- Real-time game updates using WebSockets
- Beautiful and intuitive user interface
- Hand history tracking
- Support for all poker actions (fold, check, call, bet, raise, all-in)

## Requirements

- Python 3.7+
- Node.js 14+ and npm
- Required Python packages (see requirements.txt)

## Running the Web Interface

The easiest way to run the web interface is to use the provided script:

```bash
cd /path/to/poker_ai
python poker_ai/web/run_web_interface.py
```

This script will:
1. Start the Flask backend server on port 5000
2. Start the React development server on port 3000
3. Open your web browser to http://localhost:3000

## Manual Setup

If you prefer to run the servers manually:

### Backend

```bash
cd /path/to/poker_ai
python poker_ai/web/backend/app.py
```

### Frontend

```bash
cd /path/to/poker_ai/poker_ai/web/frontend
npm install  # Only needed the first time
npm start
```

## How to Play

1. Configure the game settings on the setup screen
2. Start the game
3. When it's your turn, select an action from the available options
4. For bet/raise actions, use the slider to adjust the amount
5. The game log on the right shows the history of actions

## Architecture

The web interface is built with a client-server architecture:

- **Backend**: Flask server that manages the game state and AI players
- **Frontend**: React application that provides the user interface
- **Communication**: RESTful API for game actions and WebSockets for real-time updates

## Extending the Interface

You can extend the web interface in several ways:

- Add new AI player types by implementing new subclasses in the `poker_ai/player` directory
- Enhance the UI with additional features like player statistics or hand strength indicators
- Implement a replay system to review past hands
- Add support for different poker variants

## Troubleshooting

- If the backend fails to start, check that all required Python packages are installed
- If the frontend fails to start, ensure Node.js and npm are properly installed
- If you encounter CORS issues, verify that the backend is running on port 5000
- For WebSocket connection problems, check your browser's console for error messages
