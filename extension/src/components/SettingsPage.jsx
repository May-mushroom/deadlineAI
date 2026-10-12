import { useState } from 'react'

export default function SettingsPage({ categories, onUpdate, onAdd, onDelete }) {
  const [newName, setNewName] = useState('')

  const handleAdd = () => {
    if (!newName.trim()) return
    onAdd({ name: newName.trim(), priority: 1 })
    setNewName('')
  }

  return (
    <div className="page">
      <h2 className="page__title">Categories & Priority</h2>
      <ul className="category-list">
        {categories.map((cat) => (
          <li key={cat.id} className="category-item">
            <span className="category-item__name">{cat.name}</span>
            <input
              type="number"
              min="1"
              max="5"
              className="category-item__priority"
              value={cat.priority}
              onChange={(e) => onUpdate(cat.id, { priority: Number(e.target.value) })}
              aria-label={`${cat.name} priority`}
            />
            <button
              className="icon-btn"
              aria-label={`Delete ${cat.name}`}
              onClick={() => onDelete(cat.id)}
            >
              🗑
            </button>
          </li>
        ))}
      </ul>
      <div className="category-add">
        <input
          type="text"
          placeholder="New category name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <button className="btn" onClick={handleAdd}>
          + Add Category
        </button>
      </div>
    </div>
  )
}
