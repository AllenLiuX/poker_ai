import React from 'react';
import './HandResult.css';
import Card from '../Card/Card';

function HandResult({ result, onClose }) {
  if (!result) return null;

  return (
    <div className="hand-result-overlay">
      <div className="hand-result-modal">
        <h2 className="result-title">Hand Complete</h2>
        
        <div className="result-content">
          {result.type === 'showdown' ? (
            <>
              <h3 className="showdown-title">Showdown</h3>
              
              {result.winners.map((winner, index) => (
                <div key={index} className="winner-info">
                  <div className="winner-name">{winner.playerName}</div>
                  <div className="winner-amount">wins ${winner.amount.toFixed(2)}</div>
                  
                  <div className="winner-hand">
                    <div className="hand-cards">
                      {winner.holeCards.map((card, cardIndex) => (
                        <Card key={cardIndex} card={card} />
                      ))}
                    </div>
                    <div className="hand-description">{winner.handDescription}</div>
                  </div>
                </div>
              ))}
              
              <div className="community-cards-container">
                <div className="community-label">Community Cards</div>
                <div className="community-cards">
                  {result.communityCards.map((card, index) => (
                    <Card key={index} card={card} />
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="fold-result">
              <div className="winner-name">{result.winner.playerName}</div>
              <div className="winner-amount">wins ${result.amount.toFixed(2)}</div>
              <div className="fold-reason">All other players folded</div>
            </div>
          )}
        </div>
        
        <button className="continue-button" onClick={onClose}>
          Continue
        </button>
      </div>
    </div>
  );
}

export default HandResult;
