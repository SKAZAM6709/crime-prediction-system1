import { useEffect, useState } from "react";
import { api } from "../services/api.js";

const LABELS = {
  model: "This model",
  baseline_last_month: "Repeat last month",
  baseline_same_month_last_year: "Repeat same month last year",
};

export default function AboutModel() {
  const [info, setInfo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.modelInfo().then(setInfo).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="notice error">{error}</div>;
  if (!info) return <p className="empty">Loading…</p>;

  const rows = [["model", info.metrics], ...Object.entries(info.baselines)];
  return (
    <>
      <p className="lede">
        The forecast uses a {info.model_name} trained on monthly incident counts per state. It predicts one month at a
        time and feeds each prediction back in to reach further months.
      </p>
      <section className="panel">
        <h2>How accurate is it?</h2>
        <p className="fine-print">
          Scores come from the last {info.test_months} months of data, which the model did not see while learning.
          Lower error is better.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Method</th><th className="num">Average miss (MAE)</th><th className="num">RMSE</th><th className="num">R²</th></tr>
            </thead>
            <tbody>
              {rows.map(([key, m]) => (
                <tr key={key} className={key === "model" ? "highlight" : ""}>
                  <td>{LABELS[key] || key}</td>
                  <td className="num">{m.mae}</td>
                  <td className="num">{m.rmse}</td>
                  <td className="num">{m.r2}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="panel">
        <h2>What it looks at</h2>
        <p>Recent months, the same month a year ago, the season, the overall trend over time, and which state it is.</p>
        <p className="fine-print">
          Trained {info.trained_at?.slice(0, 10)}. Data runs through {info.last_observed_period}.
          The model finds patterns in past counts; it does not know about policy changes, events, or reporting gaps.
        </p>
      </section>
    </>
  );
}
