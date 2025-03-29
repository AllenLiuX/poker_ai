"""Poker hand evaluation module."""
from enum import Enum, auto
from typing import List, Tuple, Set, Dict, Optional
import random

from treys import Card as TreysCard
from treys import Evaluator as TreysEvaluator
from treys import Deck as TreysDeck

from poker_ai.engine.card import Card, Rank, Suit


class HandRank(Enum):
    """Poker hand rankings from highest to lowest."""
    ROYAL_FLUSH = 1
    STRAIGHT_FLUSH = 2
    FOUR_OF_A_KIND = 3
    FULL_HOUSE = 4
    FLUSH = 5
    STRAIGHT = 6
    THREE_OF_A_KIND = 7
    TWO_PAIR = 8
    ONE_PAIR = 9
    HIGH_CARD = 10


class HandEvaluator:
    """Evaluates poker hands using the Treys library."""
    
    def __init__(self):
        self.evaluator = TreysEvaluator()
    
    def _convert_to_treys_card(self, card: Card) -> int:
        """Convert our Card to Treys card integer representation."""
        # Map our ranks to Treys ranks
        rank_map = {
            Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4',
            Rank.FIVE: '5', Rank.SIX: '6', Rank.SEVEN: '7',
            Rank.EIGHT: '8', Rank.NINE: '9', Rank.TEN: 'T',
            Rank.JACK: 'J', Rank.QUEEN: 'Q', Rank.KING: 'K',
            Rank.ACE: 'A'
        }
        
        # Map our suits to Treys suits
        suit_map = {
            Suit.CLUBS: 'c', Suit.DIAMONDS: 'd',
            Suit.HEARTS: 'h', Suit.SPADES: 's'
        }
        
        card_str = f"{rank_map[card.rank]}{suit_map[card.suit]}"
        return TreysCard.new(card_str)
    
    def evaluate_hand(self, hole_cards: List[Card], community_cards: List[Card]) -> Tuple[int, HandRank, str]:
        """
        Evaluate a poker hand and return its strength.
        
        Args:
            hole_cards: The player's hole cards
            community_cards: The community cards on the board
            
        Returns:
            Tuple of (hand_strength, hand_rank, hand_description)
            Lower hand_strength values represent stronger hands
        """
        treys_hole = [self._convert_to_treys_card(card) for card in hole_cards]
        treys_community = [self._convert_to_treys_card(card) for card in community_cards]
        
        # Evaluate the hand (lower is better in Treys)
        hand_strength = self.evaluator.evaluate(treys_community, treys_hole)
        
        # Get the hand rank class
        hand_class = self.evaluator.get_rank_class(hand_strength)
        
        # Map Treys rank class to our HandRank enum
        rank_class_map = {
            0: HandRank.ROYAL_FLUSH,  # Special case for royal flush in Treys
            1: HandRank.STRAIGHT_FLUSH,
            2: HandRank.FOUR_OF_A_KIND,
            3: HandRank.FULL_HOUSE,
            4: HandRank.FLUSH,
            5: HandRank.STRAIGHT,
            6: HandRank.THREE_OF_A_KIND,
            7: HandRank.TWO_PAIR,
            8: HandRank.ONE_PAIR,
            9: HandRank.HIGH_CARD
        }
        
        # Check for royal flush specifically
        hand_rank = rank_class_map[hand_class]
        if hand_rank == HandRank.STRAIGHT_FLUSH:
            # Check if it's a royal flush (A-K-Q-J-10 of same suit)
            ranks = {card.rank for card in hole_cards + community_cards}
            royal_ranks = {Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN}
            if royal_ranks.issubset(ranks):
                # Check if they're all the same suit
                for suit in Suit:
                    royal_cards = [card for card in hole_cards + community_cards 
                                  if card.rank in royal_ranks and card.suit == suit]
                    if len(royal_cards) >= 5:
                        hand_rank = HandRank.ROYAL_FLUSH
                        break
        
        # Get a human-readable description
        hand_description = self.evaluator.class_to_string(hand_class)
        
        return hand_strength, hand_rank, hand_description
    
    def get_hand_equity(self, hole_cards: List[Card], community_cards: List[Card], 
                        num_opponents: int = 1, num_simulations: int = 1000) -> float:
        """
        Calculate the equity (probability of winning) for a hand through Monte Carlo simulation.
        
        Args:
            hole_cards: The player's hole cards
            community_cards: The community cards on the board
            num_opponents: Number of opponents to simulate against
            num_simulations: Number of Monte Carlo simulations to run
            
        Returns:
            Equity as a float between 0 and 1
        """
        # Convert our cards to Treys format
        treys_hole = [self._convert_to_treys_card(card) for card in hole_cards]
        treys_community = [self._convert_to_treys_card(card) for card in community_cards]
        
        # Create a Treys deck and remove the known cards
        treys_deck = TreysDeck()
        for card in treys_hole + treys_community:
            treys_deck.cards.remove(card)
        
        # If we have a complete board, just evaluate the hand
        if len(community_cards) == 5:
            hand_strength, _, _ = self.evaluate_hand(hole_cards, community_cards)
            normalized_strength = 1 - (hand_strength / 7462)
            return normalized_strength
        
        # Run Monte Carlo simulations
        wins = 0
        for _ in range(num_simulations):
            # Shuffle the deck
            random.shuffle(treys_deck.cards)
            
            # Create a copy of the deck for this simulation
            sim_deck = treys_deck.cards.copy()
            
            # Deal cards to opponents
            opponent_holes = []
            for _ in range(num_opponents):
                if len(sim_deck) >= 2:
                    opp_hole = sim_deck[:2]
                    opponent_holes.append(opp_hole)
                    sim_deck = sim_deck[2:]
                else:
                    # Not enough cards left
                    break
            
            # Complete the board
            remaining_community = 5 - len(treys_community)
            if remaining_community > 0 and len(sim_deck) >= remaining_community:
                simulated_board = treys_community + sim_deck[:remaining_community]
            else:
                # Not enough cards left
                continue
            
            # Evaluate our hand
            our_score = self.evaluator.evaluate(treys_hole, simulated_board)
            
            # Check if we win
            win_count = 0
            tie_count = 0
            
            for opp_hole in opponent_holes:
                opp_score = self.evaluator.evaluate(opp_hole, simulated_board)
                if our_score < opp_score:  # Lower score is better in Treys
                    win_count += 1
                elif our_score == opp_score:
                    tie_count += 1
            
            # We win if we beat all opponents
            if win_count == len(opponent_holes):
                wins += 1
            # Add partial credit for ties
            elif win_count + tie_count == len(opponent_holes) and tie_count > 0:
                wins += 0.5
        
        # Calculate equity
        if num_simulations > 0:
            return wins / num_simulations
        else:
            # Fallback to a simple approximation
            hand_strength, _, _ = self.evaluate_hand(hole_cards, community_cards)
            normalized_strength = 1 - (hand_strength / 7462)
            adjusted_equity = normalized_strength ** num_opponents
            return adjusted_equity
