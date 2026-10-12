import TaskPool from './TaskPool.jsx'
import { formatDayLabel } from '../utils/date.js'

export default function TodayPage({ tasks, onToggleTask, onDeleteTask, onAddClick }) {
  return (
    <div className="page">
      <div className="today-label">Day: {formatDayLabel()}</div>
      <TaskPool
        tasks={tasks}
        onToggleTask={onToggleTask}
        onDeleteTask={onDeleteTask}
        onAddClick={onAddClick}
      />
    </div>
  )
}
