// All backend calls go through /api, which Vite proxies to FastAPI in development.
// When Supabase Auth is wired up, attach the session token in the headers below.
export async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`;
    try {
      const { detail } = await res.json(); // FastAPI error body
      if (typeof detail === "string") message = detail;
      else if (Array.isArray(detail))
        message = detail.map((d) => d.msg).join(", ");
    } catch {
      /* keep the status text */
    }
    throw new Error(message);
  }
  return res.json();
}
