"""GTO-based AI player implementation for poker."""
import random
from typing import List, Dict, Any, Optional, Tuple
import math

from poker_ai.engine.card import Card
from poker_ai.engine.action import Action, ActionType, BettingRound
from poker_ai.engine.evaluator import HandEvaluator
from poker_ai.game.player import Player


class GTOPlayer(Player):
    """
    A GTO-based AI player that makes decisions based on game theory optimal principles.
    
    This player uses a combination of hand strength, pot odds, position, and
    randomization to approximate GTO play. It can be configured to deviate from
    GTO toward more exploitative strategies.
    """
    
    def __init__(
        self,
        player_id: Optional[str] = None,
        name: str = "GTO Player",
        stack: float = 1000.0,
        aggression: float = 1.0,
        bluff_frequency: float = 0.3,
        fold_to_3bet: float = 0.5,
        call_efficiency: float = 1.0,
        positional_awareness: float = 1.0,
        randomization: float = 1.0,
        gto_deviation: float = 0.0  # 0.0 = pure GTO, 1.0 = fully exploitative
    ):
        """
        Initialize a GTO-based AI player.
        
        Args:
            player_id: Unique identifier for the player
            name: Display name for the player
            stack: Starting chip stack
            aggression: How aggressively the player plays (1.0 = balanced)
            bluff_frequency: How often the player bluffs (0.3 = balanced)
            fold_to_3bet: How often the player folds to 3bets (0.5 = balanced)
            call_efficiency: How efficiently the player calls (1.0 = optimal)
            positional_awareness: How much position affects decisions (1.0 = optimal)
            randomization: How much randomization in decisions (1.0 = optimal)
            gto_deviation: How much to deviate from GTO toward exploitative play
        """
        super().__init__(player_id, name, stack)
        self.evaluator = HandEvaluator()
        
        # Strategy parameters
        self.aggression = aggression
        self.bluff_frequency = bluff_frequency
        self.fold_to_3bet = fold_to_3bet
        self.call_efficiency = call_efficiency
        self.positional_awareness = positional_awareness
        self.randomization = randomization
        self.gto_deviation = gto_deviation
        
        # Hand ranges by position (simplified)
        self.preflop_ranges = self._initialize_preflop_ranges()
        
        # Tracking variables
        self.opponent_models = {}
        self.hand_history = []
        self.current_hand_actions = []
        self.current_betting_round = None
    
    def _initialize_preflop_ranges(self) -> Dict[int, Dict[str, float]]:
        """
        Initialize preflop hand ranges by position.
        
        Returns:
            Dictionary mapping position to hand ranges
        """
        # This is a simplified model - a real implementation would have more detailed ranges
        ranges = {}
        
        # Button (position 0) - widest range
        ranges[0] = {
            "raise": 0.3,    # Top 30% of hands
            "call": 0.15,    # Next 15% of hands
            "fold": 0.55     # Bottom 55% of hands
        }
        
        # Small blind (position 1)
        ranges[1] = {
            "raise": 0.2,    # Top 20% of hands
            "call": 0.2,     # Next 20% of hands
            "fold": 0.6      # Bottom 60% of hands
        }
        
        # Big blind (position 2)
        ranges[2] = {
            "raise": 0.15,   # Top 15% of hands
            "call": 0.3,     # Next 30% of hands
            "fold": 0.55     # Bottom 55% of hands
        }
        
        # Early position (positions 3-4)
        for pos in [3, 4]:
            ranges[pos] = {
                "raise": 0.1,    # Top 10% of hands
                "call": 0.1,     # Next 10% of hands
                "fold": 0.8      # Bottom 80% of hands
            }
        
        # Middle position (positions 5-6)
        for pos in [5, 6]:
            ranges[pos] = {
                "raise": 0.15,   # Top 15% of hands
                "call": 0.15,    # Next 15% of hands
                "fold": 0.7      # Bottom 70% of hands
            }
        
        # Late position (positions 7-9)
        for pos in [7, 8, 9]:
            ranges[pos] = {
                "raise": 0.25,   # Top 25% of hands
                "call": 0.15,    # Next 15% of hands
                "fold": 0.6      # Bottom 60% of hands
            }
        
        return ranges
    
    def _get_hand_percentile(self, hole_cards: List[Card]) -> float:
        """
        Calculate the percentile of a starting hand (0.0 to 1.0).
        
        Args:
            hole_cards: The player's hole cards
            
        Returns:
            Hand percentile (1.0 = best hand, 0.0 = worst hand)
        """
        # This is a simplified model - a real implementation would use precomputed tables
        
        # Check for pocket pairs
        if hole_cards[0].rank == hole_cards[1].rank:
            # Rank from 2 (0.5) to A (1.0)
            pair_rank = hole_cards[0].rank.value
            if pair_rank == 14:  # Aces
                return 1.0
            elif pair_rank == 13:  # Kings
                return 0.95
            elif pair_rank == 12:  # Queens
                return 0.9
            elif pair_rank == 11:  # Jacks
                return 0.85
            else:
                # Other pairs scale from 0.5 (22) to 0.8 (TT)
                return 0.5 + ((pair_rank - 2) / 18)
        
        # Check for suited cards
        suited = hole_cards[0].suit == hole_cards[1].suit
        
        # Get the ranks in descending order
        ranks = sorted([card.rank.value for card in hole_cards], reverse=True)
        high_rank, low_rank = ranks
        
        # Calculate gap between cards
        gap = high_rank - low_rank
        
        # Base score from high card
        base_score = (high_rank - 2) / 12  # 0.0 for 2, 1.0 for A
        
        # Adjust for connectedness and suitedness
        connectedness = max(0, 1 - (gap / 12))
        suited_bonus = 0.1 if suited else 0
        
        # Premium hands (AK, AQ, KQ)
        if high_rank >= 12 and low_rank >= 10:  # AK, AQ, KQ, etc.
            if high_rank == 14 and low_rank == 13 and suited:  # AKs
                return 0.88  # Just below QQ
            elif high_rank == 14 and low_rank == 13:  # AKo
                return 0.83  # Just below JJ
            return min(0.82, 0.7 + suited_bonus + (connectedness * 0.2))
        
        # Connected and suited hands (like T9s)
        if gap <= 3 and suited:
            return min(0.7, 0.5 + base_score * 0.3 + connectedness * 0.2)
        
        # Other hands
        return min(0.6, base_score * 0.4 + connectedness * 0.1 + suited_bonus)
    
    def _adjust_for_position(self, base_value: float) -> float:
        """
        Adjust a decision value based on position.
        
        Args:
            base_value: Base decision value
            
        Returns:
            Position-adjusted value
        """
        # Position adjustments (simplified)
        position_multipliers = {
            0: 1.2,   # Button - most aggressive
            1: 0.9,   # Small blind
            2: 0.8,   # Big blind
            3: 0.7,   # UTG - tightest
            4: 0.75,  # UTG+1
            5: 0.8,   # MP1
            6: 0.85,  # MP2
            7: 0.9,   # CO-1
            8: 1.0,   # CO
            9: 1.1    # HJ
        }
        
        # Default to UTG multiplier if position not found
        multiplier = position_multipliers.get(self.position, 0.7)
        
        # Apply positional awareness parameter
        effective_multiplier = 1.0 + (multiplier - 1.0) * self.positional_awareness
        
        return base_value * effective_multiplier
    
    def _should_bluff(self, equity: float, pot_odds: float) -> bool:
        """
        Determine if the player should bluff based on equity and pot odds.
        
        Args:
            equity: Hand equity
            pot_odds: Pot odds for the current decision
            
        Returns:
            True if the player should bluff
        """
        # Base bluff threshold
        bluff_threshold = 0.3 - (equity * 0.3)  # Bluff less with stronger hands
        
        # Adjust for aggression and bluff frequency
        bluff_threshold *= (2.0 - self.aggression)  # More aggressive = more bluffs
        bluff_threshold /= (self.bluff_frequency * 3.0 + 0.1)  # Higher bluff frequency = more bluffs
        
        # Randomize the decision
        randomization_factor = random.uniform(0.7, 1.3) * self.randomization
        bluff_threshold *= randomization_factor
        
        # Decide whether to bluff
        return random.random() < bluff_threshold
    
    def _calculate_bet_sizing(self, equity: float, pot_size: float, 
                             betting_round: BettingRound) -> float:
        """
        Calculate optimal bet sizing based on hand equity and game state.
        
        Args:
            equity: Hand equity
            pot_size: Current pot size
            betting_round: Current betting round
            
        Returns:
            Bet size
        """
        # Base bet sizing as percentage of pot
        if betting_round == BettingRound.PREFLOP:
            # Preflop bets are typically 2.5-3x BB
            base_sizing = min(6, 3.0 * equity * 2.0)  # Cap at 6 units
        else:
            # Postflop bets scale with equity
            if equity < 0.4:
                # Small bets with weak hands (bluffs)
                base_sizing = 0.5 * pot_size
            elif equity < 0.7:
                # Medium bets with medium hands
                base_sizing = 0.6 * pot_size
            else:
                # Large bets with strong hands
                base_sizing = 0.75 * pot_size
                
            # Cap postflop bets at pot size
            base_sizing = min(base_sizing, pot_size)
        
        # Adjust for aggression
        sizing = base_sizing * self.aggression
        
        # Add some randomization
        randomization_factor = random.uniform(0.8, 1.2) * self.randomization
        sizing *= randomization_factor
        
        return sizing
    
    def _make_preflop_decision(self, valid_actions: List[ActionType], min_raise: float,
                              current_bet: float, pot_size: float) -> Action:
        """
        Make a preflop decision based on hand strength and position.
        
        Args:
            valid_actions: List of valid action types
            min_raise: Minimum raise amount
            current_bet: Current bet to call
            pot_size: Current pot size
            
        Returns:
            The chosen action
        """
        # Calculate hand percentile
        hand_percentile = self._get_hand_percentile(self.hole_cards)
        
        # Adjust based on position
        adjusted_percentile = self._adjust_for_position(hand_percentile)
        
        # Calculate pot odds
        to_call = current_bet - self.current_bet
        pot_odds = to_call / (pot_size + to_call) if pot_size + to_call > 0 else 0
        
        # Premium hands - raise or reraise
        if adjusted_percentile > 0.8:
            if ActionType.RAISE in valid_actions:
                bet_size = self._calculate_bet_sizing(adjusted_percentile, pot_size, BettingRound.PREFLOP)
                return Action(ActionType.RAISE, max(min_raise, bet_size), self.player_id)
            elif ActionType.BET in valid_actions:
                bet_size = self._calculate_bet_sizing(adjusted_percentile, pot_size, BettingRound.PREFLOP)
                return Action(ActionType.BET, bet_size, self.player_id)
            elif ActionType.CALL in valid_actions:
                return Action(ActionType.CALL, to_call, self.player_id)
            else:
                return Action(ActionType.CHECK, 0, self.player_id)
                
        # Strong hands - call or raise
        elif adjusted_percentile > 0.6:
            if random.random() < 0.7 * self.aggression:  # Sometimes raise
                if ActionType.RAISE in valid_actions:
                    bet_size = self._calculate_bet_sizing(adjusted_percentile, pot_size, BettingRound.PREFLOP)
                    return Action(ActionType.RAISE, max(min_raise, bet_size), self.player_id)
                elif ActionType.BET in valid_actions:
                    bet_size = self._calculate_bet_sizing(adjusted_percentile, pot_size, BettingRound.PREFLOP)
                    return Action(ActionType.BET, bet_size, self.player_id)
            
            if ActionType.CALL in valid_actions:
                return Action(ActionType.CALL, to_call, self.player_id)
            elif ActionType.CHECK in valid_actions:
                return Action(ActionType.CHECK, 0, self.player_id)
            else:
                return Action(ActionType.FOLD, 0, self.player_id)
                
        # Medium hands - call if pot odds are good
        elif adjusted_percentile > 0.4:
            if pot_odds < adjusted_percentile * self.call_efficiency:
                if ActionType.CALL in valid_actions:
                    return Action(ActionType.CALL, to_call, self.player_id)
                elif ActionType.CHECK in valid_actions:
                    return Action(ActionType.CHECK, 0, self.player_id)
            
            # Sometimes raise as a semi-bluff
            if random.random() < 0.3 * self.aggression and self.position < 3:  # Only from late position
                if ActionType.RAISE in valid_actions:
                    bet_size = self._calculate_bet_sizing(adjusted_percentile, pot_size, BettingRound.PREFLOP)
                    return Action(ActionType.RAISE, max(min_raise, bet_size), self.player_id)
                elif ActionType.BET in valid_actions:
                    bet_size = self._calculate_bet_sizing(adjusted_percentile, pot_size, BettingRound.PREFLOP)
                    return Action(ActionType.BET, bet_size, self.player_id)
            
            if ActionType.CHECK in valid_actions:
                return Action(ActionType.CHECK, 0, self.player_id)
            else:
                return Action(ActionType.FOLD, 0, self.player_id)
                
        # Weak hands - check or fold
        else:
            if ActionType.CHECK in valid_actions:
                return Action(ActionType.CHECK, 0, self.player_id)
            else:
                # Occasionally bluff from late position
                if random.random() < 0.2 * self.bluff_frequency and self.position < 2:
                    if ActionType.RAISE in valid_actions:
                        bet_size = self._calculate_bet_sizing(0.6, pot_size, BettingRound.PREFLOP)  # Pretend it's stronger
                        return Action(ActionType.RAISE, max(min_raise, bet_size), self.player_id)
                    elif ActionType.BET in valid_actions:
                        bet_size = self._calculate_bet_sizing(0.6, pot_size, BettingRound.PREFLOP)
                        return Action(ActionType.BET, bet_size, self.player_id)
                
                return Action(ActionType.FOLD, 0, self.player_id)

    def _make_postflop_decision(self, valid_actions: List[ActionType], min_raise: float,
                               current_bet: float, pot_size: float,
                               community_cards: List[Card]) -> Action:
        """
        Make a postflop decision based on hand equity and pot odds.
        
        Args:
            valid_actions: List of valid action types
            min_raise: Minimum raise amount
            current_bet: Current bet to call
            pot_size: Current pot size
            community_cards: Community cards on the board
            
        Returns:
            The chosen action
        """
        # Calculate hand equity
        equity = self.evaluator.get_hand_equity(self.hole_cards, community_cards)
        
        # Calculate pot odds
        to_call = current_bet - self.current_bet
        pot_odds = to_call / (pot_size + to_call) if pot_size + to_call > 0 else 0
        
        # Determine betting round
        if len(community_cards) == 3:
            betting_round = BettingRound.FLOP
        elif len(community_cards) == 4:
            betting_round = BettingRound.TURN
        elif len(community_cards) == 5:
            betting_round = BettingRound.RIVER
        else:
            betting_round = BettingRound.PREFLOP
        
        # Check if we can check
        if ActionType.CHECK in valid_actions:
            # With strong hands, bet for value
            if equity > 0.7:
                if ActionType.BET in valid_actions:
                    bet_size = self._calculate_bet_sizing(equity, pot_size, betting_round)
                    return Action(ActionType.BET, max(bet_size, min_raise), self.player_id)
            
            # With medium hands, sometimes bet for protection
            elif equity > 0.5 and random.random() < 0.7 * self.aggression:
                if ActionType.BET in valid_actions:
                    bet_size = self._calculate_bet_sizing(equity, pot_size, betting_round)
                    return Action(ActionType.BET, max(bet_size, min_raise), self.player_id)
            
            # With weak hands, sometimes bluff
            elif self._should_bluff(equity, pot_odds):
                if ActionType.BET in valid_actions:
                    bet_size = self._calculate_bet_sizing(0.3, pot_size, betting_round)  # Bluff sizing
                    return Action(ActionType.BET, max(bet_size, min_raise), self.player_id)
            
            # Default to checking
            return Action(ActionType.CHECK, 0, self.player_id)
        
        # We need to call, raise, or fold
        
        # With strong hands, raise for value
        if equity > 0.7:
            if ActionType.RAISE in valid_actions and self.stack > to_call + min_raise:
                bet_size = self._calculate_bet_sizing(equity, pot_size, betting_round)
                return Action(ActionType.RAISE, max(bet_size, min_raise), self.player_id)
            elif ActionType.CALL in valid_actions:
                return Action(ActionType.CALL, to_call, self.player_id)
        
        # With medium hands, call if pot odds are good
        elif equity > pot_odds * self.call_efficiency:
            if ActionType.CALL in valid_actions:
                return Action(ActionType.CALL, to_call, self.player_id)
        
        # With weak hands, sometimes bluff-raise
        elif self._should_bluff(equity, pot_odds):
            if ActionType.RAISE in valid_actions and self.stack > to_call + min_raise:
                bet_size = self._calculate_bet_sizing(0.3, pot_size, betting_round)  # Bluff sizing
                return Action(ActionType.RAISE, max(bet_size, min_raise), self.player_id)
        
        # Default to folding
        if ActionType.FOLD in valid_actions:
            return Action(ActionType.FOLD, 0, self.player_id)
        elif ActionType.CHECK in valid_actions:
            return Action(ActionType.CHECK, 0, self.player_id)
        else:
            # If we can't fold or check, call as a last resort
            return Action(ActionType.CALL, to_call, self.player_id)
    
    def act(self, valid_actions: List[ActionType], min_raise: float, 
            current_bet: float, pot_size: float, 
            community_cards: Optional[List[Card]] = None) -> Action:
        """
        Determine the GTO player's action based on game state.
        
        Args:
            valid_actions: List of valid action types
            min_raise: Minimum raise amount
            current_bet: Current bet to call
            pot_size: Current pot size
            community_cards: Community cards on the board (if any)
            
        Returns:
            The chosen action
        """
        # Default to empty list if community cards not provided
        if community_cards is None:
            community_cards = []
        
        # Determine if we're preflop or postflop
        if not community_cards:
            action = self._make_preflop_decision(valid_actions, min_raise, current_bet, pot_size)
        else:
            action = self._make_postflop_decision(valid_actions, min_raise, current_bet, 
                                                pot_size, community_cards)
        
        # Record the action
        self.current_hand_actions.append({
            "action_type": action.action_type.name,
            "amount": action.amount,
            "pot_size": pot_size,
            "community_cards": [str(card) for card in community_cards],
            "valid_actions": [a.name for a in valid_actions]
        })
        
        return action
    
    def update_opponent_model(self, opponent_id: str, action: Action, 
                             betting_round: BettingRound, pot_size: float) -> None:
        """
        Update the model of an opponent based on their action.
        
        Args:
            opponent_id: ID of the opponent
            action: The action taken by the opponent
            betting_round: Current betting round
            pot_size: Current pot size
        """
        if opponent_id not in self.opponent_models:
            self.opponent_models[opponent_id] = {
                "aggression": 1.0,
                "bluff_frequency": 0.3,
                "fold_to_3bet": 0.5,
                "actions": []
            }
        
        # Record the action
        self.opponent_models[opponent_id]["actions"].append({
            "action_type": action.action_type.name,
            "amount": action.amount,
            "betting_round": betting_round.name,
            "pot_size": pot_size
        })
        
        # Update model based on action
        model = self.opponent_models[opponent_id]
        
        if action.action_type in [ActionType.BET, ActionType.RAISE]:
            # Increase aggression for betting/raising
            model["aggression"] = model["aggression"] * 0.9 + 0.1 * 1.5
            
            # Update bluff frequency (simplified)
            if len(self.opponent_models[opponent_id]["actions"]) > 10:
                if random.random() < 0.1:  # 10% chance this was a bluff
                    model["bluff_frequency"] = model["bluff_frequency"] * 0.95 + 0.05 * 1.0
        
        elif action.action_type == ActionType.FOLD:
            # Decrease aggression for folding
            model["aggression"] = model["aggression"] * 0.95 + 0.05 * 0.5
            
            # Update fold to 3bet if relevant
            if betting_round == BettingRound.PREFLOP:
                model["fold_to_3bet"] = model["fold_to_3bet"] * 0.9 + 0.1 * 1.0
    
    def reset_for_new_hand(self) -> None:
        """Reset player state for a new hand."""
        super().reset_for_new_hand()
        self.current_hand_actions = []
        self.current_betting_round = None


