"""Player implementation for poker game."""
from typing import List, Dict, Any, Optional
import uuid

from poker_ai.engine.card import Card
from poker_ai.engine.action import Action, ActionType


class Player:
    """Base class for a poker player."""
    
    def __init__(
        self,
        player_id: Optional[str] = None,
        name: str = "Player",
        stack: float = 1000.0
    ):
        """
        Initialize a player.
        
        Args:
            player_id: Unique identifier for the player (auto-generated if None)
            name: Display name for the player
            stack: Starting chip stack
        """
        self.player_id = player_id or str(uuid.uuid4())
        self.name = name
        self.stack = stack
        self.hole_cards: List[Card] = []
        self.current_bet = 0.0
        self.is_active = True  # Whether the player is active in the current hand
        self.is_all_in = False
        self.position = -1  # Position at the table (0 = button, 1 = small blind, etc.)
        self.has_acted_this_round = False  # Whether the player has acted in the current betting round
        
    def reset_for_new_hand(self) -> None:
        """Reset player state for a new hand."""
        self.hole_cards = []
        self.current_bet = 0.0
        self.is_active = True
        self.is_all_in = False
        self.has_acted_this_round = False
    
    def receive_cards(self, cards: List[Card]) -> None:
        """Receive hole cards."""
        self.hole_cards = cards
    
    def place_bet(self, amount: float) -> float:
        """
        Place a bet of the specified amount.
        
        Args:
            amount: Amount to bet
            
        Returns:
            Actual amount bet (may be less if player doesn't have enough chips)
        """
        amount = min(amount, self.stack)
        self.stack -= amount
        self.current_bet += amount
        
        if self.stack == 0:
            self.is_all_in = True
            
        return amount
    
    def collect_winnings(self, amount: float) -> None:
        """Add winnings to the player's stack."""
        self.stack += amount
    
    def can_afford(self, amount: float) -> bool:
        """Check if the player can afford a bet of the specified amount."""
        return self.stack >= amount
    
    def fold(self) -> None:
        """Fold the current hand."""
        self.is_active = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the player to a dictionary for serialization."""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "stack": self.stack,
            "current_bet": self.current_bet,
            "is_active": self.is_active,
            "is_all_in": self.is_all_in,
            "position": self.position,
            "hole_cards": [str(card) for card in self.hole_cards]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Create a Player from a dictionary."""
        player = cls(
            player_id=data["player_id"],
            name=data["name"],
            stack=data["stack"]
        )
        player.current_bet = data["current_bet"]
        player.is_active = data["is_active"]
        player.is_all_in = data["is_all_in"]
        player.position = data["position"]
        # Note: hole cards would need to be reconstructed from strings
        return player
    
    def act(self, valid_actions: List[ActionType], min_raise: float, 
            current_bet: float, pot_size: float) -> Action:
        """
        Determine the player's action.
        This is an abstract method that should be overridden by subclasses.
        
        Args:
            valid_actions: List of valid action types
            min_raise: Minimum raise amount
            current_bet: Current bet to call
            pot_size: Current pot size
            
        Returns:
            The chosen action
        """
        raise NotImplementedError("Subclasses must implement act()")


class HumanPlayer(Player):
    """Human player implementation that takes input from the console."""
    
    def act(self, valid_actions: List[ActionType], min_raise: float, 
            current_bet: float, pot_size: float) -> Action:
        """Get action from human input."""
        to_call = current_bet - self.current_bet
        
        print(f"\n{self.name}'s turn (Stack: {self.stack:.2f})")
        print(f"Pot: {pot_size:.2f}, To call: {to_call:.2f}")
        print(f"Your cards: {' '.join(str(card) for card in self.hole_cards)}")
        
        # Display valid actions
        print("\nValid actions:")
        action_map = {}
        action_idx = 1
        
        if ActionType.FOLD in valid_actions:
            print(f"{action_idx}. Fold")
            action_map[action_idx] = (ActionType.FOLD, 0)
            action_idx += 1
            
        if ActionType.CHECK in valid_actions:
            print(f"{action_idx}. Check")
            action_map[action_idx] = (ActionType.CHECK, 0)
            action_idx += 1
        
        if ActionType.CALL in valid_actions:
            print(f"{action_idx}. Call {to_call:.2f}")
            action_map[action_idx] = (ActionType.CALL, to_call)
            action_idx += 1
            
        if ActionType.BET in valid_actions:
            print(f"{action_idx}. Bet (min: {min_raise:.2f})")
            action_map[action_idx] = (ActionType.BET, min_raise)
            action_idx += 1
            
        if ActionType.RAISE in valid_actions:
            print(f"{action_idx}. Raise (min: {min_raise:.2f})")
            action_map[action_idx] = (ActionType.RAISE, min_raise)
            action_idx += 1
            
        if ActionType.ALL_IN in valid_actions:
            print(f"{action_idx}. All-in ({self.stack:.2f})")
            action_map[action_idx] = (ActionType.ALL_IN, self.stack)
            action_idx += 1
        
        # Get player choice
        choice = 0
        while choice not in action_map:
            try:
                choice = int(input("Enter your choice (number): "))
                if choice not in action_map:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")
        
        action_type, default_amount = action_map[choice]
        
        # If bet or raise, get amount
        amount = default_amount
        if action_type in [ActionType.BET, ActionType.RAISE] and self.stack > default_amount:
            while True:
                try:
                    amount_str = input(f"Enter amount (min {default_amount:.2f}, max {self.stack:.2f}): ")
                    if not amount_str:  # Use default if empty
                        break
                    
                    amount = float(amount_str)
                    if amount < default_amount:
                        print(f"Amount must be at least {default_amount:.2f}")
                    elif amount > self.stack:
                        print(f"You only have {self.stack:.2f}")
                    else:
                        break
                except ValueError:
                    print("Please enter a valid number.")
        
        self.has_acted_this_round = True
        return Action(action_type, amount, self.player_id)
