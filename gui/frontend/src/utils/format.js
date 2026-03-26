export const formatDateTime = (value) => {
  if (!value) return '—';
  return new Date(value).toLocaleString();
};

export const formatDate = (value) => {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
};

export const formatDuration = (startedAt, completedAt) => {
  if (!startedAt) return '—';
  const start = new Date(startedAt).getTime();
  const end = completedAt ? new Date(completedAt).getTime() : Date.now();
  const seconds = Math.max(0, Math.floor((end - start) / 1000));
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const rest = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${rest}s`;
  }
  return `${rest}s`;
};

export const humanize = (value) =>
  String(value || 'unknown')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (ch) => ch.toUpperCase());

export const statusTone = (status = 'pending') => {
  const key = String(status).toLowerCase();
  if (key === 'running' || key === 'in_progress') {
    return 'bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-400/30';
  }
  if (key === 'completed' || key === 'success') {
    return 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-400/30';
  }
  if (key === 'failed' || key === 'error') {
    return 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-400/30';
  }
  if (key === 'paused') {
    return 'bg-amber-500/15 text-amber-300 ring-1 ring-amber-400/30';
  }
  return 'bg-slate-500/15 text-slate-300 ring-1 ring-slate-400/30';
};

export const severityTone = (severity = 'info') => {
  const key = String(severity).toLowerCase();
  if (key === 'critical' || key === 'error') {
    return 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-400/30';
  }
  if (key === 'warning') {
    return 'bg-amber-500/15 text-amber-300 ring-1 ring-amber-400/30';
  }
  return 'bg-cyan-500/15 text-cyan-300 ring-1 ring-cyan-400/30';
};
