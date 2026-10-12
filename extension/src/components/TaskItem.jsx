export default function TaskItem({ task, onToggle, onDelete }) {
  // status: 0 unassigned, 1 assigned, 2 pending, 3 done
  const isDone = task.status === 3;

  return (
    <li className="task-item">
      <label className="task-item__label">
        <input
          type="checkbox"
          checked={isDone}
          onChange={() => onToggle(task)}
        />
        <span className={`task-item__title${isDone ? " is-done" : ""}`}>
          {task.title}
        </span>
      </label>
      <button
        className="task-item__delete"
        aria-label={`Delete ${task.title}`}
        onClick={() => onDelete(task.task_id)}
      >
        🗑
      </button>
    </li>
  );
}
