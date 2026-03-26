import React from 'react';
import { Play, RotateCcw } from 'lucide-react';

export const Controls = ({
  sessionStatus = 'pending',
  onStart,
  onResume,
  disabled = false,
  loading = false,
}) => {
  const isPaused = sessionStatus === 'paused';
  const isPending = sessionStatus === 'pending';
  const isCompleted = sessionStatus === 'completed';
  const isFailed = sessionStatus === 'failed';

  return (
    <div className="flex flex-wrap items-center gap-3">
      <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${
        isCompleted
          ? 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-400/30'
          : isFailed
            ? 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-400/30'
            : isPaused
              ? 'bg-amber-500/15 text-amber-300 ring-1 ring-amber-400/30'
              : 'bg-slate-500/15 text-slate-300 ring-1 ring-slate-400/30'
      }`}>
        {sessionStatus}
      </span>

      {isPending && (
        <button
          onClick={onStart}
          disabled={disabled || loading}
          className="inline-flex items-center gap-2 rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Play size={18} />
          Start upgrade
        </button>
      )}

      {isPaused && (
        <button
          onClick={onResume}
          disabled={disabled || loading}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <RotateCcw size={18} />
          Resume upgrade
        </button>
      )}

      {!isPending && !isPaused && (
        <span className="text-sm text-slate-400">
          {isCompleted ? 'Session finished' : isFailed ? 'Session failed' : 'Session is running'}
        </span>
      )}

      {loading && (
        <span className="text-sm text-slate-400">Processing...</span>
      )}
    </div>
  );
};
