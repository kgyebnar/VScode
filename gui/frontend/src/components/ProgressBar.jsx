import React from 'react';

export const ProgressBar = ({
  progress = 0,
  status = 'pending',
  phase = '—',
  label = '',
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'bg-cyan-500';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'in_progress': return 'bg-blue-500';
      case 'paused': return 'bg-yellow-500';
      case 'skipped': return 'bg-purple-500';
      default: return 'bg-gray-300';
    }
  };

  const getStatusText = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <div className="flex gap-2 items-center">
          <span className="text-xs font-medium text-gray-500">{phase}</span>
          <span className="text-xs font-medium text-gray-600">{progress}%</span>
          <span className={`text-xs font-medium px-2 py-1 rounded text-white ${getStatusColor(status)}`}>
            {getStatusText(status)}
          </span>
        </div>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${getStatusColor(status)}`}
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
};
