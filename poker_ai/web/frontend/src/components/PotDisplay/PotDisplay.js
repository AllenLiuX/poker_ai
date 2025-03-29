import React from 'react';
import './PotDisplay.css';
import { DollarSign } from 'lucide-react';

function PotDisplay({ mainPot }) {
  return (
    <div className="pot-display-simple">
      <DollarSign size={20} className="pot-icon" />
      <span className="pot-amount-simple">${mainPot.toFixed(2)}</span>
    </div>
  );
}

export default PotDisplay;
