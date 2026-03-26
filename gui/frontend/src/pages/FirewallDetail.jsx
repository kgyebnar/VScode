import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Loader2, RotateCcw, Shield, Terminal } from 'lucide-react';
import apiClient from '../services/api';
import { Layout, ShellBadge } from '../components/Layout';
import { ProgressBar } from '../components/ProgressBar';
import { EmptyState } from '../components/EmptyState';
import { StatusBadge } from '../components/StatusBadge';
import { formatDateTime } from '../utils/format';

export const FirewallDetail = () => {
  const navigate = useNavigate();
  const { sessionId, firewallId } = useParams();
  const [details, setDetails] = useState(null);
  const [logs, setLogs] = useState('');
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState('');
  const [loading, setLoading] = useState(true);
  const [rollingBack, setRollingBack] = useState(false);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [detailRes, logsRes, versionsRes] = await Promise.all([
        apiClient.getFirewallDetails(sessionId, firewallId),
        apiClient.getFirewallLogs(sessionId, firewallId, 200),
        apiClient.getFirmwareVersions(),
      ]);
      const detail = detailRes.data;
      const firmwareVersions = versionsRes.data.firmware_versions || [];
      const rollbackCandidates = firmwareVersions.filter((version) => version !== detail?.firmware_version_current);
      setDetails(detail);
      setLogs(logsRes.data.log_content || '');
      setVersions(firmwareVersions);
      setSelectedVersion(
        rollbackCandidates[0] ||
        detail?.firmware_version_target ||
        detail?.firmware_version_current ||
        firmwareVersions[0] ||
        ''
      );
      setError('');
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Nem sikerült betölteni a firewall nézetet.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, [sessionId, firewallId]);

  const recentEvents = useMemo(() => details?.recent_events || [], [details]);

  const rollback = async () => {
    try {
      setRollingBack(true);
      await apiClient.rollbackFirewall(sessionId, firewallId, selectedVersion);
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Rollback failed.');
    } finally {
      setRollingBack(false);
    }
  };

  if (loading && !details) {
    return (
      <Layout title="Firewall detail" subtitle="Loading firewall information..." backTo={`/jobs/${sessionId}`}>
        <div className="flex items-center justify-center py-20 text-slate-400">
          <Loader2 className="mr-3 animate-spin" size={18} />
          Loading...
        </div>
      </Layout>
    );
  }

  if (!details) {
    return (
      <Layout title="Firewall detail" subtitle="No firewall details available." backTo={`/jobs/${sessionId}`}>
        <EmptyState
          title="Firewall not found"
          description="This firewall is not part of the selected job or the API could not load it."
          action={
            <button
              onClick={() => navigate(`/jobs/${sessionId}`)}
              className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950"
            >
              Back to job
            </button>
          }
        />
      </Layout>
    );
  }

  return (
      <Layout
      title={`${details.firewall_id}`}
      subtitle={`${details.firewall_ip} · ${details.session_id}`}
      backTo={`/jobs/${sessionId}`}
      actions={<ShellBadge>{loading ? 'refreshing' : details.status}</ShellBadge>}
    >
      {error && (
        <div className="mb-5 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-4">
          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 text-slate-300">
                  <Shield size={18} />
                  Firewall status
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <StatusBadge value={details.status} />
                  <span className="text-sm text-slate-400">{details.current_phase || 'no active phase'}</span>
                </div>
              </div>
              <button
                onClick={loadData}
                className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:text-white"
              >
                Refresh
              </button>
            </div>

            <div className="mt-6">
              <ProgressBar
                progress={details.progress_percent || 0}
                status={details.status}
                phase={details.current_phase || '—'}
                label="Upgrade progress"
              />
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <Detail label="Current firmware" value={details.firmware_version_current || '—'} />
              <Detail label="Target firmware" value={details.firmware_version_target || '—'} />
              <Detail label="HA mode" value={details.ha_enabled ? 'Enabled' : 'Disabled'} />
              <Detail label="Primary" value={details.ha_primary ? 'Yes' : 'No'} />
              <Detail label="Started at" value={formatDateTime(details.started_at)} />
              <Detail label="Completed at" value={formatDateTime(details.completed_at)} />
            </div>
          </div>

          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <div className="flex items-center gap-2 text-lg font-semibold text-white">
              <Terminal size={18} />
              Recent logs
            </div>
            <pre className="mt-4 max-h-[420px] overflow-auto rounded-2xl border border-white/8 bg-slate-950/70 p-4 text-xs leading-6 text-slate-300">
              {logs || 'No log file content available.'}
            </pre>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <h2 className="text-lg font-semibold text-white">Rollback</h2>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Choose a firmware version and trigger rollback for this firewall only.
            </p>
            <div className="mt-4 space-y-3">
              <label className="space-y-2 block">
                <span className="text-sm font-medium text-slate-300">Target version</span>
                <select
                  value={selectedVersion}
                  onChange={(e) => setSelectedVersion(e.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none"
                >
                  {versions.map((version) => (
                    <option key={version} value={version}>
                      {version}
                    </option>
                  ))}
                </select>
              </label>

              <button
                onClick={rollback}
                disabled={rollingBack || !selectedVersion}
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-rose-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-rose-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {rollingBack ? <Loader2 className="animate-spin" size={18} /> : <RotateCcw size={18} />}
                {rollingBack ? 'Rolling back...' : 'Rollback firewall'}
              </button>
            </div>
          </div>

          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <h2 className="text-lg font-semibold text-white">Recent events</h2>
            <div className="mt-4 space-y-3">
              {recentEvents.length === 0 ? (
                <EmptyState title="No recent events" description="This firewall has no audit entries yet." />
              ) : (
                recentEvents.map((event) => (
                  <div key={`${event.timestamp}-${event.event_type}`} className="rounded-2xl border border-white/8 bg-slate-950/50 p-4">
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

const Detail = ({ label, value }) => (
  <div className="rounded-2xl border border-white/8 bg-slate-950/50 p-4">
    <div className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</div>
    <div className="mt-2 text-sm font-medium text-white">{value}</div>
  </div>
);
