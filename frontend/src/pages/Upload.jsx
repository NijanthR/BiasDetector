/**
 * Upload Page - For uploading new datasets
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size > 100 * 1024 * 1024) {
        setError('File size exceeds 100MB limit');
        return;
      }
      setFile(selectedFile);
      setName(selectedFile.name.split('.')[0]);
      setError(null);
    }
  };

  const [statusMessage, setStatusMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setStatusMessage('Uploading dataset and preparing agents...');
      
      const response = await datasetAPI.upload(file, name || file.name);
      
      setStatusMessage('Upload successful! Redirecting to dashboard...');
      // Redirect to dashboard after successful upload
      setTimeout(() => {
        navigate('/');
      }, 1200);
    } catch (err) {
      const errorMsg = 
        err.response?.data?.detail || 
        err.response?.data?.error || 
        (err.code === 'ECONNABORTED' ? 'Server timed out. Render backend may still be waking up. Please try again.' : null) ||
        err.message || 
        'Upload failed. Please check server connection.';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      console.error('Upload Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-container">
        <h1>Upload Dataset</h1>
        <p>Upload your dataset for automatic analysis</p>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label>Dataset Name (Optional)</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter dataset name"
            />
          </div>

          <div className="file-upload">
            <input
              type="file"
              onChange={handleFileChange}
              accept=".csv,.xlsx,.json"
              disabled={loading}
            />
            <div className="upload-info">
              {file ? (
                <>
                  <p>✓ Selected: {file.name}</p>
                  <p>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </>
              ) : (
                <>
                  <p>📁 Drag and drop your file here or click to browse</p>
                  <p>Supported formats: CSV, XLSX, JSON</p>
                  <p>Max file size: 100 MB</p>
                </>
              )}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}
          {loading && statusMessage && (
            <div style={{ padding: '10px 14px', background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', borderRadius: '8px', fontSize: '14px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>⟳</span> {statusMessage}
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={!file || loading}
          >
            {loading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
        </form>

        <div className="upload-instructions">
          <h3>Supported Formats</h3>
          <ul>
            <li><strong>CSV</strong> - Comma-separated values</li>
            <li><strong>XLSX</strong> - Excel spreadsheets</li>
            <li><strong>JSON</strong> - JSON formatted data</li>
          </ul>

          <h3>Data Types Supported</h3>
          <ul>
            <li>Numerical Data</li>
            <li>Categorical Data</li>
            <li>Time Series Data</li>
            <li>Text/Sentiment Data</li>
            <li>Transaction Data</li>
            <li>Mixed Data</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
