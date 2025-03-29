import React from 'react';
import './PositionMarker.css';

function PositionMarker({ type }) {
  const getMarkerText = () => {
    switch (type) {
      case 'dealer':
        return 'D';
      case 'small_blind':
        return 'SB';
      case 'big_blind':
        return 'BB';
      default:
        return '';
    }
  };

  return (
    <div className={`position-marker ${type}`}>
      {getMarkerText()}
    </div>
  );
}

export default PositionMarker;
