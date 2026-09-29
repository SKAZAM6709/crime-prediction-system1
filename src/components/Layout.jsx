import Sidebar from "./Sidebar.jsx";

export default function Layout({ pages, current, onNavigate, title, children }) {
  return (
    <div className="shell">
      <Sidebar pages={pages} current={current} onNavigate={onNavigate} />
      <main className="main">
        <h1 className="page-title">{title}</h1>
        {children}
      </main>
    </div>
  );
}
