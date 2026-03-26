import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { NewSession } from './pages/NewSession';
import { SessionDetail } from './pages/SessionDetail';
import { FirewallDetail } from './pages/FirewallDetail';
import { AuditPage } from './pages/AuditPage';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/jobs/new" element={<NewSession />} />
      <Route path="/jobs/:sessionId" element={<SessionDetail />} />
      <Route path="/jobs/:sessionId/firewalls/:firewallId" element={<FirewallDetail />} />
      <Route path="/jobs/:sessionId/audit" element={<AuditPage />} />
      <Route path="/sessions/new" element={<Navigate to="/jobs/new" replace />} />
      <Route path="/sessions/:sessionId" element={<Navigate to="/jobs/:sessionId" replace />} />
      <Route path="/sessions/:sessionId/firewalls/:firewallId" element={<Navigate to="/jobs/:sessionId/firewalls/:firewallId" replace />} />
      <Route path="/sessions/:sessionId/audit" element={<Navigate to="/jobs/:sessionId/audit" replace />} />
      <Route path="/audit" element={<AuditPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
