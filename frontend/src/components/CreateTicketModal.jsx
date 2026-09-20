import React, { useState } from 'react';

export default function CreateTicketModal({ isOpen, onClose, onSubmit, isSubmitting }) {
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_email: '',
    client_name: 'Aura D2C',
    channel: 'Web Form',
    subject: '',
    description: '',
  });

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.customer_name || !formData.customer_email || !formData.subject || !formData.description) {
      return;
    }
    onSubmit(formData);
  };

  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <h3>Create Support Ticket</h3>
            <span className="modal-subtitle">
              Ingest a new multi-channel customer issue with autonomous Groq AI triage
            </span>
          </div>
          <button
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close dialog"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="modalCustomerName">
                Customer Name <span className="required">*</span>
              </label>
              <input
                id="modalCustomerName"
                name="customer_name"
                type="text"
                className="form-input"
                placeholder="e.g. Maya Lin"
                value={formData.customer_name}
                onChange={handleChange}
                required
                autoFocus
              />
            </div>
            <div className="form-group">
              <label htmlFor="modalCustomerEmail">
                Customer Email <span className="required">*</span>
              </label>
              <input
                id="modalCustomerEmail"
                name="customer_email"
                type="email"
                className="form-input"
                placeholder="e.g. maya@example.com"
                value={formData.customer_email}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="modalClientName">Tenant / Client Brand</label>
              <select
                id="modalClientName"
                name="client_name"
                className="form-input"
                value={formData.client_name}
                onChange={handleChange}
              >
                <option value="Aura D2C">Aura D2C (Apparel)</option>
                <option value="UrbanKicks">UrbanKicks (Footwear)</option>
                <option value="GlowCare">GlowCare (Skincare)</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="modalChannel">Inbound Channel</label>
              <select
                id="modalChannel"
                name="channel"
                className="form-input"
                value={formData.channel}
                onChange={handleChange}
              >
                <option value="Web Form">🌐 Web Form</option>
                <option value="Email">✉️ Email</option>
                <option value="WhatsApp">💬 WhatsApp</option>
                <option value="Shopify">🛍️ Shopify</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="modalSubject">
              Subject <span className="required">*</span>
            </label>
            <input
              id="modalSubject"
              name="subject"
              type="text"
              className="form-input"
              placeholder="e.g. Order #AUR-8821 package delivered empty or missing"
              value={formData.subject}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="modalDescription">
              Issue Description <span className="required">*</span>
            </label>
            <textarea
              id="modalDescription"
              name="description"
              className="form-input form-textarea"
              rows={4}
              placeholder="Describe the customer's problem or paste inbound message..."
              value={formData.description}
              onChange={handleChange}
              required
            />
          </div>

          <div className="ai-callout-note">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            <span>
              <strong>Autonomous Groq Triage:</strong> Upon creation, our AI Engine automatically classifies priority (Urgent/High/Normal), detects category, and generates an executive TL;DR summary.
            </span>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-ghost"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Ingesting with Groq AI...' : 'Create Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
