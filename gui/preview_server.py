#!/usr/bin/env python3
"""
Python-only preview server for the GUI.

This is a self-contained browser demo used when Node/Docker are unavailable.
It serves a single-page dashboard plus a small mock API that mimics the GUI
surface: sessions, firewalls, audit trail, start/resume, and rollback.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


HOST = os.environ.get("PREVIEW_HOST", "127.0.0.1")
PORT = int(os.environ.get("PREVIEW_PORT", "8765"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def minutes_ago(minutes: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()


STATE = {
    "config": {
        "db_path": "/data/gui.db",
        "playbook_dir": "/app",
        "backup_dir": "/data/backups",
        "log_dir": "/data/logs",
    },
    "inventory_files": ["inventory/palo_alto.yml"],
    "firmware_versions": ["11.1.0", "11.0.2", "10.2.4"],
    "sessions": {
        "upgrade_20260326T091500": {
            "session_id": "upgrade_20260326T091500",
            "status": "running",
            "created_at": minutes_ago(42),
            "started_at": minutes_ago(37),
            "completed_at": None,
            "target_firmware_version": "11.0.2",
            "execution_mode": "sequential",
            "total_firewalls": 3,
            "current_firewall_index": 1,
            "inventory_file": "inventory/palo_alto.yml",
            "notes": "OM2248 demo cycle",
            "firewalls": [
                {
                    "firewall_id": "pa-460",
                    "firewall_ip": "192.168.113.186",
                    "status": "completed",
                    "current_phase": "post_validation",
                    "progress_percent": 100,
                    "firmware_version_current": "10.2.4",
                    "firmware_version_target": "11.0.2",
                    "ha_enabled": True,
                    "ha_primary": True,
                    "started_at": minutes_ago(36),
                    "completed_at": minutes_ago(30),
                },
                {
                    "firewall_id": "pa-461",
                    "firewall_ip": "192.168.113.187",
                    "status": "running",
                    "current_phase": "install",
                    "progress_percent": 63,
                    "firmware_version_current": "10.2.4",
                    "firmware_version_target": "11.0.2",
                    "ha_enabled": True,
                    "ha_primary": False,
                    "started_at": minutes_ago(29),
                    "completed_at": None,
                },
                {
                    "firewall_id": "pa-462",
                    "firewall_ip": "192.168.113.188",
                    "status": "pending",
                    "current_phase": "queued",
                    "progress_percent": 0,
                    "firmware_version_current": "10.2.4",
                    "firmware_version_target": "11.0.2",
                    "ha_enabled": False,
                    "ha_primary": False,
                    "started_at": None,
                    "completed_at": None,
                },
            ],
            "audit": [
                {
                    "id": 1,
                    "timestamp": minutes_ago(42),
                    "event_type": "session_created",
                    "phase": None,
                    "severity": "info",
                    "firewall_id": None,
                    "message": "Upgrade session created with 3 firewalls",
                    "details": {},
                },
                {
                    "id": 2,
                    "timestamp": minutes_ago(37),
                    "event_type": "session_started",
                    "phase": None,
                    "severity": "info",
                    "firewall_id": None,
                    "message": "Upgrade session started (PID: 4812)",
                    "details": {},
                },
                {
                    "id": 3,
                    "timestamp": minutes_ago(31),
                    "event_type": "firewall_completed",
                    "phase": "post_validation",
                    "severity": "info",
                    "firewall_id": "pa-460",
                    "message": "pa-460 upgraded successfully to 11.0.2",
                    "details": {},
                },
                {
                    "id": 4,
                    "timestamp": minutes_ago(5),
                    "event_type": "phase_started",
                    "phase": "install",
                    "severity": "info",
                    "firewall_id": "pa-461",
                    "message": "pa-461 install phase started",
                    "details": {},
                },
            ],
        }
    },
}


def json_response(handler: BaseHTTPRequestHandler, status_code: int, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


def html_page() -> str:
    return """<!doctype html>
