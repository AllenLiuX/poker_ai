import React, { useState, useEffect } from 'react';
import './ActionControls.css';
import { 
  ThumbsDown, 
  Check, 
  Phone, 
  DollarSign, 
  ArrowUp, 
  Zap,
  Loader,
  MinusCircle,
  PlusCircle
} from 'lucide-react';

function ActionControls({ validActions, onAction, currentBet, minRaise, playerStack, isLoading }) {
  const [betAmount, setBetAmount] = useState(minRaise || 0);
  
  // Update bet amount when minRaise changes
  useEffect(() => {
    if (minRaise > 0) {
      setBetAmount(minRaise);
    }
  }, [minRaise]);
  
  const handleBetChange = (e) => {
    const value = parseFloat(e.target.value);
    setBetAmount(value);
  };
  
  const handleBetIncrement = (amount) => {
    const newAmount = Math.min(betAmount + amount, playerStack);
    setBetAmount(newAmount);
  };
  
  const handleBetDecrement = (amount) => {
    const newAmount = Math.max(betAmount - amount, minRaise);
    setBetAmount(newAmount);
  };
  
  const handleAction = (action, amount = 0) => {
    onAction(action, amount);
  };
  
  // Calculate min and max bet values
  const minBet = minRaise || currentBet * 2;
  const maxBet = playerStack;
  
  // Calculate bet increment values based on blinds and pot size
  const smallIncrement = Math.max(1, Math.floor(minRaise / 2));
  const mediumIncrement = minRaise;
  const largeIncrement = Math.max(minRaise * 2, Math.floor(currentBet / 2));
  
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
          <div className="basic-actions">
            {validActions.includes('FOLD') && (
              <button 
                className="action-button fold"
                onClick={() => handleAction('FOLD')}
              >
                <ThumbsDown size={16} />
                <span>Fold</span>
              </button>
            )}
            
            {validActions.includes('CHECK') && (
              <button 
                className="action-button check"
                onClick={() => handleAction('CHECK')}
              >
                <Check size={16} />
                <span>Check</span>
              </button>
            )}
            
            {validActions.includes('CALL') && (
              <button 
                className="action-button call"
                onClick={() => handleAction('CALL', currentBet)}
              >
                <Phone size={16} />
                <span>Call ${currentBet.toFixed(2)}</span>
              </button>
            )}
            
            {validActions.includes('ALL_IN') && (
              <button 
                className="action-button all-in"
                onClick={() => handleAction('ALL_IN', playerStack)}
              >
                <Zap size={16} />
                <span>All-In ${playerStack.toFixed(2)}</span>
              </button>
            )}
          </div>
          
          {validActions.includes('BET') && (
            <div className="bet-control">
              <div className="bet-control-row">
                <div className="bet-amount-display">
                  <span className="bet-label">Bet:</span>
                  <span className="bet-amount">${betAmount.toFixed(2)}</span>
                </div>
                
                <div className="bet-slider-container">
                  <span className="range-label">Min:${minBet.toFixed(0)}</span>
                  <input 
                    type="range"
                    min={minBet}
                    max={maxBet}
                    step={smallIncrement}
                    value={betAmount}
                    onChange={handleBetChange}
                    className="bet-slider"
                  />
                  <span className="range-label">Max:${maxBet.toFixed(0)}</span>
                </div>
                
                <div className="bet-increment-buttons">
                  <button 
                    className="increment-button"
                    onClick={() => handleBetDecrement(smallIncrement)}
                    disabled={betAmount <= minBet}
                  >
                    <MinusCircle size={14} />
                  </button>
                  <button 
                    className="increment-button"
                    onClick={() => handleBetIncrement(smallIncrement)}
                    disabled={betAmount >= maxBet}
                  >
                    <PlusCircle size={14} />
                  </button>
                </div>
                
                <button 
                  className="action-button bet"
                  onClick={() => handleAction('BET', betAmount)}
                >
                  <DollarSign size={16} />
                  <span>Bet</span>
                </button>
              </div>
            </div>
          )}
          
          {validActions.includes('RAISE') && (
            <div className="bet-control">
              <div className="bet-control-row">
                <div className="bet-amount-display">
                  <span className="bet-label">Raise:</span>
                  <span className="bet-amount">${betAmount.toFixed(2)}</span>
                </div>
                
                <div className="bet-slider-container">
                  <span className="range-label">Min:${minRaise.toFixed(0)}</span>
                  <input 
                    type="range"
                    min={minRaise}
                    max={maxBet}
                    step={smallIncrement}
                    value={betAmount}
                    onChange={handleBetChange}
                    className="bet-slider"
                  />
                  <span className="range-label">Max:${maxBet.toFixed(0)}</span>
                </div>
                
                <div className="bet-increment-buttons">
                  <button 
                    className="increment-button"
                    onClick={() => handleBetDecrement(smallIncrement)}
                    disabled={betAmount <= minRaise}
                  >
                    <MinusCircle size={14} />
                  </button>
                  <button 
                    className="increment-button"
                    onClick={() => handleBetIncrement(smallIncrement)}
                    disabled={betAmount >= maxBet}
                  >
                    <PlusCircle size={14} />
                  </button>
                </div>
                
                <button 
                  className="action-button raise"
                  onClick={() => handleAction('RAISE', betAmount)}
                >
                  <ArrowUp size={16} />
                  <span>Raise</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ActionControls;
