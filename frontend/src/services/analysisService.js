import { getVisualization, deleteVisualization } from './api';

export const processAnalysisResults = (results) => {
  // Format and process the raw results from API
  return {
    ...results,
    timestamp: new Date(results.timestamp),
    formattedData: formatDataForUI(results)
  };
};

export const loadVisualization = async (visualizationUrl) => {
  try {
    return await getVisualization(visualizationUrl);
  } catch (error) {
    console.error('Error loading visualization:', error);
    throw error;
  }
};

export const removeVisualization = async (visualizationUrl) => {
  try {
    return await deleteVisualization(visualizationUrl);
  } catch (error) {
    console.error('Error removing visualization:', error);
    throw error;
  }
};

// Helper functions
const formatDataForUI = (results) => {
  // Transform data structure for easier use in UI components
  const structure = results.structure || {};
  
  // Calculate statistics
  const stats = {
    totalClasses: 0,
    totalFunctions: 0,
    totalImports: 0,
    filesWithErrors: 0
  };
  
  Object.values(structure).forEach(file => {
    stats.totalClasses += Object.keys(file.classes || {}).length;
    stats.totalFunctions += Object.keys(file.functions || {}).length;
    stats.totalImports += Object.keys(file.imports || {}).length;
    stats.filesWithErrors += file.errors && file.errors.length > 0 ? 1 : 0;
  });
  
  return {
    stats,
    fileCount: results.files_analyzed
  };
};

