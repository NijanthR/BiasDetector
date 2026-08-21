/**
 * History Page - View dataset upload history and past analyses
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function History() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const response = await datasetAPI.getHistory();
        setDatasets(response.data.datasets);
        setError(null);
      } catch (err) {
        setError('Failed to load history');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="history-page">
      <h1>Dataset History</h1>

      {error && <div className="error-message">{error}</div>}

      {datasets.length > 0 ? (
        <div className="history-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Rows</th>
                <th>Columns</th>
                <th>Size (MB)</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map(dataset => (
                <tr key={dataset.id}>
                  <td>{dataset.name}</td>
                  <td>{dataset.file_type.toUpperCase()}</td>
                  <td>{dataset.rows}</td>
                  <td>{dataset.columns}</td>
                  <td>{dataset.size_mb.toFixed(2)}</td>
                  <td>
                    <span className={`status-badge status-${dataset.analysis_status}`}>
                      {dataset.analysis_status}
                    </span>
                  </td>
                  <td>{new Date(dataset.uploaded_at).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/report/${dataset.id}`} className="btn btn-sm btn-primary">
                      View Report
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <p>No datasets uploaded yet</p>
          <Link to="/upload" className="btn btn-primary">
            Upload Your First Dataset
          </Link>
        </div>
      )}
    </div>
  );
}
