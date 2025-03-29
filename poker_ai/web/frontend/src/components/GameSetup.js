import React, { useState } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { API_URL } from '../Config';

const SetupContainer = styled.div`
  background-color: #16213e;
  border-radius: 10px;
  padding: 30px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
`;

const Title = styled.h2`
  color: #e94560;
  margin-bottom: 20px;
  text-align: center;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  margin-bottom: 5px;
  font-size: 1rem;
  color: #e2e2e2;
`;

const Input = styled.input`
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #0f3460;
  background-color: #0f3460;
  color: #ffffff;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #e94560;
  }
`;

const Checkbox = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  
  input {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }
`;

const Button = styled.button`
  padding: 12px;
  border-radius: 5px;
  border: none;
  background-color: #e94560;
  color: white;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
  
  &:hover {
    background-color: #d13354;
  }
  
  &:disabled {
    background-color: #7a7a7a;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #e94560;
  margin-top: 10px;
  text-align: center;
`;

function GameSetup({ onGameCreated }) {
  const [formData, setFormData] = useState({
    num_ai_players: 2,
    starting_stack: 1000,
    small_blind: 5,
    big_blind: 10,
    ante: 0,
    advanced_ai: false
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/game/new`, formData);
      onGameCreated(response.data);
    } catch (err) {
      console.error('Error creating game:', err);
      setError('Failed to create game. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <SetupContainer>
      <Title>Game Setup</Title>
      
      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="num_ai_players">Number of AI Players</Label>
          <Input
            type="number"
            id="num_ai_players"
            name="num_ai_players"
            min="1"
            max="8"
            value={formData.num_ai_players}
            onChange={handleChange}
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="starting_stack">Starting Stack</Label>
          <Input
            type="number"
            id="starting_stack"
            name="starting_stack"
            min="100"
            step="100"
            value={formData.starting_stack}
            onChange={handleChange}
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="small_blind">Small Blind</Label>
          <Input
            type="number"
            id="small_blind"
            name="small_blind"
            min="1"
            step="1"
            value={formData.small_blind}
            onChange={handleChange}
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="big_blind">Big Blind</Label>
          <Input
            type="number"
            id="big_blind"
            name="big_blind"
            min="2"
            step="1"
            value={formData.big_blind}
            onChange={handleChange}
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="ante">Ante (Optional)</Label>
          <Input
            type="number"
            id="ante"
            name="ante"
            min="0"
            step="1"
            value={formData.ante}
            onChange={handleChange}
          />
        </FormGroup>
        
        <Checkbox>
          <input
            type="checkbox"
            id="advanced_ai"
            name="advanced_ai"
            checked={formData.advanced_ai}
            onChange={handleChange}
          />
          <Label htmlFor="advanced_ai">Use Advanced AI Players</Label>
        </Checkbox>
        
        <Button type="submit" disabled={loading}>
          {loading ? 'Creating Game...' : 'Start Game'}
        </Button>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
      </Form>
    </SetupContainer>
  );
}

export default GameSetup;
