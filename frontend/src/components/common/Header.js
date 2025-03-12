// src/components/common/Header.js
import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="app-header">
      <div className="container">
        <Link to="/" className="logo">
          <h1>Code Analyzer</h1>
        </Link>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <a href="https://github.com/yourusername/code-analyzer" target="_blank" rel="noopener noreferrer">
                GitHub
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;

// src/components/common/Footer.js
import React from 'react';

const Footer = () => {
  return (
    <footer className="app-footer">
      <div className="container">
        <p>&copy; {new Date().getFullYear()} Code Analyzer. MIT License.</p>
      </div>
    </footer>
  );
};

export default Footer;

// src/components/common/Loader.js
import React from 'react';

const Loader = ({ message = 'Loading...' }) => {
  return (
    <div className="loader-container">
      <div className="loader"></div>
      <p className="loader-message">{message}</p>
    </div>
  );
};

export default Loader;

// src/components/layout/Dashboard.js
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