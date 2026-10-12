import CheckButton from "./CheckButton";

export default function TaskItem({ task, onToggle, onEdit, onDelete }) {
  return (
    <li className="group flex items-center gap-3 rounded px-2 py-2 hover:bg-paper">
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
      <button
        onClick={() => onDelete(task.id)}
        aria-label={`Delete "${task.title}"`}
        className="px-1 text-muted opacity-0 hover:text-late focus-visible:opacity-100 group-hover:opacity-100"
      >
        ×
      </button>
    </li>
  );
}
