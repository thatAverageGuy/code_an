import React, { useState } from 'react';

const CodeStructure = ({ structure }) => {
  const [expandedFiles, setExpandedFiles] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  if (!structure || Object.keys(structure).length === 0) {
    return <div className="no-data">No structure data available</div>;
  }

  const toggleFile = (filePath) => {
    setExpandedFiles((prev) => ({
      ...prev,
      [filePath]: !prev[filePath],
    }));
  };

  const handleSearch = (e) => {
    setSearchQuery(e.target.value.toLowerCase());
  };

  const handleFilterChange = (e) => {
    setFilterType(e.target.value);
  };

  const getFileTypeIcon = (filePath) => {
    
    // Return appropriate icon based on file type
    if (filePath.endsWith('.py')) return '🐍';
    if (filePath.endsWith('.js') || filePath.endsWith('.jsx')) return '📜';
    if (filePath.endsWith('.html')) return '🌐';
    if (filePath.endsWith('.css')) return '🎨';
    if (filePath.endsWith('.md')) return '📝';
    if (filePath.endsWith('.json')) return '⚙️';
    if (filePath.endsWith('.gitignore') || filePath.includes('.git/')) return '📎';
    if (filePath.endsWith('.txt')) return '📄';
    if (filePath.endsWith('.sql') || filePath.includes('mydb') || filePath.includes('.db')) return '🗄️';
    if (filePath.endsWith('.cnf') || filePath.endsWith('.conf') || filePath.endsWith('.config') || filePath.endsWith('.ini')) return '⚙️';
    
    // Default icon
    return '📁';
  };

  const filteredFiles = Object.entries(structure).filter(([filePath, fileData]) => {
    const matchesSearch = filePath.toLowerCase().includes(searchQuery);
    
    if (filterType === 'all') return matchesSearch;
    if (filterType === 'classes' && Object.keys(fileData.classes).length > 0) return matchesSearch;
    if (filterType === 'functions' && Object.keys(fileData.functions).length > 0) return matchesSearch;
    if (filterType === 'imports' && Object.keys(fileData.imports).length > 0) return matchesSearch;
    if (filterType === 'errors' && fileData.errors && fileData.errors.length > 0) return matchesSearch;
    if (filterType === 'config' && (filePath.endsWith('.cnf') || filePath.endsWith('.conf') || filePath.includes('.git'))) return matchesSearch;
    if (filterType === 'database' && (filePath.includes('db') || filePath.endsWith('.sql'))) return matchesSearch;
    
    return false;
  });

  return (
    <div className="code-structure">
      <div className="filter-controls">
        <input
          type="text"
          placeholder="Search files..."
          value={searchQuery}
          onChange={handleSearch}
          className="search-input"
        />
        
        <select 
          value={filterType} 
          onChange={handleFilterChange}
          className="filter-select"
        >
          <option value="all">All Files</option>
          <option value="classes">Files with Classes</option>
          <option value="functions">Files with Functions</option>
          <option value="imports">Files with Imports</option>
          <option value="config">Configuration Files</option>
          <option value="database">Database Files</option>
          <option value="errors">Files with Errors</option>
        </select>
      </div>

      <div className="file-list">
        {filteredFiles.map(([filePath, fileData]) => (
          <div key={filePath} className="file-item">
            <div 
              className="file-header" 
              onClick={() => toggleFile(filePath)}
            >
              <span className={`file-toggle ${expandedFiles[filePath] ? 'open' : ''}`}>
                {expandedFiles[filePath] ? '▼' : '►'}
              </span>
              <span className="file-icon">{getFileTypeIcon(filePath)}</span>
              <span className="file-path">{filePath}</span>
              <div className="file-stats">
                <span>{Object.keys(fileData.classes).length} classes</span>
                <span>{Object.keys(fileData.functions).length} functions</span>
                <span>{Object.keys(fileData.imports).length} imports</span>
                {fileData.errors && <span className="error-badge">{fileData.errors.length} errors</span>}
              </div>
            </div>
            
            {expandedFiles[filePath] && (
              <div className="file-details">
                {/* File Summary Section */}
                {fileData.summary && (
                  <div className="section summary-section">
                    <h4>Summary</h4>
                    <div className="summary-content">
                      {fileData.summary}
                    </div>
                  </div>
                )}
              
                {fileData.errors && fileData.errors.length > 0 && (
                  <div className="section errors-section">
                    <h4>Errors</h4>
                    <ul className="error-list">
                      {fileData.errors.map((error, idx) => (
                        <li key={idx} className="error-item">{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {Object.keys(fileData.imports).length > 0 && (
                  <div className="section imports-section">
                    <h4>Imports</h4>
                    <ul className="import-list">
                      {Object.entries(fileData.imports).map(([name, source]) => (
                        <li key={name} className="import-item">
                          <span className="import-name">{name}</span> from <span className="import-source">{source}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {Object.keys(fileData.classes).length > 0 && (
                  <div className="section classes-section">
                    <h4>Classes</h4>
                    <ul className="class-list">
                      {Object.entries(fileData.classes).map(([className, classData]) => (
                        <li key={className} className="class-item">
                          <div className="class-header">
                            <span className="class-name">{className}</span>
                            {classData.bases.length > 0 && (
                              <span className="class-bases">
                                extends {classData.bases.join(', ')}
                              </span>
                            )}
                          </div>
                          {classData.methods.length > 0 && (
                            <div className="class-methods">
                              <h5>Methods:</h5>
                              <ul>
                                {classData.methods.map((method) => (
                                  <li key={method}>{method}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {Object.keys(fileData.functions).length > 0 && (
                  <div className="section functions-section">
                    <h4>Functions</h4>
                    <ul className="function-list">
                      {Object.entries(fileData.functions).map(([funcName, funcData]) => (
                        <li key={funcName} className="function-item">
                          <div className="function-header">
                            <span className="function-name">{funcName}</span>
                            <span className="function-params">({funcData.args.join(', ')})</span>
                          </div>
                          {funcData.calls.length > 0 && (
                            <div className="function-calls">
                              <h5>Calls:</h5>
                              <ul>
                                {funcData.calls.map((call, idx) => (
                                  <li key={`${call}-${idx}`}>{call}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        
        {filteredFiles.length === 0 && (
          <div className="no-matches">
            No files match your search criteria
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeStructure;