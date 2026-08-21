/**
 * QualityScoreGauge Component - Display quality/bias score as gauge
 */
export default function QualityScoreGauge({ score, color = 'blue' }) {
  const getScoreColor = (value) => {
    if (color === 'red') {
      if (value < 30) return '#22c55e';
      if (value < 60) return '#eab308';
      return '#ef4444';
    }
    // Blue color scheme
    if (value >= 80) return '#22c55e';
    if (value >= 60) return '#eab308';
    if (value >= 40) return '#f97316';
    return '#ef4444';
  };

  const scoreColor = getScoreColor(score);

  return (
    <div className="quality-gauge">
      <svg viewBox="0 0 100 60" className="gauge-svg">
        <path d="M 10 50 A 40 40 0 0 1 90 50" stroke="#e5e7eb" strokeWidth="8" fill="none" />
        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          stroke={scoreColor}
          strokeWidth="8"
          fill="none"
          strokeDasharray={`${(score / 100) * 251.2} 251.2`}
        />
      </svg>
      <div className="gauge-text">
        <span className="gauge-value">{score.toFixed(1)}</span>
        <span className="gauge-label">/ 100</span>
      </div>
    </div>
  );
}
