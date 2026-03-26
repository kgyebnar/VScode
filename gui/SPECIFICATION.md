# Palo Alto Upgrade Web GUI Specification

## Purpose

The web GUI provides a simple operational surface for Palo Alto firewall upgrades.
It is focused on two things:

1. Tracking upgrade progress in real time.
2. Observing the process audit trail in a clear, searchable way.

The first release should stay intentionally small. No role-based access control is required for now.

## Scope

### In Scope

- Create and view upgrade sessions
- Start an upgrade session
- Resume a paused or interrupted session
- Roll back a firewall or session to a previous version
- Monitor live progress by firewall and by phase
- View audit events and process history
- Inspect firewall-level status and logs
- Show the current operational state of a session at a glance

### Out of Scope

- Role-based access control
- Multi-tenant separation
- Approval workflows
- Notifications by email or chat
- Advanced scheduling
- Diff-based config comparison
- Complex report generation

## Primary Users

The UI is for operators who run upgrades and need to answer:

- What is running right now?
- Where is the session stuck?
- Which firewall is failing?
- What has already happened?
- Can I resume or roll back safely?

## Core Objects

### Upgrade Session

A session is one upgrade execution over one inventory selection.

Important fields:

- Session ID
- Created at
- Started at
- Completed at
- Status
- Target firmware version
- Execution mode
- Inventory file
- Notes

### Firewall Item

Each firewall in a session has its own state.

Important fields:

- Firewall ID
- Firewall IP
- Current firmware version
- Target firmware version
- Status
- Current phase
- Progress percent
- HA flags
- Backup file
- Log file
- Error message

### Audit Event

Every state change or operator action is written as an audit event.

Important fields:

- Timestamp
- Session ID
- Firewall ID
- Event type
- Phase
- Severity
- Message
- Details

## Main Workflows

### 1. Session Creation

The operator creates a new session from an inventory file.

Inputs:

- Inventory file path
- Target firmware version
- Execution mode
- Optional notes
- Optional extra vars

Outputs:

- Session record is created
- Firewall rows are created
- Audit event is written

### 2. Start Upgrade

The operator starts a pending session.

Behavior:

- Validate that the session exists
- Validate that the session is in `pending` state
- Launch the playbook executor
- Mark session as `running`
- Record the start event in audit log
- Stream progress updates to the UI

### 3. Resume Upgrade

The operator resumes a session that is paused or interrupted.

Behavior:

- Validate the session state
- Continue from the next actionable firewall or phase
- Keep existing progress and audit trail intact
- Record resume event

### 4. Rollback

Rollback is a per-firewall recovery action.

Behavior:

- Allow rollback from firewall detail view
- Select a target version that is already available on the device
- Launch rollback playbook for the chosen firewall
- Record rollback start, success, and failure events
- Keep rollback visible inside the session timeline

### 5. Audit Review

The operator can inspect what happened during the run.

Behavior:

- Show session-level audit log
- Filter by severity, event type, and firewall
- Drill into a single firewall timeline
- Show the latest state changes first

## UI Pages

### Dashboard

The landing page shows:

- Active sessions
- Recently completed sessions
- Failed sessions
- Current progress summary
- Recent audit activity

### Session Detail

Shows the full state of one upgrade run:

- Session metadata
- Firewall list
- Current phases
- Progress bars
- Action buttons
- Event timeline

### Firewall Detail

Shows one firewall in detail:

- Version information
- HA metadata
- Backup file reference
- Log reference
- Error state
- Per-firewall audit events
- Rollback action

### Audit View

Shows the process audit history:

- Search by session
- Filter by firewall
- Filter by severity
- Filter by event type
- Export-ready table view

## Navigation

Simple navigation is enough for the MVP:

- Dashboard
- Sessions
- Session detail
- Firewall detail
- Audit log

## Basic Actions

### Start

Used to begin a pending upgrade session.

### Resume

Used to continue a paused or interrupted session.

### Rollback

Used to revert a selected firewall.

### View Logs

Used to inspect raw output for troubleshooting.

## Live Data Requirements

The GUI should refresh state from two sources:

- REST API for session and audit data
- WebSocket for live progress and event streaming

The WebSocket channel should be used for:

- Phase transitions
- Progress updates
- Firewall status changes
- Start/resume/rollback events
- Error events

## Audit Requirements

The audit trail must be complete enough to answer:

- Who initiated the action?
- When did it happen?
- Which session was affected?
- Which firewall was affected?
- What changed?
- Did it succeed or fail?

Audit events should be written for:

- Session creation
- Session start
- Session resume
- Rollback start
- Rollback completion
- Phase start
- Phase completion
- Warning
- Error
- Session completion

## UX Principles

- Show state clearly and early
- Keep actions visible on the page where they matter
- Prefer one primary action per screen
- Make failure states explicit
- Make paused or interrupted state obvious
- Keep the UI usable on desktop and laptop first, mobile second

## Non-Functional Requirements

- Fast initial load
- Real-time status updates without polling where possible
- No RBAC for the first version
- Local persistence for audit data
- Minimal operator steps for common workflows
- Clear error messages when playbooks fail or disconnect

## Status Model

Recommended session statuses:

- `pending`
- `running`
- `paused`
- `completed`
- `failed`

Recommended firewall statuses:

- `pending`
- `in_progress`
- `completed`
- `failed`
- `skipped`
- `paused`

## Success Criteria

The MVP is successful when:

1. An operator can create a session and start it.
2. An operator can see live progress and audit events.
3. An operator can resume a paused or interrupted run.
4. An operator can roll back a selected firewall.
5. The audit trail is readable and complete.

## Suggested First Build Order

1. Session dashboard and detail views
2. Live event stream and progress rendering
3. Audit table and filters
4. Start/resume/rollback action buttons
5. Raw log viewer

## Open Questions For Next Round

- Should `pause` and `cancel` stay in the MVP or be hidden for now?
- Should rollback be session-wide or strictly firewall-level in the UI?
- Should the session list default to active sessions only or all sessions?
- Should the audit view support CSV export in v1?
