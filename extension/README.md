# Day Task Planner — Chrome Extension (UI only)

This is a Manifest V3 Chrome extension with a React + Vite side panel UI.
**Only the UI/interaction layer is implemented.** Data is in-memory React
state seeded from mock data — nothing is persisted yet, and the
"Distribute Tasks" button is a stub. See the `TODO` comments in
`src/App.jsx` and `public/background.js` for what's left.

## Setup

```bash
npm install
npm run build
```

This produces a `dist/` folder containing `manifest.json`, `background.js`,
`index.html`, and the bundled JS/CSS.

## Load into Chrome

1. Go to `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked" and select the `dist/` folder
4. Click the extension's toolbar icon to open the side panel

For active development, `npm run dev` runs Vite's dev server, but you'll
still need to `npm run build` and reload the unpacked extension in Chrome to
see changes reflected in the actual side panel (Vite's HMR doesn't apply
inside the extension context).

## Structure

```
public/
  manifest.json     MV3 manifest (side_panel + background service worker)
  background.js     Opens the side panel on toolbar click
src/
  main.jsx           React entry point
  App.jsx            Top-level state (pages, tasks, categories, modal)
  index.css          All styling (neutral gray, minimal)
  utils/date.js       Week-range / day-label helpers
  data/mockData.js    Placeholder tasks + categories
  components/
    Header.jsx         Hamburger menu + page title + close (✕) button
    WeekPage.jsx        Week nav, Task Pool, "Distribute Tasks" button
    TodayPage.jsx       Current day label + Task Pool
    TaskPool.jsx        Task list ending in a "[+]" add-task row
    TaskItem.jsx         Single checkbox task row
    AddTaskModal.jsx    Add-task form (title, deadline, description,
                        importance range, category dropdown)
    SettingsPage.jsx    Category list with editable priority + add/delete
```

## Known stubs / left for business logic

- **Distribute Tasks** (`App.jsx` → `handleDistribute`): currently just
  logs to console. Needs an actual algorithm to assign pool tasks to days
  (e.g. by importance, category priority, deadline proximity).
- **Close panel** (`App.jsx` → `handleClose`): calls `window.close()`.
  Chrome side panels don't have a universal "close yourself" API from
  inside the panel; if `window.close()` doesn't work on your Chrome
  version, you'll need to message `background.js` and use
  `chrome.sidePanel.setOptions({ tabId, enabled: false })` instead.
- **Switch-tab-closes-panel behavior**: not implemented. The manifest's
  global `side_panel.default_path` keeps the panel open across tabs by
  default. To close/reset per tab switch, manage panel registration
  per-tab from `background.js` via `chrome.tabs.onActivated`.
- **Persistence**: tasks/categories live only in React state and reset on
  reload. Swap `mockData.js` + `useState` for `chrome.storage.local` (or
  `.sync`) reads/writes.
- **Task → day assignment**: `task.day` exists on the task object but
  nothing sets it yet except being left `null` (unassigned/pool). Today's
  page currently shows all tasks; once Distribute is implemented, filter
  by `task.day === 'today'` (or similar) there.
