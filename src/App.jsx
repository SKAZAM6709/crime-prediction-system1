import { useEffect, useState } from "react";
import { getForecast, getStates } from "./services/api";
import "./styles.css";

export default function App() {
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState("");
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // First request: get the available states.
  useEffect(() => {
    let active = true;

    async function loadStates() {
      try {
        const data = await getStates();

        if (active) {
          setStates(data.states);
          setSelectedState(data.states[0] || "");
        }
      } catch (err) {
        if (active) {
          setError(err.message);
          setLoading(false);
        }
      }
    }

    loadStates();

    return () => {
      active = false;
    };
  }, []);

  // Second request: get the model result for the selected state.
  useEffect(() => {
    if (!selectedState) {
      return;
    }

    let active = true;

    async function loadForecast() {
      setLoading(true);
      setError("");
      setForecast(null);

      try {
        const data = await getForecast(selectedState);

        if (active) {
          setForecast(data);
        }
      } catch (err) {
        if (active) {
          setError(err.message);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadForecast();

    return () => {
      active = false;
    };
  }, [selectedState]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">C</div>
          <div>
            <strong>Crime Patterns</strong>
            <span>Research dashboard</span>
          </div>
        </div>

        <nav className="navigation" aria-label="Main navigation">
          <a className="nav-item active" href="#dashboard">
            Dashboard
          </a>
          <a className="nav-item" href="#forecast">
            Forecast
          </a>
          <a className="nav-item" href="#about">
            About the model
          </a>
        </nav>

        <p className="sidebar-note">
          Historical incident analysis by state and month.
        </p>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div>
            <p className="eyebrow">OVERVIEW</p>
            <h1>Crime patterns dashboard</h1>
            <p className="subtitle">
              Model forecasts loaded from the Python backend.
            </p>
          </div>

          <span className="status">
            <span className="status-dot" />
            Connected locally
          </span>
        </header>

        <section className="hero" id="forecast">
          <div>
            <p className="eyebrow">MONTHLY FORECAST</p>
            <h2>Select a state</h2>
            <p>
              Changing the state sends a request to FastAPI and
              displays the saved model&apos;s prediction.
            </p>
          </div>

          <div className="forecast-form">
            <label htmlFor="state-select">State</label>

            <select
              id="state-select"
              value={selectedState}
              onChange={(event) =>
                setSelectedState(event.target.value)
              }
              disabled={states.length === 0}
            >
              {states.map((state) => (
                <option key={state} value={state}>
                  {state}
                </option>
              ))}
            </select>
          </div>
        </section>

        {loading && (
          <div className="message" role="status">
            Loading forecast from the backend...
          </div>
        )}

        {error && (
          <div className="message error" role="alert">
            {error}
          </div>
        )}

        {forecast && !loading && (
          <section className="results" aria-live="polite">
            <div className="section-heading">
              <div>
                <p className="eyebrow">MODEL RESULT</p>
                <h2>{forecast.state}</h2>
              </div>

              <span className="period">
                Forecast: {forecast.forecast_month}
              </span>
            </div>

            <div className="card-grid">
              <article className="stat-card primary-card">
                <span>Predicted incidents</span>
                <strong>{forecast.predicted_incidents}</strong>
                <small>
                  Model estimate for {forecast.forecast_month}
                </small>
              </article>

              <article className="stat-card">
                <span>Last recorded month</span>
                <strong>
                  {forecast.previous_month_incidents}
                </strong>
                <small>
                  Recorded in {forecast.latest_data_month}
                </small>
              </article>

              <article className="stat-card">
                <span>Forecast period</span>
                <strong className="date-value">
                  {forecast.forecast_month}
                </strong>
                <small>
                  One month after the latest available data
                </small>
              </article>
            </div>
          </section>
        )}

        <section className="about-card" id="about">
          <p className="eyebrow">ABOUT THIS RESULT</p>
          <h2>How the forecast is produced</h2>
          <p>
            React requests a state forecast from FastAPI. FastAPI
            loads the trained model and uses earlier monthly counts
            to estimate the next month. The result describes a
            state-wide count, not a particular event or person.
          </p>
        </section>
      </main>
    </div>
  );
}