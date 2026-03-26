import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Loader2, RefreshCcw } from 'lucide-react';
import apiClient from '../services/api';
import { Layout, ShellBadge } from '../components/Layout';
import { Controls } from '../components/Controls';
import { ProgressBar } from '../components/ProgressBar';
import { EmptyState } from '../components/EmptyState';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { formatDateTime, formatDuration, humanize } from '../utils/format';

export const SessionDetail = () => {
  const navigate = useNavigate();
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [firewalls, setFirewalls] = useState([]);
  const [auditSummary, setAuditSummary] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  const loadSession = async () => {
    try {
      const [sessionRes, firewallsRes, summaryRes, auditRes] = await Promise.all([
        apiClient.getSession(sessionId),
        apiClient.listSessionFirewalls(sessionId),
        apiClient.getAuditSummary(sessionId),
        apiClient.getAuditLog(sessionId, { limit: 30 }),
      ]);
      setSession(sessionRes.data);
      setFirewalls(firewallsRes.data.firewalls || []);
      setAuditSummary(summaryRes.data || null);
      setAuditLog(auditRes.data.events || []);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Nem sikerült betölteni a jobot.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSession();
    const interval = setInterval(loadSession, 7000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const activeFirewalls = useMemo(
    () => firewalls.filter((firewall) => firewall.status === 'running' || firewall.status === 'in_progress'),
    [firewalls]
  );

  const pendingFirewalls = useMemo(
    () => firewalls.filter((firewall) => firewall.status === 'pending'),
    [firewalls]
  );

  const start = async () => {
    try {
      setActionLoading(true);
      await apiClient.startSession(sessionId);
      await loadSession();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Start failed.');
    } finally {
      setActionLoading(false);
    }
  };

  const resume = async () => {
    try {
      setActionLoading(true);
      await apiClient.resumeSession(sessionId);
      await loadSession();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Resume failed.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && !session) {
    return (
      <Layout title="Job detail" subtitle="Loading job..." backTo="/">
        <div className="flex items-center justify-center py-20 text-slate-400">
          <Loader2 className="mr-3 animate-spin" size={18} />
          Loading...
        </div>
      </Layout>
    );
  }

  if (!session) {
    return (
      <Layout title="Job detail" subtitle="No job available." backTo="/">
        <EmptyState
          title="Job not found"
          description="The job may not exist yet, or the backend could not read it."
          action={
            <button
              onClick={() => navigate('/')}
              className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950"
            >
              Back to dashboard
            </button>
          }
        />
      </Layout>
    );
  }

  const actionProps = {
    sessionStatus: session.status,
    onStart: start,
    onResume: resume,
    disabled: actionLoading,
    loading: actionLoading,
  };

  return (
    <Layout
      title={`Job ${session.session_id}`}
      subtitle={`${session.inventory_file} · target ${session.target_firmware_version} · ${session.execution_mode}`}
      backTo="/"
      actions={
        <>
          <ShellBadge>{session.status}</ShellBadge>
          <button
            onClick={loadSession}
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:text-white"
          >
            <RefreshCcw size={16} />
            Refresh
          </button>
        </>
      }
    >
      {error && (
        <div className="mb-5 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-4">
        <StatCard label="Firewalls" value={session.total_firewalls} hint={`${activeFirewalls.length} active, ${pendingFirewalls.length} pending`} />
        <StatCard label="Current index" value={session.current_firewall_index ?? 0} hint="Current execution pointer" accent="emerald" />
        <StatCard label="Duration" value={formatDuration(session.started_at, session.completed_at)} hint="Since start or until completion" accent="amber" />
        <StatCard label="Target version" value={session.target_firmware_version} hint="Firmware release requested" accent="rose" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="space-y-2">
                <div className="text-sm uppercase tracking-[0.18em] text-slate-500">Job controls</div>
                <Controls {...actionProps} />
              </div>
              <div className="text-right text-sm text-slate-400">
                <div>Created {formatDateTime(session.created_at)}</div>
                <div>Started {formatDateTime(session.started_at)}</div>
                <div>Completed {formatDateTime(session.completed_at)}</div>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-white">Firewall progress</h2>
              <Link to={`/sessions/${session.session_id}/audit`} className="text-sm text-cyan-300 transition hover:text-cyan-200">
                Open audit trail
              </Link>
            </div>

            <div className="mt-5 space-y-4">
              {firewalls.length === 0 ? (
                <EmptyState title="No firewalls in job" description="The selected inventory did not produce any hosts." />
              ) : (
                firewalls.map((firewall) => (
                  <Link
                    key={firewall.firewall_id}
                    to={`/sessions/${session.session_id}/firewalls/${firewall.firewall_id}`}
                    className="block rounded-2xl border border-white/8 bg-slate-950/50 p-4 transition hover:border-cyan-400/30 hover:bg-slate-950/80"
                  >
                    <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-sm font-semibold text-white">{firewall.firewall_id}</span>
                          <StatusBadge value={firewall.status} />
                        </div>
                        <div className="mt-1 text-sm text-slate-400">
                          {firewall.firewall_ip} · {humanize(firewall.current_phase)}
                        </div>
                      </div>
                      <div className="lg:min-w-[360px]">
                        <ProgressBar
                          progress={firewall.progress_percent || 0}
                          status={firewall.status}
                          phase={firewall.current_phase || '—'}
                          label="Progress"
                        />
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <h2 className="text-lg font-semibold text-white">Audit summary</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <MiniStat label="Total events" value={auditSummary?.total_events ?? 0} />
              <MiniStat label="Warnings" value={auditSummary?.by_severity?.warning ?? 0} />
              <MiniStat label="Errors" value={auditSummary?.by_severity?.error ?? 0} />
              <MiniStat label="Critical" value={auditSummary?.by_severity?.critical ?? 0} />
            </div>
          </div>

          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-white">Recent events</h2>
              <Link to={`/sessions/${session.session_id}/audit`} className="text-sm text-cyan-300 transition hover:text-cyan-200">
                View all
              </Link>
            </div>
            <div className="mt-4 space-y-3">
              {auditLog.length === 0 ? (
                <EmptyState title="No audit events yet" description="Start the job to create operational events." />
              ) : (
                auditLog.slice(0, 6).map((event) => (
                  <div key={event.id} className="rounded-2xl border border-white/8 bg-slate-950/50 p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge value={event.severity} tone="severity" />
                      <span className="text-sm font-semibold text-white">{event.event_type}</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-300">{event.message}</p>
                    <div className="mt-2 text-xs text-slate-500">{formatDateTime(event.timestamp)}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

const MiniStat = ({ label, value }) => (
  <div className="rounded-2xl border border-white/8 bg-slate-950/50 p-4">
    <div className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</div>
    <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
  </div>
);
