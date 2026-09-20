import React from 'react';

export default function Header({
  client,
  onClientChange,
  theme,
  onToggleTheme,
  onOpenCreateModal,
  onOpenShortcuts,
  onSeedDemoData,
  isSeeding,
}) {
  return (
    <header className="app-header">
      <div className="header-left">
        <div className="brand-logo" onClick={() => window.location.reload()}>
          <div className="logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <div className="logo-text">
            <span className="logo-title">
              Datastraw <span className="logo-badge">React CRM</span>
            </span>
            <span className="logo-sub">AI Customer Operations</span>
          </div>
        </div>

        {/* Multi-Tenant Client Switcher */}
        <div className="client-switcher">
          <span className="switcher-label">Client:</span>
          <select
            id="clientFilter"
            className="select-input client-select"
            value={client}
            onChange={(e) => onClientChange(e.target.value)}
            title="Switch Client Brand"
          >
            <option value="All">All Brands (Multi-Tenant)</option>
            <option value="Aura D2C">Aura D2C</option>
            <option value="UrbanKicks">UrbanKicks</option>
            <option value="GlowCare">GlowCare</option>
          </select>
        </div>
      </div>

      <div className="header-actions">
        {/* Shortcuts Helper */}
        <button
          className="btn btn-ghost keyboard-hint"
          onClick={onOpenShortcuts}
          title="Keyboard Shortcuts (Press ?)"
        >
          <kbd>⌘K</kbd> Shortcuts
        </button>

        {/* Evaluator Seed Button */}
        <button
          className="btn btn-secondary pulse-button"
          onClick={onSeedDemoData}
          disabled={isSeeding}
          title="Seed realistic D2C tickets with notes"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
          {isSeeding ? 'Seeding...' : 'Seed Demo Data'}
        </button>

        {/* Create Ticket Button */}
        <button
          className="btn btn-primary"
          onClick={onOpenCreateModal}
          title="Create Support Ticket (Press C)"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Ticket
        </button>

        {/* Dark/Light Theme Switcher */}
        <button
          className="btn btn-icon theme-btn"
          onClick={onToggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode (Press D)`}
        >
          <svg className="sun-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
          <svg className="moon-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
        </button>
      </div>
    </header>
  );
}
