"""Poker game state management."""
from typing import List, Dict, Any, Optional, Tuple, Set
import random
import logging
from collections import defaultdict

from poker_ai.engine.card import Card, Deck
from poker_ai.engine.action import Action, ActionType, BettingRound
from poker_ai.engine.evaluator import HandEvaluator
from poker_ai.game.player import Player


class GameState:
    """Manages the state of a poker game."""
    
    def __init__(
        self,
        players: List[Player],
        small_blind: float = 1.0,
        big_blind: float = 2.0,
        ante: float = 0.0
    ):
        """
        Initialize the game state.
        
        Args:
            players: List of players in the game
            small_blind: Small blind amount
            big_blind: Big blind amount
            ante: Ante amount (if any)
        """
        if len(players) < 2:
            raise ValueError("Need at least 2 players for a poker game")
            
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.ante = ante
        
        # Game state variables
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0.0
        self.side_pots: List[Tuple[float, Set[str]]] = []  # [(amount, set of eligible player IDs)]
        self.current_bet = 0.0
        self.min_raise = big_blind
        self.button_pos = 0
        self.current_player_idx = 0
        self.betting_round = BettingRound.PREFLOP
        self.hand_over = False
        self.hand_history: List[Dict[str, Any]] = []
        self.players_acted_in_round = 0  # Track how many players have acted in the current round
        self.round_started = False  # Track if the current betting round has started
        
        # Initialize player positions
        self._assign_positions()
        
        # Hand evaluator
        self.evaluator = HandEvaluator()
    
    def _assign_positions(self) -> None:
        """Assign positions to players at the table."""
        for i, player in enumerate(self.players):
            player.position = (i + self.button_pos) % len(self.players)
    
    def start_new_hand(self) -> None:
        """Start a new hand of poker."""
        # Reset the deck
        self.deck = Deck()
        
        # Reset game state variables
        self.community_cards = []
        self.pot = 0.0
        self.side_pots = []
        self.current_bet = 0.0
        self.min_raise = self.big_blind
        self.betting_round = BettingRound.PREFLOP
        self.hand_over = False
        self.hand_history = []
        self.players_acted_in_round = 0
        self.round_started = False
        
        # Check for players with low balances
        for player in self.players:
            if player.stack < 20:
                logging.warning(f"Player {player.name} has a low stack: {player.stack} at start of hand")
        
        # Reset player states for the new hand
        for player in self.players:
            player.reset_for_new_hand()
        
        # Move the button to the next player
        self.button_pos = (self.button_pos + 1) % len(self.players)
        
        # Deal cards to players
        for player in self.players:
            player.receive_cards(self.deck.deal(2))
            
        # Post blinds and antes
        self._post_blinds_and_antes()
        
        # Set the first player to act (after the big blind in preflop)
        self.current_player_idx = (self.button_pos + 3) % len(self.players)
        if len(self.players) == 2:  # Heads-up play
            self.current_player_idx = self.button_pos  # Button acts first preflop in heads-up
        
        # Make sure the first player is active
        self._move_to_next_player()
        
        # Log the start of the hand
        self._log_action({
            "type": "hand_start",
            "button_pos": self.button_pos,
            "players": [p.to_dict() for p in self.players]
        })
    
    def _post_blinds_and_antes(self) -> None:
        """Post blinds and antes for all players."""
        # Post antes if any
        if self.ante > 0:
            for player in self.players:
                if player.stack > 0:
                    ante_amount = min(self.ante, player.stack)
                    player.place_bet(ante_amount)
                    self.pot += ante_amount
                    
                    if player.stack == 0:
                        player.is_all_in = True
                        logging.debug(f"Player {player.name} is all-in after posting ante")
        
        # Post small blind
        sb_pos = (self.button_pos + 1) % len(self.players)
        sb_player = self.players[sb_pos]
        
        if sb_player.stack > 0:
            # If player's stack is less than small blind, they go all-in
            if sb_player.stack <= self.small_blind:
                logging.warning(f"Player {sb_player.name} has stack {sb_player.stack} less than small blind {self.small_blind}, going all-in")
                sb_amount = sb_player.stack
                sb_player.place_bet(sb_amount)
                sb_player.is_all_in = True
            else:
                sb_amount = self.small_blind
                sb_player.place_bet(sb_amount)
                
            self.pot += sb_amount
            self.current_bet = sb_amount
            
            self._log_action({
                "type": "post_blind",
                "player_id": sb_player.player_id,
                "amount": sb_amount,
                "blind_type": "small_blind"
            })
        
        # Post big blind
        bb_pos = (self.button_pos + 2) % len(self.players)
        bb_player = self.players[bb_pos]
        
        if bb_player.stack > 0:
            # If player's stack is less than big blind, they go all-in
            if bb_player.stack <= self.big_blind:
                logging.warning(f"Player {bb_player.name} has stack {bb_player.stack} less than big blind {self.big_blind}, going all-in")
                bb_amount = bb_player.stack
                bb_player.place_bet(bb_amount)
                bb_player.is_all_in = True
            else:
                bb_amount = self.big_blind
                bb_player.place_bet(bb_amount)
                
            self.pot += bb_amount
            self.current_bet = bb_amount
            
            self._log_action({
                "type": "post_blind",
                "player_id": bb_player.player_id,
                "amount": bb_amount,
                "blind_type": "big_blind"
            })
        
        # Log player stacks after blinds
        for player in self.players:
            if player.stack < 20:
                logging.debug(f"Player {player.name} has low stack: {player.stack} after blinds")
                logging.debug(f"  - is_active: {player.is_active}, is_all_in: {player.is_all_in}, current_bet: {player.current_bet}")
    
    def _log_action(self, action_data: Dict[str, Any]) -> None:
        """Add an action to the hand history."""
        action_data["betting_round"] = self.betting_round.name if hasattr(self.betting_round, "name") else str(self.betting_round)
        action_data["pot"] = self.pot
        self.hand_history.append(action_data)
    
    def get_valid_actions(self, player: Player) -> List[ActionType]:
        """
        Get the list of valid actions for a player.
        
        Args:
            player: The player to get valid actions for
            
        Returns:
            List of valid ActionType values
        """
        valid_actions = []
        
        # Can always fold unless can check
        if self.current_bet > player.current_bet:
            valid_actions.append(ActionType.FOLD)
        
        # Can check if no bet to call
        if self.current_bet == player.current_bet:
            valid_actions.append(ActionType.CHECK)
        
        # Can call if there's a bet to call and player has enough chips
        to_call = self.current_bet - player.current_bet
        if to_call > 0 and player.stack > 0:
            if to_call >= player.stack:
                valid_actions.append(ActionType.ALL_IN)
            else:
                valid_actions.append(ActionType.CALL)
        
        # Can bet if no current bet and player has enough chips
        if self.current_bet == 0 and player.stack > 0:
            if player.stack <= self.min_raise:
                valid_actions.append(ActionType.ALL_IN)
            else:
                valid_actions.append(ActionType.BET)
        
        # Can raise if there's a current bet and player has enough chips
        if self.current_bet > 0 and player.stack > to_call:
            if player.stack <= to_call + self.min_raise:
                valid_actions.append(ActionType.ALL_IN)
            else:
                valid_actions.append(ActionType.RAISE)
        
        return valid_actions
    
    def apply_action(self, action: Action) -> None:
        """
        Apply a player action to the game state.
        
        Args:
            action: The action to apply
        """
        player = self._get_player_by_id(action.player_id)
        if not player:
            raise ValueError(f"Player with ID {action.player_id} not found")
            
        if not player.is_active:
            raise ValueError(f"Player {player.name} is not active in this hand")
        
        # Add detailed logging for low stack situations
        for p in self.players:
            if p.stack < 20:
                logging.debug(f"Player {p.name} has low stack: {p.stack} before action {action.action_type.name}")
                logging.debug(f"  - is_active: {p.is_active}, is_all_in: {p.is_all_in}, current_bet: {p.current_bet}")
            
        # Check if player has a very small stack and mark as all-in if needed
        if player.stack <= 0.001 and player.stack > 0:
            logging.warning(f"Player {player.name} has a very small stack ({player.stack}), marking as all-in")
            player.stack = 0
            player.is_all_in = True
        
        # If player's stack is less than the minimum bet/raise, convert to ALL_IN
        if action.action_type in [ActionType.BET, ActionType.RAISE]:
            min_amount = self.big_blind
            if action.action_type == ActionType.RAISE:
                min_amount = self.current_bet + self.min_raise
                
            if player.stack <= min_amount:
                logging.warning(f"Player {player.name} has stack {player.stack} less than min {action.action_type.name} amount {min_amount}, converting to ALL_IN")
                action_type = ActionType.ALL_IN
                action_amount = player.stack
            else:
                action_type = action.action_type
                action_amount = action.amount
        else:
            action_type = action.action_type
            action_amount = action.amount
        
        # Log the action
        self._log_action({
            "type": "player_action",
            "player_id": player.player_id,
            "action": action_type.name,
            "amount": action_amount if action_type not in [ActionType.FOLD, ActionType.CHECK] else 0
        })
        
        # Apply the action
        if action_type == ActionType.FOLD:
            player.fold()
            
            # If only one player remains active, end the hand
            if self._count_active_players() == 1:
                self._end_hand()
                return
            
        elif action_type == ActionType.CHECK:
            pass
            
        elif action_type == ActionType.CALL:
            call_amount = min(self.current_bet - player.current_bet, player.stack)
            player.place_bet(call_amount)
            self.pot += call_amount
            
            # If player used all their stack, they're all-in
            if player.stack == 0:
                player.is_all_in = True
                logging.debug(f"Player {player.name} is all-in after CALL")
            
        elif action_type == ActionType.BET:
            bet_amount = player.place_bet(min(action_amount, player.stack))
            self.pot += bet_amount
            
            # If player used all their stack, they're all-in
            if player.stack == 0:
                player.is_all_in = True
                logging.debug(f"Player {player.name} is all-in after BET")
                
            # Update current bet and minimum raise
            if bet_amount > 0:
                self.current_bet = player.current_bet
                self.min_raise = max(self.min_raise, bet_amount)
                
        elif action_type == ActionType.RAISE:
            # Calculate raise amount
            raise_amount = min(action_amount, player.stack)
            player.place_bet(raise_amount)
            self.pot += raise_amount
            
            # If player used all their stack, they're all-in
            if player.stack == 0:
                player.is_all_in = True
                logging.debug(f"Player {player.name} is all-in after RAISE")
                
            # Update current bet and minimum raise
            if player.current_bet > self.current_bet:
                raise_diff = player.current_bet - self.current_bet
                self.current_bet = player.current_bet
                self.min_raise = max(self.min_raise, raise_diff)
            
        elif action_type == ActionType.ALL_IN:
            all_in_amount = player.place_bet(player.stack)
            self.pot += all_in_amount
            player.is_all_in = True  # Explicitly set the all-in flag
            logging.debug(f"Player {player.name} is ALL_IN with amount {all_in_amount}")
            
            # If this all-in raises the bet
            if player.current_bet > self.current_bet:
                raise_amount = player.current_bet - self.current_bet
                self.current_bet = player.current_bet
                self.min_raise = max(self.min_raise, raise_amount)
        
        # Mark that this player has acted in this round
        player.has_acted_this_round = True
        self.players_acted_in_round += 1
        
        # Log player states after action
        for p in self.players:
            if p.stack < 20:
                logging.debug(f"Player {p.name} has low stack: {p.stack} after action {action_type.name}")
                logging.debug(f"  - is_active: {p.is_active}, is_all_in: {p.is_all_in}, current_bet: {p.current_bet}")
        
        # Move to the next player
        self._move_to_next_player()
    
    def _get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Get a player by their ID."""
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
    
    def _move_to_next_player(self) -> None:
        """Move to the next player in the action sequence."""
        # Add a loop counter to detect infinite loops
        loop_counter = getattr(self, '_loop_counter', 0)
        self._loop_counter = loop_counter + 1
        
        # If we've been in this method too many times, we might be in an infinite loop
        if self._loop_counter > 1000:
            logging.warning(f"Potential infinite loop detected in _move_to_next_player! Counter: {self._loop_counter}")
            logging.warning(f"Betting round: {self.betting_round.name}, Current bet: {self.current_bet}")
            logging.warning(f"Players acted in round: {self.players_acted_in_round}, Round started: {self.round_started}")
            
            # Log player states
            for i, player in enumerate(self.players):
                logging.warning(f"Player {i} ({player.name}): active={player.is_active}, all_in={player.is_all_in}, " +
                              f"stack={player.stack}, bet={player.current_bet}, acted={player.has_acted_this_round}")
            
            # Emergency exit - end the betting round
            logging.warning("Emergency ending of betting round to prevent infinite loop")
            self._end_betting_round()
            # Reset the counter
            self._loop_counter = 0
            return
        
        # First, check if any player has a negative stack (this shouldn't happen, but let's be safe)
        for player in self.players:
            if player.stack < 0:
                logging.warning(f"Player {player.name} has a negative stack: {player.stack}. Setting to 0.")
                player.stack = 0
                player.is_all_in = True
        
        # Get the number of active players who can still act
        active_players = [p for p in self.players if p.is_active and not p.is_all_in and p.stack > 0]
        active_players_count = len(active_players)
        
        # If no active players can act, end the betting round
        if active_players_count == 0:
            logging.debug("No active players can act, ending betting round")
            self._end_betting_round()
            # Reset the counter
            self._loop_counter = 0
            return
        
        # Check if all active players have equal bets
        all_bets_equal = True
        for player in active_players:
            if player.current_bet < self.current_bet:
                all_bets_equal = False
                logging.debug(f"Player {player.name} has bet {player.current_bet} which is less than current bet {self.current_bet}")
                break
        
        # Count how many active players there are
        active_player_count = sum(1 for p in self.players if p.is_active)
        
        # If all players have acted and all bets are equal, end the betting round
        if all_bets_equal and self.players_acted_in_round >= active_player_count and self.round_started:
            logging.debug("All players have acted and all bets are equal, ending betting round")
            self._end_betting_round()
            # Reset the counter
            self._loop_counter = 0
            return
        
        # Find the next active player who needs to act
        start_idx = self.current_player_idx
        checked_all_players = False
        found_player_to_act = False
        
        # Loop through players to find the next one who needs to act
        for _ in range(len(self.players)):
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            current_player = self.players[self.current_player_idx]
            
            # If we've gone all the way around
            if self.current_player_idx == start_idx:
                checked_all_players = True
                logging.debug("Checked all players, back to start")
                
                # In poker, if everyone has acted and all bets are equal, the betting round ends
                if all_bets_equal and self.round_started:
                    logging.debug("All players checked and all bets equal, ending betting round")
                    self._end_betting_round()
                    # Reset the counter
                    self._loop_counter = 0
                    return
            
            # If this player can act - make sure they have a positive stack
            if current_player.is_active and not current_player.is_all_in:
                # Check if player has zero or near-zero stack
                if current_player.stack <= 0.001:  # Using a small threshold to catch floating point issues
                    # Player has no chips left, mark them as all-in
                    logging.debug(f"Player {current_player.name} has stack {current_player.stack}, marking as all-in")
                    current_player.stack = 0
                    current_player.is_all_in = True
                    continue
                
                # Check if this player needs to act (hasn't acted or needs to call a bet)
                if current_player.current_bet < self.current_bet or not current_player.has_acted_this_round:
                    logging.debug(f"Found player {current_player.name} who needs to act")
                    # Mark that the betting round has started
                    self.round_started = True
                    found_player_to_act = True
                    # Reset the counter
                    self._loop_counter = 0
                    return
        
        # If we've gone through all players and haven't found anyone who needs to act
        if not found_player_to_act:
            # If all bets are equal, end the betting round
            if all_bets_equal:
                logging.debug("Checked all players, no one needs to act, ending betting round")
                self._end_betting_round()
            else:
                # This is a safety check to prevent infinite loops
                logging.warning("WARNING - Potential logical issue detected!")
                logging.warning(f"checked_all_players: {checked_all_players}, all_bets_equal: {all_bets_equal}")
                
                # Emergency safety measure - end the betting round to prevent infinite loop
                logging.warning("Emergency ending of betting round to prevent logical issue")
                self._end_betting_round()
            
            # Reset the counter
            self._loop_counter = 0
    
    def is_betting_round_starting(self) -> bool:
        """Check if we're at the start of a betting round."""
        # In preflop, we start after the big blind
        if self.betting_round == BettingRound.PREFLOP:
            bb_pos = (self.button_pos + 2) % len(self.players)
            return self.current_player_idx == (bb_pos + 1) % len(self.players)
        
        # In other rounds, we start with the first active player after the button
        return self.current_player_idx == (self.button_pos + 1) % len(self.players)
    
    def _end_betting_round(self) -> None:
        """End the current betting round and move to the next phase."""
        # Reset player action flags for the next round
        for player in self.players:
            player.has_acted_this_round = False
            
            # Check for players with very small stacks and mark them as all-in
            if player.stack <= 0.001 and player.stack > 0:
                logging.debug(f"Player {player.name} has a very small stack ({player.stack}) at end of betting round, marking as all-in")
                player.stack = 0
                player.is_all_in = True
        
        # Reset the players acted counter
        self.players_acted_in_round = 0
        self.round_started = False
        
        # Move to the next betting round
        if self.betting_round == BettingRound.PREFLOP:
            self.betting_round = BettingRound.FLOP
            self.community_cards.extend(self.deck.deal(3))
            self._log_action({
                "type": "deal_community",
                "cards": [str(card) for card in self.community_cards],
                "street": "FLOP"
            })
            
        elif self.betting_round == BettingRound.FLOP:
            self.betting_round = BettingRound.TURN
            self.community_cards.extend(self.deck.deal(1))
            self._log_action({
                "type": "deal_community",
                "cards": [str(card) for card in self.community_cards[-1:]],
                "street": "TURN"
            })
            
        elif self.betting_round == BettingRound.TURN:
            self.betting_round = BettingRound.RIVER
            self.community_cards.extend(self.deck.deal(1))
            self._log_action({
                "type": "deal_community",
                "cards": [str(card) for card in self.community_cards[-1:]],
                "street": "RIVER"
            })
            
        elif self.betting_round == BettingRound.RIVER:
            # End the hand and determine the winner
            self._create_side_pots()
            self._showdown()
            self._end_hand()
            return
        
        # Reset the current bet for the new betting round
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
        
        # Set the first active player after the button
        self.current_player_idx = self.button_pos
        self._move_to_next_player()  # Find the first active player who needs to act
        
        # Check if we should end the hand (only one player left)
        if self._count_active_players() <= 1:
            self._end_hand()
    
    def _count_active_players(self) -> int:
        """Count the number of active players."""
        return sum(1 for p in self.players if p.is_active)
    
    def _create_side_pots(self) -> None:
        """Create side pots for all-in situations."""
        # Sort players by their current bet (all-in amount)
        sorted_players = sorted(
            [p for p in self.players if p.is_active or p.is_all_in],
            key=lambda p: p.current_bet
        )
        
        if not sorted_players:
            return
        
        # Create side pots
        self.side_pots = []
        prev_bet = 0
        
        for player in sorted_players:
            if player.current_bet > prev_bet:
                # Create a side pot for this bet level
                pot_contribution = player.current_bet - prev_bet
                eligible_players = {p.player_id for p in sorted_players if p.current_bet >= player.current_bet}
                
                self.side_pots.append((pot_contribution * len(eligible_players), eligible_players))
                prev_bet = player.current_bet
    
    def _showdown(self) -> None:
        """Determine the winners of the hand at showdown."""
        # Create side pots if needed
        self._create_side_pots()
        
        # If no side pots, create a main pot with all active players
        if not self.side_pots:
            active_player_ids = {p.player_id for p in self.players if p.is_active or p.is_all_in}
            self.side_pots = [(self.pot, active_player_ids)]
        
        # Evaluate each player's hand
        player_hands = {}
        for player in self.players:
            if player.is_active or player.is_all_in:
                hand_strength, hand_rank, hand_desc = self.evaluator.evaluate_hand(
                    player.hole_cards, self.community_cards
                )
                player_hands[player.player_id] = (hand_strength, player)
        
        # Distribute each pot to winners
        pot_distributions = []
        remaining_pot = self.pot
        
        for pot_amount, eligible_player_ids in self.side_pots:
            pot_amount = min(pot_amount, remaining_pot)
            remaining_pot -= pot_amount
            
            # Find the best hand among eligible players
            eligible_hands = {pid: player_hands[pid] for pid in eligible_player_ids if pid in player_hands}
            if not eligible_hands:
                continue
                
            best_hand_strength = min(hand[0] for hand in eligible_hands.values())
            winners = [player for pid, (strength, player) in eligible_hands.items() 
                      if strength == best_hand_strength]
            
            # Split the pot among winners
            win_amount = pot_amount / len(winners)
            for winner in winners:
                winner.collect_winnings(win_amount)
                pot_distributions.append({
                    "player_id": winner.player_id,
                    "amount": win_amount,
                    "hand_description": self.evaluator.evaluator.class_to_string(
                        self.evaluator.evaluator.get_rank_class(best_hand_strength)
                    )
                })
        
        # Log the showdown results
        self._log_action({
            "type": "showdown",
            "community_cards": [str(card) for card in self.community_cards],
            "player_hands": {
                p.player_id: [str(card) for card in p.hole_cards]
                for p in self.players if p.is_active or p.is_all_in
            },
            "pot_distributions": pot_distributions
        })
        
        # End the hand
        self._end_hand()
    
    def _end_hand(self) -> None:
        """End the current hand."""
        # If only one player is active, they win the pot
        if self._count_active_players() == 1:
            winner = next(p for p in self.players if p.is_active)
            
            # Record the pot amount before giving it to the winner
            pot_amount = self.pot
            
            # Give the pot to the winner
            winner.collect_winnings(pot_amount)
            
            self._log_action({
                "type": "hand_end",
                "winner": winner.player_id,
                "amount": pot_amount,
                "reason": "all_others_folded"
            })
        
        self.hand_over = True
        
        # Reset pot for the next hand
        self.pot = 0.0
    
    def get_current_player(self) -> Optional[Player]:
        """Get the current player who needs to act."""
        if self.hand_over:
            return None
        return self.players[self.current_player_idx]
    
    def is_hand_over(self) -> bool:
        """Check if the current hand is over."""
        return self.hand_over
