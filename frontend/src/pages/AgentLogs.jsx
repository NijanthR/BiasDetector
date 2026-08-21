/**
 * Agent Logs Page
 */
import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { TerminalSquare } from 'lucide-react';

export default function AgentLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        setLoading(true);
        const response = await dashboardAPI.getLogs();
        setLogs(response.data.logs || []);
        setError(null);
      } catch (err) {
        setError('Failed to load agent logs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="agent-logs-page" style={{ padding: '32px' }}>
      <h1 style={{ marginTop: 0, marginBottom: '32px', fontSize: '28px' }}>Agent Execution Logs</h1>
      
      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ background: '#1e293b', color: 'white', padding: '16px 24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <TerminalSquare size={20} />
          <h2 style={{ margin: 0, fontSize: '16px', fontWeight: '500' }}>System Execution Logs</h2>
        </div>
        
        {logs.length > 0 ? (
          <div style={{ maxHeight: '70vh', overflowY: 'auto', background: '#0f172a' }}>
            {logs.map((log) => (
              <div 
                key={log.id} 
                style={{ 
                  padding: '16px 24px', 
                  borderBottom: '1px solid #334155',
                  display: 'flex',
                  gap: '16px',
                  fontFamily: 'monospace',
                  fontSize: '13px',
                  color: '#e2e8f0'
                }}
              >
                <div style={{ color: '#94a3b8', minWidth: '180px' }}>
                  {new Date(log.time).toLocaleString()}
                </div>
                <div style={{ minWidth: '160px' }}>
                  <span style={{ 
                    color: log.status === 'completed' ? '#4ade80' : 
                           log.status === 'failed' ? '#f87171' : 
                           '#fbbf24',
                    fontWeight: 'bold'
                  }}>
                    [{log.agent.toUpperCase()}]
                  </span>
                </div>
                <div style={{ flex: 1 }}>
                  <div>Dataset: {log.dataset_name}</div>
                  {log.status === 'completed' && <div style={{ color: '#4ade80', marginTop: '4px' }}>✓ Execution completed in {log.execution_time.toFixed(2)}s</div>}
                  {log.status === 'failed' && <div style={{ color: '#f87171', marginTop: '4px' }}>✗ Failed: {log.error}</div>}
                  {log.status === 'processing' && <div style={{ color: '#fbbf24', marginTop: '4px' }}>⟳ Processing...</div>}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '48px', textAlign: 'center', color: '#64748b', background: '#0f172a' }}>
            No agent logs available yet.
          </div>
        )}
      </div>
    </div>
  );
}
