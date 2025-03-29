"""
Performance evaluator for poker AI players.
This module provides tools to evaluate and compare different poker AI strategies.
"""
import random
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple, Optional
import os
import json
import logging
from datetime import datetime
import glob
import numpy as np
import seaborn as sns

from poker_ai.engine.card import Card, Deck
from poker_ai.engine.action import Action, ActionType, BettingRound
from poker_ai.game.player import Player
from poker_ai.game.state import GameState
from poker_ai.player.gto_player import GTOPlayer, ExploitativePlayer


class PerformanceEvaluator:
    """Evaluates performance of poker AI strategies."""
    
    def __init__(self, output_dir: str = "results", log_dir: str = "logs"):
        """
        Initialize the performance evaluator.
        
        Args:
            output_dir: Directory to save evaluation results
            log_dir: Directory to save log files
        """
        self.output_dir = output_dir
        self.log_dir = log_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        Set up a logger with file handler.
        
        Returns:
            Configured logger
        """
        # Create logger
        logger = logging.getLogger("poker_evaluator")
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        if logger.handlers:
            for handler in logger.handlers:
                logger.removeHandler(handler)
        
        # Create a new log file with incremental index
        log_files = glob.glob(os.path.join(self.log_dir, "evaluation_*.log"))
        if log_files:
            indices = [int(f.split("_")[-1].split(".")[0]) for f in log_files if f.split("_")[-1].split(".")[0].isdigit()]
            next_index = max(indices) + 1 if indices else 1
        else:
            next_index = 1
        
        log_file = os.path.join(self.log_dir, f"evaluation_{next_index}.log")
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.info(f"Logging to file: {log_file}")
        return logger
    
    def simulate_heads_up_match(self, player1: Player, player2: Player, 
                               num_hands: int = 100, 
                               small_blind: float = 1.0, 
                               big_blind: float = 2.0) -> Tuple[float, float, Dict[str, Any]]:
        """
        Simulate a heads-up match between two players.
        
        Args:
            player1: First player
            player2: Second player
            num_hands: Number of hands to play
            small_blind: Small blind amount
            big_blind: Big blind amount
            
        Returns:
            Tuple of (player1_profit, player2_profit, match_stats)
        """
        # Reset player stacks
        initial_stack = 1000.0
        player1.stack = initial_stack
        player2.stack = initial_stack
        
        # Initialize statistics
        stats = {
            "hands_played": 0,
            "player1_wins": 0,
            "player2_wins": 0,
            "player1_vpip": 0,
            "player2_vpip": 0,
            "player1_pfr": 0,
            "player2_pfr": 0,
            "player1_af": [],
            "player2_af": [],
            "player1_stack_history": [initial_stack],
            "player2_stack_history": [initial_stack],
        }
        
        self.logger.info(f"\nStarting heads-up match: {player1.name} vs {player2.name} ({num_hands} hands)")
        
        # Play hands
        for hand_num in range(num_hands):
            if hand_num % 10 == 0:
                self.logger.info(f"  Playing hand {hand_num}/{num_hands}...")
                self.logger.info(f"  Current stacks: {player1.name}: {player1.stack:.2f}, {player2.name}: {player2.stack:.2f}")
            
            # Check if either player is out of chips
            if player1.stack <= 0 or player2.stack <= 0:
                self.logger.info(f"  Match ended early: One player has no chips left")
                break
                
            # Alternate button position
            if hand_num % 2 == 0:
                button_player = player1
                bb_player = player2
            else:
                button_player = player2
                bb_player = player1
            
            # Track initial stacks for this hand
            hand_initial_stack1 = player1.stack
            hand_initial_stack2 = player2.stack
            
            # Create game state
            players = [player1, player2]
            game = GameState(players, small_blind, big_blind)
            
            # Stats tracking
            hand_stats = {
                "player1_actions": {
                    "FOLD": 0, "CHECK": 0, "CALL": 0, "BET": 0, "RAISE": 0
                },
                "player2_actions": {
                    "FOLD": 0, "CHECK": 0, "CALL": 0, "BET": 0, "RAISE": 0
                },
            }
            
            # Track preflop actions
            p1_vpip_this_hand = False
            p2_vpip_this_hand = False
            p1_pfr_this_hand = False
            p2_pfr_this_hand = False
            
            # Track aggression
            p1_aggressive_actions = 0  # bet, raise
            p1_passive_actions = 0     # call, check
            p2_aggressive_actions = 0
            p2_passive_actions = 0
            
            # Start the hand
            game.start_new_hand()
            stats["hands_played"] += 1
            
            # Note: The hole_cards are already set by the GameState.start_new_hand method
            # No need to copy them manually
            
            # Main game loop
            while not game.is_hand_over():
                current_player = game.get_current_player()
                if not current_player:
                    break
                    
                # Get valid actions
                valid_actions = game.get_valid_actions(current_player)
                
                # Get player action
                if hasattr(current_player, 'act') and callable(current_player.act):
                    if isinstance(current_player, GTOPlayer):
                        # Make sure hole cards exist before acting
                        if not current_player.hole_cards or len(current_player.hole_cards) < 2:
                            # Default to checking if possible, otherwise fold
                            if ActionType.CHECK in valid_actions:
                                action = Action(ActionType.CHECK, 0, current_player.player_id)
                            else:
                                action = Action(ActionType.FOLD, 0, current_player.player_id)
                        else:
                            # Pass community cards to GTO player
                            action = current_player.act(
                                valid_actions,
                                game.min_raise,
                                game.current_bet,
                                game.pot,
                                game.community_cards
                            )
                    else:
                        action = current_player.act(
                            valid_actions,
                            game.min_raise,
                            game.current_bet,
                            game.pot
                        )
                else:
                    # Default to folding if player doesn't have act method
                    if ActionType.FOLD in valid_actions:
                        action = Action(ActionType.FOLD, 0, current_player.player_id)
                    else:
                        action = Action(ActionType.CHECK, 0, current_player.player_id)
                
                # Record action stats
                action_type_str = action.action_type.name
                if current_player.player_id == player1.player_id:
                    hand_stats["player1_actions"][action_type_str] += 1
                    
                    # Track VPIP and PFR
                    if game.betting_round == BettingRound.PREFLOP:
                        if action.action_type in [ActionType.CALL, ActionType.BET, ActionType.RAISE]:
                            p1_vpip_this_hand = True
                        if action.action_type in [ActionType.BET, ActionType.RAISE]:
                            p1_pfr_this_hand = True
                    
                    # Track aggression
                    if action.action_type in [ActionType.BET, ActionType.RAISE]:
                        p1_aggressive_actions += 1
                    elif action.action_type in [ActionType.CALL, ActionType.CHECK]:
                        p1_passive_actions += 1
                        
                else:
                    hand_stats["player2_actions"][action_type_str] += 1
                    
                    # Track VPIP and PFR
                    if game.betting_round == BettingRound.PREFLOP:
                        if action.action_type in [ActionType.CALL, ActionType.BET, ActionType.RAISE]:
                            p2_vpip_this_hand = True
                        if action.action_type in [ActionType.BET, ActionType.RAISE]:
                            p2_pfr_this_hand = True
                    
                    # Track aggression
                    if action.action_type in [ActionType.BET, ActionType.RAISE]:
                        p2_aggressive_actions += 1
                    elif action.action_type in [ActionType.CALL, ActionType.CHECK]:
                        p2_passive_actions += 1
                
                # Apply the action
                game.apply_action(action)
            
            # Determine hand winner based on stack changes
            hand_profit1 = player1.stack - hand_initial_stack1
            hand_profit2 = player2.stack - hand_initial_stack2
            
            if hand_profit1 > 0:
                stats["player1_wins"] += 1
            elif hand_profit2 > 0:
                stats["player2_wins"] += 1
            
            # Update VPIP and PFR stats
            if p1_vpip_this_hand:
                stats["player1_vpip"] += 1
            if p2_vpip_this_hand:
                stats["player2_vpip"] += 1
            if p1_pfr_this_hand:
                stats["player1_pfr"] += 1
            if p2_pfr_this_hand:
                stats["player2_pfr"] += 1
            
            # Calculate aggression factor for this hand
            p1_af = p1_aggressive_actions / p1_passive_actions if p1_passive_actions > 0 else 1.0
            p2_af = p2_aggressive_actions / p2_passive_actions if p2_passive_actions > 0 else 1.0
            stats["player1_af"].append(p1_af)
            stats["player2_af"].append(p2_af)
            
            # Update stack history
            stats["player1_stack_history"].append(player1.stack)
            stats["player2_stack_history"].append(player2.stack)
        
        # Calculate profits
        player1_profit = player1.stack - initial_stack
        player2_profit = player2.stack - initial_stack
        
        # Calculate final stats
        if stats["hands_played"] > 0:
            stats["player1_vpip_pct"] = stats["player1_vpip"] / stats["hands_played"] * 100
            stats["player2_vpip_pct"] = stats["player2_vpip"] / stats["hands_played"] * 100
            stats["player1_pfr_pct"] = stats["player1_pfr"] / stats["hands_played"] * 100
            stats["player2_pfr_pct"] = stats["player2_pfr"] / stats["hands_played"] * 100
        
        self.logger.info(f"  Match completed: {player1.name} profit: {player1_profit:.2f}, {player2.name} profit: {player2_profit:.2f}")
        
        return player1_profit, player2_profit, stats
    
    def evaluate_player_configs(self, player_configs: List[Dict[str, Any]], 
                              num_hands: int = 1000, 
                              num_trials: int = 5) -> Dict[str, Dict[str, float]]:
        """
        Evaluate performance of different player configurations against each other.
        
        Args:
            player_configs: List of player configuration dictionaries
            num_hands: Number of hands per match
            num_trials: Number of trials per matchup
            
        Returns:
            Dictionary of performance metrics for each player
        """
        # Create players from configurations
        players = []
        for config in player_configs:
            player_type = config.pop("type", "GTOPlayer")
            if player_type == "ExploitativePlayer":
                players.append(ExploitativePlayer(**config))
            else:
                players.append(GTOPlayer(**config))
        
        # Track results
        results = {player.name: {
            "total_profit": 0, 
            "wins": 0, 
            "matches": 0,
            "vpip": 0,
            "pfr": 0,
            "af": 0
        } for player in players}
        
        # Track matchup results
        matchups = {}
        
        # Run round-robin tournament
        total_matchups = len(players) * (len(players) - 1) // 2
        matchup_count = 0
        
        self.logger.info(f"\nRunning {total_matchups} matchups with {num_trials} trials each...")
        
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                player1 = players[i]
                player2 = players[j]
                
                matchup_count += 1
                self.logger.info(f"\nMatchup {matchup_count}/{total_matchups}: {player1.name} vs {player2.name}")
                
                player1_total_profit = 0
                player2_total_profit = 0
                
                matchup_stats = {
                    "player1_vpip": 0,
                    "player2_vpip": 0,
                    "player1_pfr": 0,
                    "player2_pfr": 0,
                    "player1_af": 0,
                    "player2_af": 0
                }
                
                for trial in range(num_trials):
                    self.logger.info(f"  Trial {trial + 1}/{num_trials}")
                    
                    player1_profit, player2_profit, stats = self.simulate_heads_up_match(
                        player1, player2, num_hands
                    )
                    
                    player1_total_profit += player1_profit
                    player2_total_profit += player2_profit
                    
                    # Accumulate stats
                    matchup_stats["player1_vpip"] += stats.get("player1_vpip_pct", 0)
                    matchup_stats["player2_vpip"] += stats.get("player2_vpip_pct", 0)
                    matchup_stats["player1_pfr"] += stats.get("player1_pfr_pct", 0)
                    matchup_stats["player2_pfr"] += stats.get("player2_pfr_pct", 0)
                    matchup_stats["player1_af"] += statistics.mean(stats.get("player1_af", [0]))
                    matchup_stats["player2_af"] += statistics.mean(stats.get("player2_af", [0]))
                
                # Record average results
                player1_avg_profit = player1_total_profit / num_trials
                player2_avg_profit = player2_total_profit / num_trials
                
                # Average stats
                for stat in matchup_stats:
                    matchup_stats[stat] /= num_trials
                
                # Record matchup results
                matchup_key = f"{player1.name} vs {player2.name}"
                matchups[matchup_key] = {
                    "player1_profit": player1_avg_profit,
                    "player2_profit": player2_avg_profit,
                    **matchup_stats
                }
                
                self.logger.info(f"  Matchup results: {player1.name} avg profit: {player1_avg_profit:.2f}, " 
                      f"{player2.name} avg profit: {player2_avg_profit:.2f}")
                
                # Update overall results
                results[player1.name]["total_profit"] += player1_avg_profit
                results[player2.name]["total_profit"] += player2_avg_profit
                
                results[player1.name]["matches"] += 1
                results[player2.name]["matches"] += 1
                
                # Update stats
                results[player1.name]["vpip"] += matchup_stats["player1_vpip"]
                results[player2.name]["vpip"] += matchup_stats["player2_vpip"]
                results[player1.name]["pfr"] += matchup_stats["player1_pfr"]
                results[player2.name]["pfr"] += matchup_stats["player2_pfr"]
                results[player1.name]["af"] += matchup_stats["player1_af"]
                results[player2.name]["af"] += matchup_stats["player2_af"]
                
                if player1_avg_profit > player2_avg_profit:
                    results[player1.name]["wins"] += 1
                elif player2_avg_profit > player1_avg_profit:
                    results[player2.name]["wins"] += 1
                else:
                    # Tie - give half win to each
                    results[player1.name]["wins"] += 0.5
                    results[player2.name]["wins"] += 0.5
        
        # Calculate additional metrics
        for name, stats in results.items():
            if stats["matches"] > 0:
                stats["avg_profit_per_match"] = stats["total_profit"] / stats["matches"]
                stats["win_rate"] = stats["wins"] / stats["matches"]
                stats["vpip"] /= stats["matches"]
                stats["pfr"] /= stats["matches"]
                stats["af"] /= stats["matches"]
            else:
                stats["avg_profit_per_match"] = 0
                stats["win_rate"] = 0
        
        # Save results
        self._save_results(results, matchups, player_configs, num_hands, num_trials)
        
        return results, matchups
    
    def _save_results(self, results: Dict[str, Dict[str, float]], 
                     matchups: Dict[str, Dict[str, float]],
                     player_configs: List[Dict[str, Any]],
                     num_hands: int,
                     num_trials: int) -> None:
        """Save evaluation results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a new results directory with incremental index
        results_dirs = glob.glob(os.path.join(self.output_dir, "sim_*"))
        if results_dirs:
            indices = [int(os.path.basename(d).split("_")[1]) for d in results_dirs if os.path.basename(d).split("_")[1].isdigit()]
            next_index = max(indices) + 1 if indices else 1
        else:
            next_index = 1
        
        sim_dir = os.path.join(self.output_dir, f"sim_{next_index}")
        os.makedirs(sim_dir, exist_ok=True)
        
        self.logger.info(f"Saving simulation results to {sim_dir}")
        
        # Save results as JSON
        result_data = {
            "timestamp": timestamp,
            "num_hands": num_hands,
            "num_trials": num_trials,
            "player_configs": player_configs,
            "results": results,
            "matchups": matchups
        }
        
        with open(os.path.join(sim_dir, "results.json"), "w") as f:
            json.dump(result_data, f, indent=2)
        
        # Create summary CSV
        summary_data = []
        for name, stats in results.items():
            summary_data.append({
                "Player": name,
                "Win Rate": stats["win_rate"],
                "Avg Profit": stats["avg_profit_per_match"],
                "VPIP%": stats["vpip"],
                "PFR%": stats["pfr"],
                "AF": stats["af"]
            })
        
        df = pd.DataFrame(summary_data)
        df.to_csv(os.path.join(sim_dir, "summary.csv"), index=False)
        
        # Create matchup CSV
        matchup_data = []
        for matchup, stats in matchups.items():
            players = matchup.split(" vs ")
            matchup_data.append({
                "Player1": players[0],
                "Player2": players[1],
                "Player1 Profit": stats["player1_profit"],
                "Player2 Profit": stats["player2_profit"],
                "Player1 VPIP%": stats["player1_vpip"],
                "Player2 VPIP%": stats["player2_vpip"],
                "Player1 PFR%": stats["player1_pfr"],
                "Player2 PFR%": stats["player2_pfr"],
                "Player1 AF": stats["player1_af"],
                "Player2 AF": stats["player2_af"]
            })
        
        df = pd.DataFrame(matchup_data)
        df.to_csv(os.path.join(sim_dir, "matchups.csv"), index=False)
    
    def visualize_results(self, results: Dict[str, Dict[str, float]], 
                         matchups: Dict[str, Dict[str, float]]) -> None:
        """
        Create visualizations of evaluation results.
        
        Args:
            results: Player results dictionary
            matchups: Matchup results dictionary
        """
        # Find the latest simulation directory
        results_dirs = glob.glob(os.path.join(self.output_dir, "sim_*"))
        if results_dirs:
            indices = [int(os.path.basename(d).split("_")[1]) for d in results_dirs if os.path.basename(d).split("_")[1].isdigit()]
            latest_index = max(indices) if indices else 1
            sim_dir = os.path.join(self.output_dir, f"sim_{latest_index}")
        else:
            # Fallback to creating a new directory
            sim_dir = os.path.join(self.output_dir, "sim_1")
            os.makedirs(sim_dir, exist_ok=True)
        
        # Create plots directory within the simulation directory
        plots_dir = os.path.join(sim_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        
        self.logger.info(f"Saving visualization plots to {plots_dir}")
        
        # Plot win rates
        plt.figure(figsize=(10, 6))
        players = list(results.keys())
        win_rates = [results[p]["win_rate"] for p in players]
        
        plt.bar(players, win_rates)
        plt.title("Win Rates by Player Strategy")
        plt.ylabel("Win Rate")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "win_rates.png"))
        
        # Plot average profits
        plt.figure(figsize=(10, 6))
        avg_profits = [results[p]["avg_profit_per_match"] for p in players]
        
        plt.bar(players, avg_profits)
        plt.title("Average Profit per Match by Player Strategy")
        plt.ylabel("Average Profit")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "avg_profits.png"))
        
        # Plot VPIP vs PFR
        plt.figure(figsize=(10, 6))
        vpip = [results[p]["vpip"] for p in players]
        pfr = [results[p]["pfr"] for p in players]
        
        plt.scatter(vpip, pfr)
        for i, player in enumerate(players):
            plt.annotate(player, (vpip[i], pfr[i]))
        
        plt.title("VPIP% vs PFR% by Player Strategy")
        plt.xlabel("VPIP%")
        plt.ylabel("PFR%")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "vpip_pfr.png"))
        
        # Plot matchup results as heatmap
        if matchups:
            # Extract unique players
            all_players = set()
            for matchup in matchups:
                players = matchup.split(" vs ")
                all_players.update(players)
            
            all_players = sorted(list(all_players))
            n_players = len(all_players)
            
            # Create profit matrix
            profit_matrix = np.zeros((n_players, n_players))
            
            for matchup, stats in matchups.items():
                players = matchup.split(" vs ")
                i = all_players.index(players[0])
                j = all_players.index(players[1])
                
                profit_matrix[i, j] = stats["player1_profit"]
                profit_matrix[j, i] = stats["player2_profit"]
            
            # Plot heatmap
            plt.figure(figsize=(12, 10))
            sns.heatmap(profit_matrix, annot=True, fmt=".1f", cmap="RdBu_r",
                       xticklabels=all_players, yticklabels=all_players)
            plt.title("Profit Matrix by Player Strategy")
            plt.xlabel("Opponent")
            plt.ylabel("Player")
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, "profit_matrix.png"))


