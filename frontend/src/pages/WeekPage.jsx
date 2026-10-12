import WeekCalendar from "../components/WeekCalendar";

export default function WeekPage({
  tasks,
  events,
  anchor,
  onAnchorChange,
  onAdd,
  onEdit,
  onToggle,
  onDistribute,
}) {
  return (
    <div className="h-[calc(100vh-8.5rem)] min-h-[32rem]">
      <WeekCalendar
        anchor={anchor}
        onAnchorChange={onAnchorChange}
        events={events}
        tasks={tasks}
        onAddTask={onAdd}
        onEditTask={onEdit}
        onToggleTask={onToggle}
        onDistribute={onDistribute}
      />
    </div>
  );
}
