import React from 'react';

export default function ShortcutsModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const shortcuts = [
    { key: '/', desc: 'Focus global search input' },
    { key: 'C', desc: 'Open New Ticket modal' },
    { key: 'J', desc: 'Select next ticket down the queue' },
    { key: 'K', desc: 'Select previous ticket up the queue' },
    { key: 'D', desc: 'Toggle Dark Mode / Day Mode theme' },
    { key: '?', desc: 'Show keyboard shortcuts helper' },
    { key: 'Esc', desc: 'Close modals / clear selection' },
  ];

  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-dialog modal-dialog-sm" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <h3>Keyboard Shortcuts</h3>
            <span className="modal-subtitle">Power-agent hotkeys for rapid customer resolution</span>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close dialog">
            ×
          </button>
        </div>

        <div className="shortcuts-list">
          {shortcuts.map((s, idx) => (
            <div key={idx} className="shortcut-item">
              <span>{s.desc}</span>
              <kbd>{s.key}</kbd>
            </div>
          ))}
        </div>

        <div className="modal-footer" style={{ marginTop: '12px' }}>
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
