// Placeholder data so the UI has something to render.
// TODO: replace with chrome.storage.sync/local-backed state (see README).

export const CATEGORIES = [
  { id: 'work', name: 'Work', priority: 3 },
  { id: 'personal', name: 'Personal', priority: 2 },
  { id: 'study', name: 'Study', priority: 4 },
]

export const MOCK_TASKS = [
  {
    id: 't1',
    title: 'Finish quarterly report',
    deadline: '2026-10-14',
    description: '',
    importance: 4,
    category: 'work',
    done: false,
    day: null, // null = unassigned (sits in the pool); TODO: used by "Distribute"
  },
  {
    id: 't2',
    title: 'Book dentist appointment',
    deadline: '2026-10-12',
    description: '',
    importance: 2,
    category: 'personal',
    done: false,
    day: null,
  },
  {
    id: 't3',
    title: 'Read chapter 5',
    deadline: '2026-10-15',
    description: '',
    importance: 3,
    category: 'study',
    done: false,
    day: null,
  },
]
