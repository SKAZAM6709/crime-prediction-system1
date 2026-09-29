import { useEffect, useState } from "react";
import FilterBar from "../components/FilterBar.jsx";
import TrendChart from "../components/TrendChart.jsx";
import StateChart from "../components/StateChart.jsx";
import StatCard from "../components/StatCard.jsx";
import { api } from "../services/api.js";

export default function ExploreData({ range }) {
  const [filters, setFilters] = useState({
    state: "",
    start_year: range.min_year,
    end_year: range.max_year,
  });
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [byState, setByState] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    const { start_year, end_year } = filters;
    Promise.all([
      api.summary(filters),
      api.trend(filters),
      api.byState({ start_year, end_year, limit: 51 }),
    ])
      .then(([s, t, b]) => { setSummary(s); setTrend(t); setByState(b); })
      .catch((e) => setError(e.message));
  }, [filters]);

  const invalid = Number(filters.start_year) > Number(filters.end_year);

  return (
    <>
      <FilterBar range={range} filters={filters} onChange={setFilters} />
      {invalid && <div className="notice">The start year must not be after the end year.</div>}
      {error && <div className="notice error">{error}</div>}
      {summary && (
        <div className="stats">
          <StatCard label="Incidents" value={summary.total_incidents.toLocaleString()} />
          <StatCard label="Months covered" value={summary.months_covered} />
          <StatCard label="Average per month" value={summary.average_per_month.toLocaleString()} />
        </div>
      )}
      <section className="panel">
        <h2>{filters.state || "All states"}: incidents per month</h2>
        <TrendChart data={trend} />
      </section>
      <section className="panel">
        <h2>Totals by state</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>State</th><th className="num">Incidents</th></tr>
            </thead>
            <tbody>
              {byState.map((r) => (
                <tr key={r.state}>
                  <td>{r.state}</td>
                  <td className="num">{r.total.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {byState.length > 0 && (
        <section className="panel">
          <h2>Top 10 states</h2>
          <StateChart data={byState.slice(0, 10)} />
        </section>
      )}
    </>
  );
}
