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
      <Route path="/sessions/new" element={<NewSession />} />
      <Route path="/sessions/:sessionId" element={<SessionDetail />} />
      <Route path="/sessions/:sessionId/firewalls/:firewallId" element={<FirewallDetail />} />
      <Route path="/sessions/:sessionId/audit" element={<AuditPage />} />
      <Route path="/audit" element={<AuditPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
