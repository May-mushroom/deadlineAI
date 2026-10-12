export default function TaskItem({ task, onToggle, onDelete }) {
  return (
    <li className="task-item">
      <label className="task-item__label">
        <input
          type="checkbox"
          checked={task.done}
          onChange={() => onToggle(task.id)}
        />
        <span className={`task-item__title${task.done ? ' is-done' : ''}`}>
          {task.title}
        </span>
      </label>
      <button
        className="task-item__delete"
        aria-label={`Delete ${task.title}`}
        onClick={() => onDelete(task.id)}
      >
        🗑
      </button>
    </li>
  )
}
