"""Tests for the poker engine."""
import pytest

from poker_ai.engine.card import Card, Rank, Suit, Deck
from poker_ai.engine.evaluator import HandEvaluator, HandRank
from poker_ai.engine.action import Action, ActionType, BettingRound
from poker_ai.game.player import Player
from poker_ai.game.state import GameState


def test_card_creation():
    """Test card creation and string representation."""
    card = Card(Rank.ACE, Suit.SPADES)
    assert str(card) == "AS"
    
    card = Card(Rank.TEN, Suit.HEARTS)
    assert str(card) == "10H"
    
    card = Card.from_str("KD")
    assert card.rank == Rank.KING
    assert card.suit == Suit.DIAMONDS


def test_deck_operations():
    """Test deck operations."""
    deck = Deck(shuffled=False)
    assert len(deck) == 52
    
    cards = deck.deal(5)
    assert len(cards) == 5
    assert len(deck) == 47
    
    # Reset the deck
    deck.reset()
    assert len(deck) == 52


def test_hand_evaluation():
    """Test hand evaluation."""
    evaluator = HandEvaluator()
    
    # Test royal flush
    hole_cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.HEARTS)
    ]
    community_cards = [
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.HEARTS),
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.THREE, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.ROYAL_FLUSH or hand_rank == HandRank.STRAIGHT_FLUSH
    
    # Test two pair
    hole_cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.DIAMONDS)
    ]
    community_cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.DIAMONDS),
        Card(Rank.FOUR, Suit.CLUBS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.TWO_PAIR


def test_game_state():
    """Test game state initialization and basic operations."""
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
    
    # Start a new hand
    game.start_new_hand()
    
    # Check that blinds were posted
    assert game.pot == 3  # Small blind + big blind
    
    # Find players by their current bet
    sb_player = next(p for p in players if p.current_bet == 1)  # Small blind
    bb_player = next(p for p in players if p.current_bet == 2)  # Big blind
    
    # Verify the blinds were posted correctly
    assert sb_player.current_bet == 1  # Small blind
    assert bb_player.current_bet == 2  # Big blind
    
    # Check that players received cards
    for player in players:
        assert len(player.hole_cards) == 2


def test_player_actions():
    """Test player actions in a game."""
    players = [
        Player(name="Player 1", stack=1000),
        Player(name="Player 2", stack=1000)
    ]
    
    game = GameState(players, small_blind=1, big_blind=2)
    game.start_new_hand()
    
    # Get the current player
    current_player = game.get_current_player()
    assert current_player is not None
    
    # Get valid actions
    valid_actions = game.get_valid_actions(current_player)
    
    # Test fold action
    if ActionType.FOLD in valid_actions:
        action = Action(ActionType.FOLD, 0, current_player.player_id)
        game.apply_action(action)
        assert not current_player.is_active
    
    # Reset for another test
    game.start_new_hand()
    current_player = game.get_current_player()
    valid_actions = game.get_valid_actions(current_player)
    
    # Test call action
    if ActionType.CALL in valid_actions:
        to_call = game.current_bet - current_player.current_bet
        action = Action(ActionType.CALL, to_call, current_player.player_id)
        game.apply_action(action)
        assert current_player.current_bet == game.current_bet


if __name__ == "__main__":
    # Run tests
    pytest.main(["-xvs", __file__])
