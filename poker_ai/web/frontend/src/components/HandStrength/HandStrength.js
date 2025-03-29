import React from 'react';
import './HandStrength.css';

function HandStrength({ handType, handRank, winProbability }) {
  // Convert numeric hand rank to descriptive text
  const getHandTypeText = () => {
    switch (handType) {
      case 1: return 'Royal Flush';
      case 2: return 'Straight Flush';
      case 3: return 'Four of a Kind';
      case 4: return 'Full House';
      case 5: return 'Flush';
      case 6: return 'Straight';
      case 7: return 'Three of a Kind';
      case 8: return 'Two Pair';
      case 9: return 'Pair';
      case 10: return 'High Card';
      default: return 'Unknown';
    }
  };

  // Get strength category based on win probability
  const getStrengthCategory = () => {
    if (winProbability >= 0.8) return 'very-strong';
    if (winProbability >= 0.6) return 'strong';
    if (winProbability >= 0.4) return 'medium';
    if (winProbability >= 0.2) return 'weak';
    return 'very-weak';
  };

  return (
    <div className="hand-strength">
      <h4 className="strength-title">Hand Strength</h4>
      
      <div className="hand-type">
        <span className="label">Hand:</span>
        <span className="value">{getHandTypeText()}</span>
      </div>
      
      <div className="win-probability">
        <span className="label">Win Probability:</span>
        <div className="probability-bar-container">
          <div 
            className={`probability-bar ${getStrengthCategory()}`}
            style={{ width: `${winProbability * 100}%` }}
          ></div>
        </div>
        <span className="probability-value">{Math.round(winProbability * 100)}%</span>
      </div>
      
      <div className="strength-advice">
        {winProbability >= 0.8 && (
          <span className="advice very-strong">Very strong hand! Consider raising or betting.</span>
        )}
        {winProbability >= 0.6 && winProbability < 0.8 && (
          <span className="advice strong">Strong hand. Betting is recommended.</span>
        )}
        {winProbability >= 0.4 && winProbability < 0.6 && (
          <span className="advice medium">Medium strength. Consider your position and opponents.</span>
        )}
        {winProbability >= 0.2 && winProbability < 0.4 && (
          <span className="advice weak">Weak hand. Check or fold unless in position.</span>
        )}
        {winProbability < 0.2 && (
          <span className="advice very-weak">Very weak hand. Consider folding.</span>
        )}
      </div>
    </div>
  );
}

export default HandStrength;
