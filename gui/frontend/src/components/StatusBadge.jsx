import React from 'react';
import { severityTone, statusTone } from '../utils/format';

export const StatusBadge = ({ value, tone = 'status' }) => {
  const className = tone === 'severity' ? severityTone(value) : statusTone(value);

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${className}`}>
      {value || 'unknown'}
    </span>
  );
};
