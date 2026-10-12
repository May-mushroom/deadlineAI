import TaskItem from "./TaskItem";

function Section({ title, addLabel, empty, tasks, onAdd, ...handlers }) {
  return (
    <section>
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">{title}</h2>
        <button
          onClick={onAdd}
          className="rounded px-2 py-1 text-sm text-accent hover:bg-accent-soft"
        >
          {addLabel}
        </button>
      </div>
      {tasks.length === 0 ? (
        <p className="px-2 py-3 text-sm text-muted">{empty}</p>
      ) : (
        <ul className="mt-1">
          {tasks.map((t) => (
            <TaskItem key={t.id} task={t} {...handlers} />
          ))}
        </ul>
      )}
    </section>
  );
}

export default function TaskList({
  tasks,
  todayISO,
  weekStart,
  onAdd,
  ...handlers
}) {
  return (
    <div className="space-y-6 rounded-lg border border-line bg-surface p-4 lg:max-h-[calc(100vh-8.5rem)] lg:overflow-y-auto">
      <Section
        title="Today"
        addLabel="Add task"
        empty="Nothing planned for today. Add a task to get started."
        tasks={tasks.filter((t) => t.date === todayISO)}
        onAdd={() => onAdd({ scheduledDate: todayISO })}
        {...handlers}
      />
      <Section
        title="This week's pool"
        addLabel="Add to pool"
        empty="No unscheduled tasks. Add one to the pool."
        tasks={tasks.filter((t) => t.poolWeek === weekStart)}
        onAdd={() => onAdd({ poolWeek: weekStart })}
        {...handlers}
      />
    </div>
  );
}
