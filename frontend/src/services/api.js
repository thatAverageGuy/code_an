// API service for communicating with the backend
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const uploadProject = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Error uploading project');
  }

  return response.json();
};

export const analyzeGithubRepo = async (githubUrl, options = { branch: 'main' }) => {
  const response = await fetch(`${API_URL}/github`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      github_url: githubUrl,
      branch: options.branch,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Error analyzing GitHub repository');
  }

  return response.json();
};

export const getVisualization = async (visualizationUrl) => {
  const response = await fetch(`${API_URL}${visualizationUrl.substring(4)}`);
  
  if (!response.ok) {
    throw new Error('Error fetching visualization');
  }
  
  const contentType = response.headers.get('content-type');
  
  if (contentType.includes('json')) {
    return response.json();
  } else {
    return response.blob();
  }
};

export const deleteVisualization = async (visualizationUrl) => {
  const response = await fetch(`${API_URL}${visualizationUrl.substring(4)}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Error deleting visualization');
  }

  return response.json();
};