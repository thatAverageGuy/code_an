import React, { useState, useEffect } from 'react';
import { getVisualization } from '../../services/api';
import Loader from '../common/Loader';

const Visualization = ({ visualizations }) => {
  const [selectedVisualization, setSelectedVisualization] = useState(null);
  const [visualizationData, setVisualizationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (visualizations && visualizations.length > 0) {
      setSelectedVisualization(visualizations[0]);
    }
  }, [visualizations]);

  useEffect(() => {
    const fetchVisualization = async () => {
      if (!selectedVisualization) return;

      setLoading(true);
      setError(null);

      try {
        const data = await getVisualization(selectedVisualization.url);
        setVisualizationData(data);
      } catch (err) {
        console.error('Error fetching visualization:', err);
        setError('Failed to load visualization. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchVisualization();
  }, [selectedVisualization]);

  if (!visualizations || visualizations.length === 0) {
    return <div className="no-data">No visualizations available</div>;
  }

  const renderD3Visualization = (data) => {
    // In a real implementation, we would use D3.js to render this data
    return (
      <div className="d3-visualization">
        <p>Interactive D3 visualization would be rendered here</p>
        <pre className="json-preview">{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  const renderNetworkXVisualization = (data) => {
    // For NetworkX, we'll just display the image
    if (data instanceof Blob) {
      const imageUrl = URL.createObjectURL(data);
      return (
        <div className="networkx-visualization">
          <img 
            src={imageUrl} 
            alt="Code dependency graph" 
            className="visualization-image" 
          />
        </div>
      );
    }
    return <div className="error">Invalid visualization data</div>;
  };

  return (
    <div className="visualization-container">
      <div className="visualization-controls">
        <select
          value={selectedVisualization ? selectedVisualization.url : ''}
          onChange={(e) => {
            const selected = visualizations.find(v => v.url === e.target.value);
            setSelectedVisualization(selected);
          }}
        >
          {visualizations.map((viz) => (
            <option key={viz.url} value={viz.url}>
              {viz.format.charAt(0).toUpperCase() + viz.format.slice(1)} Visualization
            </option>
          ))}
        </select>
      </div>
      
      <div className="visualization-display">
        {loading ? (
          <Loader message="Loading visualization..." />
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : visualizationData ? (
          selectedVisualization.format === 'd3' ? (
            renderD3Visualization(visualizationData)
          ) : (
            renderNetworkXVisualization(visualizationData)
          )
        ) : (
          <div className="no-data">Select a visualization to display</div>
        )}
      </div>
    </div>