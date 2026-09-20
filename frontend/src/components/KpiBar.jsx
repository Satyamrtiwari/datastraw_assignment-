import React from 'react';

export default function KpiBar({ metrics }) {
  const total = metrics?.total_tickets ?? 0;
  const urgent = metrics?.urgent_tickets ?? 0;
  const resolutionRate = metrics?.resolution_rate_percent ?? 0;
  const closed = metrics?.closed_tickets ?? 0;

  return (
    <section className="kpi-bar" aria-label="Support Operations Key Metrics">
      {/* Total Tickets Card */}
      <div className="kpi-card" id="kpiTotalCard">
        <div className="kpi-meta">
          <span className="kpi-title">Total Ingested</span>
          <span className="kpi-pill kpi-pill-blue">Volume</span>
        </div>
        <div className="kpi-value">{total.toLocaleString()}</div>
        <div className="kpi-sub">
          <span className="kpi-trend positive">↑ 100%</span> active queues
        </div>
      </div>

      {/* Urgent Alerts Card */}
      <div className="kpi-card urgent-highlight" id="kpiUrgentCard">
        <div className="kpi-meta">
          <span className="kpi-title">Urgent Alerts</span>
          <span className="kpi-pill kpi-pill-danger">Requires Action</span>
        </div>
        <div className="kpi-value urgent-glow">{urgent}</div>
        <div className="kpi-sub">Critical D2C issues flagged by Groq AI</div>
      </div>

      {/* SLA Timer Card */}
      <div className="kpi-card" id="kpiSlaCard">
        <div className="kpi-meta">
          <span className="kpi-title">Avg SLA Response</span>
          <span className="kpi-pill kpi-pill-success">Within Goal</span>
        </div>
        <div className="kpi-value">14m 20s</div>
        <div className="kpi-sub">Target: &lt; 30m first response</div>
      </div>

      {/* Resolution Rate Card */}
      <div className="kpi-card" id="kpiResolutionCard">
        <div className="kpi-meta">
          <span className="kpi-title">Resolution Rate</span>
          <span className="kpi-pill kpi-pill-purple">
            {closed}/{total} Resolved
          </span>
        </div>
        <div className="kpi-value">{resolutionRate}%</div>
        <div className="kpi-progress">
          <div
            className="kpi-progress-bar"
            style={{ width: `${Math.min(resolutionRate, 100)}%` }}
          ></div>
        </div>
      </div>
    </section>
  );
}
