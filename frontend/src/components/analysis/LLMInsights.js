import React, { useState } from 'react';

const LLMInsights = ({ llmAnalysis }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  if (!llmAnalysis || Object.keys(llmAnalysis).length === 0) {
    return <div className="no-data">No LLM analysis data available</div>;
  }

  const handleSearch = (e) => {
    setSearchQuery(e.target.value.toLowerCase());
  };

  const filteredFiles = Object.keys(llmAnalysis).filter(
    (filePath) => filePath.toLowerCase().includes(searchQuery)
  );

  const getAverageQualityScore = () => {
    const scores = Object.values(llmAnalysis)
      .filter(analysis => typeof analysis.quality_score === 'number')
      .map(analysis => analysis.quality_score);
    
    if (scores.length === 0) return 'N/A';
    
    const avg = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    return avg.toFixed(1);
  };

  const getTotalIssues = () => {
    let bugCount = 0;
    let suggestionCount = 0;
    
    Object.values(llmAnalysis).forEach(analysis => {
      if (Array.isArray(analysis.bugs)) {
        bugCount += analysis.bugs.length;
      }
      if (Array.isArray(analysis.suggestions)) {
        suggestionCount += analysis.suggestions.length;
      }
    });
    
    return { bugCount, suggestionCount };
  };

  const { bugCount, suggestionCount } = getTotalIssues();

  return (
    <div className="llm-insights">
      <div className="summary-stats">
        <div className="stat-card">
          <h3>Average Quality</h3>
          <div className="stat-value">{getAverageQualityScore()}/10</div>
        </div>
        <div className="stat-card">
          <h3>Potential Issues</h3>
          <div className="stat-value">{bugCount}</div>
        </div>
        <div className="stat-card">
          <h3>Suggestions</h3>
          <div className="stat-value">{suggestionCount}</div>
        </div>
      </div>

      <div className="file-filter">
        <input
          type="text"
          placeholder="Search files..."
          value={searchQuery}
          onChange={handleSearch}
          className="search-input"
        />
      </div>

      <div className="file-insights">
        <div className="file-list">
          {filteredFiles.length > 0 ? (
            filteredFiles.map((filePath) => (
              <div
                key={filePath}
                className={`file-item ${selectedFile === filePath ? 'selected' : ''}`}
                onClick={() => setSelectedFile(filePath)}
              >
                <div className="file-name">{filePath.split('/').pop()}</div>
                <div className="file-path">{filePath}</div>
                <div className="file-score">
                  Score: {llmAnalysis[filePath].quality_score || 'N/A'}
                </div>
              </div>
            ))
          ) : (
            <div className="no-matches">No files match your search</div>
          )}
        </div>

        <div className="insight-details">
          {selectedFile ? (
            <div className="selected-file-insights">
              <h3>{selectedFile.split('/').pop()}</h3>
              
              <div className="quality-score">
                <h4>Quality Score</h4>
                <div className="score-display">
                  <div 
                    className="score-bar" 
                    style={{ 
                      width: `${(llmAnalysis[selectedFile].quality_score || 0) * 10}%`,
                      backgroundColor: getScoreColor(llmAnalysis[selectedFile].quality_score)
                    }}
                  >
                    {llmAnalysis[selectedFile].quality_score || 0}/10
                  </div>
                </div>
              </div>
              
              <div className="bugs-section">
                <h4>Potential Issues</h4>
                {llmAnalysis[selectedFile].bugs && llmAnalysis[selectedFile].bugs.length > 0 ? (
                  <ul className="bugs-list">
                    {llmAnalysis[selectedFile].bugs.map((bug, idx) => (
                      <li key={idx} className="bug-item">{bug}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty-list">No issues detected</p>
                )}
              </div>
              
              <div className="suggestions-section">
                <h4>Suggestions</h4>
                {llmAnalysis[selectedFile].suggestions && llmAnalysis[selectedFile].suggestions.length > 0 ? (
                  <ul className="suggestions-list">
                    {llmAnalysis[selectedFile].suggestions.map((suggestion, idx) => (
                      <li key={idx} className="suggestion-item">{suggestion}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="empty-list">No suggestions provided</p>
                )}
              </div>
            </div>
          ) : (
            <div className="no-selection">
              <p>Select a file to view LLM insights</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Helper function to get color based on score
const getScoreColor = (score) => {
  if (!score) return '#cccccc';
  if (score >= 8) return '#4caf50'; // Green
  if (score >= 6) return '#ffb74d'; // Orange
  return '#f44336'; // Red
};

export default LLMInsights;