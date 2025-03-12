import React from 'react';
import Loader from '../common/Loader';

const Dashboard = ({ children, isLoading, error }) => {
  return (
    <div className="dashboard">
      <div className="container">
        <h1>Code Structure Analyzer</h1>
        <p className="subtitle">Analyze your project's code structure and dependencies</p>
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {isLoading ? (
          <Loader message="Analyzing your code. This may take a few moments..." />
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default Dashboard;