/**
 * Datastraw Support CRM - API Service
 * Handles communication with the FastAPI backend on port 8000.
 */

const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (typeof window !== "undefined" && window.location.port === "5173"
    ? "http://127.0.0.1:8000"
    : "");

export async function fetchTickets(params = {}) {
  const query = new URLSearchParams();
  if (params.status && params.status !== "All") query.append("status", params.status);
  if (params.priority && params.priority !== "All") query.append("priority", params.priority);
  if (params.channel && params.channel !== "All") query.append("channel", params.channel);
  if (params.client && params.client !== "All") query.append("client", params.client);
  if (params.search) query.append("search", params.search);
  query.append("limit", params.limit || "100");
  query.append("skip", params.skip || "0");

  const res = await fetch(`${API_BASE}/api/tickets?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch tickets");
  return res.json();
}

export async function fetchTicketDetail(ticketId) {
  const res = await fetch(`${API_BASE}/api/tickets/${ticketId}`);
  if (!res.ok) throw new Error("Failed to fetch ticket detail");
  return res.json();
}

export async function createTicket(ticketData) {
  const res = await fetch(`${API_BASE}/api/tickets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ticketData),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to create ticket");
  }
  return res.json();
}

export async function updateTicket(ticketId, payload) {
  const res = await fetch(`${API_BASE}/api/tickets/${ticketId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update ticket");
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/api/analytics/metrics`);
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
}

export async function fetchOrderContext(ticketId) {
  const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/order-context`);
  if (!res.ok) throw new Error("Failed to fetch order context");
  return res.json();
}

export async function fetchAiDraft(ticketId) {
  const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/ai-draft`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to generate AI draft");
  return res.json();
}

export async function runAiTriage(ticketId) {
  const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/ai-triage`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to run AI triage");
  return res.json();
}

export async function ingestWebhook(webhookData) {
  const res = await fetch(`${API_BASE}/api/webhooks/inbound`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(webhookData),
  });
  if (!res.ok) throw new Error("Failed to ingest webhook");
  return res.json();
}

export async function seedDemoData() {
  const res = await fetch(`${API_BASE}/api/tickets/seed`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to seed demo data");
  return res.json();
}

