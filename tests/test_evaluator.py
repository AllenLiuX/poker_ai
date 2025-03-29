"""Tests for poker hand evaluator."""
import pytest
from poker_ai.engine.card import Card, Rank, Suit
from poker_ai.engine.evaluator import HandEvaluator, HandRank


def test_hand_evaluation_royal_flush():
    """Test evaluation of a royal flush."""
    evaluator = HandEvaluator()
    
    # Royal flush in hearts
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
    assert hand_rank == HandRank.ROYAL_FLUSH


def test_hand_evaluation_straight_flush():
    """Test evaluation of a straight flush."""
    evaluator = HandEvaluator()
    
    # Straight flush in spades, 5-9
    hole_cards = [
        Card(Rank.NINE, Suit.SPADES),
        Card(Rank.EIGHT, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.SIX, Suit.SPADES),
        Card(Rank.FIVE, Suit.SPADES),
        Card(Rank.ACE, Suit.CLUBS),
        Card(Rank.KING, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.STRAIGHT_FLUSH


def test_hand_evaluation_four_of_a_kind():
    """Test evaluation of four of a kind."""
    evaluator = HandEvaluator()
    
    # Four aces
    hole_cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.ACE, Suit.CLUBS),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.JACK, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.FOUR_OF_A_KIND


def test_hand_evaluation_full_house():
    """Test evaluation of a full house."""
    evaluator = HandEvaluator()
    
    # Full house, kings full of queens
    hole_cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.TEN, Suit.CLUBS),
        Card(Rank.NINE, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.FULL_HOUSE


def test_hand_evaluation_flush():
    """Test evaluation of a flush."""
    evaluator = HandEvaluator()
    
    # Flush in diamonds
    hole_cards = [
        Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.KING, Suit.DIAMONDS)
    ]
    community_cards = [
        Card(Rank.SEVEN, Suit.DIAMONDS),
        Card(Rank.FIVE, Suit.DIAMONDS),
        Card(Rank.THREE, Suit.DIAMONDS),
        Card(Rank.TEN, Suit.CLUBS),
        Card(Rank.NINE, Suit.HEARTS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.FLUSH


def test_hand_evaluation_straight():
    """Test evaluation of a straight."""
    evaluator = HandEvaluator()
    
    # Straight, 7-J
    hole_cards = [
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.NINE, Suit.DIAMONDS),
        Card(Rank.EIGHT, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.THREE, Suit.CLUBS),
        Card(Rank.TWO, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.STRAIGHT


def test_hand_evaluation_three_of_a_kind():
    """Test evaluation of three of a kind."""
    evaluator = HandEvaluator()
    
    # Three queens
    hole_cards = [
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.QUEEN, Suit.DIAMONDS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.FIVE, Suit.CLUBS),
        Card(Rank.TWO, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.THREE_OF_A_KIND


def test_hand_evaluation_two_pair():
    """Test evaluation of two pair."""
    evaluator = HandEvaluator()
    
    # Two pair, aces and kings
    hole_cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.FIVE, Suit.CLUBS),
        Card(Rank.TWO, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.TWO_PAIR


def test_hand_evaluation_one_pair():
    """Test evaluation of one pair."""
    evaluator = HandEvaluator()
    
    # One pair, jacks
    hole_cards = [
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.JACK, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.FIVE, Suit.CLUBS),
        Card(Rank.TWO, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.ONE_PAIR


def test_hand_evaluation_high_card():
    """Test evaluation of high card."""
    evaluator = HandEvaluator()
    
    # High card, ace high
    hole_cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.JACK, Suit.SPADES)
    ]
    community_cards = [
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.FIVE, Suit.CLUBS),
        Card(Rank.TWO, Suit.DIAMONDS)
    ]
    
    hand_strength, hand_rank, desc = evaluator.evaluate_hand(hole_cards, community_cards)
    assert hand_rank == HandRank.HIGH_CARD


def test_hand_equity_calculation():
    """Test hand equity calculation."""
    evaluator = HandEvaluator()
    
    # Strong hand: pocket aces
    hole_cards = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.SPADES)
    ]
    community_cards = []
    
    equity = evaluator.get_hand_equity(hole_cards, community_cards)
    assert 0.8 <= equity <= 1.0  # Pocket aces should have high equity preflop
    
    # Weak hand: 7-2 offsuit
    hole_cards = [
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.TWO, Suit.SPADES)
    ]
    
    equity = evaluator.get_hand_equity(hole_cards, community_cards)
    assert 0.0 <= equity <= 0.4  # 7-2 should have low equity preflop
    
    # Medium hand with some community cards
    hole_cards = [
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS)
    ]
    community_cards = [
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.CLUBS),
        Card(Rank.TWO, Suit.DIAMONDS)
    ]
    
    equity = evaluator.get_hand_equity(hole_cards, community_cards, num_opponents=2)
    assert 0.3 <= equity <= 0.8  # KQs with draw to straight/flush should have decent equity


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
