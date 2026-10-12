import TaskList from "../components/TaskList";
import WeekCalendar from "../components/WeekCalendar";
import { startOfWeek, toISODate } from "../lib/dates";

export default function TodayPage({
  tasks,
  events,
  anchor,
  onAnchorChange,
  onAdd,
  onEdit,
  onToggle,
  onDelete,
}) {
  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,2.2fr)]">
      <TaskList
        tasks={tasks}
        todayISO={toISODate(new Date())}
        weekStart={toISODate(startOfWeek())}
        onAdd={onAdd}
        onEdit={onEdit}
        onToggle={onToggle}
        onDelete={onDelete}
      />
      <div className="h-[calc(100vh-8.5rem)] min-h-[32rem]">
        <WeekCalendar
          anchor={anchor}
          onAnchorChange={onAnchorChange}
          events={events}
        />
      </div>
    </div>
  );
}
