import { useEffect, useState } from "react";
import ForecastChart from "../components/ForecastChart.jsx";
import StatCard from "../components/StatCard.jsx";
import { api } from "../services/api.js";

export default function Forecast({ range }) {
  const [state, setState] = useState("ALL");
  const [horizon, setHorizon] = useState(12);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.forecast(state, horizon)
      .then(setData)
      .catch((e) => { setData(null); setError(e.message); })
      .finally(() => setLoading(false));
  }, [state, horizon]);

  const total = data?.forecast.reduce((sum, p) => sum + p.predicted, 0);

  return (
    <>
      <div className="filters">
        <label>
          Area
          <select value={state} onChange={(e) => setState(e.target.value)}>
            <option value="ALL">All states combined</option>
            {range.states.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        <label>
          Months ahead
          <select value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}>
            {[3, 6, 12, 18, 24, 36].map((h) => <option key={h} value={h}>{h}</option>)}
          </select>
        </label>
      </div>

      {error && <div className="notice error">{error}</div>}
      {loading && !data && <p className="empty">Calculating forecast…</p>}

      {data && (
        <>
          <div className="stats">
            <StatCard
              label={`Expected incidents, next ${horizon} months`}
              value={Math.round(total).toLocaleString()}
            />
            <StatCard
              label="First forecast month"
              value={data.forecast[0].predicted.toLocaleString()}
              note={data.forecast[0].period}
            />
            <StatCard
              label="Last recorded month"
              value={data.history[data.history.length - 1].count.toLocaleString()}
              note={data.history[data.history.length - 1].period}
            />
          </div>
          <section className="panel">
            <h2>{data.state === "ALL" ? "All states combined" : data.state}</h2>
            <ForecastChart history={data.history} forecast={data.forecast} />
            <p className="fine-print">
              The shaded band is an approximate 80% range based on the model's error on recent months.
              Forecasts get less reliable the further ahead they go.
            </p>
          </section>
        </>
      )}
    </>
  );
}
