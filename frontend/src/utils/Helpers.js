export const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'Unknown';
  const date = new Date(timestamp);
  return date.toLocaleString();
};

export const getFileExtension = (filePath) => {
  if (!filePath) return '';
  return filePath.split('.').pop().toLowerCase();
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const calculateAverageScore = (llmAnalysis) => {
  if (!llmAnalysis) return 0;
  
  const scores = Object.values(llmAnalysis)
    .filter(analysis => analysis && typeof analysis.quality_score === 'number')
    .map(analysis => analysis.quality_score);
  
  if (scores.length === 0) return 0;
  return scores.reduce((sum, score) => sum + score, 0) / scores.length;
};

export const getScoreColor = (score) => {
  if (!score) return '#cccccc';
  if (score >= 8) return '#4caf50'; // Green
  if (score >= 6) return '#ffb74d'; // Orange
  return '#f44336'; // Red
};