"""Tests for GTO-based AI player."""
import pytest
import random
from typing import List, Dict, Any, Tuple
import statistics

from poker_ai.engine.card import Card, Rank, Suit, Deck
from poker_ai.engine.action import Action, ActionType, BettingRound
from poker_ai.engine.evaluator import HandEvaluator
from poker_ai.game.player import Player
from poker_ai.game.state import GameState
from poker_ai.player.gto_player import GTOPlayer, ExploitativePlayer


def test_gto_player_initialization():
    """Test GTO player initialization with different parameters."""
    # Default GTO player
    player1 = GTOPlayer(name="GTO Default")
    assert player1.aggression == 1.0
    assert player1.bluff_frequency == 0.3
    assert player1.fold_to_3bet == 0.5
    assert player1.gto_deviation == 0.0
    
    # Aggressive GTO player
    player2 = GTOPlayer(name="GTO Aggressive", aggression=1.5, bluff_frequency=0.4)
    assert player2.aggression == 1.5
    assert player2.bluff_frequency == 0.4
    
    # Tight GTO player
    player3 = GTOPlayer(name="GTO Tight", aggression=0.7, bluff_frequency=0.2, fold_to_3bet=0.7)
    assert player3.aggression == 0.7
    assert player3.bluff_frequency == 0.2
    assert player3.fold_to_3bet == 0.7


def test_hand_percentile_calculation():
    """Test hand percentile calculation for different starting hands."""
    player = GTOPlayer()
    
    # Test premium hands
    hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
    percentile = player._get_hand_percentile(hole_cards)
    assert percentile > 0.9  # AA should be very high
    
    hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.SPADES)]
    percentile = player._get_hand_percentile(hole_cards)
    assert percentile >= 0.8  # AKs should be high
    
    # Test medium hands
    hole_cards = [Card(Rank.TEN, Suit.HEARTS), Card(Rank.NINE, Suit.HEARTS)]
    percentile = player._get_hand_percentile(hole_cards)
    assert 0.4 < percentile < 0.8  # T9s should be medium
    
    # Test weak hands
    hole_cards = [Card(Rank.SEVEN, Suit.CLUBS), Card(Rank.TWO, Suit.DIAMONDS)]
    percentile = player._get_hand_percentile(hole_cards)
    assert percentile < 0.4  # 72o should be low


def test_positional_adjustments():
    """Test how position affects decision making."""
    player = GTOPlayer()
    
    # Test button position
    player.position = 0  # Button
    base_value = 0.5
    adjusted = player._adjust_for_position(base_value)
    assert adjusted > base_value  # Button should increase value
    
    # Test early position
    player.position = 3  # UTG
    adjusted = player._adjust_for_position(base_value)
    assert adjusted < base_value  # Early position should decrease value
    
    # Test positional awareness parameter
    player.positional_awareness = 0.5  # Reduce positional awareness
    player.position = 0  # Button
    adjusted = player._adjust_for_position(base_value)
    assert base_value < adjusted < base_value * 1.2  # Less impact of position


def test_bet_sizing():
    """Test bet sizing calculations for different scenarios."""
    player = GTOPlayer()
    
    # Test preflop sizing
    equity = 0.8  # Strong hand
    pot_size = 10
    sizing = player._calculate_bet_sizing(equity, pot_size, BettingRound.PREFLOP)
    assert 4 < sizing < 8  # Should be around 3bb (6 units with BB=2)
    
    # Test postflop sizing with strong hand
    equity = 0.8
    pot_size = 20
    sizing = player._calculate_bet_sizing(equity, pot_size, BettingRound.FLOP)
    assert 10 < sizing < 20  # Should be around 60-80% of pot
    
    # Test postflop sizing with weak hand
    equity = 0.3
    sizing = player._calculate_bet_sizing(equity, pot_size, BettingRound.FLOP)
    assert 5 < sizing < 15  # Should be around 50% of pot for bluffs
    
    # Test aggression parameter effect
    player.aggression = 1.5  # More aggressive
    equity = 0.8
    sizing = player._calculate_bet_sizing(equity, pot_size, BettingRound.TURN)
    assert 15 < sizing < 25  # Should be larger due to aggression


