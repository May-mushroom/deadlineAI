// Small date helpers for the Week/Today pages.
// TODO: swap for a real date library if week logic grows more complex.

export function getWeekRange(offsetWeeks = 0) {
  const now = new Date();
  const dayOfWeek = now.getDay(); // 0 = Sunday ... 6 = Saturday
  const daysSinceMonday = (dayOfWeek + 6) % 7; // Mon=0, Tue=1, ..., Sun=6
  const start = new Date(now);
  start.setDate(now.getDate() - daysSinceMonday + offsetWeeks * 7);
  const end = new Date(start);
  end.setDate(start.getDate() + 6); // Sunday
  return { start, end };
}

export function formatDate(date) {
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function toISODate(date) {
  return date.toISOString().slice(0, 10); // YYYY-MM-DD
}

export function formatShortDayLabel(date) {
  return date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

export function formatDayLabel(date = new Date()) {
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
}
