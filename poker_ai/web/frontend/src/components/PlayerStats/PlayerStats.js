import React from 'react';
import './PlayerStats.css';

function PlayerStats({ stats }) {
  // Calculate VPIP (Voluntarily Put Money In Pot)
  const vpip = stats.handsPlayed > 0 
    ? Math.round((stats.voluntaryBets / stats.handsPlayed) * 100) 
    : 0;
  
  // Calculate PFR (Pre-Flop Raise)
  const pfr = stats.handsPlayed > 0 
    ? Math.round((stats.preflopRaises / stats.handsPlayed) * 100) 
    : 0;
  
  // Calculate AF (Aggression Factor)
  const aggressionFactor = (stats.bets + stats.raises) > 0 
    ? ((stats.bets + stats.raises) / stats.calls).toFixed(2) 
    : 0;
  
  // Calculate win rate
  const winRate = stats.handsPlayed > 0 
    ? Math.round((stats.handsWon / stats.handsPlayed) * 100) 
    : 0;

  return (
    <div className="player-stats">
      <h4 className="stats-title">Player Statistics</h4>
      
      <div className="stats-grid">
        <div className="stat-item">
          <div className="stat-label">Hands Played</div>
          <div className="stat-value">{stats.handsPlayed}</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">Hands Won</div>
          <div className="stat-value">{stats.handsWon}</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">Win Rate</div>
          <div className="stat-value">{winRate}%</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">VPIP</div>
          <div className="stat-value">{vpip}%</div>
          <div className="stat-tooltip">Voluntarily Put Money In Pot</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">PFR</div>
          <div className="stat-value">{pfr}%</div>
          <div className="stat-tooltip">Pre-Flop Raise Percentage</div>
        </div>
        
        <div className="stat-item">
          <div className="stat-label">AF</div>
          <div className="stat-value">{aggressionFactor}</div>
          <div className="stat-tooltip">Aggression Factor (bets+raises)/calls</div>
        </div>
      </div>
      
      <div className="profit-loss">
        <div className="profit-label">Total Profit/Loss</div>
        <div className={`profit-value ${stats.totalProfit >= 0 ? 'profit' : 'loss'}`}>
          {stats.totalProfit >= 0 ? '+' : ''}{stats.totalProfit.toFixed(2)}
        </div>
      </div>
    </div>
  );
}

export default PlayerStats;
