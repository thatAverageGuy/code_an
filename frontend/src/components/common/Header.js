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
              <a href="https://github.com/Shikha-code36/code_analyzer" target="_blank" rel="noopener noreferrer">
                Source Code
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;