def test_preflop_decision_making():
    """Test preflop decision making with different hand strengths and positions."""
    player = GTOPlayer(stack=1000)
    
    # Test premium hand in late position
    player.position = 0  # Button
    player.hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
    valid_actions = [ActionType.FOLD, ActionType.CALL, ActionType.RAISE]
    min_raise = 6
    current_bet = 2
    pot_size = 3
    
    action = player._make_preflop_decision(valid_actions, min_raise, current_bet, pot_size)
    assert action.action_type == ActionType.RAISE  # Should raise with AA
    
    # Test medium hand in early position
    player.position = 3  # UTG
    player.hole_cards = [Card(Rank.TEN, Suit.HEARTS), Card(Rank.NINE, Suit.HEARTS)]
    
    action = player._make_preflop_decision(valid_actions, min_raise, current_bet, pot_size)
    # Could be fold or call depending on randomization, but unlikely to raise
    assert action.action_type in [ActionType.FOLD, ActionType.CALL]
    
    # Test weak hand in any position
    player.position = 0  # Even in button
    player.hole_cards = [Card(Rank.SEVEN, Suit.CLUBS), Card(Rank.TWO, Suit.DIAMONDS)]
    
    action = player._make_preflop_decision(valid_actions, min_raise, current_bet, pot_size)
    assert action.action_type == ActionType.FOLD  # Should fold 72o


def test_postflop_decision_making():
    """Test postflop decision making with different hand strengths."""
    player = GTOPlayer(stack=1000)
    evaluator = HandEvaluator()
    
    # Set up community cards for different scenarios
    flop_cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.DIAMONDS)
    ]
    
    # Test strong hand (top pair top kicker)
    player.hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.JACK, Suit.CLUBS)]
    valid_actions = [ActionType.CHECK, ActionType.BET]
    min_raise = 10
    current_bet = 0
    pot_size = 30
    
    action = player._make_postflop_decision(valid_actions, min_raise, current_bet, pot_size, flop_cards)
    assert action.action_type == ActionType.BET  # Should bet with TPTK
    
    # Test draw (flush draw)
    player.hole_cards = [Card(Rank.TEN, Suit.HEARTS), Card(Rank.NINE, Suit.HEARTS)]
    
    action = player._make_postflop_decision(valid_actions, min_raise, current_bet, pot_size, flop_cards)
    # Could be check or bet depending on randomization
    assert action.action_type in [ActionType.CHECK, ActionType.BET]
    
    # Test weak hand facing a bet
    player.hole_cards = [Card(Rank.SEVEN, Suit.CLUBS), Card(Rank.SIX, Suit.DIAMONDS)]
    valid_actions = [ActionType.FOLD, ActionType.CALL]
    current_bet = 20
    
    action = player._make_postflop_decision(valid_actions, min_raise, current_bet, pot_size, flop_cards)
    assert action.action_type == ActionType.FOLD  # Should fold weak hand to bet


def simulate_heads_up_match(player1: Player, player2: Player, 
                           num_hands: int = 100, 
                           small_blind: float = 1.0, 
                           big_blind: float = 2.0) -> Tuple[float, float]:
    """
    Simulate a heads-up match between two players and return their final stacks.
    
    Args:
        player1: First player
        player2: Second player
        num_hands: Number of hands to play
        small_blind: Small blind amount
        big_blind: Big blind amount
        
    Returns:
        Tuple of (player1_profit, player2_profit)
    """
    # Reset player stacks
    player1.stack = 1000.0
    player2.stack = 1000.0
    
    # Track initial stacks
    initial_stack1 = player1.stack
    initial_stack2 = player2.stack
    
    # Create game state
    players = [player1, player2]
    game = GameState(players, small_blind, big_blind)
    
    # Play hands
    for _ in range(num_hands):
        if player1.stack <= 0 or player2.stack <= 0:
            break
            
        game.start_new_hand()
        
        # Main game loop
        while not game.is_hand_over():
            current_player = game.get_current_player()
            if not current_player:
                break
                
            # Get valid actions
            valid_actions = game.get_valid_actions(current_player)
            
            # Get player action
            if hasattr(current_player, 'act') and callable(current_player.act):
                if isinstance(current_player, GTOPlayer):
                    # Pass community cards to GTO player
                    action = current_player.act(
                        valid_actions,
                        game.min_raise,
                        game.current_bet,
                        game.pot,
                        game.community_cards
                    )
                else:
                    action = current_player.act(
                        valid_actions,
                        game.min_raise,
                        game.current_bet,
                        game.pot
                    )
            else:
                # Default to folding if player doesn't have act method
                if ActionType.FOLD in valid_actions:
                    action = Action(ActionType.FOLD, 0, current_player.player_id)
                else:
                    action = Action(ActionType.CHECK, 0, current_player.player_id)
            
            # Apply the action
            game.apply_action(action)
    
    # Calculate profits
    player1_profit = player1.stack - initial_stack1
    player2_profit = player2.stack - initial_stack2
    
    return player1_profit, player2_profit


