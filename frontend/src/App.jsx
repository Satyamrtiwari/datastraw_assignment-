import React, { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import KpiBar from './components/KpiBar';
import TicketQueue from './components/TicketQueue';
import TicketDetail from './components/TicketDetail';
import CreateTicketModal from './components/CreateTicketModal';
import ShortcutsModal from './components/ShortcutsModal';
import Toast from './components/Toast';
import {
  fetchTickets,
  fetchTicketDetail,
  createTicket,
  updateTicket,
  fetchMetrics,
  fetchOrderContext,
  fetchAiDraft,
  runAiTriage,
  seedDemoData,
} from './api';

export default function App() {
  // Theme State (Day Mode by default)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('datastraw_theme') || 'light';
  });

  // Filter States
  const [client, setClient] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [channelFilter, setChannelFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Data States
  const [tickets, setTickets] = useState([]);
  const [selectedTicketId, setSelectedTicketId] = useState(null);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [orderContext, setOrderContext] = useState(null);
  const [aiDraft, setAiDraft] = useState('');
  const [metrics, setMetrics] = useState(null);

  // Loading States
  const [loadingQueue, setLoadingQueue] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [isSubmittingTicket, setIsSubmittingTicket] = useState(false);
  const [isTriageLoading, setIsTriageLoading] = useState(false);
  const [isDraftLoading, setIsDraftLoading] = useState(false);

  // Modal States
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isShortcutsModalOpen, setIsShortcutsModalOpen] = useState(false);

  // Toast System
  const [toasts, setToasts] = useState([]);
  const toastIdRef = useRef(0);

  const addToast = useCallback((message, type = 'info', duration = 3200) => {
    const id = ++toastIdRef.current;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Synchronize Theme with Document Element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('datastraw_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Load KPI Metrics
  const loadMetrics = useCallback(async () => {
    try {
      const data = await fetchMetrics();
      setMetrics(data);
    } catch (err) {
      console.warn('Could not fetch metrics:', err);
    }
  }, []);

  // Load Tickets from API
  const loadTickets = useCallback(async (preferredSelectId = null) => {
    setLoadingQueue(true);
    try {
      const data = await fetchTickets({
        client,
        status: statusFilter,
        priority: priorityFilter,
        channel: channelFilter,
        search: searchQuery,
      });
      setTickets(data);

      // Auto-select logic
      if (preferredSelectId) {
        setSelectedTicketId(preferredSelectId);
      } else if (data.length > 0) {
        setSelectedTicketId((curr) => {
          const exists = data.some((t) => t.ticket_id === curr);
          return exists ? curr : data[0].ticket_id;
        });
      } else {
        setSelectedTicketId(null);
        setSelectedTicket(null);
      }
    } catch (err) {
      addToast('Error connecting to backend API. Please ensure server is running.', 'error');
    } finally {
      setLoadingQueue(false);
    }
  }, [client, statusFilter, priorityFilter, channelFilter, searchQuery, addToast]);

  // Initial mount: load metrics and tickets
  useEffect(() => {
    loadMetrics();
    loadTickets();
  }, [loadMetrics, loadTickets]);

  // Load Ticket Detail and Context when selectedTicketId changes
  useEffect(() => {
    if (!selectedTicketId) {
      setSelectedTicket(null);
      setOrderContext(null);
      setAiDraft('');
      return;
    }

    let isMounted = true;

    async function loadDetail() {
      try {
        const detail = await fetchTicketDetail(selectedTicketId);
        if (!isMounted) return;
        setSelectedTicket(detail);

        // Fetch Order Context concurrently
        fetchOrderContext(selectedTicketId)
          .then((ctx) => {
            if (isMounted) setOrderContext(ctx);
          })
          .catch((e) => console.warn('Order context error:', e));

        // Generate AI draft for this ticket
        setIsDraftLoading(true);
        fetchAiDraft(selectedTicketId)
          .then((draftRes) => {
            if (isMounted) setAiDraft(draftRes.suggested_reply || '');
          })
          .catch((e) => {
            if (isMounted) setAiDraft('Dear Customer,\n\nThank you for reaching out to customer support...');
          })
          .finally(() => {
            if (isMounted) setIsDraftLoading(false);
          });
      } catch (err) {
        if (isMounted) addToast(`Failed to load ticket ${selectedTicketId}`, 'error');
      }
    }

    loadDetail();

    return () => {
      isMounted = false;
    };
  }, [selectedTicketId, addToast]);

  // Handlers
  const handleSelectTicket = (ticketId) => {
    setSelectedTicketId(ticketId);
  };

  const handleUpdateStatus = async (ticketId, newStatus) => {
    try {
      await updateTicket(ticketId, { status: newStatus });
      addToast(`Ticket ${ticketId} updated to ${newStatus}`, 'success');

      // Update state locally for instant snappy UI
      setTickets((prev) =>
        prev.map((t) => (t.ticket_id === ticketId ? { ...t, status: newStatus } : t))
      );
      if (selectedTicket && selectedTicket.ticket_id === ticketId) {
        setSelectedTicket((prev) => ({ ...prev, status: newStatus }));
      }
      loadMetrics();
    } catch (err) {
      addToast(`Failed to update status for ${ticketId}`, 'error');
    }
  };

  const handleCycleStatus = (e, ticketId, currentStatus) => {
    e.stopPropagation();
    const cycle = {
      'Open': 'In Progress',
      'In Progress': 'Closed',
      'Closed': 'Open',
    };
    const nextStatus = cycle[currentStatus] || 'Open';
    handleUpdateStatus(ticketId, nextStatus);
  };

  const handleAddNote = async (noteText) => {
    if (!selectedTicketId) return;
    try {
      await updateTicket(selectedTicketId, { notes: noteText });
      addToast('Internal team note added', 'success');
      // Reload ticket detail to fetch newly created note
      const updated = await fetchTicketDetail(selectedTicketId);
      setSelectedTicket(updated);
    } catch (err) {
      addToast('Failed to add note', 'error');
    }
  };

  const handleReanalyzeAi = async (ticketId) => {
    setIsTriageLoading(true);
    try {
      const triageRes = await runAiTriage(ticketId);
      addToast(`Groq AI triage complete: ${triageRes.priority} • ${triageRes.category}`, 'success');

      // Update detail and queue
      const updated = await fetchTicketDetail(ticketId);
      setSelectedTicket(updated);
      setTickets((prev) =>
        prev.map((t) => (t.ticket_id === ticketId ? { ...t, priority: triageRes.priority, category: triageRes.category } : t))
      );
      loadMetrics();
    } catch (err) {
      addToast('Groq AI triage re-analysis failed', 'error');
    } finally {
      setIsTriageLoading(false);
    }
  };

  const handleRegenerateDraft = async (ticketId) => {
    setIsDraftLoading(true);
    try {
      const draftRes = await fetchAiDraft(ticketId);
      setAiDraft(draftRes.suggested_reply || '');
      addToast('Generated fresh resolution draft with Groq AI', 'success');
    } catch (err) {
      addToast('Could not regenerate draft', 'error');
    } finally {
      setIsDraftLoading(false);
    }
  };

  const handleApproveAndSend = async (ticketId, finalDraft) => {
    try {
      // 1. Add dispatch note
      await updateTicket(ticketId, {
        notes: `[AI Copilot Resolution Sent to Customer]:\n${finalDraft}`,
        status: 'Closed',
      });
      addToast(`Resolution dispatched & ${ticketId} marked Closed!`, 'success');

      // Update state locally
      setTickets((prev) =>
        prev.map((t) => (t.ticket_id === ticketId ? { ...t, status: 'Closed' } : t))
      );
      if (selectedTicket && selectedTicket.ticket_id === ticketId) {
        setSelectedTicket((prev) => ({
          ...prev,
          status: 'Closed',
          notes: [
            ...(prev.notes || []),
            {
              id: Date.now(),
              note_text: `[AI Copilot Resolution Sent to Customer]:\n${finalDraft}`,
              created_at: new Date().toISOString(),
            },
          ],
        }));
      }
      loadMetrics();
    } catch (err) {
      addToast('Failed to send resolution', 'error');
    }
  };

  const handleCreateTicket = async (ticketData) => {
    setIsSubmittingTicket(true);
    try {
      const res = await createTicket(ticketData);
      setIsCreateModalOpen(false);
      addToast(`Ticket ${res.ticket_id} created with Groq AI triage (${res.priority})!`, 'success');

      // Refresh list & select newly created ticket
      await loadTickets(res.ticket_id);
      loadMetrics();
    } catch (err) {
      addToast(`Error creating ticket: ${err.message}`, 'error');
    } finally {
      setIsSubmittingTicket(false);
    }
  };

  const handleSeedDemoData = async () => {
    setIsSeeding(true);
    try {
      await seedDemoData();
      addToast('Successfully seeded 7 realistic D2C tickets with notes!', 'success');
      await loadTickets();
      loadMetrics();
    } catch (err) {
      addToast('Failed to seed demo data', 'error');
    } finally {
      setIsSeeding(false);
    }
  };

  const handleExportCsv = () => {
    if (!tickets || tickets.length === 0) {
      addToast('No tickets to export in current view', 'info');
      return;
    }

    const headers = ['Ticket ID', 'Customer Name', 'Customer Email', 'Subject', 'Status', 'Priority', 'Category', 'Channel', 'Client Brand', 'Created At'];
    const rows = tickets.map((t) => [
      t.ticket_id,
      `"${(t.customer_name || '').replace(/"/g, '""')}"`,
      t.customer_email,
      `"${(t.subject || '').replace(/"/g, '""')}"`,
      t.status,
      t.priority,
      t.category,
      t.channel,
      t.client_name,
      t.created_at,
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `datastraw_tickets_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    addToast(`Exported ${tickets.length} tickets to CSV`, 'success');
  };

  const handleResetFilters = () => {
    setClient('All');
    setStatusFilter('All');
    setPriorityFilter('All');
    setChannelFilter('All');
    setSearchQuery('');
  };

  // Keyboard Shortcuts Navigation Listener
  useEffect(() => {
    const handleKeyDown = (e) => {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      const isInputActive = activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select';

      // Global shortcuts that work even if input is focused
      if (e.key === 'Escape') {
        if (isCreateModalOpen) setIsCreateModalOpen(false);
        if (isShortcutsModalOpen) setIsShortcutsModalOpen(false);
        return;
      }

      if (isInputActive) return;

      if (e.key === '/') {
        e.preventDefault();
        const searchEl = document.getElementById('searchInput');
        if (searchEl) searchEl.focus();
      } else if (e.key === 'c' || e.key === 'C') {
        e.preventDefault();
        setIsCreateModalOpen(true);
      } else if (e.key === 'd' || e.key === 'D') {
        e.preventDefault();
        toggleTheme();
      } else if (e.key === '?' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) {
        e.preventDefault();
        setIsShortcutsModalOpen((prev) => !prev);
      } else if (e.key === 'j' || e.key === 'J') {
        // Next ticket down
        e.preventDefault();
        if (tickets.length === 0) return;
        const currentIndex = tickets.findIndex((t) => t.ticket_id === selectedTicketId);
        const nextIndex = currentIndex < tickets.length - 1 ? currentIndex + 1 : 0;
        setSelectedTicketId(tickets[nextIndex].ticket_id);
      } else if (e.key === 'k' || e.key === 'K') {
        // Previous ticket up
        e.preventDefault();
        if (tickets.length === 0) return;
        const currentIndex = tickets.findIndex((t) => t.ticket_id === selectedTicketId);
        const prevIndex = currentIndex > 0 ? currentIndex - 1 : tickets.length - 1;
        setSelectedTicketId(tickets[prevIndex].ticket_id);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCreateModalOpen, isShortcutsModalOpen, tickets, selectedTicketId]);

  return (
    <div className="app-container">
      {/* 1. Header Navigation */}
      <Header
        client={client}
        onClientChange={setClient}
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenCreateModal={() => setIsCreateModalOpen(true)}
        onOpenShortcuts={() => setIsShortcutsModalOpen(true)}
        onSeedDemoData={handleSeedDemoData}
        isSeeding={isSeeding}
      />

      {/* 2. Key Performance Indicators Bar */}
      <KpiBar metrics={metrics} />

      {/* 3. Main Split-Pane Workspace */}
      <main className="main-workspace">
        {/* Ticket Queue Pane */}
        <TicketQueue
          tickets={tickets}
          selectedTicketId={selectedTicketId}
          onSelectTicket={handleSelectTicket}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          priorityFilter={priorityFilter}
          onPriorityFilterChange={setPriorityFilter}
          channelFilter={channelFilter}
          onChannelFilterChange={setChannelFilter}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onClearSearch={() => setSearchQuery('')}
          onCycleStatus={handleCycleStatus}
          onExportCsv={handleExportCsv}
          onResetFilters={handleResetFilters}
          loading={loadingQueue}
        />

        {/* Ticket Detail & AI Copilot Pane */}
        <TicketDetail
          ticket={selectedTicket}
          orderContext={orderContext}
          aiDraft={aiDraft}
          onUpdateStatus={handleUpdateStatus}
          onAddNote={handleAddNote}
          onReanalyzeAi={handleReanalyzeAi}
          onRegenerateDraft={handleRegenerateDraft}
          onApproveAndSend={handleApproveAndSend}
          isTriageLoading={isTriageLoading}
          isDraftLoading={isDraftLoading}
        />
      </main>

      {/* 4. Modals */}
      <CreateTicketModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateTicket}
        isSubmitting={isSubmittingTicket}
      />

      <ShortcutsModal
        isOpen={isShortcutsModalOpen}
        onClose={() => setIsShortcutsModalOpen(false)}
      />

      {/* 5. Non-Intrusive Floating Toasts */}
      <Toast toasts={toasts} onDismiss={removeToast} />
    </div>
  );
}
