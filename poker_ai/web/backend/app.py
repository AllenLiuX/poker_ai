"""Flask backend for the poker AI web interface."""
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import uuid
import json
import os
import sys
import ssl

# Add the project root to the path so we can import the poker_ai modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from poker_ai.game.state import GameState
from poker_ai.game.player import Player, HumanPlayer
from poker_ai.player.ai_player import BasicAIPlayer, AdvancedAIPlayer
from poker_ai.engine.action import Action, ActionType, BettingRound

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active games
active_games = {}

@app.route('/game/new', methods=['POST'])
def create_game():
    """Create a new poker game."""
    data = request.json
    
    # Extract game parameters
    num_ai_players = data.get('num_ai_players', 5)
    starting_stack = data.get('starting_stack', 1000.0)
    small_blind = data.get('small_blind', 1.0)
    big_blind = data.get('big_blind', 2.0)
    ante = data.get('ante', 0.0)
    advanced_ai = data.get('advanced_ai', False)
    
    # Create a unique game ID
    game_id = str(uuid.uuid4())
    
    # Create a human player with a web-friendly ID
    human_player = HumanPlayer(name="Human", stack=starting_stack)
    
    # Create AI players
    players = [human_player]
    ai_class = AdvancedAIPlayer if advanced_ai else BasicAIPlayer
    for i in range(num_ai_players):
        players.append(ai_class(name=f"AI-{i+1}", stack=starting_stack))
    
    # Create game state
    game_state = GameState(
        players=players,
        small_blind=small_blind,
        big_blind=big_blind,
        ante=ante
    )
    
    # Start the first hand
    game_state.start_new_hand()
    
    # Process AI actions until it's the human's turn
    process_ai_turns(game_state, human_player.player_id)
    
    # Store the game
    active_games[game_id] = {
        'game_state': game_state,
        'human_player_id': human_player.player_id,
        'hand_history': []
    }
    
    # Return game info
    return jsonify({
        'game_id': game_id,
        'human_player_id': human_player.player_id,
        'state': get_game_state_for_client(game_state, human_player.player_id)
    })

