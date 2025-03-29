"""Tests for card and deck components."""
import pytest
from poker_ai.engine.card import Card, Rank, Suit, Deck


def test_card_creation_and_comparison():
    """Test card creation, comparison, and string representation."""
    # Test creation and string representation
    card1 = Card(Rank.ACE, Suit.SPADES)
    assert str(card1) == "AS"
    
    card2 = Card(Rank.TEN, Suit.HEARTS)
    assert str(card2) == "10H"
    
    # Test from_str method
    card3 = Card.from_str("KD")
    assert card3.rank == Rank.KING
    assert card3.suit == Suit.DIAMONDS
    
    # Test equality
    card4 = Card(Rank.ACE, Suit.SPADES)
    assert card1 == card4
    assert card1 != card2
    
    # Test hash
    card_set = {card1, card2, card3, card4}
    assert len(card_set) == 3  # card1 and card4 are the same


def test_rank_and_suit_methods():
    """Test rank and suit methods."""
    # Test rank string representation
    assert str(Rank.ACE) == "A"
    assert str(Rank.KING) == "K"
    assert str(Rank.TEN) == "10"
    assert str(Rank.TWO) == "2"
    
    # Test suit string representation
    assert str(Suit.SPADES) == "S"
    assert str(Suit.HEARTS) == "H"
    assert str(Suit.DIAMONDS) == "D"
    assert str(Suit.CLUBS) == "C"
    
    # Test rank from_str method
    assert Rank.from_str("A") == Rank.ACE
    assert Rank.from_str("K") == Rank.KING
    assert Rank.from_str("10") == Rank.TEN
    assert Rank.from_str("T") == Rank.TEN
    assert Rank.from_str("2") == Rank.TWO
    
    # Test suit from_str method
    assert Suit.from_str("S") == Suit.SPADES
    assert Suit.from_str("H") == Suit.HEARTS
    assert Suit.from_str("D") == Suit.DIAMONDS
    assert Suit.from_str("C") == Suit.CLUBS
    
    # Test invalid inputs
    with pytest.raises(ValueError):
        Rank.from_str("Z")
    
    with pytest.raises(ValueError):
        Suit.from_str("X")


def test_deck_operations():
    """Test deck operations."""
    # Test deck initialization
    deck = Deck(shuffled=False)
    assert len(deck) == 52
    
    # Test dealing cards
    cards = deck.deal(5)
    assert len(cards) == 5
    assert len(deck) == 47
    
    # Test dealing a single card
    card = deck.deal_card()
    assert isinstance(card, Card)
    assert len(deck) == 46
    
    # Test dealing too many cards
    with pytest.raises(ValueError):
        deck.deal(50)
    
    # Test reset
    deck.reset(shuffled=False)
    assert len(deck) == 52
    assert len(deck.dealt_cards) == 0
    
    # Test shuffle (indirectly)
    deck1 = Deck(shuffled=False)
    deck2 = Deck(shuffled=True)
    
    # The probability of two shuffled decks being identical is extremely low
    # This is not a perfect test but should catch obvious issues
    cards1 = deck1.deal(10)
    cards2 = deck2.deal(10)
    assert cards1 != cards2


def test_full_deck_uniqueness():
    """Test that a deck contains 52 unique cards."""
    deck = Deck(shuffled=False)
    all_cards = deck.deal(52)
    
    # Check that all cards are unique
    card_set = set(all_cards)
    assert len(card_set) == 52
    
    # Check that all ranks and suits are represented
    ranks = {card.rank for card in all_cards}
    suits = {card.suit for card in all_cards}
    
    assert len(ranks) == 13
    assert len(suits) == 4
    
    # Check that the deck is now empty
    assert len(deck) == 0
    
    # Check that we can't deal more cards
    with pytest.raises(ValueError):
        deck.deal_card()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
