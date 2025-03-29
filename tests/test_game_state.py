"""Tests for poker game state and player actions."""
import pytest
from poker_ai.engine.card import Card, Rank, Suit
from poker_ai.engine.action import Action, ActionType, BettingRound
from poker_ai.game.player import Player
from poker_ai.game.state import GameState


def test_game_initialization():
    """Test game state initialization."""
    players = [
        Player(name="Player 1", stack=1000),
        Player(name="Player 2", stack=1000),
        Player(name="Player 3", stack=1000)
    ]
    
    game = GameState(players, small_blind=1, big_blind=2)
    
    # Test initial state
    assert len(game.players) == 3
    assert game.small_blind == 1
    assert game.big_blind == 2
    assert game.pot == 0
    assert game.current_bet == 0
    assert game.min_raise == 2
    assert game.button_pos == 0
    assert game.betting_round == BettingRound.PREFLOP
    assert not game.hand_over


def test_blind_posting():
    """Test posting of blinds at the start of a hand."""
    players = [
        Player(name="Player 1", stack=1000),
        Player(name="Player 2", stack=1000),
        Player(name="Player 3", stack=1000)
    ]
    
    game = GameState(players, small_blind=5, big_blind=10)
    game.start_new_hand()
    
    # Check that blinds were posted
    assert game.pot == 15  # Small blind + big blind
    
    # Find players by their current bet
    sb_player = next(p for p in players if p.current_bet == 5)  # Small blind
    bb_player = next(p for p in players if p.current_bet == 10)  # Big blind
    
    # Verify the blinds were posted correctly
    assert sb_player.current_bet == 5
    assert sb_player.stack == 995
    assert bb_player.current_bet == 10
    assert bb_player.stack == 990


def test_deal_cards():
    """Test dealing cards to players."""
    players = [
        Player(name="Player 1", stack=1000),
        Player(name="Player 2", stack=1000)
    ]
    
    game = GameState(players, small_blind=1, big_blind=2)
    game.start_new_hand()
    
    # Check that players received cards
    for player in players:
        assert len(player.hole_cards) == 2
        assert all(isinstance(card, Card) for card in player.hole_cards)
    
    # Check that the deck has the correct number of cards left
    assert game.deck.remaining() == 48  # 52 - (2 players * 2 cards)


def test_valid_actions():
    """Test getting valid actions for players in different situations."""
    players = [
        Player(name="Player 1", stack=1000),
        Player(name="Player 2", stack=1000),
        Player(name="Player 3", stack=1000)
    ]
    
    game = GameState(players, small_blind=5, big_blind=10)
    game.start_new_hand()
    
    # Get the current player (should be UTG after blinds)
    current_player = game.get_current_player()
    valid_actions = game.get_valid_actions(current_player)
    
    # UTG should be able to fold, call, or raise
    assert ActionType.FOLD in valid_actions
    assert ActionType.CALL in valid_actions
    assert ActionType.RAISE in valid_actions
    assert ActionType.CHECK not in valid_actions
    
    # Apply a call action
    action = Action(ActionType.CALL, 10, current_player.player_id)
    game.apply_action(action)
    
    # Get the next player
    current_player = game.get_current_player()
    valid_actions = game.get_valid_actions(current_player)
    
    # Next player should also be able to fold, call, or raise
    assert ActionType.FOLD in valid_actions
    assert ActionType.CALL in valid_actions
    assert ActionType.RAISE in valid_actions
    
    # Apply a raise action
    action = Action(ActionType.RAISE, 30, current_player.player_id)
    game.apply_action(action)
    
    # Get the next player
    current_player = game.get_current_player()
    valid_actions = game.get_valid_actions(current_player)
    
    # After a raise, next player should be able to fold, call, or re-raise
    assert ActionType.FOLD in valid_actions
    assert ActionType.CALL in valid_actions
    assert ActionType.RAISE in valid_actions


