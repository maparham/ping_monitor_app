import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = 'Loading...', 
  size = 'medium' 
}) => {
  const sizeClass = `spinner-${size}`;
  
  return (
    <div className="loading-container">
      <div className={`spinner ${sizeClass}`}></div>
      <p className="loading-text">{message}</p>
    </div>
  );
};

export default LoadingSpinner; 