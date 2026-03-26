import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Activity, ArrowLeft, FileClock, LayoutDashboard, Plus, Shield } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/jobs/new', label: 'Upgrade', icon: Plus },
  { to: '/audit', label: 'Audit', icon: FileClock },
];

export const Layout = ({ title, subtitle, actions, children, backTo, backLabel = 'Back' }) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.16),_transparent_28%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.12),_transparent_25%),linear-gradient(180deg,#08111f_0%,#091622_55%,#04070c_100%)] text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside className="hidden w-72 flex-col border-r border-white/8 bg-slate-950/70 px-5 py-6 backdrop-blur xl:flex">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/15 text-cyan-300 ring-1 ring-cyan-400/30">
              <Shield size={22} />
            </div>
            <div>
              <div className="text-lg font-semibold tracking-tight">Upgrade Console</div>
              <div className="text-xs uppercase tracking-[0.32em] text-slate-400">Palo Alto workflow</div>
            </div>
          </div>

          <nav className="space-y-2">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  [
                    'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition',
                    isActive
                      ? 'bg-cyan-400/15 text-cyan-200 ring-1 ring-cyan-400/30'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white',
                  ].join(' ')
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto rounded-3xl border border-white/8 bg-white/5 p-4 text-sm text-slate-300">
            <div className="mb-2 flex items-center gap-2 text-cyan-300">
              <Activity size={16} />
              Live monitoring
            </div>
            <p className="leading-6 text-slate-400">
              Jobs, audit events and rollback actions stay visible in one place.
            </p>
          </div>
        </aside>

        <main className="flex-1 px-4 py-4 sm:px-6 lg:px-8">
          <div className="rounded-[2rem] border border-white/8 bg-slate-950/45 shadow-2xl shadow-black/25 backdrop-blur">
            <header className="flex flex-col gap-4 border-b border-white/8 px-5 py-5 sm:px-8 lg:px-10">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-2">
                  {backTo && (
                    <button
                      onClick={() => navigate(backTo)}
                      className="inline-flex items-center gap-2 text-sm font-medium text-slate-400 transition hover:text-white"
                    >
                      <ArrowLeft size={16} />
                      {backLabel}
                    </button>
                  )}
                  <div>
                    <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{title}</h1>
                    {subtitle && <p className="mt-1 max-w-3xl text-sm text-slate-400 sm:text-base">{subtitle}</p>}
                  </div>
                </div>
                {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
              </div>
            </header>

            <div className="px-5 py-5 sm:px-8 lg:px-10">{children}</div>
          </div>
        </main>
      </div>
    </div>
  );
};

export const ShellBadge = ({ children }) => (
  <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-slate-300">
    {children}
  </span>
);
