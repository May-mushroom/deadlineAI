import { useState } from 'react'
import Header from './components/Header.jsx'
import WeekPage from './components/WeekPage.jsx'
import TodayPage from './components/TodayPage.jsx'
import SettingsPage from './components/SettingsPage.jsx'
import AddTaskModal from './components/AddTaskModal.jsx'
import { MOCK_TASKS, CATEGORIES } from './data/mockData.js'

const PAGES = { WEEK: 'week', TODAY: 'today', SETTINGS: 'settings' }

export default function App() {
  const [page, setPage] = useState(PAGES.WEEK)
  const [menuOpen, setMenuOpen] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [tasks, setTasks] = useState(MOCK_TASKS)
  const [categories, setCategories] = useState(CATEGORIES)
  const [weekOffset, setWeekOffset] = useState(0)

  const toggleTask = (id) => {
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, done: !t.done } : t)))
  }

  const deleteTask = (id) => {
    setTasks((prev) => prev.filter((t) => t.id !== id))
  }

  const addTask = (newTask) => {
    setTasks((prev) => [...prev, { ...newTask, id: `t${Date.now()}`, done: false }])
    setModalOpen(false)
  }

  const handleDistribute = () => {
    // TODO (business logic): distribute Task Pool items across the week's
    // days, e.g. based on importance + category priority + deadline
    // proximity. Currently a no-op stub.
    console.log('Distribute tasks clicked — not yet implemented')
  }

  const handleClose = () => {
    // TODO (platform specifics): see notes in public/background.js.
    if (window.close) window.close()
  }

  const updateCategory = (id, updates) => {
    setCategories((prev) => prev.map((c) => (c.id === id ? { ...c, ...updates } : c)))
  }

  const addCategory = (category) => {
    setCategories((prev) => [...prev, { ...category, id: `c${Date.now()}` }])
  }

  const deleteCategory = (id) => {
    setCategories((prev) => prev.filter((c) => c.id !== id))
  }

  return (
    <div className="app">
      <Header
        page={page}
        setPage={setPage}
        menuOpen={menuOpen}
        setMenuOpen={setMenuOpen}
        onClose={handleClose}
      />

      <main className="app__content">
        {page === PAGES.WEEK && (
          <WeekPage
            tasks={tasks}
            weekOffset={weekOffset}
            setWeekOffset={setWeekOffset}
            onToggleTask={toggleTask}
            onDeleteTask={deleteTask}
            onAddClick={() => setModalOpen(true)}
            onDistribute={handleDistribute}
          />
        )}

        {page === PAGES.TODAY && (
          <TodayPage
            tasks={tasks}
            onToggleTask={toggleTask}
            onDeleteTask={deleteTask}
            onAddClick={() => setModalOpen(true)}
          />
        )}

        {page === PAGES.SETTINGS && (
          <SettingsPage
            categories={categories}
            onUpdate={updateCategory}
            onAdd={addCategory}
            onDelete={deleteCategory}
          />
        )}
      </main>

      {modalOpen && (
        <AddTaskModal
          categories={categories}
          onCancel={() => setModalOpen(false)}
          onSave={addTask}
        />
      )}
    </div>
  )
}
