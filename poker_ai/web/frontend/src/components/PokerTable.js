import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import io from 'socket.io-client';
import Card from './Card';
import PlayerSeat from './PlayerSeat';
import ActionControls from './ActionControls';
import GameLog from './GameLog';
import { API_URL } from '../Config';

const TableContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
`;

const GameInfo = styled.div`
  background-color: #16213e;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
`;

const InfoItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const InfoLabel = styled.span`
  font-size: 0.9rem;
  color: #e2e2e2;
  margin-bottom: 5px;
`;

const InfoValue = styled.span`
  font-size: 1.2rem;
  font-weight: bold;
  color: #e94560;
`;

const Table = styled.div`
  position: relative;
  background-color: #0f3460;
  border-radius: 200px;
  height: 400px;
  margin: 50px auto;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 50px rgba(0, 0, 0, 0.3);
  border: 15px solid #16213e;
`;

const CommunityCards = styled.div`
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
`;

const PotInfo = styled.div`
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(22, 33, 62, 0.8);
  padding: 10px 20px;
  border-radius: 20px;
  text-align: center;
`;

const PotValue = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #e94560;
`;

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

const GameControls = styled.div`
  margin-top: 20px;
`;

const FlexContainer = styled.div`
  display: flex;
  gap: 20px;
  margin-top: 20px;
`;

const LeftPanel = styled.div`
  flex: 1;
`;

const RightPanel = styled.div`
  flex: 1;
  background-color: #16213e;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  max-height: 400px;
  overflow-y: auto;
`;

function PokerTable({ gameId, humanPlayerId, gameState, onGameStateUpdated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [socket, setSocket] = useState(null);
  const [gameLog, setGameLog] = useState([]);

  // Initialize socket connection
  useEffect(() => {
    // const newSocket = io('http://localhost:5001');
    const newSocket = io(API_URL);
    
    newSocket.on('connect', () => {
      console.log('Connected to server');
    });
    
    newSocket.on('ai_action', (data) => {
      console.log('AI action:', data);
      // Add to game log
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

  const fetchGameState = async () => {
    try {
      const response = await axios.get(`${API_URL}/game/${gameId}/state`);
      onGameStateUpdated(response.data.state);
    } catch (err) {
      console.error('Error fetching game state:', err);
      setError('Failed to fetch game state');
    }
  };

  const handleAction = async (actionType, amount = 0) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/game/${gameId}/action`, {
        action_type: actionType,
        amount: amount
      });
      
      onGameStateUpdated(response.data.state);
      
      // Add to game log
      setGameLog(prevLog => [...prevLog, {
        type: 'action',
        playerName: 'You',
        action: actionType,
        amount: amount
      }]);
    } catch (err) {
      console.error('Error performing action:', err);
      setError('Failed to perform action');
    } finally {
      setLoading(false);
    }
  };

  // Find the human player
  const humanPlayer = gameState.players.find(player => player.is_human);
  
  // Organize players for display
  const organizedPlayers = [];
  
  // Find the button position
  const buttonPlayer = gameState.players.find(player => player.position === 0);
  const buttonPos = buttonPlayer ? gameState.players.indexOf(buttonPlayer) : 0;
  
  // Start with the button player and go around the table
  for (let i = 0; i < gameState.players.length; i++) {
    const playerIndex = (buttonPos + i) % gameState.players.length;
    organizedPlayers.push(gameState.players[playerIndex]);
  }
  
  // Move the human player to the bottom position
  const humanIndex = organizedPlayers.findIndex(player => player.is_human);
  if (humanIndex !== -1) {
    const human = organizedPlayers.splice(humanIndex, 1)[0];
    organizedPlayers.splice(6, 0, human); // Position 6 is bottom
  }

  return (
    <TableContainer>
      <GameInfo>
        <InfoItem>
          <InfoLabel>Betting Round</InfoLabel>
          <InfoValue>{gameState.betting_round}</InfoValue>
        </InfoItem>
        <InfoItem>
          <InfoLabel>Small Blind</InfoLabel>
          <InfoValue>${gameState.players.find(p => p.position === 1)?.current_bet || 0}</InfoValue>
        </InfoItem>
        <InfoItem>
          <InfoLabel>Big Blind</InfoLabel>
          <InfoValue>${gameState.players.find(p => p.position === 2)?.current_bet || 0}</InfoValue>
        </InfoItem>
        <InfoItem>
          <InfoLabel>Current Bet</InfoLabel>
          <InfoValue>${gameState.current_bet}</InfoValue>
        </InfoItem>
      </GameInfo>
      
      <Table>
        <PotInfo>
          <InfoLabel>Pot</InfoLabel>
          <PotValue>${gameState.pot}</PotValue>
        </PotInfo>
        
        {organizedPlayers.map((player, index) => (
          <PlayerSeat
            key={player.id}
            player={player}
            position={PlayerPositions[index]}
            isButton={player.position === 0}
            isSmallBlind={player.position === 1}
            isBigBlind={player.position === 2}
            isCurrentPlayer={player.is_current}
          />
        ))}
      </Table>
      
      <CommunityCards>
        {gameState.community_cards.length > 0 ? (
          gameState.community_cards.map((card, index) => (
            <Card key={index} card={card} />
          ))
        ) : (
          <InfoValue>No community cards yet</InfoValue>
        )}
      </CommunityCards>
      
      <FlexContainer>
        <LeftPanel>
          {gameState.is_human_turn && (
            <GameControls>
              <ActionControls
                validActions={gameState.valid_actions}
                onAction={handleAction}
                loading={loading}
                playerStack={humanPlayer.stack}
              />
            </GameControls>
          )}
        </LeftPanel>
        
        <RightPanel>
          <GameLog log={gameLog} />
        </RightPanel>
      </FlexContainer>
      
      {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
    </TableContainer>
  );
}

export default PokerTable;
