import { create } from 'zustand';

export const useSessionStore = create((set, get) => ({
  // Sessions
  sessions: [],
  currentSession: null,
  currentSessionId: null,

  // UI state
  loading: false,
  error: null,

  // Actions
  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (session) => set({ currentSession: session, currentSessionId: session?.session_id }),
  setCurrentSessionId: (id) => set({ currentSessionId: id }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // Session operations
  addSession: (session) => set((state) => ({
    sessions: [session, ...state.sessions]
  })),

  updateSession: (sessionId, updates) => set((state) => ({
    sessions: state.sessions.map(s =>
      s.session_id === sessionId ? { ...s, ...updates } : s
    ),
    currentSession: state.currentSession?.session_id === sessionId
      ? { ...state.currentSession, ...updates }
      : state.currentSession,
  })),

  // Firewall operations
  updateFirewall: (firewallId, updates) => set((state) => ({
    currentSession: state.currentSession ? {
      ...state.currentSession,
      firewalls: state.currentSession.firewalls.map(fw =>
        fw.firewall_id === firewallId ? { ...fw, ...updates } : fw
      )
    } : null,
  })),

  getFirewall: (firewallId) => {
    const session = get().currentSession;
    return session?.firewalls?.find(fw => fw.firewall_id === firewallId);
  },
}));

export const useAuditStore = create((set) => ({
  auditLog: [],
  auditSummary: null,
  setAuditLog: (log) => set({ auditLog: log }),
  setAuditSummary: (summary) => set({ auditSummary: summary }),
  addAuditEntry: (entry) => set((state) => ({
    auditLog: [entry, ...state.auditLog]
  })),
}));

export const useUIStore = create((set) => ({
  sidebarOpen: true,
  theme: localStorage.getItem('theme') || 'light',
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setTheme: (theme) => {
    localStorage.setItem('theme', theme);
    set({ theme });
  },
}));
