/**
 * Report Viewer Page - Display detailed analysis reports
 */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { reportAPI, datasetAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import QualityScoreGauge from '../components/QualityScoreGauge';
import BiasChart from '../components/BiasChart';

export default function ReportViewer() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        
        const [reportRes, analysisRes] = await Promise.all([
          reportAPI.getOne(id),
          datasetAPI.getResults(id)
        ]);
        
        setReport(reportRes.data);
        setAnalysis(analysisRes.data);
        setError(null);
      } catch (err) {
        setError('Failed to load report');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="report-viewer">
      {report && (
        <>
          <div className="report-header">
            <h1>{report.title}</h1>
            <div className="report-meta">
              <span className={`health-badge health-${report.overall_health.toLowerCase()}`}>
                {report.overall_health} Health
              </span>
              <span>Generated: {new Date(report.created_at).toLocaleString()}</span>
            </div>
          </div>

          <div className="report-tabs">
            <button 
              className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button 
              className={`tab ${activeTab === 'quality' ? 'active' : ''}`}
              onClick={() => setActiveTab('quality')}
            >
              Quality
            </button>
            <button 
              className={`tab ${activeTab === 'bias' ? 'active' : ''}`}
              onClick={() => setActiveTab('bias')}
            >
              Bias Detection
            </button>
            <button 
              className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommendations')}
            >
              Recommendations
            </button>
          </div>

          <div className="report-content">
            {activeTab === 'overview' && (
              <div className="overview-section">
                <h2>Dataset Overview</h2>
                <div className="info-grid">
                  <div className="info-card">
                    <h3>Dataset Type</h3>
                    <p>{report.dataset_type}</p>
                  </div>
                  <div className="info-card">
                    <h3>Data Quality Score</h3>
                    <QualityScoreGauge score={report.data_quality_score} />
                  </div>
                  <div className="info-card">
                    <h3>Bias Score</h3>
                    <QualityScoreGauge score={report.bias_score} color="red" />
                  </div>
                </div>

                {report.summary && (
                  <div className="summary-section">
                    <h3>Summary</h3>
                    <p>{report.summary.overview || 'No summary available'}</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'quality' && (
              <div className="quality-section">
                <h2>Data Quality Metrics</h2>
                {report.quality_metrics && (
                  <div className="metrics-grid">
                    <div className="metric-card">
                      <h4>Completeness</h4>
                      <p>{report.quality_metrics.completeness?.toFixed(1)}%</p>
                    </div>
                    <div className="metric-card">
                      <h4>Missing Data</h4>
                      <p>{report.quality_metrics.missing_percentage?.toFixed(1)}%</p>
                    </div>
                    <div className="metric-card">
                      <h4>Duplicates</h4>
                      <p>{report.quality_metrics.duplicate_percentage?.toFixed(1)}%</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'bias' && (
              <div className="bias-section">
                <h2>Bias Detection</h2>
                {report.bias_analysis && (
                  <>
                    <p className="bias-summary">{report.bias_analysis.fairness_report?.summary}</p>
                    {report.bias_analysis.biased_columns && (
                      <div className="biased-columns">
                        <h3>Flagged Columns</h3>
                        {report.bias_analysis.biased_columns.map((col, idx) => (
                          <div key={idx} className="column-flag">
                            <strong>{col.column}</strong>
                            <p>Bias Score: {col.bias_score.toFixed(1)}</p>
                            <p>Status: {col.balance_status}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="recommendations-section">
                <h2>Recommendations</h2>
                {report.recommendations && report.recommendations.length > 0 ? (
                  <ul className="recommendations-list">
                    {report.recommendations.map((rec, idx) => (
                      <li key={idx} className="recommendation-item">
                        {typeof rec === 'string' ? rec : rec.action}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No recommendations at this time</p>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
