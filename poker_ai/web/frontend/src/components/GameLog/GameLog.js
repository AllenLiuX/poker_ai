import React from 'react';
import './GameLog.css';

function GameLog({ log }) {
  // Function to render a log entry based on its type
  const renderLogEntry = (entry, index) => {
    if (entry.type === 'action') {
      return (
        <div key={index} className="log-entry action">
          <span className="player-name">{entry.playerName}</span>
          <span className="action-type">
            {formatAction(entry.action, entry.amount)}
          </span>
        </div>
      );
    } else if (entry.type === 'deal_community') {
      return (
        <div key={index} className="log-entry deal">
          <span className="deal-type">{entry.data.street}</span>
          <span className="cards">
            {entry.data.cards.join(' ')}
          </span>
        </div>
      );
    } else if (entry.type === 'showdown') {
      return (
        <div key={index} className="log-entry showdown">
          <span className="showdown-title">Showdown</span>
          {entry.data.pot_distributions && entry.data.pot_distributions.map((dist, i) => (
            <div key={i} className="pot-distribution">
              <span className="winner-name">
                {getPlayerNameById(dist.player_id)} wins ${dist.amount.toFixed(2)}
              </span>
              <span className="hand-description">
                with {dist.hand_description}
              </span>
            </div>
          ))}
        </div>
      );
    } else if (entry.type === 'hand_end') {
      return (
        <div key={index} className="log-entry hand-end">
          <span className="winner-name">
            {getPlayerNameById(entry.data.winner)} wins ${entry.data.amount.toFixed(2)}
          </span>
          <span className="reason">
            {formatReason(entry.data.reason)}
          </span>
        </div>
      );
    }
    
    return null;
  };
  
  // Helper function to format action text
  const formatAction = (action, amount) => {
    switch (action) {
      case 'FOLD':
        return 'folds';
      case 'CHECK':
        return 'checks';
      case 'CALL':
        return `calls $${amount.toFixed(2)}`;
      case 'BET':
        return `bets $${amount.toFixed(2)}`;
      case 'RAISE':
        return `raises to $${amount.toFixed(2)}`;
      case 'ALL_IN':
        return `goes all-in with $${amount.toFixed(2)}`;
      default:
        return action;
    }
  };
  
  // Helper function to format reason text
  const formatReason = (reason) => {
    switch (reason) {
      case 'all_others_folded':
        return 'All other players folded';
      default:
        return reason;
    }
  };
  
  // Helper function to get player name by ID (placeholder)
  const getPlayerNameById = (playerId) => {
    // In a real implementation, this would look up the player name from the game state
    // For now, just return a generic name
    return 'Player';
  };
  
  return (
    <div className="game-log">
      <h3 className="log-title">Hand History</h3>
      
      <div className="log-entries">
        {log.length === 0 ? (
          <div className="empty-log">No actions yet</div>
        ) : (
          log.map((entry, index) => renderLogEntry(entry, index))
        )}
      </div>
    </div>
  );
}

export default GameLog;
