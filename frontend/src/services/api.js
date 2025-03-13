// API service for communicating with the backend
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Function to convert File object to base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Extract the base64 string (remove the data:application/zip;base64, prefix)
      let base64String = reader.result;
      if (base64String.includes(',')) {
        base64String = base64String.split(',')[1];
      }
      resolve(base64String);
    };
    reader.onerror = (error) => {
      reject(error);
    };
  });
};

export const uploadProject = async (file, options = { visualization_type: 'networkx' }) => {
  try {
    // Convert file to base64
    const base64Content = await fileToBase64(file);
    
    // Create the request payload
    const payload = {
      file_content: base64Content,
      file_name: file.name,
      visualization_type: options.visualization_type || 'networkx'
    };
    
    // Send the request
    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error uploading project');
    }

    return response.json();
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
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
      visualization_type: options.visualization_type || 'networkx',
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