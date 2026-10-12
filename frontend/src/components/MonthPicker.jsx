import { useEffect, useRef, useState } from "react";
import { addDays, startOfWeek, toISODate, weekDays } from "../lib/dates";

// Small month popover. Clicking a date selects it (the calendar then shows that date's week).
export default function MonthPicker({ selected, onSelect, onClose }) {
  const [view, setView] = useState(
    () => new Date(selected.getFullYear(), selected.getMonth(), 1),
  );
  const ref = useRef(null);

  useEffect(() => {
    // Clicks inside the parent (title button + popover) are handled by their own handlers.
    const onDown = (e) =>
      !ref.current.parentElement.contains(e.target) && onClose();
    const onKey = (e) => e.key === "Escape" && onClose();
    document.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [onClose]);

  const cells = Array.from({ length: 42 }, (_, i) =>
    addDays(startOfWeek(view), i),
  );
  const selectedWeek = new Set(weekDays(selected).map(toISODate));
  const todayISO = toISODate(new Date());
  const shiftMonth = (n) =>
    setView(new Date(view.getFullYear(), view.getMonth() + n, 1));

  return (
    <div
      ref={ref}
      className="absolute left-0 top-full z-30 mt-1 w-64 rounded-lg border border-line bg-surface p-3 shadow-xl"
    >
      <div className="mb-2 flex items-center justify-between">
        <button
          onClick={() => shiftMonth(-1)}
          aria-label="Previous month"
          className="grid size-8 place-items-center rounded hover:bg-paper"
        >
          ‹
        </button>
        <p className="text-sm font-medium">
          {view.toLocaleDateString(undefined, {
            month: "long",
            year: "numeric",
          })}
        </p>
        <button
          onClick={() => shiftMonth(1)}
          aria-label="Next month"
          className="grid size-8 place-items-center rounded hover:bg-paper"
        >
          ›
        </button>
      </div>
      <div className="grid grid-cols-7 text-center text-xs text-muted">
        {cells.slice(0, 7).map((d, i) => (
          <span key={i} className="py-1">
            {d.toLocaleDateString(undefined, { weekday: "narrow" })}
          </span>
        ))}
      </div>
      <div className="grid grid-cols-7">
        {cells.map((d) => {
          const iso = toISODate(d);
          return (
            <button
              key={iso}
              onClick={() => onSelect(d)}
              aria-label={d.toLocaleDateString(undefined, {
                dateStyle: "full",
              })}
              aria-current={iso === todayISO ? "date" : undefined}
              className={`h-8 text-sm ${selectedWeek.has(iso) ? "bg-accent-soft" : "hover:bg-paper"} ${
                d.getMonth() !== view.getMonth() ? "text-muted/60" : ""
              } ${iso === todayISO ? "font-bold text-accent" : ""}`}
            >
              {d.getDate()}
            </button>
          );
        })}
      </div>
    </div>
  );
}
