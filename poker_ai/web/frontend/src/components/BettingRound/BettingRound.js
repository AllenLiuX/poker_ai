import React from 'react';
import './BettingRound.css';
import { CircleDot, Circle, ArrowRight } from 'lucide-react';

function BettingRound({ round }) {
  const rounds = ['PREFLOP', 'FLOP', 'TURN', 'RIVER'];
  
  // Get the index of the current round
  const currentIndex = rounds.indexOf(round.toUpperCase());
  
  // Get display names for rounds
  const getDisplayName = (roundName) => {
    switch(roundName) {
      case 'PREFLOP': return 'Pre-Flop';
      case 'FLOP': return 'Flop';
      case 'TURN': return 'Turn';
      case 'RIVER': return 'River';
      default: return roundName;
    }
  };
  
  return (
    <div className="betting-round">
      <div className="round-title">Betting Round</div>
      <div className="round-indicators">
        {rounds.map((r, index) => {
          const isActive = r.toUpperCase() === round.toUpperCase();
          const isPast = rounds.indexOf(r.toUpperCase()) < currentIndex;
          
          return (
            <React.Fragment key={r}>
              {index > 0 && (
                <div className="round-connector">
                  <ArrowRight size={12} className={isPast ? 'completed' : ''} />
                </div>
              )}
              <div className={`round-indicator ${isActive ? 'active' : ''} ${isPast ? 'past' : ''}`}>
                {isActive ? (
                  <CircleDot size={16} className="round-icon" />
                ) : (
                  <Circle size={16} className="round-icon" />
                )}
                <span className="round-name">{getDisplayName(r)}</span>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

export default BettingRound;
