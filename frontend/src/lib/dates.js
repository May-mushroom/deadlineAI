export const toISODate = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

export const addDays = (d, n) => {
  const x = new Date(d);
  x.setDate(x.getDate() + n);
  return x;
};

// Weeks start on Monday, matching the backend (TaskDistribution.day_of_week: 0 = Monday).
export const startOfWeek = (d = new Date()) =>
  addDays(
    new Date(d.getFullYear(), d.getMonth(), d.getDate()),
    -((d.getDay() + 6) % 7),
  );

export const weekDays = (d = new Date()) => {
  const start = startOfWeek(d);
  return Array.from({ length: 7 }, (_, i) => addDays(start, i));
};

export const toMinutes = (hhmm) => {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
};

export const hourLabel = (h) =>
  h === 0 ? "12 AM" : h < 12 ? `${h} AM` : h === 12 ? "12 PM" : `${h - 12} PM`;

export const weekTitle = (days) => {
  const fmt = (d, o) => d.toLocaleDateString(undefined, o);
  const [first, last] = [days[0], days[6]];
  return first.getMonth() === last.getMonth()
    ? fmt(first, { month: "long", year: "numeric" })
    : `${fmt(first, { month: "short" })} – ${fmt(last, { month: "short", year: "numeric" })}`;
};
