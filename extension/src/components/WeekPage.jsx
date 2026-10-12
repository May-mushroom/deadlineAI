import TaskPool from './TaskPool.jsx'
import { getWeekRange, formatDate } from '../utils/date.js'

export default function WeekPage({
  tasks,
  weekOffset,
  setWeekOffset,
  onToggleTask,
  onDeleteTask,
  onAddClick,
  onDistribute,
}) {
  const { start, end } = getWeekRange(weekOffset)

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
        tasks={tasks}
        onToggleTask={onToggleTask}
        onDeleteTask={onDeleteTask}
        onAddClick={onAddClick}
      />

      <button className="btn btn--primary btn--block" onClick={onDistribute}>
        Distribute Tasks
      </button>
    </div>
  )
}
