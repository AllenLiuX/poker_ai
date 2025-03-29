import React from 'react';
import './Card.css';

function Card({ card }) {
  // Handle edge cases for card format
  if (!card || card.length < 2) {
    return <div className="card black">Invalid</div>;
  }
  
  // Parse the card string (e.g., "Ah" or "AH" or "14S" for Ace of hearts/spades)
  let rank = card.charAt(0);
  let suit = '';
  
  // Handle different card formats
  if (card.length === 2) {
    // Format like "AS" or "KH"
    suit = card.charAt(1).toLowerCase();
  } else if (card.length === 3 && !isNaN(card.substring(0, 2))) {
    // Format like "10S" or "14H" (for Ace)
    rank = card.substring(0, 2);
    suit = card.charAt(2).toLowerCase();
  } else {
    // Other formats, just take first and last char
    rank = card.charAt(0);
    suit = card.charAt(card.length - 1).toLowerCase();
  }
  
  // Get the full rank name
  const getRankName = () => {
    switch (rank) {
      case 'A': return 'A';
      case 'K': return 'K';
      case 'Q': return 'Q';
      case 'J': return 'J';
      case 'T': return '10';
      case '1': return 'A'; // Convert '1' to 'A' for Ace
      case '14': return 'A'; // Convert '14' to 'A' for Ace
      case '11': return 'J'; // Convert '11' to 'J' for Jack
      case '12': return 'Q'; // Convert '12' to 'Q' for Queen
      case '13': return 'K'; // Convert '13' to 'K' for King
      default: return rank;
    }
  };
  
  // Get suit info
  const getSuitInfo = () => {
    switch (suit) {
      case 'h':
        return { 
          symbol: '♥',
          textSymbol: 'H',
          color: 'red',
          name: 'hearts'
        };
      case 'd':
        return { 
          symbol: '♦',
          textSymbol: 'D',
          color: 'red',
          name: 'diamonds'
        };
      case 'c':
        return { 
          symbol: '♣',
          textSymbol: 'C',
          color: 'black',
          name: 'clubs'
        };
      case 's':
        return { 
          symbol: '♠',
          textSymbol: 'S',
          color: 'black',
          name: 'spades'
        };
      default:
        // Handle uppercase suits as well
        const upperSuit = suit.toUpperCase();
        if (upperSuit === 'H') {
          return {
            symbol: '♥',
            textSymbol: 'H',
            color: 'red',
            name: 'hearts'
          };
        } else if (upperSuit === 'D') {
          return {
            symbol: '♦',
            textSymbol: 'D',
            color: 'red',
            name: 'diamonds'
          };
        } else if (upperSuit === 'C') {
          return {
            symbol: '♣',
            textSymbol: 'C',
            color: 'black',
            name: 'clubs'
          };
        } else if (upperSuit === 'S') {
          return {
            symbol: '♠',
            textSymbol: 'S',
            color: 'black',
            name: 'spades'
          };
        }
        return { 
          symbol: '',
          textSymbol: suit.toUpperCase(),
          color: 'black',
          name: 'unknown'
        };
    }
  };
  
  const suitInfo = getSuitInfo();
  const rankName = getRankName();
  
  return (
    <div className={`card ${suitInfo.color}`}>
      <div className="card-corner top-left">
        <div className="card-rank">{rankName}</div>
        <div className="card-suit">
          <span className="suit-symbol">{suitInfo.symbol}</span>
          <span className="suit-text">{suitInfo.textSymbol}</span>
        </div>
      </div>
      
      <div className="card-center">
        <div className="card-suit-large">
          <span className="suit-symbol">{suitInfo.symbol}</span>
          <span className="suit-text">{suitInfo.textSymbol}</span>
        </div>
      </div>
      
      <div className="card-corner bottom-right">
        <div className="card-rank">{rankName}</div>
        <div className="card-suit">
          <span className="suit-symbol">{suitInfo.symbol}</span>
          <span className="suit-text">{suitInfo.textSymbol}</span>
        </div>
      </div>
    </div>
  );
}

export default Card;
