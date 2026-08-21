/**
 * Dashboard Page - Exact UI Match
 */
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import WordCloud from 'react-d3-cloud';
import { dashboardAPI, reportAPI } from '../services/api';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  ShieldCheck,
  Scale,
  PieChart,
  List,
  LayoutGrid,
  Database,
  CheckCircle2,
  Terminal,
  Activity
} from 'lucide-react';

const columnInsights = [
  { name: 'review_id', type: 'int64', uniqueValues: '25,350', missing: '0%' },
  { name: 'user_name', type: 'object', uniqueValues: '18,932', missing: '5.2%' },
  { name: 'review_text', type: 'object', uniqueValues: '24,987', missing: '15.8%' },
  { name: 'rating', type: 'int64', uniqueValues: '5', missing: '7.1%' },
  { name: 'timestamp', type: 'datetime64', uniqueValues: '25,350', missing: '3.4%' },
  { name: 'category', type: 'object', uniqueValues: '12', missing: '1.2%' },
  { name: 'sentiment', type: 'object', uniqueValues: '3', missing: '0%' },
  { name: 'product_id', type: 'object', uniqueValues: '5,630', missing: '0.1%' },
];

const negativeWords = ['bad', 'awful', 'terrible', 'poor', 'hate', 'worst', 'disappointing', 'not good', 'spam', 'cheap', 'horrible'];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [overview, setOverview] = useState(null);
  const [latestReport, setLatestReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liveLogs, setLiveLogs] = useState([]);
  const [logsVisible, setLogsVisible] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const logsEndRef = React.useRef(null);

  const [isWakingUp, setIsWakingUp] = useState(false);

  const fetchDashboardData = async (isPolling = false) => {
    try {
      if (!isPolling) setLoading(true);
      
      const timer = setTimeout(() => {
        setIsWakingUp(true);
      }, 3500);

      const [statsRes, overviewRes, reportsRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getOverview(),
        reportAPI.getLatest().catch(() => ({ data: { reports: [] } }))
      ]);

      clearTimeout(timer);
      setIsWakingUp(false);

      const statsData = statsRes.data;
      setStats(statsData);
      setOverview(overviewRes.data);

      if (reportsRes.data.reports && reportsRes.data.reports.length > 0) {
        setLatestReport(reportsRes.data.reports[0]);
      }
      setError(null);

      // Update live logs whenever available
      if (statsData.active_logs && statsData.active_logs.length > 0) {
        setLiveLogs(statsData.active_logs);
        setLogsVisible(true);
      }

      const analyzing = statsData.analysis_in_progress > 0;
      setIsAnalyzing(analyzing);

      const activeStatus = statsData.active_dataset_status;

      if (analyzing) {
        // actively processing – poll every 2 seconds
        if (!intervalId) {
          intervalId = setInterval(() => fetchDashboardData(true), 2000);
        }
      } else if (activeStatus === 'completed' && statsData.active_logs?.length > 0) {
        // just finished – keep polling for 10 more seconds to get final logs + report
        if (!stopAfter) stopAfter = Date.now() + 10000;
        if (!intervalId) {
          intervalId = setInterval(() => fetchDashboardData(true), 2000);
        }
        if (Date.now() >= stopAfter) {
          clearInterval(intervalId);
          intervalId = null;
        }
      } else {
        // nothing running – clear interval
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      }
    } catch (err) {
      setIsWakingUp(false);
      if (!isPolling) setError('Unable to connect to backend server. If this is the first load, Render may be waking up from sleep.');
      console.error(err);
    } finally {
      if (!isPolling) setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  // Auto-scroll logs terminal to bottom when new logs arrive
  useEffect(() => {
    if (logsEndRef.current && logsEndRef.current.parentElement) {
      const parent = logsEndRef.current.parentElement;
      parent.scrollTop = parent.scrollHeight;
    }
  }, [liveLogs]);

  if (loading) {
    return (
      <LoadingSpinner 
        message={isWakingUp 
          ? "Connecting to backend... (Waking up Render free tier container, please wait a moment)" 
          : "Loading dashboard data..."
        } 
      />
    );
  }

  const totalDatasets = overview?.total_datasets ?? stats?.total_datasets ?? 0;
  const completedAnalyses = overview?.completed_analyses ?? 0;
  const successRate = overview?.success_rate ?? 0;

  // Prefer latestReport as the primary data source for stat cards
  const qualityScore = Number(latestReport?.data_quality_score ?? overview?.average_quality_score ?? 0);
  const biasScore = Number(latestReport?.bias_score ?? overview?.average_bias_score ?? 0);

  // Completeness = 100 - missing_percentage (from quality result stored in report)
  const missingPct = Number(latestReport?.quality_metrics?.missing_percentage ?? 0);
  const completenessValue = latestReport ? (100 - missingPct).toFixed(1) : 0;

  const hasData = totalDatasets > 0;

  // Overall health = avg of quality + inverse-bias (mirrors _generate_report backend logic)
  const overallAvg = (qualityScore + (100 - biasScore)) / 2;
  const overallHealth = latestReport?.overall_health ||
    (overallAvg >= 80 ? 'Excellent' : overallAvg >= 60 ? 'Good' : overallAvg >= 40 ? 'Fair' : 'Poor');
  const overallHealthColor = overallHealth === 'Excellent' ? 'green' : overallHealth === 'Good' ? 'teal' : overallHealth === 'Fair' ? 'orange' : 'red';

  // Quality card subtext: shows structural quality + bias warning if both present
  const qualitySubtext = !hasData ? '-' : biasScore >= 60
    ? `Structurally ${qualityScore > 70 ? 'Good' : 'Weak'} (bias risk)`
    : qualityScore > 70 ? 'Structurally Complete' : 'Needs Improvement';
  const qualitySubtextColor = !hasData ? 'gray' : biasScore >= 60 ? 'orange' : qualityScore > 70 ? 'green' : 'orange';

  // Bias card: 3-tier grading
  const biasSubtext = !hasData ? '-' : biasScore < 30 ? 'Low Bias — Balanced' : biasScore < 60 ? 'Moderate Bias' : 'High Bias — Needs Attention';
  const biasSubtextColor = !hasData ? 'gray' : biasScore < 30 ? 'green' : biasScore < 60 ? 'orange' : 'red';
  
  const datasetType = latestReport?.dataset_type || stats?.recent_analyses?.[0]?.type || (hasData ? 'Unknown' : 'None');
  const totalRows = latestReport?.dataset?.rows ?? stats?.recent_analyses?.[0]?.rows ?? 0;
  const totalColumns = latestReport?.dataset?.columns ?? stats?.recent_analyses?.[0]?.columns ?? 0;
  const recentAnalyses = stats?.recent_analyses || [];

  // Dynamic extraction from report or fallback to empty
  const columnData = latestReport?.statistics?.columns || [];
  const topPositive = latestReport?.summary?.top_positive_words || [];
  const topNegative = latestReport?.summary?.top_negative_words || [];
  const recommendations = latestReport?.recommendations || [];
  
  // Missing value stats
  const missingColumns = latestReport?.quality_metrics?.missing_values || [];
  const allMissingData = columnData.length > 0 
    ? columnData.map(col => ({
        column: col.name || col.column,
        value: parseFloat(col.missing) || 0
      }))
    : missingColumns;
  
  // Sentiment distribution
  const sentimentDistribution = latestReport?.statistics?.sentiment_distribution || [];

  const gaugeAngle = Math.max(0, Math.min(180, (biasScore / 100) * 180));
  const gaugeTurn = (gaugeAngle / 360).toFixed(2);

  // Fallback visual properties if empty
  const isDonutEmpty = !sentimentDistribution || sentimentDistribution.length === 0;
  
  const isProcessing = isAnalyzing;

  return (
    <div className="dashboard-page">
      {error && (
        <div style={{
          marginBottom: '16px',
          padding: '12px 18px',
          borderRadius: '10px',
          background: '#fef2f2',
          border: '1px solid #fca5a5',
          color: '#991b1b',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '14px'
        }}>
          <div>
            <strong>Backend Connection Notice:</strong> {error}
          </div>
          <button 
            onClick={() => fetchDashboardData()} 
            style={{
              padding: '6px 14px',
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '500',
              fontSize: '13px'
            }}
          >
            Retry Connection
          </button>
        </div>
      )}
      <div className="dashboard-grid dashboard-grid-top">
        <StatCard 
          title="Structural Quality" 
          value={`${qualityScore.toFixed(0)} / 100`}
          subtext={qualitySubtext}
          subtextColor={qualitySubtextColor}
          icon={<ShieldCheck size={28} className="text-green" />} 
          color="green" 
        />
        <StatCard 
          title="Bias Score" 
          value={`${biasScore.toFixed(0)} / 100`}
          subtext={biasSubtext}
          subtextColor={biasSubtextColor}
          icon={<Scale size={28} className="text-orange" />} 
          color="orange" 
        />
        <StatCard 
          title="Completeness" 
          value={`${completenessValue} %`}
          subtext={hasData ? "Dataset Completeness" : "-"}
          subtextColor={hasData ? "green" : "gray"}
          icon={<PieChart size={28} className="text-blue" />} 
          color="blue" 
        />
        <StatCard 
          title="Rows" 
          value={totalRows.toLocaleString()}
          subtext={hasData ? "Total Rows" : "-"}
          subtextColor="gray"
          icon={<List size={28} className="text-purple" />} 
          color="purple" 
        />
        <StatCard 
          title="Columns" 
          value={Number(totalColumns).toLocaleString()}
          subtext={hasData ? "Total Columns" : "-"}
          subtextColor="gray"
          icon={<LayoutGrid size={28} className="text-pink" />} 
          color="pink" 
        />
        <StatCard 
          title="Dataset Type" 
          value={datasetType}
          subtext={hasData ? "Detected" : "-"}
          subtextColor="gray"
          icon={<Database size={28} className="text-teal" />} 
          color="teal" 
        />
      </div>

      {/* Overall Health Banner - combines quality + bias */}
      {hasData && (
        <div style={{
          margin: '0 0 16px 0',
          padding: '12px 20px',
          borderRadius: '12px',
          background: overallHealth === 'Excellent' ? '#e8f5e9' : overallHealth === 'Good' ? '#e3f2fd' : overallHealth === 'Fair' ? '#fff3e0' : '#ffebee',
          border: `1.5px solid ${overallHealth === 'Excellent' ? '#4caf50' : overallHealth === 'Good' ? '#2196f3' : overallHealth === 'Fair' ? '#ff9800' : '#f44336'}`,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '14px',
        }}>
          <span style={{ fontSize: '20px' }}>
            {overallHealth === 'Excellent' ? '✅' : overallHealth === 'Good' ? '🟡' : overallHealth === 'Fair' ? '🟠' : '🔴'}
          </span>
          <div>
            <strong>Overall Dataset Health: {overallHealth}</strong>
            <span style={{ marginLeft: '12px', color: '#666' }}>
              Structural quality is high ({qualityScore.toFixed(0)}/100), but bias score is {biasScore.toFixed(0)}/100 — 
              {biasScore >= 60 ? ' significant bias detected. Data may not be representative.' :
               biasScore >= 30 ? ' moderate bias present. Review recommended.' :
               ' dataset looks balanced and fair.'}
            </span>
          </div>
        </div>
      )}

      {logsVisible && (
        <div className="terminal-container">
          <div className="terminal-header">
            <Terminal size={18} />
            <span>Agent Execution Logs</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: 'auto' }}>
              {isAnalyzing && (
                <div className="terminal-pulse"><Activity size={14} className="pulse-icon" /> Processing</div>
              )}
              {!isAnalyzing && (
                <div style={{ color: '#4caf50', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle2 size={14} /> All agents completed
                </div>
              )}
              <button
                onClick={() => setLogsVisible(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#999', fontSize: '16px', lineHeight: 1 }}
                title="Close logs"
              >✕</button>
            </div>
          </div>
          <div className="terminal-body">
            {liveLogs.length === 0 ? (
              <div className="terminal-log text-muted">
                <span className="log-time">{new Date().toLocaleTimeString()}</span>
                <span className="log-agent">[System]</span>
                <span className="log-status">Initializing agents...</span>
              </div>
            ) : (
              liveLogs.map((log, idx) => (
                <div key={idx} className={`terminal-log log-${log.status}`}>
                  <span className="log-time">{new Date(log.time).toLocaleTimeString()}</span>
                  <span className="log-agent">[{log.agent}]</span>
                  <span className="log-status">
                    {log.status === 'running' && '🔄 Running...'}
                    {log.status === 'completed' && `✅ Completed${log.execution_time ? ` (${log.execution_time.toFixed(1)}s)` : ''}`}
                    {log.status === 'failed' && `❌ Failed${log.error ? ': ' + log.error.substring(0, 120) + (log.error.length > 120 ? '…' : '') : ''}`}
                    {log.status === 'pending' && '⏳ Waiting...'}
                  </span>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </div>
      )}

      <div className="dashboard-insight-grid">
        <section className="dashboard-card dashboard-card-chart">
          <div className="section-heading">
            <h2>{datasetType === 'sentiment' ? 'Sentiment Distribution' : 'Category Distribution'}</h2>
          </div>
          <div className="donut-layout">
            <div className="donut-chart">
              <div
                className="donut-center"
                style={{ 
                  background: isDonutEmpty ? '#e2e8f0' : (() => {
                    let gradient = 'conic-gradient(';
                    let currentPercentage = 0;
                    const order = { 'Positive': 1, 'Negative': 2, 'Neutral': 3 };
                    const sorted = [...sentimentDistribution].sort((a, b) => (order[a.label] || 99) - (order[b.label] || 99));
                    const colors = { 'Positive': '#4caf50', 'Negative': '#ef5350', 'Neutral': '#9ca3af' };
                    const fallbackColors = ['#2196f3', '#ff9800', '#9c27b0', '#00bcd4', '#4caf50', '#f44336'];
                    
                    sorted.forEach((item, index) => {
                      const color = colors[item.label] || fallbackColors[index % fallbackColors.length];
                      const start = currentPercentage;
                      const end = currentPercentage + item.percentage;
                      gradient += `${color} ${start}% ${end}%${index < sorted.length - 1 ? ', ' : ''}`;
                      currentPercentage = end;
                    });
                    return gradient + ')';
                  })()
                }}
              >
                <div className="donut-hole">
                  <strong>{isDonutEmpty ? '0%' : (() => {
                    const highest = [...sentimentDistribution].sort((a,b) => b.percentage - a.percentage)[0];
                    return highest ? `${highest.percentage}%` : '0%';
                  })()}</strong>
                </div>
              </div>
            </div>

            <ul className="chart-legend">
              {isDonutEmpty ? (
                <li><span className="text-muted">No categorical data available</span></li>
              ) : (
                [...sentimentDistribution].sort((a, b) => {
                  const order = { 'Positive': 1, 'Negative': 2, 'Neutral': 3 };
                  return (order[a.label] || 99) - (order[b.label] || 99);
                }).map((item, idx) => {
                  const fallbackColors = ['#2196f3', '#ff9800', '#9c27b0', '#00bcd4', '#4caf50', '#f44336'];
                  const color = ['positive', 'negative', 'neutral'].includes(item.label.toLowerCase()) 
                    ? undefined // Let CSS handle it
                    : fallbackColors[idx % fallbackColors.length];
                  return (
                  <li key={idx}>
                    <span className={`legend-dot sentiment-${item.label.toLowerCase()}`} style={color ? {backgroundColor: color} : {}} />
                    <div>
                      <strong>{item.label}</strong>
                      <span>{item.percentage}% ({item.value.toLocaleString()})</span>
                    </div>
                  </li>
                )})
              )}
            </ul>
          </div>

          <div className="assistant-note success-note">
            <CheckCircle2 size={16} className="note-icon" />
            <span>{isDonutEmpty 
              ? "Upload a dataset to view distribution." 
              : datasetType === 'sentiment' 
                ? "The dataset contains more Positive sentiments. Looks balanced."
                : `The dataset has ${sentimentDistribution.length} target categories.`}</span>
          </div>
        </section>

        <section className="dashboard-card dashboard-card-chart">
          <div className="section-heading">
            <h2>Missing Values Overview</h2>
          </div>
          <div className="bar-chart-container">
            <div className="y-axis">
              <span>{Math.ceil(Math.max(...allMissingData.map(d => d.value), 20))}%</span>
              <span>{Math.ceil(Math.max(...allMissingData.map(d => d.value), 20) * 0.75)}%</span>
              <span>{Math.ceil(Math.max(...allMissingData.map(d => d.value), 20) * 0.5)}%</span>
              <span>{Math.ceil(Math.max(...allMissingData.map(d => d.value), 20) * 0.25)}%</span>
              <span>0%</span>
            </div>
            <div className="mini-bar-chart" aria-label="Missing values overview chart">
              {allMissingData.length > 0 ? allMissingData.map((item, idx) => {
                const maxVal = Math.max(...allMissingData.map(d => d.value), 20);
                return (
                <div className="mini-bar-column" key={idx}>
                  <div className="mini-bar-track">
                    <div className="mini-bar-fill" style={{ height: `${(item.value / maxVal) * 100}%` }} />
                  </div>
                  <span className="x-axis-label">{item.column || item.label}</span>
                </div>
              )}) : (
                <div className="text-muted" style={{position:'absolute', top:'50%', left:'50%', transform:'translate(-50%,-50%)'}}>No missing values data</div>
              )}
            </div>
          </div>
          <p className="chart-axis-label text-center">Columns</p>
          <p className="chart-axis-y-label">Missing %</p>
        </section>

        <section className="dashboard-card dashboard-card-chart">
          <div className="section-heading">
            <h2>Bias Detection</h2>
          </div>
          <div className="gauge-wrap">
            <div className="gauge">
              <div className="gauge-background"></div>
              <div className="gauge-fill" style={{ transform: `rotate(${gaugeTurn}turn)` }}></div>
              <div className="gauge-cover"></div>
              <div className="gauge-needle" style={{ transform: `rotate(${-90 + gaugeAngle}deg)` }}>
                <div className="needle-head"></div>
              </div>
            </div>
            <div className="gauge-readout">
              <strong>{biasScore.toFixed(0)} / 100</strong>
              <span style={{ color: biasSubtextColor }}>
                {hasData ? biasSubtext : 'No Data'}
              </span>
            </div>
          </div>
          <div className="assistant-note success-note">
            <CheckCircle2 size={16} className="note-icon" />
            <span>
              {!hasData ? 'Upload a dataset to evaluate bias.' :
               biasScore >= 60 ? 'High bias detected — data may not represent all groups equally.' :
               biasScore >= 30 ? 'Moderate bias present — some groups may be underrepresented.' :
               'Low bias detected. Dataset distribution looks fair.'}
            </span>
          </div>
        </section>
      </div>

      <div className="dashboard-insight-grid dashboard-insight-grid-secondary">
        <section className="dashboard-card table-card">
          <div className="section-heading">
            <h2>Column Data Type</h2>
          </div>
          <div className="table-wrap">
            <table className="insight-table">
              <thead>
                <tr>
                  <th>Column Name</th>
                  <th>Data Type</th>
                  <th>Unique Values</th>
                  <th>Missing %</th>
                </tr>
              </thead>
              <tbody>
                {columnData.length > 0 ? columnData.map((row, idx) => {
                  const rawType = row.type || '';
                  const typeMap = {
                    'numerical': 'INT', 'float64': 'FLOAT', 'float32': 'FLOAT',
                    'int64': 'INT', 'int32': 'INT', 'int': 'INT', 'float': 'FLOAT',
                    'categorical': 'STRING', 'text': 'STRING', 'object': 'STRING',
                    'boolean': 'BOOLEAN', 'bool': 'BOOLEAN',
                    'datetime': 'DATE', 'datetime64': 'DATE',
                    'INT': 'INT', 'FLOAT': 'FLOAT', 'STRING': 'STRING',
                    'BOOLEAN': 'BOOLEAN', 'DATE': 'DATE',
                  };
                  const displayType = typeMap[rawType] || typeMap[rawType.toLowerCase()] || rawType.toUpperCase();
                  return (
                  <tr key={idx}>
                    <td>{row.name || row.column}</td>
                    <td><span className={`type-text type-${displayType.toLowerCase()}`}>{displayType}</span></td>
                    <td>{row.uniqueValues || row.unique_count || 0}</td>
                    <td>{row.missing || '0%'}</td>
                  </tr>
                )}) : (
                  <tr><td colSpan="4" className="text-center text-muted py-4">No column data available</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="dashboard-card word-cloud-card">
          <div className="section-heading">
            <h2>Top Words (Positive)</h2>
          </div>
          <div className="word-cloud-container" style={{ minHeight: '150px' }}>
            {topPositive.length > 0 ? (
              <WordCloud
                data={topPositive.map((word, idx) => ({ 
                  text: word, 
                  value: idx === 0 ? 45 : idx === 1 ? 28 : Math.max(10, 22 - (idx * 2))
                }))}
                width={300}
                height={150}
                font="Inter"
                fontStyle="normal"
                fontWeight="bold"
                fontSize={(word) => word.value}
                spiral="archimedean"
                rotate={(word) => (Math.random() > 0.5 ? 0 : 0)} 
                padding={3}
                fill={() => '#4caf50'}
              />
            ) : <span className="text-muted" style={{ display: 'block', padding: '20px' }}>No positive words</span>}
          </div>
          <div className="section-heading section-heading-sub">
            <h2>Top Words (Negative)</h2>
          </div>
          <div className="word-cloud-container" style={{ minHeight: '150px' }}>
            {topNegative.length > 0 ? (
              <WordCloud
                data={topNegative.map((word, idx) => ({ 
                  text: word, 
                  value: idx === 0 ? 45 : idx === 1 ? 28 : Math.max(10, 22 - (idx * 2))
                }))}
                width={300}
                height={150}
                font="Inter"
                fontStyle="normal"
                fontWeight="bold"
                fontSize={(word) => word.value}
                spiral="archimedean"
                rotate={(word) => (Math.random() > 0.5 ? 0 : 0)}
                padding={3}
                fill={() => '#ef5350'}
              />
            ) : <span className="text-muted" style={{ display: 'block', padding: '20px' }}>No negative words</span>}
          </div>
        </section>

        <div className="right-stack">
          <section className="dashboard-card recommendations-card">
            <div className="section-heading">
              <h2>Recommendations</h2>
            </div>
            <ul className="recommendation-list">
              {recommendations.length > 0 ? recommendations.map((rec, idx) => (
                <li key={idx}><CheckCircle2 size={16} className="text-green" /> <span>{rec}</span></li>
              )) : (
                <li><span className="text-muted">No recommendations generated yet.</span></li>
              )}
            </ul>
            <div className="recommendations-action">
              <button className="btn btn-outline-purple" disabled={!hasData}>View Full Recommendations</button>
            </div>
          </section>

          <section className="dashboard-card recent-card">
            <div className="section-heading section-heading-row">
              <h2>Recent Analyses</h2>
              <Link to="/history" className="inline-link">View All</Link>
            </div>
            <div className="recent-analysis-list">
              {recentAnalyses.length > 0 ? recentAnalyses.map((analysis) => (
                <div className="recent-analysis-row" key={analysis.id}>
                  <div className="recent-info">
                    <strong>{analysis.name}</strong>
                    <span>{analysis.type || 'Unknown'}</span>
                  </div>
                  <div className="recent-meta">
                    <span className="recent-date">{new Date(analysis.uploaded).toLocaleDateString()}</span>
                    <span className="status-badge status-completed">Completed</span>
                  </div>
                </div>
              )) : (
                <div className="text-muted text-center py-4">No recent analyses</div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