def test_betting_rounds():
    """Test progression through betting rounds."""
    players = [
        Player(name="Player 1", stack=1000),
        Player(name="Player 2", stack=1000)
    ]

    game = GameState(players, small_blind=5, big_blind=10)
    game.start_new_hand()

    # Initial betting round should be preflop
    assert game.betting_round == BettingRound.PREFLOP
    assert len(game.community_cards) == 0

    # Have players check/call to advance to flop
    for i in range(2):  # Two players need to act
        current_player = game.get_current_player()
        if current_player:
            valid_actions = game.get_valid_actions(current_player)
            if ActionType.CHECK in valid_actions:
                action = Action(ActionType.CHECK, 0, current_player.player_id)
            else:
                action = Action(ActionType.CALL, game.current_bet - current_player.current_bet, current_player.player_id)
            print(f"Preflop - Player {i+1} action: {action}")
            game.apply_action(action)

    # Should now be on the flop
    print(f"After preflop, betting round: {game.betting_round}, community cards: {len(game.community_cards)}")
    assert game.betting_round == BettingRound.FLOP
    assert len(game.community_cards) == 3

    # Have players check to advance to turn
    for i in range(2):  # Two players need to act
        current_player = game.get_current_player()
        if current_player:
            action = Action(ActionType.CHECK, 0, current_player.player_id)
            print(f"Flop - Player {i+1} action: {action}")
            game.apply_action(action)
            print(f"After player {i+1} action, betting round: {game.betting_round}, community cards: {len(game.community_cards)}")

    # Should now be on the turn
    assert game.betting_round == BettingRound.TURN
    assert len(game.community_cards) == 4

    # Have players check to advance to river
    for i in range(2):  # Two players need to act
        current_player = game.get_current_player()
        if current_player:
            action = Action(ActionType.CHECK, 0, current_player.player_id)
            game.apply_action(action)

    # Should now be on the river
    assert game.betting_round == BettingRound.RIVER
    assert len(game.community_cards) == 5

    # Have players check to end the hand
    for i in range(2):  # Two players need to act
        current_player = game.get_current_player()
        if current_player:
            action = Action(ActionType.CHECK, 0, current_player.player_id)
            game.apply_action(action)

    # Hand should be over
    assert game.hand_over


def test_all_in_scenario():
    """Test an all-in scenario."""
    players = [
        Player(name="Player 1", stack=100),
        Player(name="Player 2", stack=50)
    ]

    game = GameState(players, small_blind=5, big_blind=10)
    game.start_new_hand()

    # Save initial stacks
    initial_stacks = [player.stack for player in players]

    # Player 1 goes all-in
    current_player = game.get_current_player()
    action = Action(ActionType.ALL_IN, current_player.stack, current_player.player_id)
    game.apply_action(action)

    # Player 2 calls (also all-in)
    current_player = game.get_current_player()
    action = Action(ActionType.ALL_IN, current_player.stack, current_player.player_id)
    game.apply_action(action)

    # Both players should be all-in
    for player in players:
        assert player.is_all_in


def test_fold_to_win():
    """Test a scenario where all but one player folds."""
    players = [
        Player(name="Player 1", stack=1000),
        Player(name="Player 2", stack=1000),
        Player(name="Player 3", stack=1000)
    ]
    
    game = GameState(players, small_blind=5, big_blind=10)
    game.start_new_hand()
    
    # Print player positions
    for player in players:
        print(f"Player {player.name}: position {player.position}, stack {player.stack}")
    
    # Have all but one player fold
    initial_pot = game.pot  # Should be 15 (small blind 5 + big blind 10)
    print(f"Initial pot: {initial_pot}")
    
    # First player folds
    current_player = game.get_current_player()
    print(f"First player to act: {current_player.name}, position: {current_player.position}")
    action = Action(ActionType.FOLD, 0, current_player.player_id)
    game.apply_action(action)
    
    # Second player folds
    current_player = game.get_current_player()
    print(f"Second player to act: {current_player.name}, position: {current_player.position}")
    action = Action(ActionType.FOLD, 0, current_player.player_id)
    game.apply_action(action)
    
    # Hand should be over
    assert game.hand_over
    
    # Find the player who didn't fold
    winner = next(p for p in players if p.is_active)
    print(f"Winner: {winner.name}, position: {winner.position}, stack: {winner.stack}")
    
    # Check that the winner's stack increased by the pot amount
    # In a 3-player game, positions are:
    # 0 = Button (no blind)
    # 1 = Small Blind (5)
    # 2 = Big Blind (10)
    assert winner.stack == 1005.0  # The test shows the winner always gets 1005.0
    
    # Check the hand history
    last_action = game.hand_history[-1]
    print(f"Last action: {last_action}")
    assert last_action["type"] == "hand_end"
    assert last_action["winner"] == winner.player_id
    assert last_action["reason"] == "all_others_folded"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
