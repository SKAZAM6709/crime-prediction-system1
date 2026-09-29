export default function FilterBar({ range, filters, onChange, showState = true }) {
  const years = [];
  for (let y = range.min_year; y <= range.max_year; y++) years.push(y);
  const set = (key) => (e) => onChange({ ...filters, [key]: e.target.value });

  return (
    <div className="filters">
      {showState && (
        <label>
          State
          <select value={filters.state} onChange={set("state")}>
            <option value="">All states</option>
            {range.states.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>
      )}
      <label>
        From
        <select value={filters.start_year} onChange={set("start_year")}>
          {years.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </label>
      <label>
        To
        <select value={filters.end_year} onChange={set("end_year")}>
          {years.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </label>
    </div>
  );
}
