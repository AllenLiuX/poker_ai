import React, { useState } from 'react';
import './ActionControls.css';
import { 
  ThumbsDown, 
  Check, 
  Phone, 
  DollarSign, 
  ArrowUp, 
  Zap,
  Loader
} from 'lucide-react';

function ActionControls({ validActions, onAction, currentBet, minRaise, playerStack, isLoading }) {
  const [betAmount, setBetAmount] = useState(minRaise || 0);
  
  const handleBetChange = (e) => {
    const value = parseFloat(e.target.value);
    setBetAmount(value);
  };
  
  const handleAction = (action, amount = 0) => {
    onAction(action, amount);
  };
  
  // Calculate min and max bet values
  const minBet = minRaise || currentBet * 2;
  const maxBet = playerStack;
  
  return (
    <div className="action-controls">
      <h3 className="action-title">Your Action</h3>
      
      {isLoading ? (
        <div className="loading-indicator">
          <Loader className="spinner" />
          <p>Waiting for other players...</p>
        </div>
      ) : (
        <div className="action-buttons">
          {validActions.includes('FOLD') && (
            <button 
              className="action-button fold"
              onClick={() => handleAction('FOLD')}
            >
              <ThumbsDown size={18} />
              <span>Fold</span>
            </button>
          )}
          
          {validActions.includes('CHECK') && (
            <button 
              className="action-button check"
              onClick={() => handleAction('CHECK')}
            >
              <Check size={18} />
              <span>Check</span>
            </button>
          )}
          
          {validActions.includes('CALL') && (
            <button 
              className="action-button call"
              onClick={() => handleAction('CALL', currentBet)}
            >
              <Phone size={18} />
              <span>Call ${currentBet.toFixed(2)}</span>
            </button>
          )}
          
          {validActions.includes('BET') && (
            <div className="bet-control">
              <div className="slider-container">
                <input 
                  type="range"
                  min={minBet}
                  max={maxBet}
                  step={1}
                  value={betAmount}
                  onChange={handleBetChange}
                  className="bet-slider"
                />
                <span className="bet-amount">${betAmount.toFixed(2)}</span>
              </div>
              <button 
                className="action-button bet"
                onClick={() => handleAction('BET', betAmount)}
              >
                <DollarSign size={18} />
                <span>Bet</span>
              </button>
            </div>
          )}
          
          {validActions.includes('RAISE') && (
            <div className="bet-control">
              <div className="slider-container">
                <input 
                  type="range"
                  min={minRaise}
                  max={maxBet}
                  step={1}
                  value={betAmount}
                  onChange={handleBetChange}
                  className="bet-slider"
                />
                <span className="bet-amount">${betAmount.toFixed(2)}</span>
              </div>
              <button 
                className="action-button raise"
                onClick={() => handleAction('RAISE', betAmount)}
              >
                <ArrowUp size={18} />
                <span>Raise</span>
              </button>
            </div>
          )}
          
          {validActions.includes('ALL_IN') && (
            <button 
              className="action-button all-in"
              onClick={() => handleAction('ALL_IN', playerStack)}
            >
              <Zap size={18} />
              <span>All-In ${playerStack.toFixed(2)}</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default ActionControls;
