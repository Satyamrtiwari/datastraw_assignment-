import React, { useState } from 'react';

export default function TicketDetail({
  ticket,
  orderContext,
  aiDraft,
  onUpdateStatus,
  onAddNote,
  onReanalyzeAi,
  onRegenerateDraft,
  onApproveAndSend,
  isTriageLoading,
  isDraftLoading,
}) {
  const [noteText, setNoteText] = useState('');
  const [draftContent, setDraftContent] = useState(aiDraft || '');

  // Keep local draft in sync if prop changes
  React.useEffect(() => {
    setDraftContent(aiDraft || '');
  }, [aiDraft]);

  if (!ticket) {
    return (
      <section className="panel detail-panel" aria-label="Ticket Detail & AI Copilot">
        <div className="detail-placeholder">
          <div className="placeholder-graphic">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
          </div>
          <h3>Select a Ticket to Open Copilot</h3>
          <p>Click any ticket from the queue to view customer issue, AI triage, Shopify order data, and 1-click suggested response.</p>
          <div className="placeholder-hint">
            Tip: Press <kbd>J</kbd> and <kbd>K</kbd> on your keyboard to navigate through tickets.
          </div>
        </div>
      </section>
    );
  }

  const handleNoteSubmit = (e) => {
    e.preventDefault();
    if (!noteText.trim()) return;
    onAddNote(noteText.trim());
    setNoteText('');
  };

  const getInitials = (name) => {
    if (!name) return '??';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
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
    return date.toLocaleDateString();
  };

  return (
    <section className="panel detail-panel" aria-label="Ticket Detail & AI Copilot">
      <div className="active-detail-view">
        {/* Detail Header */}
        <div className="detail-header">
          <div className="detail-title-group">
            <div className="ticket-header-badges">
              <span className="ticket-id-badge">{ticket.ticket_id}</span>
              <span className="client-tag">{ticket.client_name || 'Aura D2C'}</span>
              <span className="channel-pill">
                {ticket.channel === 'WhatsApp' && '💬 '}
                {ticket.channel === 'Email' && '✉️ '}
                {ticket.channel === 'Shopify' && '🛍️ '}
                {ticket.channel || 'Web Form'}
              </span>
            </div>
            <h2 className="detail-subject">{ticket.subject}</h2>
            <div className="detail-customer-meta">
              <span className="customer-avatar">{getInitials(ticket.customer_name)}</span>
              <span className="customer-name">{ticket.customer_name}</span>
              <span className="customer-email">{ticket.customer_email}</span>
              <span className="meta-dot">•</span>
              <span className="meta-time">Opened {formatTimeAgo(ticket.created_at)}</span>
            </div>
          </div>

          {/* Status Dropdown */}
          <div className="status-action-box">
            <label htmlFor="dStatusSelect">Status:</label>
            <select
              id="dStatusSelect"
              className="status-dropdown"
              value={ticket.status}
              onChange={(e) => onUpdateStatus(ticket.ticket_id, e.target.value)}
            >
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Closed">Closed</option>
            </select>
          </div>
        </div>

        {/* Detail Body (Scrollable) */}
        <div className="detail-body">
          {/* 🤖 1. AI Executive Summary Card */}
          <div className="ai-summary-card">
            <div className="ai-card-header">
              <div className="ai-badge-group">
                <span className="ai-chip">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                  </svg>
                  AI Executive Summary
                </span>
                <span className="engine-badge">Groq Cloud • Llama 3</span>
              </div>
              <div className="ai-header-pills">
                <span className={`priority-pill priority-${(ticket.priority || 'Normal').toLowerCase()}`}>
                  {ticket.priority || 'Normal'}
                </span>
                <span className="category-pill">{ticket.category || 'General'}</span>
              </div>
            </div>

            <div className="ai-summary-content">
              {isTriageLoading ? 'Re-analyzing with Groq Cloud...' : ticket.ai_summary || 'Analyzing customer message with Groq AI...'}
            </div>

            <div className="ai-card-footer">
              <button
                className="btn btn-ghost btn-xs"
                onClick={() => onReanalyzeAi(ticket.ticket_id)}
                disabled={isTriageLoading}
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="1 4 1 10 7 10"></polyline>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
                </svg>
                {isTriageLoading ? 'Analyzing...' : 'Re-run Groq Triage'}
              </button>
            </div>
          </div>

          {/* Customer Issue Description Box */}
          <div className="section-box">
            <div className="section-title">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              Customer's Issue Description
            </div>
            <div className="customer-description-box">{ticket.description}</div>
          </div>

          {/* 📦 2. Simulated D2C Order Context Card */}
          <div className="section-box order-context-box">
            <div className="section-title">
              <div className="title-with-badge" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line>
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
                Simulated D2C Order Context
              </div>
              <span className="store-badge">🛍️ Shopify Connected</span>
            </div>

            {orderContext ? (
              <div className="order-grid">
                <div className="order-meta-row">
                  <span>Order Number:</span>
                  <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--brand-primary)' }}>
                    {orderContext.order_id}
                  </strong>
                </div>
                <div className="order-meta-row">
                  <span>Fulfillment Status:</span>
                  <span className="kpi-pill kpi-pill-success">{orderContext.fulfillment_status}</span>
                </div>
                <div className="order-meta-row">
                  <span>Carrier &amp; Tracking:</span>
                  <span>
                    {orderContext.carrier} -{' '}
                    <a href={orderContext.tracking_url} target="_blank" rel="noreferrer" className="tracking-link">
                      {orderContext.tracking_number} ↗
                    </a>
                  </span>
                </div>
                <div className="order-meta-row">
                  <span>Order Total:</span>
                  <strong>{orderContext.order_total}</strong>
                </div>
                <div className="order-items-list" style={{ marginTop: '6px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    Items:
                  </span>
                  {(orderContext.items || []).map((item, idx) => (
                    <div key={idx} className="order-item-row">
                      <span>• {item.title} (x{item.qty})</span>
                      <span style={{ fontWeight: 600 }}>{item.price}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Syncing Shopify order data...</div>
            )}
          </div>

          {/* 👥 3. Internal Notes Thread */}
          <div className="section-box notes-box">
            <div className="section-title">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
              </svg>
              Internal Team Notes ({ticket.notes?.length || 0})
            </div>

            <div className="notes-thread">
              {ticket.notes && ticket.notes.length > 0 ? (
                ticket.notes.map((note) => (
                  <div key={note.id} className="note-bubble">
                    <div>{note.note_text}</div>
                    <div className="note-time">{formatTimeAgo(note.created_at)}</div>
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                  No internal notes yet. Add one below for team collaboration.
                </div>
              )}
            </div>

            <form onSubmit={handleNoteSubmit} className="add-note-container">
              <input
                type="text"
                className="note-input"
                placeholder="Add an internal note or agent handoff... (Press Enter)"
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
              />
              <button type="submit" className="btn btn-secondary btn-sm">
                Add Note
              </button>
            </form>
          </div>

          {/* ✨ 4. 1-Click AI Suggested Resolution Draft */}
          <div className="ai-draft-card">
            <div className="draft-card-header">
              <div className="draft-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                </svg>
                1-Click AI Resolution Copilot
              </div>
              <button
                className="btn btn-ghost btn-xs"
                onClick={() => onRegenerateDraft(ticket.ticket_id)}
                disabled={isDraftLoading}
                title="Regenerate Draft with Groq"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="23 4 23 10 17 10"></polyline>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
                {isDraftLoading ? 'Generating...' : 'Regenerate Draft'}
              </button>
            </div>

            <div className="draft-textarea-container">
              <textarea
                className="draft-textarea"
                rows={7}
                value={draftContent}
                onChange={(e) => setDraftContent(e.target.value)}
                placeholder={isDraftLoading ? 'Groq Cloud AI is analyzing order history and crafting personalized reply...' : 'AI draft will appear here...'}
              />
            </div>

            <div className="draft-actions">
              <button
                className="btn btn-primary"
                onClick={() => onApproveAndSend(ticket.ticket_id, draftContent)}
                title="Approve and send resolution to customer"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
                Approve &amp; Send Resolution
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => onUpdateStatus(ticket.ticket_id, 'Closed')}
                title="Mark ticket as Closed"
              >
                ✓ Mark Resolved
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
