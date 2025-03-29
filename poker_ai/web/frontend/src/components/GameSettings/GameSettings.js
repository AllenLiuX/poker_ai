import React, { useState } from 'react';
import './GameSettings.css';

function GameSettings({ gameInfo, onEndGame }) {
  const [showSettings, setShowSettings] = useState(false);
  
  const toggleSettings = () => {
    setShowSettings(!showSettings);
  };

  return (
    <div className="game-settings">
      <button 
        className="settings-toggle" 
        onClick={toggleSettings}
      >
        {showSettings ? 'Hide Settings' : 'Game Settings'}
      </button>
      
      {showSettings && (
        <div className="settings-panel">
          <h3 className="settings-title">Game Information</h3>
          
          <div className="settings-info">
            <div className="info-row">
              <span className="info-label">Game ID:</span>
              <span className="info-value">{gameInfo.gameId}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Players:</span>
              <span className="info-value">{gameInfo.playerCount}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Small Blind:</span>
              <span className="info-value">${gameInfo.smallBlind.toFixed(2)}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Big Blind:</span>
              <span className="info-value">${gameInfo.bigBlind.toFixed(2)}</span>
            </div>
            
            {gameInfo.ante > 0 && (
              <div className="info-row">
                <span className="info-label">Ante:</span>
                <span className="info-value">${gameInfo.ante.toFixed(2)}</span>
              </div>
            )}
            
            <div className="info-row">
              <span className="info-label">Starting Stack:</span>
              <span className="info-value">${gameInfo.startingStack.toFixed(2)}</span>
            </div>
            
            <div className="info-row">
              <span className="info-label">Hand #:</span>
              <span className="info-value">{gameInfo.handNumber}</span>
            </div>
          </div>
          
          <div className="settings-actions">
            <button 
              className="end-game-button" 
              onClick={onEndGame}
            >
              End Game
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default GameSettings;
