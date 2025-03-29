"""Poker actions and betting round management."""
from enum import Enum, auto
from typing import Optional, Dict, Any


class ActionType(Enum):
    """Types of actions a player can take in poker."""
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    BET = auto()
    RAISE = auto()
    ALL_IN = auto()


class Action:
    """Represents a player action in the game."""
    
    def __init__(
        self, 
        action_type: ActionType, 
        amount: float = 0.0,
        player_id: Optional[str] = None
    ):
        """
        Initialize a player action.
        
        Args:
            action_type: The type of action
            amount: The bet/raise amount (if applicable)
            player_id: ID of the player taking the action
        """
        self.action_type = action_type
        self.amount = amount
        self.player_id = player_id
    
    def __str__(self) -> str:
        if self.action_type in [ActionType.FOLD, ActionType.CHECK]:
            return f"{self.action_type.name}"
        return f"{self.action_type.name} {self.amount:.2f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the action to a dictionary for serialization."""
        return {
            "action_type": self.action_type.name,
            "amount": self.amount,
            "player_id": self.player_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        """Create an Action from a dictionary."""
        return cls(
            action_type=ActionType[data["action_type"]],
            amount=data.get("amount", 0.0),
            player_id=data.get("player_id")
        )


class BettingRound(Enum):
    """Betting rounds in a poker hand."""
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()
    
    @classmethod
    def next_round(cls, current_round: "BettingRound") -> Optional["BettingRound"]:
        """Get the next betting round after the current one."""
        if current_round == cls.PREFLOP:
            return cls.FLOP
        elif current_round == cls.FLOP:
            return cls.TURN
        elif current_round == cls.TURN:
            return cls.RIVER
        elif current_round == cls.RIVER:
            return cls.SHOWDOWN
        return None  # No next round after showdown
