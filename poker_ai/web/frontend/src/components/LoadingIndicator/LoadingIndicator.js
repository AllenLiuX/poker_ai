import React from 'react';
import './LoadingIndicator.css';

function LoadingIndicator({ message = 'Loading...' }) {
  return (
    <div className="loading-indicator">
      <div className="spinner"></div>
      <p className="loading-message">{message}</p>
    </div>
  );
}

export default LoadingIndicator;
