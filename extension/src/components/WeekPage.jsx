import TaskPool from "./TaskPool.jsx";
import {
  getWeekRange,
  formatDate,
  formatShortDayLabel,
  toISODate,
} from "../utils/date.js";

export default function WeekPage({
  tasks,
  weekOffset,
  setWeekOffset,
  onToggleTask,
  onDeleteTask,
  onAddToPool,
  onAddToDay,
  onDistribute,
}) {
  const { start, end } = getWeekRange(weekOffset);

  // Unscheduled (no scheduled_date) -> Task Pool. Scheduled -> that day's section.
  const poolTasks = tasks.filter((t) => !t.scheduled_date);
  const days = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(start);
    date.setDate(start.getDate() + i);
    const iso = toISODate(date);
    return {
      iso,
      label: formatShortDayLabel(date),
      tasks: tasks.filter((t) => t.scheduled_date === iso),
    };
  });

  return (
    <div className="page">
      <div className="week-nav">
        <button
          className="icon-btn"
          onClick={() => setWeekOffset((w) => w - 1)}
          aria-label="Previous week"
        >
          ‹
        </button>
        <span className="week-nav__range">
          {formatDate(start)} – {formatDate(end)}
        </span>
        <button
          className="icon-btn"
          onClick={() => setWeekOffset((w) => w + 1)}
          aria-label="Next week"
        >
          ›
        </button>
      </div>

      <TaskPool
        tasks={poolTasks}
        onToggleTask={onToggleTask}
        onDeleteTask={onDeleteTask}
        onAddClick={onAddToPool}
      />

      <section className="week-days">
        {days.map((day) => (
          <DaySection
            key={day.iso}
            label={day.label}
            tasks={day.tasks}
            onToggleTask={onToggleTask}
            onDeleteTask={onDeleteTask}
            onAddClick={() => onAddToDay(day.iso)}
          />
        ))}
      </section>

      <button className="btn btn--primary btn--block" onClick={onDistribute}>
        Distribute Tasks
      </button>
    </div>
  );
}
import TaskItem from "./TaskItem.jsx";

function DaySection({ label, tasks, onToggleTask, onDeleteTask, onAddClick }) {
  return (
    <div className="day-section">
      <div className="day-section__label">{label}</div>
      <ul className="day-section__list">
        {tasks.length === 0 && <li className="day-section__empty">No tasks</li>}
        {tasks.map((task) => (
          <TaskItem
            key={task.task_id}
            task={task}
            onToggle={onToggleTask}
            onDelete={onDeleteTask}
          />
        ))}
        <li className="task-item task-item--add">
          <button
            className="task-item__add-btn"
            onClick={onAddClick}
            aria-label={`Add task to ${label}`}
          >
            +
          </button>
        </li>
      </ul>
    </div>
  );
}
