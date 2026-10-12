import { useCallback, useEffect, useRef, useState } from "react";
import { startOfWeek, toISODate } from "../lib/dates";
import {
  addTask,
  deleteTask,
  fetchWeek,
  setDone,
  updateTask,
} from "../lib/taskApi";

// Tasks live in the backend. We hold this week (Today page) and the viewed week (Week page),
// and refetch after every change so the UI always shows what is in the database.
export function useTasks(anchor) {
  const currentWeek = toISODate(startOfWeek());
  const viewedWeek = toISODate(startOfWeek(anchor));
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);
  const latest = useRef(0); // ignore responses that arrive after a newer request

  const reload = useCallback(async () => {
    const id = ++latest.current;
    try {
      const weeks = [...new Set([currentWeek, viewedWeek])];
      const loaded = (await Promise.all(weeks.map(fetchWeek))).flat();
      if (id === latest.current) {
        setTasks(loaded);
        setError(null);
      }
    } catch (e) {
      if (id === latest.current) setError(e.message);
    }
  }, [currentWeek, viewedWeek]);

  useEffect(() => {
    reload();
  }, [reload]);

  // Run a change, then reload. Resolves true on success so a dialog can close itself.
  const mutate = async (change) => {
    try {
      await change();
      await reload();
      return true;
    } catch (e) {
      setError(e.message);
      return false;
    }
  };

  return {
    tasks,
    error,
    reload,
    add: (values) => mutate(() => addTask(values)),
    update: (id, values) => mutate(() => updateTask(id, values)),
    remove: (id) => mutate(() => deleteTask(id)),
    toggle: (id) => {
      const task = tasks.find((t) => t.id === id);
      return task
        ? mutate(() => setDone(id, !task.done))
        : Promise.resolve(false);
    },
  };
}
