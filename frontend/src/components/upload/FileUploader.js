import React, { useState, useRef } from 'react';
import { uploadProject } from '../../services/api';

const FileUploader = ({ onAnalysisComplete, onAnalysisError, onLoading }) => {
  const [file, setFile] = useState(null);
  const [useLLM, setUseLLM] = useState(false);
  const [visualizationType, setVisualizationType] = useState('networkx');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.zip')) {
      setFile(selectedFile);
    } else {
      setFile(null);
      alert('Please select a valid ZIP file');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.zip')) {
        setFile(droppedFile);
      } else {
        alert('Please drop a valid ZIP file');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      alert('Please select a ZIP file first');
      return;
    }

    try {
      onLoading(true);
      
      const options = {
        use_llm: useLLM,
        visualization_type: visualizationType
      };
      
      const results = await uploadProject(file, options);
      onAnalysisComplete(results);
    } catch (error) {
      onAnalysisError(error);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="file-uploader">
      <h2>Upload Project ZIP</h2>
      <form onSubmit={handleSubmit}>
        <div
          className="drop-area"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={triggerFileInput}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".zip"
            style={{ display: 'none' }}
          />
          {file ? (
            <div className="file-info">
              <p>Selected file: {file.name}</p>
              <p>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <p>Drag and drop a ZIP file here, or click to browse</p>
          )}
        </div>

        <div className="options">
          <label>
            <input
              type="checkbox"
              checked={useLLM}
              onChange={(e) => setUseLLM(e.target.checked)}
            />
            Use LLM for enhanced analysis
          </label>
          
          <div className="select-container">
            <label>Visualization Type:</label>
            <select
              value={visualizationType}
              onChange={(e) => setVisualizationType(e.target.value)}
            >
              <option value="networkx">NetworkX</option>
              <option value="d3">D3.js</option>
            </select>
          </div>
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={!file}
        >
          Analyze Project
        </button>
      </form>
    </div>
  );
};

export default FileUploader;