export default function CheckButton({ done, onClick, label }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={done}
      aria-label={label}
      className={`grid size-5 shrink-0 place-items-center rounded-full border ${done ? "border-accent bg-accent text-white" : "border-muted"}`}
    >
      {done && (
        <svg viewBox="0 0 12 12" className="size-3" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M2.5 6.5l2.5 2.5 4.5-5" />
        </svg>
      )}
    </button>
  );
}
