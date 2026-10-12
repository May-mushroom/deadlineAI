import { useEffect, useRef, useState } from "react";
import CheckButton from "./CheckButton";
import MonthPicker from "./MonthPicker";
import {
  addDays,
  hourLabel,
  toISODate,
  toMinutes,
  weekDays,
  weekTitle,
} from "../lib/dates";

const HOUR_H = 48; // keep in sync with the Tailwind h-12 on hour rows
const HOURS = Array.from({ length: 24 }, (_, i) => i);
const COLS = "grid grid-cols-[3.5rem_repeat(7,minmax(0,1fr))]";
const SWIPE_PX = 80; // touch distance that counts as a swipe
const WHEEL_PX = 120; // accumulated trackpad distance that counts as a swipe
const navBtn = "grid size-8 place-items-center rounded hover:bg-paper";

// Can the grid still scroll horizontally in this direction (-1 left, 1 right)?
// Swiping only changes the week once the grid is at its edge (matters on narrow screens).
const canScrollX = (el, dir) =>
  dir < 0
    ? el.scrollLeft > 0
    : el.scrollLeft + el.clientWidth < el.scrollWidth - 1;

function TaskChip({ task, onEdit, onToggle, className = "" }) {
  return (
    <div
      className={`flex items-center gap-1 rounded bg-paper px-1 py-0.5 text-xs ${className}`}
    >
      <CheckButton
        done={task.done}
        onClick={() => onToggle(task.id)}
        label={`Mark "${task.title}" ${task.done ? "incomplete" : "complete"}`}
      />
      <button
        onClick={() => onEdit(task)}
        className={`min-w-0 flex-1 truncate text-left ${task.done ? "text-muted line-through" : ""}`}
      >
        {task.title}
      </button>
    </div>
  );
}

