import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import Card from '../Card/Card';
import PlayerSeat from '../PlayerSeat/PlayerSeat';
import ActionControls from '../ActionControls/ActionControls';
import GameLog from '../GameLog/GameLog';
import PotDisplay from '../PotDisplay/PotDisplay';
import BettingRound from '../BettingRound/BettingRound';
import HandStrength from '../HandStrength/HandStrength';
import GameSettings from '../GameSettings/GameSettings';
import HandResult from '../HandResult/HandResult';
import { API_URL } from '../../Config';

import { 
  RotateCcw, 
  AlertTriangle, 
  Award, 
  Clock, 
  DollarSign
} from 'lucide-react';
import './PokerTable.css';

// Player positions around the table
const PlayerPositions = [
  { top: '50%', left: '10%', transform: 'translate(-50%, -50%)' }, // Left
  { top: '15%', left: '25%', transform: 'translate(-50%, -50%)' }, // Top-left
  { top: '15%', left: '50%', transform: 'translate(-50%, -50%)' }, // Top
  { top: '15%', left: '75%', transform: 'translate(-50%, -50%)' }, // Top-right
  { top: '50%', left: '90%', transform: 'translate(-50%, -50%)' }, // Right
  { top: '85%', left: '75%', transform: 'translate(-50%, -50%)' }, // Bottom-right
  { top: '85%', left: '50%', transform: 'translate(-50%, -50%)' }, // Bottom (human player)
  { top: '85%', left: '25%', transform: 'translate(-50%, -50%)' }, // Bottom-left
];

