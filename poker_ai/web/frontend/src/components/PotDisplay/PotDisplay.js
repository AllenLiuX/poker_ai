import React from 'react';
import './PotDisplay.css';
import { DollarSign, Users } from 'lucide-react';

function PotDisplay({ mainPot, sidePots = [] }) {
  return (
    <div className="pot-display">
      <div className="main-pot">
        <div className="pot-label">
          <DollarSign size={16} />
          <span>Main Pot</span>
        </div>
        <div className="pot-amount">${mainPot.toFixed(2)}</div>
      </div>
      
      {sidePots.length > 0 && (
        <div className="side-pots">
          {sidePots.map((pot, index) => (
            <div key={index} className="side-pot">
              <div className="pot-label">
                <DollarSign size={16} />
                <span>Side Pot {index + 1}</span>
              </div>
              <div className="pot-amount">${pot.amount.toFixed(2)}</div>
              <div className="pot-eligible">
                <Users size={14} />
                <span>Eligible: {pot.eligiblePlayers.join(', ')}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PotDisplay;
