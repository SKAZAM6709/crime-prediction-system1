import { useEffect, useState } from "react";
import StatCard from "../components/StatCard.jsx";
import TrendChart from "../components/TrendChart.jsx";
import StateChart from "../components/StateChart.jsx";
import { api } from "../services/api.js";

const fmt = (n) => (n == null ? "–" : n.toLocaleString());

export default function Dashboard({ range }) {
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [states, setStates] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.summary({}), api.trend({}), api.byState({ limit: 10 })])
      .then(([s, t, b]) => { setSummary(s); setTrend(t); setStates(b); })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="notice error">{error}</div>;
  if (!summary) return <p className="empty">Loading…</p>;

  const change = summary.year_over_year_change_pct;
  return (
    <>
      <p className="lede">
        Recorded incidents from {range.min_year} to {range.max_year} across {range.states.length} states.
      </p>
      <div className="stats">
        <StatCard label="Total incidents" value={fmt(summary.total_incidents)} />
        <StatCard label="Average per month" value={fmt(summary.average_per_month)} />
        <StatCard
          label="Busiest month"
          value={fmt(summary.peak_month?.count)}
          note={summary.peak_month?.period}
        />
        <StatCard
          label={`Change in ${summary.latest_year}`}
          value={change == null ? "–" : `${change > 0 ? "+" : ""}${change}%`}
          note="Compared with the previous year"
          tone={change > 0 ? "up" : change < 0 ? "down" : ""}
        />
      </div>
      <section className="panel">
        <h2>Incidents per month</h2>
        <TrendChart data={trend} />
      </section>
      <section className="panel">
        <h2>States with the most incidents</h2>
        <StateChart data={states} />
      </section>
    </>
  );
}
