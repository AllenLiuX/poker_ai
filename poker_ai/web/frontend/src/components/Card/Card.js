import React from 'react';
import './Card.css';
import { Heart, Club, Diamond, Spade } from 'lucide-react';

function Card({ card }) {
  // Parse the card string (e.g., "Ah" for Ace of hearts)
  const rank = card.charAt(0);
  const suit = card.charAt(1);
  
  // Get the full rank name
  const getRankName = () => {
    switch (rank) {
      case 'A': return 'A';
      case 'K': return 'K';
      case 'Q': return 'Q';
      case 'J': return 'J';
      case 'T': return '10';
      default: return rank;
    }
  };
  
  // Get suit icon and color
  const getSuitInfo = () => {
    switch (suit) {
      case 'h':
        return { 
          icon: <Heart size={16} className="suit-icon" />,
          color: 'red',
          name: 'hearts'
        };
      case 'd':
        return { 
          icon: <Diamond size={16} className="suit-icon" />,
          color: 'red',
          name: 'diamonds'
        };
      case 'c':
        return { 
          icon: <Club size={16} className="suit-icon" />,
          color: 'black',
          name: 'clubs'
        };
      case 's':
        return { 
          icon: <Spade size={16} className="suit-icon" />,
          color: 'black',
          name: 'spades'
        };
      default:
        return { 
          icon: null,
          color: 'black',
          name: 'unknown'
        };
    }
  };
  
  const suitInfo = getSuitInfo();
  
  return (
    <div className={`card ${suitInfo.color}`}>
      <div className="card-corner top-left">
        <div className="card-rank">{getRankName()}</div>
        <div className="card-suit">{suitInfo.icon}</div>
      </div>
      
      <div className="card-center">
        {suitInfo.icon && React.cloneElement(suitInfo.icon, { size: 24 })}
      </div>
      
      <div className="card-corner bottom-right">
        <div className="card-rank">{getRankName()}</div>
        <div className="card-suit">{suitInfo.icon}</div>
      </div>
    </div>
  );
}

export default Card;
