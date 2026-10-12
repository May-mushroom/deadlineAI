import TaskItem from './TaskItem.jsx'

// Task Pool list, with the "+" add-task row as its last item, as requested:
//   [ ] task 1
//   [ + ]
export default function TaskPool({ tasks, onToggleTask, onDeleteTask, onAddClick }) {
  return (
    <section className="task-pool">
      <h2 className="task-pool__title">Task Pool</h2>
      <ul className="task-pool__list">
        {tasks.map((task) => (
          <TaskItem key={task.id} task={task} onToggle={onToggleTask} onDelete={onDeleteTask} />
        ))}
        <li className="task-item task-item--add">
          <button className="task-item__add-btn" onClick={onAddClick} aria-label="Add task">
            +
          </button>
        </li>
      </ul>
    </section>
  )
}
