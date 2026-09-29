export default function Sidebar({ pages, current, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true" />
        <span className="brand-name">Crime forecast</span>
      </div>
      <nav aria-label="Main">
        {Object.entries(pages).map(([key, { label }]) => (
          <button
            key={key}
            className={`nav-item${key === current ? " active" : ""}`}
            aria-current={key === current ? "page" : undefined}
            onClick={() => onNavigate(key)}
          >
            {label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
