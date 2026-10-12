import { useEffect, useState } from "react";
import { addDays, startOfWeek, toISODate } from "../lib/dates";

const field = "mt-1 block w-full rounded border border-line px-3 py-2";
const WEEKS_AHEAD = 12;
const shortDate = (d) =>
  d.toLocaleDateString(undefined, { month: "short", day: "numeric" });

// This week plus the next 11, and the task's own week if it is outside that range.
function weekOptions(selected) {
  const start = startOfWeek();
  const weeks = Array.from({ length: WEEKS_AHEAD }, (_, i) =>
    toISODate(addDays(start, i * 7)),
  );
  if (selected && !weeks.includes(selected)) weeks.push(selected);
  return weeks.sort().map((iso) => {
    const first = new Date(`${iso}T00:00`);
    const range = `${shortDate(first)} – ${shortDate(addDays(first, 6))}`;
    const offset = Math.round((first - start) / (7 * 864e5));
    const prefix = offset === 0 ? "This week" : offset === 1 ? "Next week" : "";
    return { iso, label: prefix ? `${prefix} (${range})` : range };
  });
}

// Add (no `task`) or edit (`task`) dialog. `defaults` pre-fills { scheduledDate } or { poolWeek } when adding.
export default function TaskForm({
  task,
  defaults = {},
  error,
  onSave,
  onDelete,
  onClose,
}) {
  const start = task
    ? { scheduledDate: task.date, poolWeek: task.poolWeek }
    : defaults;
  const [mode, setMode] = useState(start.scheduledDate ? "specific" : "pool");
  const [scheduledDate, setScheduledDate] = useState(start.scheduledDate ?? "");
  const [poolWeek, setPoolWeek] = useState(
    start.poolWeek ?? toISODate(startOfWeek()),
  );
  const [title, setTitle] = useState(task?.title ?? "");
  const [category, setCategory] = useState(task?.category ?? "");
  const [importance, setImportance] = useState(task?.importance ?? 5);
  const [description, setDescription] = useState(task?.description ?? "");
  const [note, setNote] = useState(task?.note ?? "");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const submit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    setSaving(true);
    await onSave({
      title: title.trim(),
      category: category.trim(),
      importance,
      description: description.trim(),
      note: note.trim(),
      scheduledDate: mode === "specific" ? scheduledDate : null,
      poolWeek: mode === "pool" ? poolWeek : null,
    });
    setSaving(false);
  };

  return (
    <div
      className="fixed inset-0 z-20 grid place-items-center bg-ink/40 p-4"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <form
        role="dialog"
        aria-modal="true"
        aria-labelledby="task-form-title"
        onSubmit={submit}
        className="max-h-[90vh] w-full max-w-md space-y-4 overflow-y-auto rounded-lg bg-surface p-5 shadow-xl"
      >
        <h2 id="task-form-title" className="text-lg font-semibold">
          {task ? "Edit task" : "Add task"}
        </h2>

        <label className="block text-sm">
          Title
          <input
            autoFocus
            required
            maxLength={100}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className={field}
          />
        </label>

        <fieldset>
          <legend className="text-sm">When</legend>
          <div
            role="group"
            className="mt-1 grid grid-cols-2 gap-1 rounded bg-paper p-1"
          >
            {[
              ["specific", "Specific day"],
              ["pool", "Week pool"],
            ].map(([id, label]) => (
              <button
                key={id}
                type="button"
                aria-pressed={mode === id}
                onClick={() => setMode(id)}
                className={`rounded px-3 py-1.5 text-sm ${mode === id ? "bg-surface font-medium shadow-sm" : "text-muted"}`}
              >
                {label}
              </button>
            ))}
          </div>
          {mode === "specific" ? (
            <label className="mt-3 block text-sm">
              Date
              <input
                type="date"
                required
                value={scheduledDate}
                onChange={(e) => setScheduledDate(e.target.value)}
                className={field}
              />
            </label>
          ) : (
            <label className="mt-3 block text-sm">
              Week
              <select
                value={poolWeek}
                onChange={(e) => setPoolWeek(e.target.value)}
                className={field}
              >
                {weekOptions(poolWeek).map((w) => (
                  <option key={w.iso} value={w.iso}>
                    {w.label}
                  </option>
                ))}
              </select>
            </label>
          )}
        </fieldset>

        <div className="grid grid-cols-2 gap-3">
          <label className="block text-sm">
            Category
            <input
              maxLength={100}
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className={field}
            />
          </label>
          <label className="block text-sm">
            Importance: <span className="font-medium">{importance}</span>/10
            <input
              type="range"
              min={0}
              max={10}
              value={importance}
              onChange={(e) => setImportance(Number(e.target.value))}
              className="mt-3 block w-full accent-accent"
            />
          </label>
        </div>

        <label className="block text-sm">
          Description
          <textarea
            rows={2}
            maxLength={100}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={field}
          />
        </label>
        <label className="block text-sm">
          Note
          <input
            maxLength={100}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className={field}
          />
        </label>

        {error && (
          <p role="alert" className="text-sm text-late">
            {error}
          </p>
        )}

        <div className="flex items-center gap-2">
          {task && (
            <button
              type="button"
              onClick={onDelete}
              className="mr-auto rounded px-3 py-2 text-sm text-late hover:bg-paper"
            >
              Delete task
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            className="ml-auto rounded px-3 py-2 text-sm hover:bg-paper"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="rounded bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {task ? "Save changes" : "Add task"}
          </button>
        </div>
      </form>
    </div>
  );
}