function PokerTable({ gameId, humanPlayerId, gameState, onGameStateUpdated, onAction, onEndGame }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [socket, setSocket] = useState(null);
  const [gameLog, setGameLog] = useState([]);
  const [showHandResult, setShowHandResult] = useState(false);
  const [handResult, setHandResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Initialize socket connection
  useEffect(() => {
    // const newSocket = io('http://localhost:5001');
    const newSocket = io(API_URL);
    
    newSocket.on('connect', () => {
      console.log('Connected to server');
    });
    
    newSocket.on('ai_action', (data) => {
      setGameLog(prevLog => [...prevLog, {
        type: 'action',
        playerName: data.player_name,
        action: data.action_type,
        amount: data.amount
      }]);
      
      // Refresh game state
      fetchGameState();
    });
    
    setSocket(newSocket);
    
    return () => {
      newSocket.disconnect();
    };
  }, [gameId]);

  // Update game log when game state changes
  useEffect(() => {
    if (gameState && gameState.hand_history) {
      const newLog = gameState.hand_history.map(item => {
        if (item.type === 'action') {
          return {
            type: 'action',
            playerName: item.player_name,
            action: item.action,
            amount: item.amount
          };
        } else {
          return item;
        }
      });
      setGameLog(newLog);
    }
  }, [gameState]);

  // Check for hand end
  useEffect(() => {
    if (gameState && gameState.is_hand_over) {
      // Show hand result
      setHandResult({
        winners: gameState.winners || [],
        players: gameState.players
      });
      setShowHandResult(true);
    }
  }, [gameState]);

  const handleAction = (action, amount) => {
    setIsLoading(true);
    
    // Send action to server
    axios.post(`${API_URL}/game/${gameId}/action`, {
      action_type: action,
      amount: amount
    })
    .then(response => {
      onGameStateUpdated(response.data.state);
      setIsLoading(false);
    })
    .catch(err => {
      console.error('Error submitting action:', err);
      setError('Failed to submit action');
      setIsLoading(false);
    });
  };
  
  // Close hand result modal
  const closeHandResult = () => {
    setShowHandResult(false);
  };
  
  // Get player position on the table
  const getPlayerPosition = (index, totalPlayers) => {
    // Find the human player index
    const humanIndex = gameState.players.findIndex(player => player.is_human);
    
    // If this is the human player, always position at bottom middle
    if (index === humanIndex) {
      return { 
        bottom: '10px', 
        left: '50%', 
        transform: 'translateX(-50%)',
        position: 'absolute'
      };
    }
    
    const positions = {
      2: [
        { top: '10%', left: '50%', transform: 'translateX(-50%)' }     // top
      ],
      3: [
        { top: '10%', left: '25%', transform: 'translateX(-50%)' },    // top left
        { top: '10%', left: '75%', transform: 'translateX(-50%)' }     // top right
      ],
      4: [
        { top: '50%', right: '10%', transform: 'translateY(-50%)' },   // right
        { top: '10%', left: '50%', transform: 'translateX(-50%)' },    // top
        { top: '50%', left: '10%', transform: 'translateY(-50%)' }     // left
      ],
      6: [
        { bottom: '25%', right: '10%', transform: 'translateY(-50%)' }, // bottom right
        { top: '25%', right: '10%', transform: 'translateY(-50%)' },    // top right
        { top: '10%', left: '50%', transform: 'translateX(-50%)' },     // top
        { top: '25%', left: '10%', transform: 'translateY(-50%)' },     // top left
        { bottom: '25%', left: '10%', transform: 'translateY(-50%)' }   // bottom left
      ],
      8: [
        { bottom: '15%', right: '20%', transform: 'translateY(-50%)' }, // bottom right
        { right: '10%', top: '50%', transform: 'translateY(-50%)' },    // right
        { top: '15%', right: '20%', transform: 'translateY(-50%)' },    // top right
        { top: '10%', left: '50%', transform: 'translateX(-50%)' },     // top
        { top: '15%', left: '20%', transform: 'translateY(-50%)' },     // top left
        { left: '10%', top: '50%', transform: 'translateY(-50%)' },     // left
        { bottom: '15%', left: '20%', transform: 'translateY(-50%)' }   // bottom left
      ]
    };
    
    // Adjust index to skip the human player
    let adjustedIndex = index;
    if (humanIndex !== -1 && index > humanIndex) {
      adjustedIndex -= 1;
    }
    
    // Default to 6 positions if not defined
    const tablePositions = positions[totalPlayers] || positions[6];
    return tablePositions[adjustedIndex < tablePositions.length ? adjustedIndex : 0];
  };
  
  // Calculate the hand strength (placeholder - would be provided by backend)
  const calculateHandStrength = () => {
    // This would be calculated by the backend in a real implementation
    return {
      handType: 9, // Pair
      handRank: 0.3,
      winProbability: 0.35
    };
  };
  
  // Get formatted betting round name
  const getBettingRound = () => {
    return gameState.betting_round || 'PREFLOP';
  };
  
  const fetchGameState = async () => {
    try {
      const response = await axios.get(`${API_URL}/game/${gameId}/state`);
      onGameStateUpdated(response.data.state);
    } catch (err) {
      console.error('Error fetching game state:', err);
      setError('Failed to fetch game state');
    }
  };

  // Find the human player
  const humanPlayer = gameState.players ? gameState.players.find(player => player.is_human) : null;

  return (
    <div className="poker-table-container">
      <div className="table-header">
        <GameSettings 
          gameInfo={{
            gameId: gameId,
            playerCount: gameState.players ? gameState.players.length : 0,
            smallBlind: gameState.smallBlind,
            bigBlind: gameState.bigBlind,
            ante: 0,
            startingStack: humanPlayer ? humanPlayer.stack + humanPlayer.current_bet : 1000,
            handNumber: 1
          }}
          onEndGame={onEndGame}
        />
        
        <div className="table-status">
          {error ? (
            <div className="error-message">
              <AlertTriangle size={18} />
              <span>{error}</span>
            </div>
          ) : loading ? (
            <div className="waiting-message">
              <Clock size={18} />
              <span>Waiting for other players...</span>
            </div>
          ) : null}
        </div>
      </div>
      
      <div className="table-layout">
        <div className="left-sidebar">
          <HandStrength {...calculateHandStrength()} />
          
          <div className="game-info">
            <BettingRound round={getBettingRound()} />
            
            <div className="blinds-info">
              <div className="blind-item">
                <span className="blind-label">Small Blind</span>
                <span className="blind-value">
                  <DollarSign size={14} />
                  {gameState.smallBlind && gameState.smallBlind.toFixed(2)}
                </span>
              </div>
              <div className="blind-item">
                <span className="blind-label">Big Blind</span>
                <span className="blind-value">
                  <DollarSign size={14} />
                  {gameState.bigBlind && gameState.bigBlind.toFixed(2)}
                </span>
              </div>
            </div>
            
            <div className="hand-info">
              <span className="hand-label">
                <RotateCcw size={14} />
                Hand #1
              </span>
            </div>
          </div>
        </div>
        
        <div className="poker-table">
          {/* Render player seats */}
          {gameState.players && gameState.players.map((player, index) => {
            const position = getPlayerPosition(index, gameState.players.length);
            
            return (
              <div 
                key={player.id} 
                className="player-position"
                style={position}
              >
                <PlayerSeat 
                  player={player}
                  isDealer={false}
                  isSmallBlind={false}
                  isBigBlind={false}
                  isActive={player.is_current}
                  isWinner={false}
                  showCards={player.is_human || gameState.betting_round === 'SHOWDOWN'}
                />
              </div>
            );
          })}
          
          {/* Community cards */}
          <div className="community-cards">
            {gameState.community_cards && gameState.community_cards.map((card, index) => (
              <Card key={index} card={card} />
            ))}
          </div>
          
          {/* Pot display */}
          <div className="pot-display-container">
            <PotDisplay 
              mainPot={gameState.pot || 0}
            />
          </div>
        </div>
        
        <div className="right-sidebar">
          <GameLog log={gameLog} />
        </div>
      </div>
      
      <div className="table-footer">
        {/* Action controls for human player */}
        {gameState.is_human_turn && (
          <ActionControls 
            validActions={gameState.valid_actions || []}
            onAction={handleAction}
            currentBet={gameState.current_bet || 0}
            minRaise={gameState.min_raise || 0}
            playerStack={humanPlayer ? humanPlayer.stack : 0}
            isLoading={isLoading}
          />
        )}
      </div>
      
      {/* Hand result modal */}
      {showHandResult && (
        <HandResult 
          result={handResult}
          onClose={closeHandResult}
        />
      )}
    </div>
  );
}

export default PokerTable;