def run_evaluation(output_dir: str = "results", log_dir: str = "logs"):
    """Run a comprehensive evaluation of poker strategies."""
    # Define player configurations to test
    player_configs = [
        {"name": "GTO Balanced", "type": "GTOPlayer", "aggression": 1.0, "bluff_frequency": 0.3},
        {"name": "TAG", "type": "GTOPlayer", "aggression": 1.3, "bluff_frequency": 0.25, "fold_to_3bet": 0.6},
        {"name": "LAG", "type": "GTOPlayer", "aggression": 1.5, "bluff_frequency": 0.4, "fold_to_3bet": 0.4},
        {"name": "Nit", "type": "GTOPlayer", "aggression": 0.7, "bluff_frequency": 0.1, "fold_to_3bet": 0.8},
        {"name": "Calling Station", "type": "GTOPlayer", "aggression": 0.9, "call_efficiency": 1.5, "fold_to_3bet": 0.3},
        {"name": "Exploitative", "type": "ExploitativePlayer", "adaptation_rate": 0.3}
    ]
    
    # Create evaluator
    evaluator = PerformanceEvaluator(output_dir, log_dir)
    
    # Run evaluation
    evaluator.logger.info(f"Starting poker strategy evaluation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    evaluator.logger.info(f"Testing {len(player_configs)} player configurations:")
    for config in player_configs:
        evaluator.logger.info(f"  - {config['name']}")
    
    results, matchups = evaluator.evaluate_player_configs(
        player_configs, 
        num_hands=200,  # Reduced for testing, use 1000+ for real evaluation
        num_trials=3    # Reduced for testing, use 10+ for real evaluation
    )
    
    # Print summary
    evaluator.logger.info("\nEvaluation Results:")
    for name, stats in results.items():
        evaluator.logger.info(f"{name}:")
        evaluator.logger.info(f"  Win Rate: {stats['win_rate']:.2f}")
        evaluator.logger.info(f"  Avg Profit: {stats['avg_profit_per_match']:.2f}")
        evaluator.logger.info(f"  VPIP%: {stats['vpip']:.1f}%")
        evaluator.logger.info(f"  PFR%: {stats['pfr']:.1f}%")
        evaluator.logger.info(f"  AF: {stats['af']:.2f}")
    
    # Create visualizations
    evaluator.logger.info("\nGenerating visualizations...")
    evaluator.visualize_results(results, matchups)
    evaluator.logger.info(f"Results saved to {output_dir}")
    evaluator.logger.info(f"Evaluation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_evaluation()