<html lang="hu">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Palo Alto Upgrade GUI Preview</title>
  <style>
    :root {
      --bg: #070b14;
      --panel: rgba(16, 22, 37, 0.86);
      --panel-2: rgba(17, 24, 39, 0.72);
      --line: rgba(148, 163, 184, 0.16);
      --text: #e5eefb;
      --muted: #94a3b8;
      --cyan: #22d3ee;
      --emerald: #34d399;
      --amber: #fbbf24;
      --rose: #fb7185;
      --shadow: 0 30px 100px rgba(0,0,0,.35);
      font-synthesis-weight: none;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; background:
      radial-gradient(circle at top left, rgba(34,211,238,.17), transparent 28%),
      radial-gradient(circle at top right, rgba(52,211,153,.14), transparent 24%),
      linear-gradient(180deg, #07101d 0%, #08111a 45%, #04060a 100%);
      color: var(--text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    a { color: inherit; text-decoration: none; }
    .shell { max-width: 1620px; margin: 0 auto; padding: 22px; min-height: 100vh; display: grid; grid-template-columns: 260px 1fr; gap: 18px; }
    .sidebar, .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 28px; box-shadow: var(--shadow); backdrop-filter: blur(16px); }
    .sidebar { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
    .brand { display: flex; gap: 14px; align-items: center; }
    .brand-badge { width: 48px; height: 48px; border-radius: 18px; display: grid; place-items: center; background: rgba(34,211,238,.12); color: #a5f3fc; border: 1px solid rgba(34,211,238,.22); font-size: 22px; }
    .brand-title { font-size: 18px; font-weight: 700; }
    .brand-sub { color: var(--muted); text-transform: uppercase; letter-spacing: .26em; font-size: 11px; margin-top: 2px; }
    .nav { display: grid; gap: 10px; margin-top: 8px; }
    .nav a { padding: 12px 14px; border-radius: 18px; border: 1px solid transparent; color: #d9e7ff; background: rgba(255,255,255,.02); }
    .nav a.active, .nav a:hover { background: rgba(34,211,238,.12); border-color: rgba(34,211,238,.25); }
    .mini-card { margin-top: auto; padding: 14px; border-radius: 22px; background: rgba(255,255,255,.04); border: 1px solid var(--line); color: var(--muted); line-height: 1.55; }
    main { display: grid; gap: 18px; }
    .panel { padding: 18px; }
    .topbar { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--line); }
    h1 { margin: 0; font-size: clamp(28px, 3vw, 40px); letter-spacing: -0.03em; }
    .subtitle { margin-top: 8px; color: var(--muted); max-width: 900px; line-height: 1.6; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
    .pill { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,.05); border: 1px solid var(--line); color: #cbd5e1; font-size: 12px; text-transform: uppercase; letter-spacing: .18em; }
    .button { border: 0; border-radius: 14px; padding: 12px 16px; font-weight: 700; cursor: pointer; transition: transform .15s ease, opacity .15s ease, background .15s ease; }
    .button:hover { transform: translateY(-1px); }
    .button.primary { background: var(--cyan); color: #03111a; }
    .button.success { background: var(--emerald); color: #04120e; }
    .button.warn { background: var(--amber); color: #1a1202; }
    .button.ghost { background: rgba(255,255,255,.05); color: var(--text); border: 1px solid var(--line); }
    .grid-stats { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
    .stat { padding: 18px; border-radius: 24px; border: 1px solid var(--line); background: rgba(255,255,255,.04); }
    .stat .label { text-transform: uppercase; letter-spacing: .2em; font-size: 11px; color: var(--muted); }
    .stat .value { font-size: 34px; font-weight: 800; margin-top: 12px; letter-spacing: -0.04em; }
    .stat .hint { margin-top: 10px; color: var(--muted); font-size: 13px; line-height: 1.5; }
    .layout { display: grid; grid-template-columns: 1.15fr .85fr; gap: 18px; margin-top: 16px; }
    .section-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
    .section-title h2 { margin: 0; font-size: 18px; }
    .subtle { color: var(--muted); font-size: 13px; }
    .list { display: grid; gap: 12px; }
    .session-card, .event-card, .firewall-row, .info-card { border-radius: 22px; border: 1px solid var(--line); background: rgba(7, 10, 18, .55); padding: 14px; }
    .session-card.active { border-color: rgba(34,211,238,.24); background: rgba(34,211,238,.06); }
    .row { display: flex; justify-content: space-between; gap: 12px; align-items: start; }
    .badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }
    .pending { background: rgba(148,163,184,.12); color: #cbd5e1; }
    .running { background: rgba(34,211,238,.12); color: #a5f3fc; }
    .completed { background: rgba(52,211,153,.12); color: #86efac; }
    .failed { background: rgba(251,113,133,.12); color: #fda4af; }
    .paused { background: rgba(251,191,36,.12); color: #fcd34d; }
    .muted { color: var(--muted); }
    .small { font-size: 13px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 12px 10px; border-bottom: 1px solid rgba(148,163,184,.12); text-align: left; font-size: 14px; }
    th { text-transform: uppercase; letter-spacing: .16em; font-size: 11px; color: var(--muted); }
    .progress { height: 10px; border-radius: 999px; background: rgba(148,163,184,.14); overflow: hidden; }
    .bar { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #22d3ee, #34d399); }
    .audit { max-height: 600px; overflow: auto; display: grid; gap: 10px; }
    .right-grid { display: grid; gap: 18px; }
    .log { white-space: pre-wrap; font-size: 12px; line-height: 1.7; background: rgba(0,0,0,.22); padding: 14px; border-radius: 18px; border: 1px solid rgba(148,163,184,.12); }
    .toast { position: fixed; right: 22px; bottom: 22px; background: rgba(8, 15, 27, .92); border: 1px solid rgba(148,163,184,.18); color: #e2e8f0; padding: 12px 14px; border-radius: 18px; box-shadow: var(--shadow); opacity: 0; transform: translateY(10px); transition: opacity .18s ease, transform .18s ease; pointer-events: none; }
    .toast.show { opacity: 1; transform: translateY(0); }
    @media (max-width: 1200px) { .shell { grid-template-columns: 1fr; } .grid-stats { grid-template-columns: repeat(2, minmax(0,1fr)); } .layout { grid-template-columns: 1fr; } }
    @media (max-width: 720px) { .grid-stats { grid-template-columns: 1fr; } .topbar { flex-direction: column; } .actions { width: 100%; } .button { width: 100%; } }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-badge">⬢</div>
        <div>
          <div class="brand-title">Upgrade Console</div>
          <div class="brand-sub">Palo Alto workflow</div>
        </div>
      </div>
      <nav class="nav">
        <a class="active" href="#dashboard">Dashboard</a>
        <a href="#session">Session</a>
        <a href="#audit">Audit</a>
      </nav>
      <div class="mini-card">
        This is the Python-only preview. It mirrors the OM2248 GUI flow:
        session tracking, progress, audit events, and rollback.
      </div>
    </aside>

    <main>
      <section class="panel" id="dashboard">
        <div class="topbar">
          <div>
            <h1>Palo Alto Upgrade GUI</h1>
            <div class="subtitle">Single-pane view for upgrade tracking, audit observation, start/resume, and firewall rollback. The preview is wired to a mock API so you can interact with it in the browser right now.</div>
          </div>
          <div class="actions">
            <span class="pill" id="session-count">loading</span>
            <button class="button ghost" onclick="refreshAll()">Refresh</button>
            <button class="button primary" onclick="startSelected()">Start</button>
            <button class="button success" onclick="resumeSelected()">Resume</button>
            <button class="button warn" onclick="rollbackSelected()">Rollback</button>
          </div>
        </div>
        <div class="grid-stats" id="stats"></div>
      </section>

      <section class="layout">
        <div class="right-grid">
          <div class="panel" id="session">
            <div class="section-title">
              <h2>Sessions</h2>
              <div class="subtle">Click a session to inspect it</div>
            </div>
            <div class="list" id="sessions"></div>
          </div>

          <div class="panel">
            <div class="section-title">
              <h2>Firewalls</h2>
              <div class="subtle" id="selected-session-label"></div>
            </div>
            <div id="firewalls"></div>
          </div>
        </div>

        <div class="right-grid">
          <div class="panel">
            <div class="section-title">
              <h2>Selected session</h2>
              <div class="subtle" id="selected-session-status"></div>
            </div>
            <div id="selected-session" class="info-card"></div>
          </div>

          <div class="panel" id="audit">
            <div class="section-title">
              <h2>Audit trail</h2>
              <div class="subtle">Latest operational events</div>
            </div>
            <div class="audit" id="audit-log"></div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    let currentSessionId = null;

    function showToast(message) {
      const toast = document.getElementById('toast');
      toast.textContent = message;
      toast.classList.add('show');
      clearTimeout(window.__toastTimer);
      window.__toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
    }

    async function api(path, opts = {}) {
      const response = await fetch(path, {
        headers: { 'Content-Type': 'application/json' },
        ...opts,
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || response.statusText);
      }
      return response.json();
    }

    function statusBadge(status) {
      return `<span class="badge ${status}">${status}</span>`;
    }

    function selectSession(sessionId) {
      currentSessionId = sessionId;
      refreshAll();
    }

    async function refreshAll() {
      const list = await api('/api/sessions');
      const sessions = list.sessions || [];
      document.getElementById('session-count').textContent = `${sessions.length} sessions`;

      const stats = [
        ['Total sessions', sessions.length, 'All known upgrade runs'],
        ['Running', sessions.filter(s => s.status === 'running').length, 'Active upgrade runs'],
        ['Paused', sessions.filter(s => s.status === 'paused').length, 'Waiting for resume'],
        ['Completed', sessions.filter(s => s.status === 'completed').length, 'Closed successfully'],
        ['Failed', sessions.filter(s => s.status === 'failed').length, 'Attention needed'],
      ];
      document.getElementById('stats').innerHTML = stats.map(([label, value, hint]) => `
        <div class="stat">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
          <div class="hint">${hint}</div>
        </div>
      `).join('');

      document.getElementById('sessions').innerHTML = sessions.map(session => `
        <button class="session-card ${session.session_id === currentSessionId ? 'active' : ''}" onclick="selectSession('${session.session_id}')">
          <div class="row">
            <div>
              <div style="font-weight:800; font-size:16px">${session.session_id}</div>
              <div class="muted small">${session.total_firewalls} firewalls · target ${session.target_firmware_version}</div>
            </div>
            ${statusBadge(session.status)}
          </div>
          <div style="margin-top:12px" class="progress"><div class="bar" style="width:${session.status === 'completed' ? 100 : session.status === 'running' ? 63 : 0}%"></div></div>
        </button>
      `).join('');

      if (!currentSessionId && sessions.length) {
        currentSessionId = sessions[0].session_id;
      }

      if (currentSessionId) {
        await refreshSession(currentSessionId);
      }
    }

    async function refreshSession(sessionId) {
      const session = await api(`/api/sessions/${sessionId}`);
      const fwList = await api(`/api/firewalls/sessions/${sessionId}`);
      const summary = await api(`/api/audit/sessions/${sessionId}/summary`);
      const audit = await api(`/api/audit/sessions/${sessionId}?limit=30`);

      document.getElementById('selected-session-label').textContent = sessionId;
      document.getElementById('selected-session-status').textContent = session.status;
      document.getElementById('selected-session').innerHTML = `
        <div class="row">
          <div>
            <div style="font-size:20px; font-weight:800">${session.session_id}</div>
            <div class="muted small" style="margin-top:6px">${session.inventory_file} · ${session.execution_mode} · ${session.target_firmware_version}</div>
          </div>
          ${statusBadge(session.status)}
        </div>
        <div style="display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:12px; margin-top:14px">
          <div class="info-card"><div class="muted small">Created</div><div style="margin-top:6px">${session.created_at}</div></div>
          <div class="info-card"><div class="muted small">Started</div><div style="margin-top:6px">${session.started_at || '—'}</div></div>
          <div class="info-card"><div class="muted small">Current firewall index</div><div style="margin-top:6px">${session.current_firewall_index}</div></div>
          <div class="info-card"><div class="muted small">Audit events</div><div style="margin-top:6px">${summary.total_events}</div></div>
        </div>
      `;

      document.getElementById('firewalls').innerHTML = (fwList.firewalls || []).map(fw => `
        <div class="firewall-row">
          <div class="row">
            <div>
              <div style="font-weight:800">${fw.firewall_id}</div>
              <div class="muted small">${fw.firewall_ip} · ${fw.current_phase || 'queued'}</div>
            </div>
            ${statusBadge(fw.status)}
          </div>
          <div style="margin-top:10px" class="progress"><div class="bar" style="width:${fw.progress_percent || 0}%"></div></div>
          <div class="row" style="margin-top:10px; align-items:center">
            <div class="muted small">Current: ${fw.firmware_version_current || '—'} → Target: ${fw.firmware_version_target}</div>
            <button class="button warn" style="padding:8px 12px; font-size:12px" onclick="firewallRollback('${fw.firewall_id}')">Rollback</button>
          </div>
        </div>
      `).join('');

      document.getElementById('audit-log').innerHTML = (audit.events || []).map(event => `
        <div class="event-card">
          <div class="row">
            <div>
              <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap">
                ${statusBadge(event.severity)}
                <div style="font-weight:800">${event.event_type}</div>
                ${event.firewall_id ? `<div class="muted small">${event.firewall_id}</div>` : ''}
              </div>
              <div class="muted small" style="margin-top:8px">${event.message}</div>
            </div>
            <div class="muted small">${event.timestamp}</div>
          </div>
        </div>
      `).join('');
    }

    async function startSelected() {
      if (!currentSessionId) return;
      await api(`/api/sessions/${currentSessionId}/start`, { method: 'POST', body: '{}' });
      showToast('Session start requested');
      await refreshSession(currentSessionId);
    }

    async function resumeSelected() {
      if (!currentSessionId) return;
      await api(`/api/sessions/${currentSessionId}/resume`, { method: 'POST', body: '{}' });
      showToast('Session resume requested');
      await refreshSession(currentSessionId);
    }

    async function rollbackSelected() {
      if (!currentSessionId) return;
      const session = await api(`/api/sessions/${currentSessionId}`);
      const currentFw = (session.firewalls || []).find(fw => fw.status !== 'completed') || (session.firewalls || [])[0];
      if (!currentFw) return;
      const target = prompt(`Rollback ${currentFw.firewall_id} to which version?`, '10.2.4');
      if (!target) return;
      await api(`/api/firewalls/sessions/${currentSessionId}/${currentFw.firewall_id}/rollback`, {
        method: 'POST',
        body: JSON.stringify({ target_version: target }),
      });
      showToast(`Rollback triggered for ${currentFw.firewall_id}`);
      await refreshSession(currentSessionId);
    }

    async function firewallRollback(firewallId) {
      const target = prompt(`Rollback ${firewallId} to which version?`, '10.2.4');
      if (!target) return;
      await api(`/api/firewalls/sessions/${currentSessionId}/${firewallId}/rollback`, {
        method: 'POST',
        body: JSON.stringify({ target_version: target }),
      });
      showToast(`Rollback triggered for ${firewallId}`);
      await refreshSession(currentSessionId);
    }

    window.selectSession = selectSession;
    window.startSelected = startSelected;
    window.resumeSelected = resumeSelected;
    window.rollbackSelected = rollbackSelected;
    window.firewallRollback = firewallRollback;
    window.refreshAll = refreshAll;

    refreshAll().catch(err => {
      console.error(err);
      document.body.insertAdjacentHTML('beforeend', `<pre style="color:#fca5a5; padding:20px">${err.stack || err}</pre>`);
    });
    setInterval(() => refreshAll().catch(console.error), 5000);
  </script>
</body>
</html>
"""


class PreviewHandler(BaseHTTPRequestHandler):
    server_version = "PaloAltoPreview/1.0"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def _session(self, session_id: str) -> dict | None:
        return STATE["sessions"].get(session_id)

    def _selected_fw(self, session: dict, firewall_id: str) -> dict | None:
        for fw in session.get("firewalls", []):
            if fw["firewall_id"] == firewall_id:
                return fw
        return None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            html = html_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        if path == "/api/health":
            json_response(self, 200, {"status": "healthy", "component": "preview"})
            return

        if path == "/api/config":
            json_response(self, 200, STATE["config"])
            return

        if path == "/api/inventory-files":
            json_response(self, 200, {"inventory_files": STATE["inventory_files"], "total": len(STATE["inventory_files"])})
            return

        if path == "/api/firmware-versions":
            json_response(self, 200, {"firmware_versions": STATE["firmware_versions"], "total": len(STATE["firmware_versions"])})
            return

        if path == "/api/sessions":
            sessions = list(STATE["sessions"].values())
            json_response(self, 200, {"total": len(sessions), "sessions": [
                {
                    k: s[k]
                    for k in [
                        "session_id",
                        "status",
                        "created_at",
                        "started_at",
                        "completed_at",
                        "target_firmware_version",
                        "total_firewalls",
                    ]
                }
                for s in sessions
            ]})
            return

        if path.startswith("/api/sessions/") and path.count("/") == 3:
            session_id = path.rsplit("/", 1)[-1]
            session = self._session(session_id)
            if not session:
                json_response(self, 404, {"detail": "Session not found"})
                return
            json_response(self, 200, {
                "session_id": session["session_id"],
                "status": session["status"],
                "created_at": session["created_at"],
                "started_at": session["started_at"],
                "completed_at": session["completed_at"],
                "target_firmware_version": session["target_firmware_version"],
                "execution_mode": session["execution_mode"],
                "total_firewalls": session["total_firewalls"],
                "current_firewall_index": session["current_firewall_index"],
                "inventory_file": session["inventory_file"],
                "notes": session["notes"],
                "firewalls": session["firewalls"],
            })
            return

        if path.startswith("/api/sessions/") and path.endswith("/status"):
            session_id = path.split("/")[3]
            session = self._session(session_id)
            if not session:
                json_response(self, 404, {"detail": "Session not found"})
                return
            json_response(self, 200, {
                "session_id": session_id,
                "session_status": session["status"],
                "process_status": "running" if session["status"] == "running" else "idle",
                "current_firewall_index": session["current_firewall_index"],
                "total_firewalls": session["total_firewalls"],
            })
            return

        if path.startswith("/api/firewalls/sessions/"):
            parts = path.split("/")
            if len(parts) == 5:
                session_id = parts[4]
                session = self._session(session_id)
                if not session:
                    json_response(self, 404, {"detail": "Session not found"})
                    return
                json_response(self, 200, {
                    "session_id": session_id,
                    "total": len(session["firewalls"]),
                    "firewalls": session["firewalls"],
                })
                return
            if len(parts) == 6 and parts[5] != "logs":
                session_id = parts[4]
                firewall_id = parts[5]
                session = self._session(session_id)
                if not session:
                    json_response(self, 404, {"detail": "Session not found"})
                    return
                fw = self._selected_fw(session, firewall_id)
                if not fw:
                    json_response(self, 404, {"detail": "Firewall not found in session"})
                    return
                json_response(self, 200, {
                    "session_id": session_id,
                    "firewall_id": fw["firewall_id"],
                    "firewall_ip": fw["firewall_ip"],
                    "status": fw["status"],
                    "current_phase": fw["current_phase"],
                    "progress_percent": fw["progress_percent"],
                    "firmware_version_current": fw["firmware_version_current"],
                    "firmware_version_target": fw["firmware_version_target"],
                    "ha_enabled": fw["ha_enabled"],
                    "ha_primary": fw["ha_primary"],
                    "ha_peer_id": None,
                    "backup_file": None,
                    "error_message": None,
                    "started_at": fw["started_at"],
                    "completed_at": fw["completed_at"],
                    "recent_events": [
                        event for event in session["audit"] if event.get("firewall_id") == firewall_id
                    ],
                })
                return
            if len(parts) == 7 and parts[6] == "logs":
                session_id = parts[4]
                firewall_id = parts[5]
                session = self._session(session_id)
                if not session:
                    json_response(self, 404, {"detail": "Session not found"})
                    return
                log_content = f"Mock logs for {firewall_id}\n{('-' * 60)}\nBackup created\nImage installed\nPost validation passed\n"
                json_response(self, 200, {"session_id": session_id, "firewall_id": firewall_id, "log_content": log_content})
                return

        if path.startswith("/api/audit/sessions/") and path.endswith("/summary"):
            session_id = path.split("/")[4]
            session = self._session(session_id)
            if not session:
                json_response(self, 404, {"detail": "Session not found"})
                return
            events = session["audit"]
            summary = {"total_events": len(events), "by_event_type": {}, "by_severity": {"info": 0, "warning": 0, "error": 0, "critical": 0}}
            for e in events:
                summary["by_event_type"][e["event_type"]] = summary["by_event_type"].get(e["event_type"], 0) + 1
                summary["by_severity"][e["severity"]] += 1
            json_response(self, 200, {"session_id": session_id, **summary})
            return

        if path.startswith("/api/audit/sessions/"):
            session_id = path.split("/")[4]
            session = self._session(session_id)
            if not session:
                json_response(self, 404, {"detail": "Session not found"})
                return
            query = parse_qs(parsed.query)
            severity = query.get("severity", [None])[0]
            event_type = query.get("event_type", [None])[0]
            limit = int(query.get("limit", ["100"])[0])
            events = session["audit"]
            if severity:
                events = [e for e in events if e["severity"] == severity]
            if event_type:
                events = [e for e in events if e["event_type"] == event_type]
            events = events[:limit]
            json_response(self, 200, {"session_id": session_id, "total": len(events), "events": events})
            return

        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        body = self._read_json()

        if path.startswith("/api/sessions/") and path.endswith("/start"):
            session_id = path.split("/")[3]
            session = self._session(session_id)
            if not session:
                json_response(self, 404, {"detail": "Session not found"})
                return
            session["status"] = "running"
            session["started_at"] = session["started_at"] or now_iso()
            session["audit"].insert(0, {
                "id": len(session["audit"]) + 1,
                "timestamp": now_iso(),
                "event_type": "session_started",
                "phase": None,
                "severity": "info",
                "firewall_id": None,
                "message": "Upgrade session started from preview",
                "details": {},
            })
            json_response(self, 200, {"status": "started", "session_id": session_id})
            return

        if path.startswith("/api/sessions/") and path.endswith("/resume"):
            session_id = path.split("/")[3]
            session = self._session(session_id)
            if not session:
                json_response(self, 404, {"detail": "Session not found"})
                return
            session["status"] = "running"
            session["audit"].insert(0, {
                "id": len(session["audit"]) + 1,
                "timestamp": now_iso(),
                "event_type": "session_resumed",
                "phase": None,
                "severity": "info",
                "firewall_id": None,
                "message": "Upgrade session resumed from preview",
                "details": {},
            })
            json_response(self, 200, {"status": "resumed", "session_id": session_id})
            return

        if path.startswith("/api/firewalls/sessions/") and path.endswith("/rollback"):
            parts = path.split("/")
            session_id = parts[4]
            firewall_id = parts[5]
            session = self._session(session_id)
            if not session:
                json_response(self, 404, {"detail": "Session not found"})
                return
            fw = self._selected_fw(session, firewall_id)
            if not fw:
                json_response(self, 404, {"detail": "Firewall not found in session"})
                return
            target_version = body.get("target_version", fw["firmware_version_current"])
            fw["firmware_version_current"] = target_version
            fw["status"] = "completed"
            fw["current_phase"] = "post_validation"
            fw["progress_percent"] = 100
            fw["completed_at"] = now_iso()
            session["audit"].insert(0, {
                "id": len(session["audit"]) + 1,
                "timestamp": now_iso(),
                "event_type": "rollback_started",
                "phase": "rollback",
                "severity": "warning",
                "firewall_id": firewall_id,
                "message": f"Rollback triggered to version {target_version}",
                "details": {"target_version": target_version},
            })
            json_response(self, 200, {"status": "started", "session_id": session_id, "firewall_id": firewall_id, "version": target_version})
            return

        self.send_error(404, "Not found")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), PreviewHandler)
    print(f"Preview GUI running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
