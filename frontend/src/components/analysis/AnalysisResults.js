import React, { useState } from 'react';
import CodeStructure from './CodeStructure';
import Visualization from './Visualization';

const AnalysisResults = ({ results }) => {
  const [activeTab, setActiveTab] = useState('structure');

  if (!results) {
    return <div className="no-results">No analysis results available</div>;
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="analysis-results">
      <div className="results-header">
        <h2>Analysis Results</h2>
        <div className="project-info">
          <p><strong>Project ID:</strong> {results.project_id}</p>
          <p><strong>Files Analyzed:</strong> {results.files_analyzed}</p>
          <p><strong>Timestamp:</strong> {formatTimestamp(results.timestamp)}</p>
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'structure' ? 'active' : ''}`}
          onClick={() => setActiveTab('structure')}
        >
          Code Structure
        </button>
        <button
          className={`tab-button ${activeTab === 'visualization' ? 'active' : ''}`}
          onClick={() => setActiveTab('visualization')}
        >
          Visualization
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'structure' && (
          <CodeStructure structure={results.structure} />
        )}
        {activeTab === 'visualization' && (
          <Visualization rawData={results.raw_data} />
        )}
      </div>
    </div>
  );
};

export default AnalysisResults;