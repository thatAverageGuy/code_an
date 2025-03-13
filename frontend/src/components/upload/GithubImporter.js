import React, { useState } from 'react';
import { analyzeGithubRepo } from '../../services/api';

const GithubImporter = ({ onAnalysisComplete, onAnalysisError, onLoading }) => {
  const [githubUrl, setGithubUrl] = useState('');
  const [branch, setBranch] = useState('main');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!githubUrl || !githubUrl.includes('github.com')) {
      alert('Please enter a valid GitHub URL');
      return;
    }

    try {
      onLoading(true);
      
      const options = {
        branch: branch
      };
      
      const results = await analyzeGithubRepo(githubUrl, options);
      onAnalysisComplete(results);
    } catch (error) {
      onAnalysisError(error);
    }
  };

  return (
    <div className="github-importer">
      <h2>GitHub Repository</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="github-url">GitHub URL:</label>
          <input
            type="url"
            id="github-url"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
            placeholder="https://github.com/username/repository"
            required
          />
        </div>
        
        <div className="input-group">
          <label htmlFor="branch">Branch:</label>
          <input
            type="text"
            id="branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="main"
          />
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={!githubUrl}
        >
          Analyze Repository
        </button>
      </form>
    </div>
  );
};

export default GithubImporter;