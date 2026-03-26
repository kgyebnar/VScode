import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

const resolveWsBase = () => {
  const raw = import.meta.env.VITE_WS_URL || '/ws';
  const normalized = raw.replace(/\/$/, '');
  if (normalized.endsWith('/ws')) {
    return normalized;
  }
  return `${normalized}/ws`;
};

const WS_BASE_URL = resolveWsBase();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const apiClient = {
  // Sessions
  listSessions: () => api.get('/sessions'),
  getSession: (sessionId) => api.get(`/sessions/${sessionId}`),
  createSession: (data) => api.post('/sessions', data),
  startSession: (sessionId) => api.post(`/sessions/${sessionId}/start`),
  pauseSession: (sessionId) => api.post(`/sessions/${sessionId}/pause`),
  resumeSession: (sessionId) => api.post(`/sessions/${sessionId}/resume`),
  cancelSession: (sessionId) => api.post(`/sessions/${sessionId}/cancel`),
  getSessionStatus: (sessionId) => api.get(`/sessions/${sessionId}/status`),

  // Firewalls
  listSessionFirewalls: (sessionId) => api.get(`/firewalls/sessions/${sessionId}`),
  getFirewallDetails: (sessionId, firewallId) =>
    api.get(`/firewalls/sessions/${sessionId}/${firewallId}`),
  rollbackFirewall: (sessionId, firewallId, targetVersion) =>
    api.post(`/firewalls/sessions/${sessionId}/${firewallId}/rollback`, { target_version: targetVersion }),
  getFirewallLogs: (sessionId, firewallId, lines = 100) =>
    api.get(`/firewalls/sessions/${sessionId}/${firewallId}/logs`, { params: { lines } }),

  // Audit log
  getAuditLog: (sessionId, params = {}) =>
    api.get(`/audit/sessions/${sessionId}`, { params }),
  getAuditSummary: (sessionId) =>
    api.get(`/audit/sessions/${sessionId}/summary`),

  // Configuration
  getInventoryFiles: () => api.get('/inventory-files'),
  getFirmwareVersions: () => api.get('/firmware-versions'),
  getConfig: () => api.get('/config'),
};

export const resolveWebSocketUrl = (sessionId) => `${WS_BASE_URL}/sessions/${sessionId}`;

export default apiClient;
