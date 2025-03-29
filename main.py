#!/usr/bin/env python
"""Main entry point for the poker AI agent."""
import argparse
import sys

from poker_ai.game.runner import GameRunner


def main():
    """Main entry point for the poker AI agent."""
    parser = argparse.ArgumentParser(description="Poker AI Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Local game command
    local_parser = subparsers.add_parser("local", help="Run a local poker game")
    local_parser.add_argument("--ai-players", type=int, default=5, help="Number of AI players")
    local_parser.add_argument("--stack", type=float, default=1000.0, help="Starting stack size")
    local_parser.add_argument("--small-blind", type=float, default=1.0, help="Small blind amount")
    local_parser.add_argument("--big-blind", type=float, default=2.0, help="Big blind amount")
    local_parser.add_argument("--ante", type=float, default=0.0, help="Ante amount")
    local_parser.add_argument("--hands", type=int, default=10, help="Number of hands to play")
    local_parser.add_argument("--no-human", action="store_true", help="Don't include a human player")
    local_parser.add_argument("--advanced-ai", action="store_true", help="Use advanced AI players")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "local":
        # Run local game
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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
