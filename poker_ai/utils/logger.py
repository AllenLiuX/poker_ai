"""Logging utilities for poker AI."""
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


class HandHistoryLogger:
    """Logger for poker hand histories."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the hand history logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("poker_ai.hand_history")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"hand_history_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        
        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def log_hand(self, hand_history: List[Dict[str, Any]], session_id: Optional[str] = None) -> None:
        """
        Log a complete hand history.
        
        Args:
            hand_history: List of actions and events in the hand
            session_id: Optional session identifier
        """
        hand_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "hand_history": hand_history
        }
        
        self.logger.info(json.dumps(hand_data))
    
    def log_action(self, action_data: Dict[str, Any], session_id: Optional[str] = None) -> None:
        """
        Log a single action or event.
        
        Args:
            action_data: Data describing the action or event
            session_id: Optional session identifier
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "action": action_data
        }
        
        self.logger.info(json.dumps(log_data))


class PerformanceLogger:
    """Logger for AI performance metrics."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the performance logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("poker_ai.performance")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"performance_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        
        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def log_session_result(
        self, 
        player_id: str, 
        player_name: str, 
        hands_played: int, 
        profit_loss: float,
        win_rate: float,
        vpip: float,  # Voluntarily put money in pot percentage
        pfr: float,   # Pre-flop raise percentage
        session_id: Optional[str] = None
    ) -> None:
        """
        Log the results of a playing session.
        
        Args:
            player_id: ID of the player
            player_name: Name of the player
            hands_played: Number of hands played
            profit_loss: Total profit or loss
            win_rate: Win rate in BB/100 hands
            vpip: Voluntarily put money in pot percentage
            pfr: Pre-flop raise percentage
            session_id: Optional session identifier
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "player_id": player_id,
            "player_name": player_name,
            "hands_played": hands_played,
            "profit_loss": profit_loss,
            "win_rate": win_rate,
            "vpip": vpip,
            "pfr": pfr
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_decision_quality(
        self,
        player_id: str,
        hand_id: str,
        decision: Dict[str, Any],
        equity: float,
        ev: float,  # Expected value of the decision
        optimal_decision: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Log the quality of an AI decision.
        
        Args:
            player_id: ID of the player
            hand_id: ID of the hand
            decision: The decision that was made
            equity: Hand equity at the time of decision
            ev: Expected value of the decision
            optimal_decision: The optimal decision (if known)
            session_id: Optional session identifier
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "player_id": player_id,
            "hand_id": hand_id,
            "decision": decision,
            "equity": equity,
            "ev": ev,
            "optimal_decision": optimal_decision
        }
        
        self.logger.info(json.dumps(log_data))
