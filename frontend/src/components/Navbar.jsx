const ITEMS = [
  ["today", "Today's tasks"],
  ["week", "Tasks this week"],
  ["dashboard", "Dashboard"],
];

export default function Navbar({ page, onChange, children }) {
  return (
    <header className="flex h-14 items-center gap-8 bg-pine px-6 text-white">
      <span className="font-semibold">AI ticketing system</span>
      <nav className="flex gap-1">
        {ITEMS.map(([id, label]) => (
          <button
            key={id}
            onClick={() => onChange(id)}
            aria-current={page === id ? "page" : undefined}
            className={`rounded px-3 py-1.5 text-sm ${page === id ? "bg-white/15 font-medium" : "text-white/70 hover:bg-white/10"}`}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className="ml-auto">{children}</div>
    </header>
  );
}
