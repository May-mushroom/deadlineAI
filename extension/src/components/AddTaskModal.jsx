import { useState } from "react";

export default function AddTaskModal({ categories, onCancel, onSave }) {
  const [title, setTitle] = useState("");
  const [deadline, setDeadline] = useState("");
  const [description, setDescription] = useState("");
  const [importance, setImportance] = useState(5);
  const [category, setCategory] = useState(categories[0]?.name ?? "");

  const handleSave = () => {
    if (!title.trim()) return;
    onSave({
      title: title.trim(),
      category,
      // backend's TaskRequest field is named `deadlines` (not `deadline`)
      deadlines: deadline,
      description,
      importance: Number(importance),
    });
  };

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h2>Add New Task</h2>
          <button className="icon-btn" aria-label="Close" onClick={onCancel}>
            ✕
          </button>
        </div>

        <label className="field">
          <span className="field__label">Title</span>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Task title"
            autoFocus
          />
        </label>

        <label className="field">
          <span className="field__label">
            Deadline (optional — defaults to end of this week)
          </span>
          <input
            type="date"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          />
        </label>

        <label className="field">
          <span className="field__label">Description</span>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional details"
          />
        </label>

        <label className="field">
          <span className="field__label">Importance ({importance})</span>
          <input
            type="range"
            min="0"
            max="10"
            value={importance}
            onChange={(e) => setImportance(e.target.value)}
          />
        </label>

        <label className="field">
          <span className="field__label">Category</span>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            {categories.map((c) => (
              <option key={c.id} value={c.name}>
                {c.name}
              </option>
            ))}
          </select>
        </label>

        <div className="modal__actions">
          <button className="btn" onClick={onCancel}>
            Cancel
          </button>
          <button className="btn btn--primary" onClick={handleSave}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