// Google Calendar style week grid. Pass `tasks` to show the task row under the day headers.
export default function WeekCalendar({
  anchor,
  onAnchorChange,
  events,
  tasks,
  onAddTask,
  onEditTask,
  onToggleTask,
  onDistribute,
}) {
  const scroller = useRef(null);
  const touch = useRef(null);
  const wheel = useRef({ sum: 0, last: 0, lockedUntil: 0 });
  const [pickerOpen, setPickerOpen] = useState(false);

  useEffect(() => {
    scroller.current.scrollTop = 7 * HOUR_H;
  }, []);

  const days = weekDays(anchor);
  const now = new Date();
  const todayISO = toISODate(now);
  const nowTop = ((now.getHours() * 60 + now.getMinutes()) / 60) * HOUR_H;
  const isCurrentWeek = days.some((d) => toISODate(d) === todayISO);
  const weekISO = toISODate(days[0]); // Monday, matches the backend's pool_week_start

  const shiftWeek = (n) => onAnchorChange(addDays(anchor, n * 7));

  const onWheel = (e) => {
    if (Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return; // vertical scroll
    const dir = Math.sign(e.deltaX);
    if (canScrollX(scroller.current, dir)) return; // let the grid scroll first
    const w = wheel.current;
    const t = Date.now();
    if (t < w.lockedUntil) return; // ignore trackpad inertia after a change
    if (t - w.last > 200) w.sum = 0;
    w.last = t;
    w.sum += e.deltaX;
    if (Math.abs(w.sum) > WHEEL_PX) {
      shiftWeek(dir);
      w.sum = 0;
      w.lockedUntil = t + 600;
    }
  };

  const onTouchStart = (e) => {
    const { clientX: x, clientY: y } = e.touches[0];
    touch.current = {
      x,
      y,
      left: canScrollX(scroller.current, -1),
      right: canScrollX(scroller.current, 1),
    };
  };

  const onTouchEnd = (e) => {
    const s = touch.current;
    if (!s) return;
    const dx = e.changedTouches[0].clientX - s.x;
    const dy = e.changedTouches[0].clientY - s.y;
    if (Math.abs(dx) < SWIPE_PX || Math.abs(dx) < 2 * Math.abs(dy)) return;
    if (dx < 0 && !s.right) shiftWeek(1);
    if (dx > 0 && !s.left) shiftWeek(-1);
  };

  return (
    <section className="flex h-full flex-col rounded-lg border border-line bg-surface">
      <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
        <div className="relative">
          <h2 className="text-lg font-semibold">
            <button
              onClick={() => setPickerOpen((o) => !o)}
              aria-haspopup="dialog"
              aria-expanded={pickerOpen}
              className="-ml-2 flex items-center gap-1 rounded px-2 py-1 hover:bg-paper"
            >
              {weekTitle(days)}
              <span aria-hidden className="text-sm text-muted">
                ▾
              </span>
            </button>
          </h2>
          {pickerOpen && (
            <MonthPicker
              selected={anchor}
              onSelect={(d) => {
                onAnchorChange(d);
                setPickerOpen(false);
              }}
              onClose={() => setPickerOpen(false)}
            />
          )}
        </div>
        <div className="flex items-center gap-1">
          {onDistribute && (
            <button
              onClick={onDistribute}
              className="mr-1 rounded border border-line px-3 py-1 text-sm hover:bg-paper"
            >
              Distribute tasks
            </button>
          )}
          <button
            disabled={isCurrentWeek}
            onClick={() => onAnchorChange(new Date())}
            className="mr-1 rounded border border-line px-3 py-1 text-sm hover:bg-paper disabled:pointer-events-none disabled:opacity-50"
          >
            Today
          </button>
          <button
            onClick={() => shiftWeek(-1)}
            aria-label="Previous week"
            className={navBtn}
          >
            ‹
          </button>
          <button
            onClick={() => shiftWeek(1)}
            aria-label="Next week"
            className={navBtn}
          >
            ›
          </button>
        </div>
      </div>

      <div
        ref={scroller}
        onWheel={onWheel}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
        className="min-h-0 flex-1 overflow-auto overscroll-x-contain border-t border-line"
      >
        <div className="min-w-[44rem]">
          <div className="sticky top-0 z-10 border-b border-line bg-surface">
            <div className={COLS}>
              <div />
              {days.map((d) => (
                <div
                  key={d.getTime()}
                  className="border-l border-line py-2 text-center"
                >
                  <p className="text-xs text-muted">
                    {d.toLocaleDateString(undefined, { weekday: "short" })}
                  </p>
                  <p
                    className={`mx-auto mt-0.5 grid size-8 place-items-center rounded-full text-lg ${
                      toISODate(d) === todayISO ? "bg-accent text-white" : ""
                    }`}
                  >
                    {d.getDate()}
                  </p>
                </div>
              ))}
            </div>

            {tasks && (
              <>
                <div className={`${COLS} border-t border-line`}>
                  <p className="p-2 text-right text-xs text-muted">Tasks</p>
                  {days.map((d) => {
                    const iso = toISODate(d);
                    return (
                      <div
                        key={iso}
                        className="space-y-1 border-l border-line p-1"
                      >
                        {tasks
                          .filter((t) => t.date === iso)
                          .map((t) => (
                            <TaskChip
                              key={t.id}
                              task={t}
                              onEdit={onEditTask}
                              onToggle={onToggleTask}
                            />
                          ))}
                        <button
                          onClick={() => onAddTask({ scheduledDate: iso })}
                          aria-label={`Add task on ${iso}`}
                          className="w-full rounded text-sm text-muted hover:bg-paper"
                        >
                          +
                        </button>
                      </div>
                    );
                  })}
                </div>
                <div className={`${COLS} border-t border-line`}>
                  <p className="p-2 text-right text-xs text-muted">Pool</p>
                  <div className="col-span-7 flex flex-wrap items-center gap-1 border-l border-line p-1">
                    {tasks
                      .filter((t) => t.poolWeek === weekISO)
                      .map((t) => (
                        <TaskChip
                          key={t.id}
                          task={t}
                          onEdit={onEditTask}
                          onToggle={onToggleTask}
                          className="max-w-[14rem]"
                        />
                      ))}
                    <button
                      onClick={() => onAddTask({ poolWeek: weekISO })}
                      aria-label="Add task to this week's pool"
                      className="rounded px-2 text-sm text-muted hover:bg-paper"
                    >
                      +
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className={COLS}>
            <div>
              {HOURS.map((h) => (
                <div
                  key={h}
                  className="h-12 -translate-y-2 pr-2 text-right text-xs text-muted"
                >
                  {h ? hourLabel(h) : ""}
                </div>
              ))}
            </div>
            {days.map((d) => {
              const iso = toISODate(d);
              return (
                <div key={iso} className="relative border-l border-line">
                  {HOURS.map((h) => (
                    <div key={h} className="h-12 border-b border-line" />
                  ))}
                  {events
                    .filter((e) => e.date === iso)
                    .map((e) => {
                      const start = toMinutes(e.start);
                      const height =
                        ((toMinutes(e.end) - start) / 60) * HOUR_H - 2;
                      return (
                        <div
                          key={e.id}
                          className="absolute inset-x-0.5 overflow-hidden rounded border-l-4 border-accent bg-accent-soft px-1.5 py-0.5 text-xs"
                          style={{
                            top: (start / 60) * HOUR_H,
                            height: Math.max(height, 18),
                          }}
                        >
                          <p className="truncate font-medium">{e.title}</p>
                          <p className="truncate text-muted">
                            {e.start}–{e.end}
                          </p>
                        </div>
                      );
                    })}
                  {iso === todayISO && (
                    <div
                      className="pointer-events-none absolute inset-x-0 border-t-2 border-late"
                      style={{ top: nowTop }}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