def test_gto_vs_basic_strategies():
    """Test GTO player against different basic strategies."""
    # Create players with different strategies
    gto_player = GTOPlayer(name="GTO Default")
    aggressive_player = GTOPlayer(name="Aggressive", aggression=1.8, bluff_frequency=0.5)
    tight_player = GTOPlayer(name="Tight", aggression=0.7, bluff_frequency=0.1, fold_to_3bet=0.7)
    loose_player = GTOPlayer(name="Loose", aggression=1.2, bluff_frequency=0.4, fold_to_3bet=0.3)
    
    # Run simulations
    num_hands = 200
    num_trials = 5
    
    results = {
        "GTO vs Aggressive": [],
        "GTO vs Tight": [],
        "GTO vs Loose": []
    }
    
    for _ in range(num_trials):
        # GTO vs Aggressive
        gto_profit, agg_profit = simulate_heads_up_match(gto_player, aggressive_player, num_hands)
        results["GTO vs Aggressive"].append(gto_profit)
        
        # GTO vs Tight
        gto_profit, tight_profit = simulate_heads_up_match(gto_player, tight_player, num_hands)
        results["GTO vs Tight"].append(gto_profit)
        
        # GTO vs Loose
        gto_profit, loose_profit = simulate_heads_up_match(gto_player, loose_player, num_hands)
        results["GTO vs Loose"].append(gto_profit)
    
    # Calculate average profits
    avg_results = {
        match: statistics.mean(profits) for match, profits in results.items()
    }
    
    # Print results
    print("\nGTO Player Performance:")
    for match, avg_profit in avg_results.items():
        print(f"{match}: {avg_profit:.2f} chips")
    
    # We don't assert specific values since results are stochastic,
    # but we can check that the results are reasonable
    for match, profits in results.items():
        # Check that results are within reasonable range
        assert min(profits) > -500, f"Unreasonable loss in {match}"
        assert max(profits) < 500, f"Unreasonable win in {match}"


def test_exploitative_adaptation():
    """Test how exploitative player adapts to opponent tendencies."""
    # Create players
    exploitative_player = ExploitativePlayer(name="Exploitative")
    calling_station = GTOPlayer(name="Calling Station", call_efficiency=1.5, fold_to_3bet=0.2)
    
    # Set up initial parameters
    initial_bluff_freq = exploitative_player.bluff_frequency
    initial_aggression = exploitative_player.aggression
    
    # Simulate opponent actions that should trigger adaptation
    for _ in range(20):
        # Simulate opponent calling a lot
        exploitative_player.update_opponent_model(
            calling_station.player_id,
            Action(ActionType.CALL, 10, calling_station.player_id),
            BettingRound.FLOP,
            30
        )
    
    # Check that exploitative player adapted
    assert exploitative_player.bluff_frequency < initial_bluff_freq, \
        "Should reduce bluffing against calling station"
    
    # Reset and test against a different opponent
    exploitative_player = ExploitativePlayer(name="Exploitative")
    nit_player = GTOPlayer(name="Nit", aggression=0.5, fold_to_3bet=0.9)
    
    initial_aggression = exploitative_player.aggression
    
    # Simulate opponent folding a lot
    for _ in range(20):
        exploitative_player.update_opponent_model(
            nit_player.player_id,
            Action(ActionType.FOLD, 0, nit_player.player_id),
            BettingRound.PREFLOP,
            10
        )
    
    # Check that exploitative player adapted
    assert exploitative_player.aggression > initial_aggression, \
        "Should increase aggression against nitty player"


