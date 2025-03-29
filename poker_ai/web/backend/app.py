"""Flask backend for the poker AI web interface."""
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import uuid
import json
import os
import sys

# Add the project root to the path so we can import the poker_ai modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from poker_ai.game.state import GameState
from poker_ai.game.player import Player, HumanPlayer
from poker_ai.player.ai_player import BasicAIPlayer, AdvancedAIPlayer
from poker_ai.engine.action import Action, ActionType, BettingRound

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active games
active_games = {}

@app.route('/api/game/new', methods=['POST'])
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

@app.route('/api/game/<game_id>/state', methods=['GET'])
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

@app.route('/api/game/<game_id>/action', methods=['POST'])
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
    if current_player and current_player.player_id == human_player_id:
        valid_action_types = game_state.get_valid_actions(human_player)
        
        for action_type in valid_action_types:
            action_data = {
                'type': action_type.name,
                'min_amount': 0,
                'max_amount': 0
            }
            
            if action_type == ActionType.CALL:
                action_data['min_amount'] = game_state.current_bet - human_player.current_bet
                action_data['max_amount'] = action_data['min_amount']
            elif action_type == ActionType.BET:
                action_data['min_amount'] = game_state.min_raise
                action_data['max_amount'] = human_player.stack
            elif action_type == ActionType.RAISE:
                action_data['min_amount'] = game_state.min_raise
                action_data['max_amount'] = human_player.stack
            elif action_type == ActionType.ALL_IN:
                action_data['min_amount'] = human_player.stack
                action_data['max_amount'] = human_player.stack
            
            valid_actions.append(action_data)
    
    # Format hand history for the current hand
    formatted_history = []
    for action in game_state.hand_history:
        if action['type'] == 'player_action':
            player = next((p for p in game_state.players if p.player_id == action['player_id']), None)
            if player:
                formatted_history.append({
                    'type': 'action',
                    'player_name': player.name,
                    'action': action['action'],
                    'amount': action['amount']
                })
        elif action['type'] in ['deal_community', 'showdown', 'hand_end']:
            formatted_history.append({
                'type': action['type'],
                'data': action
            })
    
    # Return the formatted state
    return {
        'betting_round': game_state.betting_round.name,
        'pot': game_state.pot,
        'current_bet': game_state.current_bet,
        'min_raise': game_state.min_raise,
        'community_cards': [str(card) for card in game_state.community_cards],
        'players': players_data,
        'current_player_id': current_player_id,
        'is_human_turn': current_player and current_player.player_id == human_player_id,
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
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
