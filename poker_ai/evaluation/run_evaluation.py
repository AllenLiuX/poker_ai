#!/usr/bin/env python3
"""
Script to run performance evaluation of poker AI strategies.
This script provides a command-line interface to evaluate different poker AI configurations.
"""
import argparse
import os
import sys
from typing import List, Dict, Any

# Add the project root to the path so we can import the poker_ai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from poker_ai.evaluation.performance_evaluator import PerformanceEvaluator


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate poker AI strategies")
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="results",
        help="Directory to save evaluation results"
    )
    
    parser.add_argument(
        "--num-hands", 
        type=int, 
        default=500,
        help="Number of hands to play per match"
    )
    
    parser.add_argument(
        "--num-trials", 
        type=int, 
        default=5,
        help="Number of trials per matchup"
    )
    
    parser.add_argument(
        "--preset", 
        type=str, 
        choices=["basic", "comprehensive", "exploitative"],
        default="basic",
        help="Preset configuration to use"
    )
    
    return parser.parse_args()


def get_preset_configs(preset: str) -> List[Dict[str, Any]]:
    """Get preset player configurations."""
    presets = {
        "basic": [
            {"name": "GTO Balanced", "type": "GTOPlayer", "aggression": 1.0, "bluff_frequency": 0.3},
            {"name": "TAG", "type": "GTOPlayer", "aggression": 1.3, "bluff_frequency": 0.25, "fold_to_3bet": 0.6},
            {"name": "LAG", "type": "GTOPlayer", "aggression": 1.5, "bluff_frequency": 0.4, "fold_to_3bet": 0.4},
            {"name": "Nit", "type": "GTOPlayer", "aggression": 0.7, "bluff_frequency": 0.1, "fold_to_3bet": 0.8}
        ],
        "comprehensive": [
            {"name": "GTO Balanced", "type": "GTOPlayer", "aggression": 1.0, "bluff_frequency": 0.3},
            {"name": "TAG", "type": "GTOPlayer", "aggression": 1.3, "bluff_frequency": 0.25, "fold_to_3bet": 0.6},
            {"name": "LAG", "type": "GTOPlayer", "aggression": 1.5, "bluff_frequency": 0.4, "fold_to_3bet": 0.4},
            {"name": "Nit", "type": "GTOPlayer", "aggression": 0.7, "bluff_frequency": 0.1, "fold_to_3bet": 0.8},
            {"name": "Calling Station", "type": "GTOPlayer", "aggression": 0.9, "call_efficiency": 1.5, "fold_to_3bet": 0.3},
            {"name": "Semi-Loose", "type": "GTOPlayer", "aggression": 1.1, "bluff_frequency": 0.35, "fold_to_3bet": 0.45},
            {"name": "Semi-Tight", "type": "GTOPlayer", "aggression": 0.9, "bluff_frequency": 0.2, "fold_to_3bet": 0.65}
        ],
        "exploitative": [
            {"name": "GTO Balanced", "type": "GTOPlayer", "aggression": 1.0, "bluff_frequency": 0.3},
            {"name": "TAG", "type": "GTOPlayer", "aggression": 1.3, "bluff_frequency": 0.25, "fold_to_3bet": 0.6},
            {"name": "LAG", "type": "GTOPlayer", "aggression": 1.5, "bluff_frequency": 0.4, "fold_to_3bet": 0.4},
            {"name": "Nit", "type": "GTOPlayer", "aggression": 0.7, "bluff_frequency": 0.1, "fold_to_3bet": 0.8},
            {"name": "Calling Station", "type": "GTOPlayer", "aggression": 0.9, "call_efficiency": 1.5, "fold_to_3bet": 0.3},
            {"name": "Exploitative-Fast", "type": "ExploitativePlayer", "adaptation_rate": 0.5},
            {"name": "Exploitative-Medium", "type": "ExploitativePlayer", "adaptation_rate": 0.3},
            {"name": "Exploitative-Slow", "type": "ExploitativePlayer", "adaptation_rate": 0.1}
        ]
    }
    
    return presets.get(preset, presets["basic"])


def main():
    """Main function to run the evaluation."""
    args = parse_args()
    
    # Get player configurations
    player_configs = get_preset_configs(args.preset)
    
    # Create evaluator
    evaluator = PerformanceEvaluator(args.output_dir)
    
    # Run evaluation
    print(f"Starting poker strategy evaluation with {args.preset} preset...")
    print(f"Running {args.num_hands} hands per match, {args.num_trials} trials per matchup")
    print(f"Evaluating {len(player_configs)} different player configurations")
    
    results, matchups = evaluator.evaluate_player_configs(
        player_configs, 
        num_hands=args.num_hands,
        num_trials=args.num_trials
    )
    
    # Print summary
    print("\nEvaluation Results:")
    for name, stats in results.items():
        print(f"{name}:")
        print(f"  Win Rate: {stats['win_rate']:.2f}")
        print(f"  Avg Profit: {stats['avg_profit_per_match']:.2f}")
        print(f"  VPIP%: {stats['vpip']:.1f}%")
        print(f"  PFR%: {stats['pfr']:.1f}%")
        print(f"  AF: {stats['af']:.2f}")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    evaluator.visualize_results(results, matchups)
    print(f"Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
