import React from 'react';

export const EmptyState = ({ title, description, action }) => (
  <div className="rounded-3xl border border-dashed border-white/10 bg-white/3 p-8 text-center">
    <div className="mx-auto max-w-xl">
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  </div>
);
