const API_BASE = "http://127.0.0.1:8000";

async function getJson(path) {
  let response;

  try {
    response = await fetch(`${API_BASE}${path}`);
  } catch {
    throw new Error(
      "Cannot connect to the backend. Check that FastAPI is running on port 8000."
    );
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "The backend returned an error.");
  }

  return data;
}

export function getStates() {
  return getJson("/api/states");
}

export function getForecast(state) {
  return getJson(`/api/forecast/${encodeURIComponent(state)}`);
}