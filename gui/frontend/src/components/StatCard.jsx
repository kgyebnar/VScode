import React from 'react';

export const StatCard = ({ label, value, hint, accent = 'cyan' }) => {
  const accents = {
    cyan: 'from-cyan-400/20 to-cyan-500/5 text-cyan-200',
    emerald: 'from-emerald-400/20 to-emerald-500/5 text-emerald-200',
    amber: 'from-amber-400/20 to-amber-500/5 text-amber-200',
    rose: 'from-rose-400/20 to-rose-500/5 text-rose-200',
  };

  return (
    <div className="rounded-3xl border border-white/8 bg-white/5 p-5 shadow-lg shadow-black/10">
      <div className={`mb-4 inline-flex rounded-2xl bg-gradient-to-br px-3 py-2 text-xs font-semibold uppercase tracking-[0.22em] ${accents[accent] || accents.cyan}`}>
        {label}
      </div>
      <div className="text-3xl font-semibold tracking-tight text-white">{value}</div>
      {hint && <div className="mt-2 text-sm text-slate-400">{hint}</div>}
    </div>
  );
};
