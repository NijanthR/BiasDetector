/**
 * RecentAnalysisCard Component - Show recent analysis
 */
import { Link } from 'react-router-dom';

export default function RecentAnalysisCard({ analysis }) {
  return (
    <div className="recent-analysis-card">
      <h3>{analysis.name}</h3>
      <div className="card-info">
        <span>📊 Type: {analysis.type}</span>
        <span>📈 Rows: {analysis.rows.toLocaleString()}</span>
        <span>📋 Columns: {analysis.columns}</span>
      </div>
      <p className="card-date">
        Uploaded: {new Date(analysis.uploaded).toLocaleDateString()}
      </p>
      <Link to={`/report/${analysis.id}`} className="btn btn-sm btn-outline">
        View Report →
      </Link>
    </div>
  );
}
