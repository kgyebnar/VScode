import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Loader2, Plus, RefreshCw } from 'lucide-react';
import apiClient from '../services/api';
import { Layout, ShellBadge } from '../components/Layout';
import { EmptyState } from '../components/EmptyState';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { formatDate } from '../utils/format';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSessions();
    const interval = setInterval(loadSessions, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.listSessions();
      setSessions(response.data.sessions || []);
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const stats = useMemo(() => ({
    total: sessions.length,
    running: sessions.filter((s) => s.status === 'running').length,
    completed: sessions.filter((s) => s.status === 'completed').length,
    failed: sessions.filter((s) => s.status === 'failed').length,
    paused: sessions.filter((s) => s.status === 'paused').length,
  }), [sessions]);

  const recentSessions = sessions.slice(0, 8);
  const activeSessions = sessions.filter((s) => s.status === 'running' || s.status === 'paused');

  return (
    <Layout
      title="Upgrade dashboard"
      subtitle="Track active sessions, see the latest audit context, and jump into start/resume/rollback flows."
      actions={
        <>
          <ShellBadge>{loading ? 'syncing' : `${sessions.length} sessions`}</ShellBadge>
          <button
            onClick={loadSessions}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:text-white disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
          <button
            onClick={() => navigate('/sessions/new')}
            className="inline-flex items-center gap-2 rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
          >
            <Plus size={16} />
            New session
          </button>
        </>
      }
    >
      {error && (
        <div className="mb-5 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-5">
        <StatCard label="Total" value={stats.total} hint="All known sessions" />
        <StatCard label="Running" value={stats.running} hint="Currently executing" accent="cyan" />
        <StatCard label="Paused" value={stats.paused} hint="Waiting for resume" accent="amber" />
        <StatCard label="Completed" value={stats.completed} hint="Finished successfully" accent="emerald" />
        <StatCard label="Failed" value={stats.failed} hint="Need attention" accent="rose" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl border border-white/8 bg-white/5 p-6">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-white">Active sessions</h2>
            <span className="text-sm text-slate-400">{activeSessions.length} live</span>
          </div>
          <div className="mt-4 space-y-3">
            {activeSessions.length === 0 ? (
              <EmptyState title="No active sessions" description="Create a session to start an upgrade cycle." />
            ) : (
              activeSessions.map((session) => (
                <Link
                  key={session.session_id}
                  to={`/sessions/${session.session_id}`}
                  className="block rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-4 transition hover:border-cyan-400/40 hover:bg-cyan-400/10"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-semibold text-white">{session.session_id}</span>
                        <StatusBadge value={session.status} />
                      </div>
                      <div className="mt-2 text-sm text-slate-400">
                        {session.total_firewalls} firewalls · target {session.target_firmware_version}
                      </div>
                    </div>
                    <ArrowRight size={18} className="text-slate-500" />
                  </div>
                </Link>
              ))
            )}
          </div>
        </section>

        <section className="rounded-3xl border border-white/8 bg-white/5 p-6">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-white">Recent sessions</h2>
            {loading && <Loader2 className="animate-spin text-slate-400" size={16} />}
          </div>

          <div className="mt-4 overflow-hidden rounded-2xl border border-white/8">
            <table className="w-full">
              <thead className="bg-slate-950/50 text-left text-xs uppercase tracking-[0.18em] text-slate-500">
                <tr>
                  <th className="px-4 py-3">Session</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Target</th>
                  <th className="px-4 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/8">
                {recentSessions.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8">
                      <EmptyState title="No sessions yet" description="Create the first upgrade session from the inventory files." />
                    </td>
                  </tr>
                ) : (
                  recentSessions.map((session) => (
                    <tr
                      key={session.session_id}
                      onClick={() => navigate(`/sessions/${session.session_id}`)}
                      className="cursor-pointer transition hover:bg-white/5"
                    >
                      <td className="px-4 py-4 text-sm font-medium text-cyan-300">{session.session_id}</td>
                      <td className="px-4 py-4"><StatusBadge value={session.status} /></td>
                      <td className="px-4 py-4 text-sm text-slate-300">{session.target_firmware_version}</td>
                      <td className="px-4 py-4 text-sm text-slate-400">{formatDate(session.created_at)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </Layout>
  );
};
