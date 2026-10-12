import { api } from "./api";

// Backend Task -> shape used by the UI.
const fromApi = (t) => ({
  id: t.task_id,
  title: t.title,
  category: t.category,
  importance: t.importance,
  description: t.description,
  note: t.note,
  src: t.src,
  status: t.status,
  done: t.status === 3,
  date: t.scheduled_date, // "YYYY-MM-DD", or null for a week pool task
  poolWeek: t.pool_week_start, // Monday of the pool week, or null once the task has a day
});

// Form values -> TaskRequest. Send a specific day or a pool week, never both.
const toBody = (v) => ({
  title: v.title,
  category: v.category,
  importance: v.importance,
  description: v.description,
  note: v.note,
  scheduled_date: v.scheduledDate || null,
  pool_week: v.scheduledDate ? null : v.poolWeek || null,
});

const json = (method, body) => ({ method, body: JSON.stringify(body) });

export const fetchWeek = async (weekStart) =>
  (await api(`/task/week?week_start=${weekStart}`)).map(fromApi);
export const addTask = (v) =>
  api(
    `/task/add/${v.scheduledDate ? "specific" : "pool"}`,
    json("POST", toBody(v)),
  );
export const updateTask = (id, v) =>
  api(`/task/${id}`, json("PATCH", toBody(v)));
export const setDone = (id, done) =>
  api(`/task/${id}/done`, json("PATCH", { done }));
export const deleteTask = (id) =>
  api(`/task/delete/${id}`, { method: "DELETE" });
