import React, { useState } from 'react';
import GameSetup from './components/GameSetup/GameSetup';
import PokerTable from './components/PokerTable/PokerTable';
import './App.css';

function App() {
  const [gameState, setGameState] = useState(null);
  const [gameId, setGameId] = useState(null);
  const [humanPlayerId, setHumanPlayerId] = useState(null);

  const handleGameCreated = (data) => {
    setGameId(data.game_id);
    setHumanPlayerId(data.human_player_id);
    setGameState(data.state);
  };

  const handleGameStateUpdated = (state) => {
    setGameState(state);
  };

  return (
    <div className="app-container">
      <h1 className="app-title">Poker AI Challenge</h1>
      
      {!gameState ? (
        <GameSetup onGameCreated={handleGameCreated} />
      ) : (
        <PokerTable 
          gameId={gameId}
          humanPlayerId={humanPlayerId}
          gameState={gameState}
          onGameStateUpdated={handleGameStateUpdated}
        />
      )}
    </div>
  );
}

export default App;
