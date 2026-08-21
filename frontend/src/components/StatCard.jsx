import React from 'react';

export default function StatCard({ title, value, subtext, subtextColor, icon, color }) {
  return (
    <div className={`stat-card stat-card-${color}`}>
      <div className={`stat-icon-wrap icon-${color}`}>
        {icon}
      </div>
      <div className="stat-content">
        <h3>{title}</h3>
        <p className="stat-value">{value}</p>
        {subtext && (
          <p className={`stat-subtext text-${subtextColor}`}>
            {subtext}
          </p>
        )}
      </div>
    </div>
  );
}
