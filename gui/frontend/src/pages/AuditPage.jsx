import React, { useEffect, useMemo, useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { Filter, Loader2, RotateCcw } from 'lucide-react';
import apiClient from '../services/api';
import { Layout, ShellBadge } from '../components/Layout';
import { EmptyState } from '../components/EmptyState';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { formatDateTime } from '../utils/format';

export const AuditPage = () => {
  const { sessionId: routeSessionId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const sessionId = routeSessionId || searchParams.get('session') || '';
  const [auditLog, setAuditLog] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    severity: searchParams.get('severity') || '',
    event_type: searchParams.get('event_type') || '',
  });

  useEffect(() => {
    if (!sessionId) return;

    const loadAudit = async () => {
      try {
        setLoading(true);
        const [logRes, summaryRes] = await Promise.all([
          apiClient.getAuditLog(sessionId, {
            limit: 200,
            ...(filters.severity ? { severity: filters.severity } : {}),
            ...(filters.event_type ? { event_type: filters.event_type } : {}),
          }),
          apiClient.getAuditSummary(sessionId),
        ]);
        setAuditLog(logRes.data.events || []);
        setSummary(summaryRes.data || null);
        setError('');
      } catch (err) {
        setError(err?.response?.data?.detail || err.message || 'Nem sikerült betölteni az auditot.');
      } finally {
        setLoading(false);
      }
    };

    loadAudit();
  }, [sessionId, filters.severity, filters.event_type]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (sessionId) params.set('session', sessionId);
    if (filters.severity) params.set('severity', filters.severity);
    if (filters.event_type) params.set('event_type', filters.event_type);
    setSearchParams(params, { replace: true });
  }, [sessionId, filters.severity, filters.event_type, setSearchParams]);

  const eventTypes = useMemo(() => {
    const values = new Set(auditLog.map((entry) => entry.event_type).filter(Boolean));
    return Array.from(values).sort();
  }, [auditLog]);

  if (!sessionId) {
    return (
      <Layout
        title="Audit trail"
        subtitle="Pick a session to inspect its event history."
        actions={<ShellBadge>no session selected</ShellBadge>}
      >
        <EmptyState
          title="No session selected"
          description="Open a session detail page and jump to its audit trail, or append ?session=<id> to the URL."
        />
      </Layout>
    );
  }

  return (
    <Layout
      title={`Audit trail · ${sessionId}`}
      subtitle="Watch the operational trail for this session: lifecycle changes, warnings, errors and rollback events."
      backTo={`/sessions/${sessionId}`}
      actions={
        <ShellBadge>{loading ? 'refreshing' : `${auditLog.length} events`}</ShellBadge>
      }
    >
      {error && (
        <div className="mb-5 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-3">
        <StatCard label="Total events" value={summary?.total_events ?? auditLog.length ?? 0} hint="Events stored for this session" />
        <StatCard label="Warnings" value={summary?.by_severity?.warning ?? 0} hint="Non-blocking operational signals" accent="amber" />
        <StatCard label="Errors" value={summary?.by_severity?.error ?? 0} hint="Failed tasks or rollback failures" accent="rose" />
      </div>

      <div className="mt-6 rounded-3xl border border-white/8 bg-white/5 p-5">
        <div className="flex flex-col gap-3 border-b border-white/8 pb-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">
              <Filter size={14} />
              Filters
            </div>
            <p className="mt-1 text-sm text-slate-400">Narrow the audit stream by severity or event type.</p>
          </div>
          <button
            onClick={() => setFilters({ severity: '', event_type: '' })}
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:text-white"
          >
            <RotateCcw size={16} />
            Reset filters
          </button>
        </div>

        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-300">Severity</span>
            <select
              value={filters.severity}
              onChange={(e) => setFilters((current) => ({ ...current, severity: e.target.value }))}
              className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none"
            >
              <option value="">All severities</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="critical">Critical</option>
            </select>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-300">Event type</span>
            <select
              value={filters.event_type}
              onChange={(e) => setFilters((current) => ({ ...current, event_type: e.target.value }))}
              className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none"
            >
              <option value="">All event types</option>
              {eventTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="mt-6 rounded-3xl border border-white/8 bg-white/5">
        <div className="border-b border-white/8 px-5 py-4">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-white">Audit events</h2>
            <div className="text-sm text-slate-400">{loading ? 'Refreshing…' : 'Live refresh on load'}</div>
          </div>
        </div>

        {loading && auditLog.length === 0 ? (
          <div className="flex items-center justify-center px-5 py-16 text-slate-400">
            <Loader2 className="mr-3 animate-spin" size={18} />
            Loading audit events...
          </div>
        ) : auditLog.length === 0 ? (
          <div className="p-5">
            <EmptyState title="No audit events found" description="Try a different filter or start the session to generate events." />
          </div>
        ) : (
          <div className="divide-y divide-white/8">
            {auditLog.map((entry) => (
              <div key={entry.id} className="grid gap-4 px-5 py-4 lg:grid-cols-[1fr_150px_120px] lg:items-start">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusBadge value={entry.severity} tone="severity" />
                    <span className="text-sm font-semibold text-white">{entry.event_type}</span>
                    {entry.firewall_id && (
                      <Link
                        to={`/sessions/${sessionId}/firewalls/${entry.firewall_id}`}
                        className="text-sm text-cyan-300 transition hover:text-cyan-200"
                      >
                        {entry.firewall_id}
                      </Link>
                    )}
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{entry.message}</p>
                </div>
                <div className="text-sm text-slate-400">{entry.phase || '—'}</div>
                <div className="text-sm text-slate-400">{formatDateTime(entry.timestamp)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};