class ExploitativePlayer(GTOPlayer):
    """
    An exploitative AI player that adapts to opponent tendencies.
    
    This player starts with GTO principles but adjusts its strategy
    based on observed opponent behaviors.
    """
    
    def __init__(
        self,
        player_id: Optional[str] = None,
        name: str = "Exploitative Player",
        stack: float = 1000.0,
        aggression: float = 1.0,
        bluff_frequency: float = 0.3,
        fold_to_3bet: float = 0.5,
        call_efficiency: float = 1.0,
        positional_awareness: float = 1.0,
        randomization: float = 0.7,  # Less randomization for exploitative play
        adaptation_rate: float = 0.3  # How quickly to adapt to opponent tendencies
    ):
        """
        Initialize an exploitative AI player.
        
        Args:
            player_id: Unique identifier for the player
            name: Display name for the player
            stack: Starting chip stack
            aggression: How aggressively the player plays (1.0 = balanced)
            bluff_frequency: How often the player bluffs (0.3 = balanced)
            fold_to_3bet: How often the player folds to 3bets (0.5 = balanced)
            call_efficiency: How efficiently the player calls (1.0 = optimal)
            positional_awareness: How much position affects decisions (1.0 = optimal)
            randomization: How much randomization in decisions (0.7 = less than GTO)
            adaptation_rate: How quickly to adapt to opponent tendencies
        """
        super().__init__(
            player_id=player_id,
            name=name,
            stack=stack,
            aggression=aggression,
            bluff_frequency=bluff_frequency,
            fold_to_3bet=fold_to_3bet,
            call_efficiency=call_efficiency,
            positional_awareness=positional_awareness,
            randomization=randomization,
            gto_deviation=0.5  # Start with moderate deviation from GTO
        )
        self.adaptation_rate = adaptation_rate
        self.opponent_stats = {}
        # Store initial values for reference
        self.initial_bluff_frequency = bluff_frequency
        self.initial_aggression = aggression
        self.initial_fold_to_3bet = fold_to_3bet
        self.initial_call_efficiency = call_efficiency
    
    def _adjust_strategy_for_opponent(self, opponent_id: str) -> None:
        """
        Adjust strategy based on opponent tendencies.
        
        Args:
            opponent_id: ID of the opponent
        """
        if opponent_id not in self.opponent_models:
            return
        
        model = self.opponent_models[opponent_id]
        
        # Adjust aggression based on opponent's fold frequency
        if model.get("fold_to_3bet", 0.5) > 0.7:
            # Opponent folds to 3bets often, increase aggression
            new_aggression = min(2.0, self.aggression * (1.0 + 0.1 * self.adaptation_rate))
            self.aggression = new_aggression
        elif model.get("fold_to_3bet", 0.5) < 0.3:
            # Opponent calls 3bets often, decrease aggression
            new_aggression = max(0.5, self.aggression * (1.0 - 0.1 * self.adaptation_rate))
            self.aggression = new_aggression
        
        # Adjust bluff frequency based on opponent's calling frequency
        call_frequency = self._estimate_call_frequency(opponent_id)
        if call_frequency > 0.7:
            # Opponent calls often, bluff less
            new_bluff = max(0.1, self.bluff_frequency - 0.05 * self.adaptation_rate)
            self.bluff_frequency = new_bluff
        elif call_frequency < 0.3:
            # Opponent folds often, bluff more
            new_bluff = min(0.6, self.bluff_frequency + 0.05 * self.adaptation_rate)
            self.bluff_frequency = new_bluff
        
        # Adjust call efficiency based on opponent's aggression
        if model.get("aggression", 1.0) > 1.3:
            # Opponent is aggressive, tighten up
            self.call_efficiency = max(0.7, self.call_efficiency * (1.0 - 0.1 * self.adaptation_rate))
            self.fold_to_3bet = min(0.7, self.fold_to_3bet * (1.0 + 0.1 * self.adaptation_rate))
        elif model.get("aggression", 1.0) < 0.7:
            # Opponent is passive, loosen up
            self.call_efficiency = min(1.3, self.call_efficiency * (1.0 + 0.1 * self.adaptation_rate))
            self.fold_to_3bet = max(0.3, self.fold_to_3bet * (1.0 - 0.1 * self.adaptation_rate))

    def _estimate_call_frequency(self, opponent_id: str) -> float:
        """
        Estimate an opponent's calling frequency.
        
        Args:
            opponent_id: ID of the opponent
            
        Returns:
            Estimated calling frequency (0.0 to 1.0)
        """
        if opponent_id not in self.opponent_models:
            return 0.5  # Default to balanced
        
        actions = self.opponent_models[opponent_id].get("actions", [])
        if not actions:
            return 0.5
        
        # Count calls and total facing bets
        calls = sum(1 for a in actions if a.get("action_type") == "CALL")
        facing_bets = sum(1 for a in actions if a.get("action_type") in ["CALL", "FOLD"])
        
        if facing_bets == 0:
            return 0.5
        
        return calls / facing_bets
    
    def act(self, valid_actions: List[ActionType], min_raise: float, 
            current_bet: float, pot_size: float, 
            community_cards: Optional[List[Card]] = None,
            opponent_id: Optional[str] = None) -> Action:
        """
        Determine the exploitative player's action based on game state and opponent tendencies.
        
        Args:
            valid_actions: List of valid action types
            min_raise: Minimum raise amount
            current_bet: Current bet to call
            pot_size: Current pot size
            community_cards: Community cards on the board (if any)
            opponent_id: ID of the primary opponent (if known)
            
        Returns:
            The chosen action
        """
        # Adjust strategy for opponent if known
        if opponent_id and opponent_id in self.opponent_models:
            self._adjust_strategy_for_opponent(opponent_id)
        
        # Use the GTO player's action logic
        return super().act(valid_actions, min_raise, current_bet, pot_size, community_cards)

    def update_opponent_model(self, opponent_id: str, action: Action, 
                             betting_round: BettingRound, pot_size: float) -> None:
        """
        Update the model of an opponent based on their action.
        
        Args:
            opponent_id: ID of the opponent
            action: The action taken by the opponent
            betting_round: Current betting round
            pot_size: Current pot size
        """
        super().update_opponent_model(opponent_id, action, betting_round, pot_size)
        
        # After updating the model, adjust our strategy
        self._adjust_strategy_for_opponent(opponent_id)
        
        # Log the adaptation for debugging
        print(f"Adapted strategy against {opponent_id}: bluff_freq={self.bluff_frequency:.2f}, aggression={self.aggression:.2f}")
