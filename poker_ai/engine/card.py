"""Card and Deck implementation for poker game."""
from enum import Enum
import random
from typing import List, Optional, Set, Tuple


class Suit(Enum):
    """Card suit enumeration."""
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4
    
    def __str__(self) -> str:
        return self.name[0]
    
    @classmethod
    def from_str(cls, s: str) -> "Suit":
        """Create a Suit from a string representation."""
        s = s.upper()
        if s in ('C', 'CLUBS'):
            return cls.CLUBS
        elif s in ('D', 'DIAMONDS'):
            return cls.DIAMONDS
        elif s in ('H', 'HEARTS'):
            return cls.HEARTS
        elif s in ('S', 'SPADES'):
            return cls.SPADES
        raise ValueError(f"Invalid suit: {s}")


class Rank(Enum):
    """Card rank enumeration."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    
    def __str__(self) -> str:
        if self.value <= 10:
            return str(self.value)
        return self.name[0]
    
    @classmethod
    def from_str(cls, r: str) -> "Rank":
        """Create a Rank from a string representation."""
        r = r.upper()
        if r == 'A':
            return cls.ACE
        elif r == 'K':
            return cls.KING
        elif r == 'Q':
            return cls.QUEEN
        elif r == 'J':
            return cls.JACK
        elif r == 'T' or r == '10':
            return cls.TEN
        elif r.isdigit() and 2 <= int(r) <= 9:
            return cls(int(r))
        raise ValueError(f"Invalid rank: {r}")


class Card:
    """A playing card with a rank and suit."""
    
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"
    
    def __repr__(self) -> str:
        return f"Card({self.rank}, {self.suit})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
    
    @classmethod
    def from_str(cls, s: str) -> "Card":
        """Create a Card from a string representation (e.g., 'AS' for Ace of Spades)."""
        if len(s) < 2:
            raise ValueError(f"Invalid card string: {s}")
        
        rank_str = s[:-1]
        suit_str = s[-1]
        
        return cls(Rank.from_str(rank_str), Suit.from_str(suit_str))


class Deck:
    """A deck of playing cards."""
    
    def __init__(self, shuffled: bool = True):
        self.cards: List[Card] = []
        self.dealt_cards: Set[Card] = set()
        self.reset(shuffled)
    
    def reset(self, shuffled: bool = True) -> None:
        """Reset the deck to a full set of cards."""
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.dealt_cards = set()
        if shuffled:
            self.shuffle()
    
    def shuffle(self) -> None:
        """Shuffle the remaining cards in the deck."""
        random.shuffle(self.cards)
    
    def deal(self, n: int = 1) -> List[Card]:
        """Deal n cards from the deck."""
        if n > len(self.cards):
            raise ValueError(f"Cannot deal {n} cards, only {len(self.cards)} remaining")
        
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        self.dealt_cards.update(dealt)
        return dealt
    
    def deal_card(self) -> Card:
        """Deal a single card from the deck."""
        return self.deal(1)[0]
    
    def remaining(self) -> int:
        """Return the number of cards remaining in the deck."""
        return len(self.cards)
    
    def __len__(self) -> int:
        return self.remaining()
