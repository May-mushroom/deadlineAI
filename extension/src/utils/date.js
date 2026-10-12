// Small date helpers for the Week/Today pages.
// TODO: swap for a real date library if week logic grows more complex.

export function getWeekRange(offsetWeeks = 0) {
  const now = new Date()
  const dayOfWeek = now.getDay() // 0 = Sunday
  const start = new Date(now)
  start.setDate(now.getDate() - dayOfWeek + offsetWeeks * 7)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return { start, end }
}

export function formatDate(date) {
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function formatDayLabel(date = new Date()) {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  })
}
