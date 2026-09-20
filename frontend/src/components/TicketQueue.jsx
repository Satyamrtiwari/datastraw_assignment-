import React from 'react';

export default function TicketQueue({
  tickets,
  selectedTicketId,
  onSelectTicket,
  statusFilter,
  onStatusFilterChange,
  priorityFilter,
  onPriorityFilterChange,
  channelFilter,
  onChannelFilterChange,
  searchQuery,
  onSearchChange,
  onClearSearch,
  onCycleStatus,
  onExportCsv,
  onResetFilters,
  loading,
}) {
  const getChannelIcon = (channel) => {
    switch ((channel || '').toLowerCase()) {
      case 'whatsapp':
        return '💬';
      case 'email':
        return '✉️';
      case 'shopify':
        return '🛍️';
      default:
        return '🌐';
    }
  };

  const formatTimeAgo = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffSec = Math.floor((now - date) / 1000);

    if (diffSec < 60) return 'Just now';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour}h ago`;
    const diffDays = Math.floor(diffHour / 24);
    if (diffDays < 30) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <section className="panel queue-panel" aria-label="Ticket Queue">
      {/* Search & Filter Header */}
      <div className="queue-controls">
        <div className="search-box">
          <svg
            className="search-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            id="searchInput"
            placeholder="Search by name, ID, email, or issue... (Press /)"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            autoComplete="off"
          />
          {searchQuery && (
            <button
              className="clear-btn"
              onClick={onClearSearch}
              title="Clear search"
            >
              ×
            </button>
          )}
        </div>

        {/* Status Filter Tabs */}
        <div className="filter-tabs" role="tablist">
          {['All', 'Open', 'In Progress', 'Closed'].map((s) => (
            <button
              key={s}
              className={`filter-tab ${statusFilter === s ? 'active' : ''}`}
              onClick={() => onStatusFilterChange(s)}
              role="tab"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Secondary Filter Dropdowns & Export */}
        <div className="secondary-filters">
          <div className="filter-group">
            <label htmlFor="priorityFilter">Priority:</label>
            <select
              id="priorityFilter"
              className="select-input"
              value={priorityFilter}
              onChange={(e) => onPriorityFilterChange(e.target.value)}
            >
              <option value="All">All Priorities</option>
              <option value="Urgent">🔴 Urgent</option>
              <option value="High">🟡 High</option>
              <option value="Medium">Medium</option>
              <option value="Normal">🟢 Normal</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="channelFilter">Channel:</label>
            <select
              id="channelFilter"
              className="select-input"
              value={channelFilter}
              onChange={(e) => onChannelFilterChange(e.target.value)}
            >
              <option value="All">All Channels</option>
              <option value="WhatsApp">💬 WhatsApp</option>
              <option value="Email">✉️ Email</option>
              <option value="Shopify">🛍️ Shopify</option>
              <option value="Web Form">🌐 Web Form</option>
            </select>
          </div>

          <button
            className="btn btn-ghost btn-sm"
            onClick={onExportCsv}
            title="Export filtered tickets to CSV"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Export
          </button>
        </div>
      </div>

      {/* Ticket Table */}
      <div className="table-container">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Syncing tickets with backend...</p>
          </div>
        ) : tickets.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No tickets found</h3>
            <p>Try resetting filters or seeding demo tickets.</p>
            <button className="btn btn-secondary btn-sm" onClick={onResetFilters}>
              Reset All Filters
            </button>
          </div>
        ) : (
          <table className="tickets-table">
            <thead>
              <tr>
                <th style={{ width: '95px' }}>Ticket ID</th>
                <th>Customer</th>
                <th>Subject</th>
                <th style={{ width: '110px' }}>Channel</th>
                <th style={{ width: '100px' }}>Priority</th>
                <th style={{ width: '120px' }}>Status</th>
                <th style={{ width: '90px', textAlign: 'right' }}>Updated</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((t) => {
                const isSelected = selectedTicketId === t.ticket_id;
                const priorityClass = `priority-${(t.priority || 'Normal').toLowerCase()}`;
                const statusClass = `status-${(t.status || 'Open').toLowerCase().replace(' ', '-')}`;

                return (
                  <tr
                    key={t.ticket_id}
                    className={`ticket-row ${isSelected ? 'active' : ''}`}
                    onClick={() => onSelectTicket(t.ticket_id)}
                  >
                    <td>
                      <span className="ticket-code">{t.ticket_id}</span>
                    </td>
                    <td>
                      <div className="customer-cell">
                        <span className="cust-name">{t.customer_name}</span>
                        <span className="cust-email">{t.customer_email}</span>
                      </div>
                    </td>
                    <td>
                      <div className="subject-cell" title={t.subject}>
                        {t.subject}
                      </div>
                    </td>
                    <td>
                      <span className="badge-channel">
                        {getChannelIcon(t.channel)} {t.channel || 'Web'}
                      </span>
                    </td>
                    <td>
                      <span className={`priority-pill ${priorityClass}`}>
                        {t.priority || 'Normal'}
                      </span>
                    </td>
                    <td>
                      <button
                        className={`status-pill-btn ${statusClass}`}
                        onClick={(e) => onCycleStatus(e, t.ticket_id, t.status)}
                        title="Click to cycle status"
                      >
                        {t.status}
                      </button>
                    </td>
                    <td className="time-cell">{formatTimeAgo(t.updated_at || t.created_at)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Queue Footer */}
      <div className="queue-footer">
        <div className="queue-count">
          Showing {tickets.length} ticket{tickets.length === 1 ? '' : 's'}
        </div>
        <div className="pagination-controls">
          <button className="btn btn-ghost btn-sm" disabled>
            Previous
          </button>
          <span className="page-indicator">Page 1</span>
          <button className="btn btn-ghost btn-sm" disabled>
            Next
          </button>
        </div>
      </div>
    </section>
  );
}
