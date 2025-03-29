import React, { useState } from 'react';
import axios from 'axios';
import './GameSetup.css';

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
      const response = await axios.post('/api/game/new', formData);
      onGameCreated(response.data);
    } catch (err) {
      console.error('Error creating game:', err);
      setError('Failed to create game. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="setup-container">
      <h2 className="setup-title">Game Setup</h2>
      
      <form className="setup-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="num_ai_players">Number of AI Players</label>
          <input
            type="number"
            id="num_ai_players"
            name="num_ai_players"
            min="1"
            max="8"
            value={formData.num_ai_players}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="starting_stack">Starting Stack</label>
          <input
            type="number"
            id="starting_stack"
            name="starting_stack"
            min="100"
            step="100"
            value={formData.starting_stack}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="small_blind">Small Blind</label>
          <input
            type="number"
            id="small_blind"
            name="small_blind"
            min="1"
            step="1"
            value={formData.small_blind}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="big_blind">Big Blind</label>
          <input
            type="number"
            id="big_blind"
            name="big_blind"
            min="2"
            step="1"
            value={formData.big_blind}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="ante">Ante (Optional)</label>
          <input
            type="number"
            id="ante"
            name="ante"
            min="0"
            step="1"
            value={formData.ante}
            onChange={handleChange}
          />
        </div>
        
        <div className="checkbox-group">
          <input
            type="checkbox"
            id="advanced_ai"
            name="advanced_ai"
            checked={formData.advanced_ai}
            onChange={handleChange}
          />
          <label htmlFor="advanced_ai">Use Advanced AI Players</label>
        </div>
        
        <button 
          type="submit" 
          className="submit-button" 
          disabled={loading}
        >
          {loading ? 'Creating Game...' : 'Start Game'}
        </button>
        
        {error && <div className="error-message">{error}</div>}
      </form>
    </div>
  );
}

export default GameSetup;
