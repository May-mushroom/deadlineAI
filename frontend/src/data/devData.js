// Mock data for development. Dates are relative to the current week so the UI always has content.
import { addDays, startOfWeek, toISODate } from "../lib/dates";

const weekStart = startOfWeek();
const day = (offset) => toISODate(addDays(weekStart, offset)); // 0 = Sunday
const today = toISODate(new Date());

// Calendar events (read-only for now; they will come from Google Calendar).
export const events = [
  { id: "e1", title: "Team standup", date: day(1), start: "09:30", end: "10:00" },
  { id: "e2", title: "Design review", date: day(1), start: "14:00", end: "15:30" },
  { id: "e3", title: "1:1 with Sam", date: day(2), start: "11:00", end: "12:00" },
  { id: "e4", title: "Team standup", date: day(3), start: "09:30", end: "10:00" },
  { id: "e5", title: "Lunch with Priya", date: day(3), start: "13:00", end: "14:00" },
  { id: "e6", title: "Sprint planning", date: day(4), start: "16:00", end: "17:30" },
  { id: "e7", title: "Client call", date: day(5), start: "10:00", end: "11:30" },
  { id: "e8", title: "Gym", date: day(6), start: "10:00", end: "11:00" },
];

// Tasks. date === null means the task is in the task pool.
export const tasks = [
  { id: "t1", title: "Reply to Acme proposal", description: "", date: today, done: false },
  { id: "t2", title: "Book dentist appointment", description: "", date: today, done: true },
  { id: "t3", title: "Prepare sprint demo", description: "Slides and a short live walkthrough", date: day(4), done: false },
  { id: "t4", title: "Submit expense report", description: "", date: day(5), done: false },
  { id: "t5", title: "Read the onboarding doc", description: "", date: null, done: false },
  { id: "t6", title: "Renew passport", description: "", date: null, done: false },
];
