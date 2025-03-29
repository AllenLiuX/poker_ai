"""Poker game runner for local testing and simulation."""
import argparse
import time
from typing import List, Optional

from poker_ai.game.player import Player, HumanPlayer
from poker_ai.player.ai_player import BasicAIPlayer, AdvancedAIPlayer
from poker_ai.game.state import GameState
from poker_ai.engine.action import Action, ActionType


class GameRunner:
    """Runs a poker game simulation."""
    
    def __init__(
        self,
        num_ai_players: int = 5,
        starting_stack: float = 1000.0,
        small_blind: float = 1.0,
        big_blind: float = 2.0,
        ante: float = 0.0,
        include_human: bool = True,
        advanced_ai: bool = False
    ):
        """
        Initialize the game runner.
        
        Args:
            num_ai_players: Number of AI players
            starting_stack: Starting chip stack for all players
            small_blind: Small blind amount
            big_blind: Big blind amount
            ante: Ante amount
            include_human: Whether to include a human player
            advanced_ai: Whether to use advanced AI players
        """
        self.players: List[Player] = []
        
        # Add human player if requested
        if include_human:
            self.players.append(HumanPlayer(name="Human", stack=starting_stack))
        
        # Add AI players
        ai_class = AdvancedAIPlayer if advanced_ai else BasicAIPlayer
        for i in range(num_ai_players):
            self.players.append(ai_class(name=f"AI-{i+1}", stack=starting_stack))
        
        # Create game state
        self.game_state = GameState(
            players=self.players,
            small_blind=small_blind,
            big_blind=big_blind,
            ante=ante
        )
    
    def run_hand(self) -> None:
        """Run a single hand of poker."""
        # Start a new hand
        self.game_state.start_new_hand()
        print("\n" + "="*50)
        print(f"Starting new hand (Button: {self.players[self.game_state.button_pos].name})")
        print("="*50)
        
        # Main game loop
        while not self.game_state.is_hand_over():
            current_player = self.game_state.get_current_player()
            if not current_player:
                break
                
            # Display game state
            self._display_game_state()
            
            # Get valid actions
            valid_actions = self.game_state.get_valid_actions(current_player)
            
            # Get player action
            action = current_player.act(
                valid_actions,
                self.game_state.min_raise,
                self.game_state.current_bet,
                self.game_state.pot
            )
            
            # Display the action
            print(f"{current_player.name} {action}")
            
            # Apply the action
            self.game_state.apply_action(action)
            
            # Small delay for readability
            time.sleep(0.5)
        
        # Display final hand result
        self._display_hand_result()
    
    def _display_game_state(self) -> None:
        """Display the current game state."""
        print("\n" + "-"*50)
        
        # Show betting round
        print(f"Betting round: {self.game_state.betting_round.name}")
        
        # Show community cards
        if self.game_state.community_cards:
            print(f"Community cards: {' '.join(str(card) for card in self.game_state.community_cards)}")
        else:
            print("Community cards: None")
        
        # Show pot
        print(f"Pot: {self.game_state.pot:.2f}")
        
        # Show current bet
        print(f"Current bet: {self.game_state.current_bet:.2f}")
        
        # Show players and their states
        print("\nPlayers:")
        for player in self.game_state.players:
            status = "Active" if player.is_active else "Folded"
            if player.is_all_in:
                status = "All-in"
                
            position = ""
            if player.position == 0:
                position = "(BTN)"
            elif player.position == 1:
                position = "(SB)"
            elif player.position == 2:
                position = "(BB)"
                
            print(f"  {player.name} {position}: ${player.stack:.2f} - Bet: ${player.current_bet:.2f} - {status}")
        
        print("-"*50)
    
    def _display_hand_result(self) -> None:
        """Display the result of the hand."""
        print("\n" + "="*50)
        print("Hand complete!")
        
        # Find the last action in the hand history
        if self.game_state.hand_history:
            last_action = self.game_state.hand_history[-1]
            
            if last_action["type"] == "hand_end":
                winner_id = last_action["winner"]
                winner = next((p for p in self.players if p.player_id == winner_id), None)
                if winner:
                    print(f"{winner.name} wins ${last_action['amount']:.2f}")
                    
            elif last_action["type"] == "showdown":
                print("Showdown results:")
                for dist in last_action.get("pot_distributions", []):
                    winner_id = dist["player_id"]
                    winner = next((p for p in self.players if p.player_id == winner_id), None)
                    if winner:
                        print(f"  {winner.name} wins ${dist['amount']:.2f} with {dist['hand_description']}")
        
        # Show player stacks
        print("\nFinal stacks:")
        for player in sorted(self.players, key=lambda p: p.stack, reverse=True):
            print(f"  {player.name}: ${player.stack:.2f}")
        
        print("="*50)
    
    def run_game(self, num_hands: int = 10) -> None:
        """
        Run multiple hands of poker.
        
        Args:
            num_hands: Number of hands to play
        """
        for i in range(num_hands):
            self.run_hand()
            
            # Check if any players are out of chips
            self.players = [p for p in self.players if p.stack > 0]
            if len(self.players) < 2:
                print("Game over: Not enough players with chips remaining.")
                break
            
            # Update the game state with the current players
            self.game_state = GameState(
                players=self.players,
                small_blind=self.game_state.small_blind,
                big_blind=self.game_state.big_blind,
                ante=self.game_state.ante
            )


def main():
    """Main entry point for the poker game runner."""
    parser = argparse.ArgumentParser(description="Run a poker game simulation")
    parser.add_argument("--ai-players", type=int, default=5, help="Number of AI players")
    parser.add_argument("--stack", type=float, default=1000.0, help="Starting stack size")
    parser.add_argument("--small-blind", type=float, default=1.0, help="Small blind amount")
    parser.add_argument("--big-blind", type=float, default=2.0, help="Big blind amount")
    parser.add_argument("--ante", type=float, default=0.0, help="Ante amount")
    parser.add_argument("--hands", type=int, default=10, help="Number of hands to play")
    parser.add_argument("--no-human", action="store_true", help="Don't include a human player")
    parser.add_argument("--advanced-ai", action="store_true", help="Use advanced AI players")
    
    args = parser.parse_args()
    
    runner = GameRunner(
        num_ai_players=args.ai_players,
        starting_stack=args.stack,
        small_blind=args.small_blind,
        big_blind=args.big_blind,
        ante=args.ante,
        include_human=not args.no_human,
        advanced_ai=args.advanced_ai
    )
    
    runner.run_game(num_hands=args.hands)


if __name__ == "__main__":
    main()
