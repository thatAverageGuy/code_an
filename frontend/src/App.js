import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/layout/Dashboard';
import FileUploader from './components/upload/FileUploader';
import GithubImporter from './components/upload/GithubImporter';
import AnalysisResults from './components/analysis/AnalysisResults';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import './styles.css';

function App() {
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalysisComplete = (results) => {
    setAnalysisResults(results);
    setIsLoading(false);
    setError(null);
  };

  const handleAnalysisError = (err) => {
    setError(err.message || 'An error occurred during analysis');
    setIsLoading(false);
  };

  const handleLoading = (loading) => {
    setIsLoading(loading);
    if (loading) {
      setError(null);
    }
  };

  return (
    <Router>
      <div className="app-container">
        <Header />
        <main className="main-content">
          <Routes>
            <Route
              path="/"
              element={
                <Dashboard
                  isLoading={isLoading}
                  error={error}
                >
                  <div className="upload-section">
                    <FileUploader
                      onAnalysisComplete={handleAnalysisComplete}
                      onAnalysisError={handleAnalysisError}
                      onLoading={handleLoading}
                    />
                    <div className="divider">OR</div>
                    <GithubImporter
                      onAnalysisComplete={handleAnalysisComplete}
                      onAnalysisError={handleAnalysisError}
                      onLoading={handleLoading}
                    />
                  </div>
                  {analysisResults && (
                    <AnalysisResults results={analysisResults} />
                  )}
                </Dashboard>
              }
            />
            <Route
              path="/results"
              element={
                analysisResults ? (
                  <AnalysisResults results={analysisResults} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;