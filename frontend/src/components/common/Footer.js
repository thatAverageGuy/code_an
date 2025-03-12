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