"""Test script for the poker AI web API."""
import requests
import json
import time

BASE_URL = 'http://localhost:5001/api'

def test_create_game():
    """Test creating a new game."""
    response = requests.post(f'{BASE_URL}/game/new', json={
        'num_ai_players': 2,
        'starting_stack': 1000.0,
        'small_blind': 5.0,
        'big_blind': 10.0,
        'ante': 0.0,
        'advanced_ai': False
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert 'game_id' in data
    assert 'human_player_id' in data
    assert 'state' in data
    
    print("Game created successfully!")
    print(f"Game ID: {data['game_id']}")
    
    return data['game_id']

def test_get_game_state(game_id):
    """Test getting the game state."""
    response = requests.get(f'{BASE_URL}/game/{game_id}/state')
    
    assert response.status_code == 200
    data = response.json()
    
    assert 'state' in data
    
    print("Game state retrieved successfully!")
    print(f"Current betting round: {data['state']['betting_round']}")
    print(f"Pot: {data['state']['pot']}")
    print(f"Community cards: {data['state']['community_cards']}")
    
    return data['state']

def test_player_action(game_id, action_type, amount=0):
    """Test submitting a player action."""
    response = requests.post(f'{BASE_URL}/game/{game_id}/action', json={
        'action_type': action_type,
        'amount': amount
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert 'state' in data
    
    print(f"Action {action_type} applied successfully!")
    print(f"Current betting round: {data['state']['betting_round']}")
    print(f"Pot: {data['state']['pot']}")
    
    return data['state']

def run_test_sequence():
    """Run a sequence of API tests."""
    # Create a new game
    game_id = test_create_game()
    print("\n" + "="*50)
    
    # Get the initial game state
    state = test_get_game_state(game_id)
    print("\n" + "="*50)
    
    # Check if it's the human player's turn
    if state['is_human_turn']:
        # Get valid actions
        valid_actions = state['valid_actions']
        print("Valid actions:")
        for action in valid_actions:
            print(f"  {action['type']} - Min: {action['min_amount']}, Max: {action['max_amount']}")
        
        # Choose an action (e.g., CALL, CHECK, FOLD)
        if any(action['type'] == 'CALL' for action in valid_actions):
            action_type = 'CALL'
            amount = next(action['min_amount'] for action in valid_actions if action['type'] == 'CALL')
        elif any(action['type'] == 'CHECK' for action in valid_actions):
            action_type = 'CHECK'
            amount = 0
        else:
            action_type = 'FOLD'
            amount = 0
        
        # Submit the action
        state = test_player_action(game_id, action_type, amount)
        print("\n" + "="*50)
    else:
        print("It's not the human player's turn yet.")
    
    # Get the updated game state
    state = test_get_game_state(game_id)
    print("\n" + "="*50)
    
    print("Test sequence completed successfully!")

if __name__ == '__main__':
    run_test_sequence()
