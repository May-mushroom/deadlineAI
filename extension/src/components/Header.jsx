const PAGES = [
  { id: 'week', label: 'Week' },
  { id: 'today', label: 'Today' },
  { id: 'settings', label: 'Settings' },
]

export default function Header({ page, setPage, menuOpen, setMenuOpen, onClose }) {
  return (
    <header className="header">
      <div className="header__bar">
        <button
          className="icon-btn"
          aria-label="Open menu"
          onClick={() => setMenuOpen((v) => !v)}
        >
          ☰
        </button>
        <span className="header__title">Day Task Planner</span>
        <button className="icon-btn" aria-label="Close panel" onClick={onClose}>
          ✕
        </button>
      </div>

      {menuOpen && (
        <nav className="header__menu">
          {PAGES.map((p) => (
            <button
              key={p.id}
              className={`header__menu-item ${page === p.id ? 'is-active' : ''}`}
              onClick={() => {
                setPage(p.id)
                setMenuOpen(false)
              }}
            >
              {p.label}
            </button>
          ))}
        </nav>
      )}
    </header>
  )
}
