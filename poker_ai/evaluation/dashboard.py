#!/usr/bin/env python3
"""
Interactive dashboard for visualizing poker AI performance evaluation results.
This dashboard allows for easy analysis of different poker AI strategies.
"""
import os
import json
import glob
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import sys
from datetime import datetime

# Add the project root to the path so we can import the poker_ai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class PerformanceDashboard:
    """Interactive dashboard for poker AI performance analysis."""
    
    def __init__(self, results_dir: str = "results"):
        """
        Initialize the dashboard.
        
        Args:
            results_dir: Directory containing evaluation results
        """
        self.results_dir = results_dir
        self.results_files = self._get_results_files()
        self.current_results = None
        self.current_matchups = None
        self.player_configs = None
    
    def _get_results_files(self) -> List[str]:
        """Get list of result files in the results directory."""
        json_files = glob.glob(os.path.join(self.results_dir, "results_*.json"))
        return sorted(json_files, key=os.path.getmtime, reverse=True)
    
    def load_results(self, file_path: Optional[str] = None) -> None:
        """
        Load results from a file.
        
        Args:
            file_path: Path to results file, or None to load most recent
        """
        if file_path is None:
            if not self.results_files:
                print("No results files found")
                return
            file_path = self.results_files[0]
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            self.current_results = data.get("results", {})
            self.current_matchups = data.get("matchups", {})
            self.player_configs = data.get("player_configs", [])
            
            print(f"Loaded results from {file_path}")
            print(f"Evaluation ran with {data.get('num_hands', 'unknown')} hands per match")
            print(f"and {data.get('num_trials', 'unknown')} trials per matchup")
            
        except Exception as e:
            print(f"Error loading results: {e}")
    
    def list_available_results(self) -> None:
        """List available result files."""
        if not self.results_files:
            print("No results files found")
            return
        
        print("Available result files:")
        for i, file_path in enumerate(self.results_files):
            filename = os.path.basename(file_path)
            timestamp = os.path.getmtime(file_path)
            dt = datetime.fromtimestamp(timestamp)
            print(f"{i+1}. {filename} - {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def plot_win_rates(self) -> None:
        """Plot win rates for each player."""
        if not self.current_results:
            print("No results loaded")
            return
        
        plt.figure(figsize=(12, 6))
        players = list(self.current_results.keys())
        win_rates = [self.current_results[p]["win_rate"] for p in players]
        
        # Sort by win rate
        sorted_indices = np.argsort(win_rates)[::-1]
        sorted_players = [players[i] for i in sorted_indices]
        sorted_win_rates = [win_rates[i] for i in sorted_indices]
        
        # Create bar chart
        bars = plt.bar(sorted_players, sorted_win_rates, color=sns.color_palette("viridis", len(players)))
        
        plt.title("Win Rates by Player Strategy", fontsize=16)
        plt.ylabel("Win Rate", fontsize=14)
        plt.xticks(rotation=45, ha="right", fontsize=12)
        plt.ylim(0, 1)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    
    def plot_average_profits(self) -> None:
        """Plot average profits for each player."""
        if not self.current_results:
            print("No results loaded")
            return
        
        plt.figure(figsize=(12, 6))
        players = list(self.current_results.keys())
        avg_profits = [self.current_results[p]["avg_profit_per_match"] for p in players]
        
        # Sort by profit
        sorted_indices = np.argsort(avg_profits)[::-1]
        sorted_players = [players[i] for i in sorted_indices]
        sorted_profits = [avg_profits[i] for i in sorted_indices]
        
        # Create bar chart with color gradient based on profit
        colors = sns.color_palette("RdYlGn", len(players))
        bars = plt.bar(sorted_players, sorted_profits, color=[colors[i] for i in range(len(players))])
        
        plt.title("Average Profit per Match by Player Strategy", fontsize=16)
        plt.ylabel("Average Profit (chips)", fontsize=14)
        plt.xticks(rotation=45, ha="right", fontsize=12)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., 
                    height + 5 if height >= 0 else height - 15,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_vpip_pfr(self) -> None:
        """Plot VPIP vs PFR for each player."""
        if not self.current_results:
            print("No results loaded")
            return
        
        plt.figure(figsize=(10, 8))
        players = list(self.current_results.keys())
        vpip = [self.current_results[p]["vpip"] for p in players]
        pfr = [self.current_results[p]["pfr"] for p in players]
        
        # Create scatter plot
        plt.scatter(vpip, pfr, s=100, alpha=0.7)
        
        # Add player labels
        for i, player in enumerate(players):
            plt.annotate(player, (vpip[i], pfr[i]), fontsize=12,
                        xytext=(5, 5), textcoords='offset points')
        
        # Add reference lines for common player types
        plt.plot([0, 100], [0, 100], 'k--', alpha=0.3)  # VPIP = PFR line
        
        # Add player type regions
        plt.fill_between([0, 15], [0, 15], color='blue', alpha=0.1, label='Nit')
        plt.fill_between([15, 30], [10, 25], color='green', alpha=0.1, label='TAG')
        plt.fill_between([30, 50], [20, 40], color='orange', alpha=0.1, label='LAG')
        plt.fill_between([30, 70], [5, 15], color='red', alpha=0.1, label='Calling Station')
        
        plt.title("VPIP% vs PFR% by Player Strategy", fontsize=16)
        plt.xlabel("VPIP% (Voluntarily Put Money In Pot)", fontsize=14)
        plt.ylabel("PFR% (Preflop Raise)", fontsize=14)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(loc='upper left')
        
        # Set axis limits
        max_val = max(max(vpip), max(pfr)) * 1.1
        plt.xlim(0, max_val)
        plt.ylim(0, max_val)
        
        plt.tight_layout()
        plt.show()
    
    def plot_aggression_factor(self) -> None:
        """Plot aggression factor for each player."""
        if not self.current_results:
            print("No results loaded")
            return
        
        plt.figure(figsize=(12, 6))
        players = list(self.current_results.keys())
        af = [self.current_results[p]["af"] for p in players]
        
        # Sort by aggression factor
        sorted_indices = np.argsort(af)[::-1]
        sorted_players = [players[i] for i in sorted_indices]
        sorted_af = [af[i] for i in sorted_indices]
        
        # Create bar chart
        bars = plt.bar(sorted_players, sorted_af, color=sns.color_palette("rocket", len(players)))
        
        plt.title("Aggression Factor by Player Strategy", fontsize=16)
        plt.ylabel("Aggression Factor (bets+raises)/(calls+checks)", fontsize=14)
        plt.xticks(rotation=45, ha="right", fontsize=12)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        # Add reference lines for common aggression factors
        plt.axhline(y=1.0, color='green', linestyle='--', alpha=0.7, label='Balanced (AF=1)')
        plt.axhline(y=2.0, color='orange', linestyle='--', alpha=0.7, label='Aggressive (AF=2)')
        plt.axhline(y=0.5, color='blue', linestyle='--', alpha=0.7, label='Passive (AF=0.5)')
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    def plot_profit_matrix(self) -> None:
        """Plot profit matrix as heatmap."""
        if not self.current_results or not self.current_matchups:
            print("No results loaded")
            return
        
        # Extract unique players
        all_players = set()
        for matchup in self.current_matchups:
            players = matchup.split(" vs ")
            all_players.update(players)
        
        all_players = sorted(list(all_players))
        n_players = len(all_players)
        
        # Create profit matrix
        profit_matrix = pd.DataFrame(0, index=all_players, columns=all_players)
        
        for matchup, stats in self.current_matchups.items():
            players = matchup.split(" vs ")
            p1, p2 = players
            profit_matrix.loc[p1, p2] = stats["player1_profit"]
            profit_matrix.loc[p2, p1] = stats["player2_profit"]
        
        # Plot heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(profit_matrix, cmap="RdYlGn", annot=True, fmt=".1f", 
                   center=0, cbar_kws={'label': 'Profit'})
        
        plt.title("Profit Matrix: Row Player vs Column Player", fontsize=16)
        plt.tight_layout()
        plt.show()
    
    def plot_player_config_comparison(self) -> None:
        """Plot comparison of player configurations with performance."""
        if not self.current_results or not self.player_configs:
            print("No results loaded or no player configurations available")
            return
        
        # Extract configuration parameters and performance metrics
        data = []
        for config in self.player_configs:
            name = config.get("name", "Unknown")
            if name in self.current_results:
                player_type = config.get("type", "GTOPlayer")
                aggression = config.get("aggression", 1.0)
                bluff_frequency = config.get("bluff_frequency", 0.3)
                fold_to_3bet = config.get("fold_to_3bet", 0.5)
                
                win_rate = self.current_results[name]["win_rate"]
                avg_profit = self.current_results[name]["avg_profit_per_match"]
                
                data.append({
                    "Name": name,
                    "Type": player_type,
                    "Aggression": aggression,
                    "Bluff Frequency": bluff_frequency,
                    "Fold to 3Bet": fold_to_3bet,
                    "Win Rate": win_rate,
                    "Avg Profit": avg_profit
                })
        
        if not data:
            print("No matching data found")
            return
        
        df = pd.DataFrame(data)
        
        # Plot parameter correlations with performance
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Aggression vs Win Rate
        sns.scatterplot(x="Aggression", y="Win Rate", data=df, ax=axes[0], s=100)
        for i, row in df.iterrows():
            axes[0].annotate(row["Name"], (row["Aggression"], row["Win Rate"]),
                           xytext=(5, 5), textcoords='offset points')
        axes[0].set_title("Aggression vs Win Rate")
        axes[0].grid(True, linestyle="--", alpha=0.7)
        
        # Bluff Frequency vs Win Rate
        sns.scatterplot(x="Bluff Frequency", y="Win Rate", data=df, ax=axes[1], s=100)
        for i, row in df.iterrows():
            axes[1].annotate(row["Name"], (row["Bluff Frequency"], row["Win Rate"]),
                           xytext=(5, 5), textcoords='offset points')
        axes[1].set_title("Bluff Frequency vs Win Rate")
        axes[1].grid(True, linestyle="--", alpha=0.7)
        
        # Fold to 3Bet vs Win Rate
        sns.scatterplot(x="Fold to 3Bet", y="Win Rate", data=df, ax=axes[2], s=100)
        for i, row in df.iterrows():
            axes[2].annotate(row["Name"], (row["Fold to 3Bet"], row["Win Rate"]),
                           xytext=(5, 5), textcoords='offset points')
        axes[2].set_title("Fold to 3Bet vs Win Rate")
        axes[2].grid(True, linestyle="--", alpha=0.7)
        
        plt.tight_layout()
        plt.show()
        
        # Plot parameter correlations with profit
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Aggression vs Profit
        sns.scatterplot(x="Aggression", y="Avg Profit", data=df, ax=axes[0], s=100)
        for i, row in df.iterrows():
            axes[0].annotate(row["Name"], (row["Aggression"], row["Avg Profit"]),
                           xytext=(5, 5), textcoords='offset points')
        axes[0].set_title("Aggression vs Avg Profit")
        axes[0].grid(True, linestyle="--", alpha=0.7)
        
        # Bluff Frequency vs Profit
        sns.scatterplot(x="Bluff Frequency", y="Avg Profit", data=df, ax=axes[1], s=100)
        for i, row in df.iterrows():
            axes[1].annotate(row["Name"], (row["Bluff Frequency"], row["Avg Profit"]),
                           xytext=(5, 5), textcoords='offset points')
        axes[1].set_title("Bluff Frequency vs Avg Profit")
        axes[1].grid(True, linestyle="--", alpha=0.7)
        
        # Fold to 3Bet vs Profit
        sns.scatterplot(x="Fold to 3Bet", y="Avg Profit", data=df, ax=axes[2], s=100)
        for i, row in df.iterrows():
            axes[2].annotate(row["Name"], (row["Fold to 3Bet"], row["Avg Profit"]),
                           xytext=(5, 5), textcoords='offset points')
        axes[2].set_title("Fold to 3Bet vs Avg Profit")
        axes[2].grid(True, linestyle="--", alpha=0.7)
        
        plt.tight_layout()
        plt.show()
    
    def run_dashboard(self) -> None:
        """Run the interactive dashboard."""
        if not self.results_files:
            print("No results files found")
            return
        
        # Load most recent results
        self.load_results()
        
        while True:
            print("\nPoker AI Performance Dashboard")
            print("1. List available result files")
            print("2. Load a different result file")
            print("3. Plot win rates")
            print("4. Plot average profits")
            print("5. Plot VPIP vs PFR")
            print("6. Plot aggression factor")
            print("7. Plot profit matrix")
            print("8. Plot player configuration comparison")
            print("9. Exit")
            
            choice = input("Enter your choice (1-9): ")
            
            if choice == "1":
                self.list_available_results()
            elif choice == "2":
                self.list_available_results()
                file_idx = input("Enter the number of the file to load: ")
                try:
                    idx = int(file_idx) - 1
                    if 0 <= idx < len(self.results_files):
                        self.load_results(self.results_files[idx])
                    else:
                        print("Invalid file number")
                except ValueError:
                    print("Invalid input")
            elif choice == "3":
                self.plot_win_rates()
            elif choice == "4":
                self.plot_average_profits()
            elif choice == "5":
                self.plot_vpip_pfr()
            elif choice == "6":
                self.plot_aggression_factor()
            elif choice == "7":
                self.plot_profit_matrix()
            elif choice == "8":
                self.plot_player_config_comparison()
            elif choice == "9":
                print("Exiting dashboard")
                break
            else:
                print("Invalid choice")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Poker AI Performance Dashboard")
    
    parser.add_argument(
        "--results-dir", 
        type=str, 
        default="results",
        help="Directory containing evaluation results"
    )
    
    return parser.parse_args()


def main():
    """Main function to run the dashboard."""
    args = parse_args()
    
    dashboard = PerformanceDashboard(args.results_dir)
    dashboard.run_dashboard()


if __name__ == "__main__":
    main()
