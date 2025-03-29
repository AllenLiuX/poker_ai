import React from 'react';
import './PlayerSeat.css';
import Card from '../Card/Card';
import { User, Clock, Award, Timer } from 'lucide-react';

function PlayerSeat({ 
  player, 
  isActive, 
  isDealer, 
  isSmallBlind, 
  isBigBlind, 
  showCards, 
  isWinner,
  lastAction
}) {
  // Determine player status class
  const getStatusClass = () => {
    if (isWinner) return 'winner';
    if (!player.is_active) return 'folded';
    if (player.is_all_in) return 'all-in';
    if (isActive) return 'active';
    return '';
  };
  
  // Determine position indicator
  const getPositionIndicator = () => {
    if (isDealer) return 'D';
    if (isSmallBlind) return 'SB';
    if (isBigBlind) return 'BB';
    return null;
  };
  
  return (
    <div className={`player-seat ${getStatusClass()}`}>
      {getPositionIndicator() && (
        <div className={`position-indicator ${isDealer ? 'dealer' : isSmallBlind ? 'small-blind' : 'big-blind'}`}>
          {getPositionIndicator()}
        </div>
      )}
      
      <div className="player-info">
        <div className="player-avatar">
          {player.is_human ? (
            <User size={24} className="avatar-icon human" />
          ) : (
            <Award size={24} className="avatar-icon ai" />
          )}
        </div>
        
        <div className="player-details">
          <div className="player-name">{player.name}</div>
          <div className="player-stack">${player.stack.toFixed(2)}</div>
        </div>
      </div>
      
      {player.current_bet > 0 && (
        <div className="player-bet">${player.current_bet.toFixed(2)}</div>
      )}
      
      <div className="player-cards">
        {player.hole_cards && player.hole_cards.length > 0 && (showCards || player.is_human) ? (
          <div className="hole-cards">
            {player.hole_cards.map((card, index) => (
              <Card key={index} card={card} style={{display: 'inline-block', marginRight: '10px'}} />
            ))}
          </div>
        ) : player.hole_cards && player.hole_cards.length > 0 ? (
          <div className="card-backs">
            <div className="card-back"></div>
            <div className="card-back"></div>
          </div>
        ) : null}
        
        {isActive && (
          <div className="thinking-indicator">
            <Timer size={16} className="thinking-icon" />
            <span>Thinking...</span>
          </div>
        )}
      </div>
      
      {lastAction && (
        <div className="last-action">
          <Clock size={14} className="action-icon" />
          <span>{lastAction}</span>
        </div>
      )}
    </div>
  );
}

export default PlayerSeat;
