export default function StatCard({ label, value, note, tone }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className={`stat-value${tone ? ` ${tone}` : ""}`}>{value}</div>
      {note && <div className="stat-note">{note}</div>}
    </div>
  );
}