def evaluate_player_performance(player_configs: List[Dict[str, Any]], 
                               num_hands: int = 1000, 
                               num_trials: int = 5) -> Dict[str, Dict[str, float]]:
    """
    Evaluate performance of different player configurations against each other.
    
    Args:
        player_configs: List of player configuration dictionaries
        num_hands: Number of hands per match
        num_trials: Number of trials per matchup
        
    Returns:
        Dictionary of performance metrics for each player
    """
    # Create players from configurations
    players = []
    for config in player_configs:
        player_type = config.pop("type", "GTOPlayer")
        if player_type == "ExploitativePlayer":
            players.append(ExploitativePlayer(**config))
        else:
            players.append(GTOPlayer(**config))
    
    # Track results
    results = {player.name: {"total_profit": 0, "wins": 0, "matches": 0} for player in players}
    
    # Run round-robin tournament
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player1 = players[i]
            player2 = players[j]
            
            player1_total_profit = 0
            player2_total_profit = 0
            
            for _ in range(num_trials):
                player1_profit, player2_profit = simulate_heads_up_match(
                    player1, player2, num_hands
                )
                
                player1_total_profit += player1_profit
                player2_total_profit += player2_profit
            
            # Record average results
            player1_avg_profit = player1_total_profit / num_trials
            player2_avg_profit = player2_total_profit / num_trials
            
            results[player1.name]["total_profit"] += player1_avg_profit
            results[player2.name]["total_profit"] += player2_avg_profit
            
            results[player1.name]["matches"] += 1
            results[player2.name]["matches"] += 1
            
            if player1_avg_profit > player2_avg_profit:
                results[player1.name]["wins"] += 1
            elif player2_avg_profit > player1_avg_profit:
                results[player2.name]["wins"] += 1
            else:
                # Tie - give half win to each
                results[player1.name]["wins"] += 0.5
                results[player2.name]["wins"] += 0.5
    
    # Calculate additional metrics
    for name, stats in results.items():
        if stats["matches"] > 0:
            stats["avg_profit_per_match"] = stats["total_profit"] / stats["matches"]
            stats["win_rate"] = stats["wins"] / stats["matches"]
        else:
            stats["avg_profit_per_match"] = 0
            stats["win_rate"] = 0
    
    return results


def test_comprehensive_strategy_evaluation():
    """Comprehensive evaluation of different poker strategies."""
    # Define player configurations to test
    player_configs = [
        {"name": "GTO Balanced", "type": "GTOPlayer", "aggression": 1.0, "bluff_frequency": 0.3},
        {"name": "TAG", "type": "GTOPlayer", "aggression": 1.3, "bluff_frequency": 0.25, "fold_to_3bet": 0.6},
        {"name": "LAG", "type": "GTOPlayer", "aggression": 1.5, "bluff_frequency": 0.4, "fold_to_3bet": 0.4},
        {"name": "Nit", "type": "GTOPlayer", "aggression": 0.7, "bluff_frequency": 0.1, "fold_to_3bet": 0.8},
        {"name": "Calling Station", "type": "GTOPlayer", "aggression": 0.9, "call_efficiency": 1.5, "fold_to_3bet": 0.3},
        {"name": "Exploitative", "type": "ExploitativePlayer", "adaptation_rate": 0.3}
    ]
    
    # Run evaluation with smaller parameters for testing
    # In a real evaluation, use larger values
    results = evaluate_player_performance(player_configs, num_hands=50, num_trials=2)
    
    # Print results
    print("\nStrategy Evaluation Results:")
    for name, stats in results.items():
        print(f"{name}:")
        print(f"  Win Rate: {stats['win_rate']:.2f}")
        print(f"  Avg Profit: {stats['avg_profit_per_match']:.2f}")
    
    # We don't assert specific values since results are stochastic


if __name__ == "__main__":
    # Set seed for reproducibility
    random.seed(42)
    
    # Run individual tests
    test_gto_player_initialization()
    test_hand_percentile_calculation()
    test_positional_adjustments()
    test_bet_sizing()
    test_preflop_decision_making()
    test_postflop_decision_making()
    
    # Run simulation tests
    test_gto_vs_basic_strategies()
    test_exploitative_adaptation()
    
    # Run comprehensive evaluation
    test_comprehensive_strategy_evaluation()
