// Minimal API client for the Task Planner backend.
// TODO: point this at your actual server (and env-ify it) before shipping.
const API_BASE_URL = "http://localhost:8000/api";

// TODO: no auth flow exists yet. Once there's a login/token step, read the
// stored token here (e.g. chrome.storage.local) and attach it below.
async function getAuthHeaders() {
  return {
    "Content-Type": "application/json",
    // Authorization: `Bearer ${token}`,
  };
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { ...(await getAuthHeaders()), ...(options.headers || {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `${options.method || "GET"} ${path} failed (${res.status}): ${text}`,
    );
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- READ ---------------------------------------------------------------

export function getWeekTasks(weekStartIso) {
  return request(`/task/week?week_start=${weekStartIso}`);
}

export function getTodayTasks(todayIso) {
  return request(`/task/today?today=${todayIso}`);
}

// --- CREATE ---------------------------------------------------------------
// `form` is { title, category, deadlines, description, importance }

export function createPoolTask(form, weekStartIso) {
  console.log(form);
  return request("/task/add/pool", {
    method: "POST",
    body: JSON.stringify({ ...form, pool_week: weekStartIso }),
  });
}

export function createSpecificDayTask(form, scheduledDateIso) {
  return request("/task/add/specific", {
    method: "POST",
    body: JSON.stringify({ ...form, scheduled_date: scheduledDateIso }),
  });
}

// --- UPDATE / DELETE -------------------------------------------------------

export function setTaskDone(taskId, done) {
  return request(`/task/${taskId}/done`, {
    method: "PATCH",
    body: JSON.stringify({ done }),
  });
}

export function deleteTask(taskId) {
  return request(`/task/delete/${taskId}`, { method: "DELETE" });
}
