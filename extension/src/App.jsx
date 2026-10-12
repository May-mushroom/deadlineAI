import { useCallback, useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import WeekPage from "./components/WeekPage.jsx";
import TodayPage from "./components/TodayPage.jsx";
import SettingsPage from "./components/SettingsPage.jsx";
import AddTaskModal from "./components/AddTaskModal.jsx";
import { CATEGORIES } from "./data/mockData.js";
import { getWeekRange, toISODate } from "./utils/date.js";
import * as api from "../../backend/app/api/client.js";

const PAGES = { WEEK: "week", TODAY: "today", SETTINGS: "settings" };

export default function App() {
  const [page, setPage] = useState(PAGES.WEEK);
  const [menuOpen, setMenuOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  // Which "+" opened the modal, and what the task should be created against:
  // { type: 'pool', weekStart: 'YYYY-MM-DD' } | { type: 'today', date: 'YYYY-MM-DD' }
  const [addContext, setAddContext] = useState(null);

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Categories stay local-only for now: there's no Category table backend
  // side yet, and the priority values are only meant to feed "Distribute",
  // which is intentionally left unimplemented.
  const [categories, setCategories] = useState(CATEGORIES);
  const [weekOffset, setWeekOffset] = useState(0);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (page === PAGES.WEEK) {
        const { start } = getWeekRange(weekOffset);
        setTasks(await api.getWeekTasks(toISODate(start)));
      } else if (page === PAGES.TODAY) {
        setTasks(await api.getTodayTasks(toISODate(new Date())));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [page, weekOffset]);

  useEffect(() => {
    if (page === PAGES.WEEK || page === PAGES.TODAY) loadTasks();
  }, [loadTasks, page]);

  const toggleTask = async (task) => {
    try {
      await api.setTaskDone(task.task_id, task.status !== 3);
      loadTasks();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await api.deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.task_id !== taskId));
    } catch (err) {
      setError(err.message);
    }
  };

  const openAddForPool = () => {
    const { start, end } = getWeekRange(weekOffset);
    setAddContext({
      type: "pool",
      weekStart: toISODate(start),
      weekEnd: toISODate(end),
    });
    setModalOpen(true);
  };

  // Used by both Today page's [+] and each Week-page day section's [+] —
  // both hit POST /task/add/specific with scheduled_date = dateIso.
  const openAddForDate = (dateIso, weekEndIso) => {
    setAddContext({ type: "specific", date: dateIso, weekEnd: weekEndIso });
    setModalOpen(true);
  };

  const openAddForToday = () => {
    // Today's page is always the actual current week, regardless of what
    // week the Week page happens to be scrolled to.
    const { end } = getWeekRange(0);
    openAddForDate(toISODate(new Date()), toISODate(end));
  };

  const openAddForDay = (dateIso) => {
    // Default deadline falls back to the end of whichever week is on screen.
    const { end } = getWeekRange(weekOffset);
    openAddForDate(dateIso, toISODate(end));
  };

  const addTask = async (form) => {
    try {
      // No deadline given → default to the end (Sunday) of the relevant week.
      const payload = {
        ...form,
        deadlines: form.deadlines || addContext.weekEnd,
      };
      if (addContext.type === "pool") {
        await api.createPoolTask(payload, addContext.weekStart);
      } else {
        await api.createSpecificDayTask(payload, addContext.date);
      }
      setModalOpen(false);
      loadTasks();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDistribute = () => {
    // TODO (business logic): distribute pool tasks across the week's days.
    console.log("Distribute tasks clicked — not yet implemented");
  };

  const handleClose = () => {
    // TODO: see notes in public/background.js
    if (window.close) window.close();
  };

  const updateCategory = (id, updates) => {
    setCategories((prev) =>
      prev.map((c) => (c.id === id ? { ...c, ...updates } : c)),
    );
  };

  const addCategory = (category) => {
    setCategories((prev) => [...prev, { ...category, id: `c${Date.now()}` }]);
  };

  const deleteCategory = (id) => {
    setCategories((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <div className="app">
      <Header
        page={page}
        setPage={setPage}
        menuOpen={menuOpen}
        setMenuOpen={setMenuOpen}
        onClose={handleClose}
      />

      <main className="app__content">
        {error && <div className="banner banner--error">{error}</div>}
        {loading && <div className="banner">Loading…</div>}

        {page === PAGES.WEEK && (
          <WeekPage
            tasks={tasks}
            weekOffset={weekOffset}
            setWeekOffset={setWeekOffset}
            onToggleTask={toggleTask}
            onDeleteTask={deleteTask}
            onAddToPool={openAddForPool}
            onAddToDay={openAddForDay}
            onDistribute={handleDistribute}
          />
        )}

        {page === PAGES.TODAY && (
          <TodayPage
            tasks={tasks}
            onToggleTask={toggleTask}
            onDeleteTask={deleteTask}
            onAddClick={openAddForToday}
          />
        )}

        {page === PAGES.SETTINGS && (
          <SettingsPage
            categories={categories}
            onUpdate={updateCategory}
            onAdd={addCategory}
            onDelete={deleteCategory}
          />
        )}
      </main>

      {modalOpen && (
        <AddTaskModal
          categories={categories}
          onCancel={() => setModalOpen(false)}
          onSave={addTask}
        />
      )}
    </div>
  );
}