@app.route('/game/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    """Get the current state of a game."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_data = active_games[game_id]
    game_state = game_data['game_state']
    human_player_id = game_data['human_player_id']
    
    return jsonify({
        'state': get_game_state_for_client(game_state, human_player_id)
    })

@app.route('/game/<game_id>/action', methods=['POST'])
def submit_action(game_id):
    """Submit a player action."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    action_type = data.get('action_type')
    amount = data.get('amount', 0)
    
    game_data = active_games[game_id]
    game_state = game_data['game_state']
    human_player_id = game_data['human_player_id']
    
    # Get the human player
    human_player = None
    for player in game_state.players:
        if player.player_id == human_player_id:
            human_player = player
            break
    
    if not human_player:
        return jsonify({'error': 'Human player not found'}), 500
    
    # Check if it's the human player's turn
    current_player = game_state.get_current_player()
    if not current_player or current_player.player_id != human_player_id:
        return jsonify({'error': 'Not your turn'}), 400
    
    # Convert action type string to enum
    try:
        action_type_enum = ActionType[action_type]
    except KeyError:
        return jsonify({'error': f'Invalid action type: {action_type}'}), 400
    
    # Validate action
    valid_actions = game_state.get_valid_actions(human_player)
    if action_type_enum not in valid_actions:
        return jsonify({'error': f'Invalid action: {action_type}'}), 400
    
    # Create and apply the action
    action = Action(action_type_enum, float(amount), human_player_id)
    game_state.apply_action(action)
    
    # Process AI actions until it's the human's turn again or the hand is over
    process_ai_turns(game_state, human_player_id)
    
    # If the hand is over, start a new one
    if game_state.is_hand_over():
        # Save the hand history
        game_data['hand_history'].append(game_state.hand_history.copy())
        
        # Start a new hand
        game_state.start_new_hand()
        
        # Process AI actions if human is not the first to act
        process_ai_turns(game_state, human_player_id)
    
    # Return updated game state
    return jsonify({
        'state': get_game_state_for_client(game_state, human_player_id)
    })

def process_ai_actions(game_state, human_player_id):
    """Process AI player actions until it's the human player's turn or the hand is over."""
    current_player = game_state.get_current_player()
    
    # Keep processing AI actions until it's the human's turn or the hand is over
    while (current_player and 
           current_player.player_id != human_player_id and 
           not game_state.is_hand_over()):
        
        # Get the AI's action
        valid_actions = game_state.get_valid_actions(current_player)
        action = current_player.act(
            valid_actions,
            game_state.min_raise,
            game_state.current_bet,
            game_state.pot
        )
        
        # Apply the action to the game state
        game_state.apply_action(action)
        
        # Emit the action via Socket.IO for real-time updates
        socketio.emit('ai_action', {
            'player_name': current_player.name,
            'action_type': action.action_type.name,
            'amount': action.amount
        })
        
        # Get the next player
        current_player = game_state.get_current_player()

def process_ai_turns(game_state, human_player_id):
    """Process AI player turns until it's the human player's turn."""
    current_player = game_state.get_current_player()
    
    # Keep processing AI turns until it's the human's turn
    while current_player and current_player.player_id != human_player_id:
        
        # Get the AI's action
        valid_actions = game_state.get_valid_actions(current_player)
        action = current_player.act(
            valid_actions,
            game_state.min_raise,
            game_state.current_bet,
            game_state.pot
        )
        
        # Apply the action to the game state
        game_state.apply_action(action)
        
        # Emit the action via Socket.IO for real-time updates
        socketio.emit('ai_action', {
            'player_name': current_player.name,
            'action_type': action.action_type.name,
            'amount': action.amount
        })
        
        # Get the next player
        current_player = game_state.get_current_player()

def get_game_state_for_client(game_state, human_player_id):
    """Convert the game state to a client-friendly format."""
    # Find the human player
    human_player = None
    for player in game_state.players:
        if player.player_id == human_player_id:
            human_player = player
            break
    
    # Get the current player
    current_player = game_state.get_current_player()
    current_player_id = current_player.player_id if current_player else None
    
    # Format player data
    players_data = []
    for player in game_state.players:
        player_data = {
            'id': player.player_id,
            'name': player.name,
            'stack': player.stack,
            'current_bet': player.current_bet,
            'is_active': player.is_active,
            'is_all_in': player.is_all_in,
            'position': player.position,
            'is_current': current_player and player.player_id == current_player.player_id,
            'is_human': player.player_id == human_player_id
        }
        
        # Only show the human player's cards
        if player.player_id == human_player_id:
            player_data['hole_cards'] = [str(card) for card in player.hole_cards]
        else:
            # For AI players, only show cards at showdown
            if game_state.betting_round == BettingRound.SHOWDOWN:
                player_data['hole_cards'] = [str(card) for card in player.hole_cards]
            else:
                player_data['hole_cards'] = []
        
        players_data.append(player_data)
    
    # Get valid actions for the human player if it's their turn
    valid_actions = []
    is_human_turn = current_player and current_player.player_id == human_player_id
    
    if is_human_turn:
        valid_action_types = game_state.get_valid_actions(human_player)
        valid_actions = [action_type.name for action_type in valid_action_types]
    
    # Format community cards
    community_cards = [str(card) for card in game_state.community_cards]
    
    # Format hand history for the current hand
    formatted_history = []
    for entry in game_state.hand_history:
        if entry['type'] == 'player_action':
            player = next((p for p in game_state.players if p.player_id == entry['player_id']), None)
            if player:
                formatted_history.append({
                    'type': 'action',
                    'player_name': player.name,
                    'action': entry['action'],
                    'amount': entry['amount']
                })
    
    # Return the formatted game state
    return {
        'betting_round': game_state.betting_round.name,
        'pot': game_state.pot,
        'current_bet': game_state.current_bet,
        'min_raise': game_state.min_raise,
        'community_cards': community_cards,
        'players': players_data,
        'current_player_id': current_player_id,
        'is_human_turn': is_human_turn,
        'valid_actions': valid_actions,
        'hand_history': formatted_history,
        'is_hand_over': game_state.is_hand_over(),
        'smallBlind': game_state.small_blind,
        'bigBlind': game_state.big_blind
    }

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

if __name__ == '__main__':
    """Run the Socket.IO server.

    In production we want to serve the application over HTTPS using the
    LetsEncrypt certificates provisioned on the host. When developing or when
    the current user does not have permission to read those certificate files
    (which is very common when running as a non-root user), we gracefully
    fall back to HTTP so that the application can still be started without
    crashing.
    """
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'

    # Default certificate locations – can be overridden with environment vars
    key_path = os.environ.get('SSL_KEY_PATH', '/etc/letsencrypt/live/aico-music.com/privkey.pem')
    cert_path = os.environ.get('SSL_CERT_PATH', '/etc/letsencrypt/live/aico-music.com/fullchain.pem')

    # Determine if we can read the certificate files
    use_ssl = (
        os.path.exists(key_path)
        and os.path.exists(cert_path)
        and os.access(key_path, os.R_OK)
        and os.access(cert_path, os.R_OK)
    )

    if use_ssl:
        print(f"Starting server with SSL – cert: {cert_path}, key: {key_path}")
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True,
            keyfile=key_path,
            certfile=cert_path,
        )
    else:
        print("SSL certificates not found or unreadable – starting server **without** SSL.\n"
              "This is expected when running locally. In production make sure the\n"
              "application has permission to read the certificate files.")
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True,
        )
