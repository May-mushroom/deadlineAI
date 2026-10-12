import { useState } from "react";
import GoogleButton from "./components/GoogleButton";
import Navbar from "./components/Navbar";
import TaskForm from "./components/TaskForm";
import DashboardPage from "./pages/DashboardPage";
import TodayPage from "./pages/TodayPage";
import WeekPage from "./pages/WeekPage";
import { useGoogle } from "./hooks/useGoogle";
import { useTasks } from "./hooks/useTasks";

const PAGES = { today: TodayPage, week: WeekPage, dashboard: DashboardPage };

export default function App() {
  const [page, setPage] = useState("today");
  const [anchor, setAnchor] = useState(() => new Date()); // any date in the week being viewed
  const [form, setForm] = useState(null); // null | { task } to edit | { defaults } to add
  const { tasks, error, reload, add, update, remove, toggle } =
    useTasks(anchor);
  const google = useGoogle(anchor, reload);

  const save = async (values) => {
    const ok = form.task
      ? await update(form.task.id, values)
      : await add(values);
    if (ok) setForm(null);
  };
  const del = async () => {
    if (await remove(form.task.id)) setForm(null);
  };

  const Page = PAGES[page];
  const message = error || google.error;
  return (
    <>
      <Navbar page={page} onChange={setPage}>
        <GoogleButton
          connected={google.connected}
          busy={google.busy}
          onConnect={google.connect}
          onSync={google.sync}
        />
      </Navbar>
      {message && (
        <p role="alert" className="bg-late/10 px-6 py-2 text-sm text-late">
          {message}
        </p>
      )}
      <main className="p-6">
        <Page
          tasks={tasks}
          events={google.events}
          anchor={anchor}
          onAnchorChange={setAnchor}
          onAdd={(defaults) => setForm({ defaults })}
          onEdit={(task) => setForm({ task })}
          onToggle={toggle}
          onDelete={remove}
          onDistribute={() => {}} // TODO: trigger AI task distribution
        />
      </main>
      {form && (
        <TaskForm
          task={form.task}
          defaults={form.defaults}
          error={error}
          onSave={save}
          onDelete={del}
          onClose={() => setForm(null)}
        />
      )}
    </>
  );
}
