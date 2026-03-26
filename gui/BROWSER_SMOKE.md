# Browser Smoke Test

Use this checklist after deploying the GUI on the VM or OM2248 container.

## URL

- `http://192.168.113.128:8080`

## Expected page

- The React dashboard shell should load.
- The page title should be `Palo Alto Upgrade GUI`.
- The top navigation should show `Dashboard`, `Upgrade`, `Audit`, and the session pages reached from the dashboard.

## Quick verification steps

1. Open the URL in a browser.
2. Confirm the page does not show the default nginx welcome page.
3. Confirm the API health endpoint works in the same browser session:
   - `http://192.168.113.128:8080/health`
4. Open DevTools and confirm there are no red console errors.
5. Click `Upgrade` and verify the upload form loads.
6. Upload a `.yml` or `.yaml` inventory file and confirm it appears in the inventory dropdown.
7. Click `Audit` and verify the filter panel loads.
8. Open an existing session and verify:
   - start/resume controls render
   - firewall list renders
   - rollback action is visible on firewall detail

## CLI smoke check

If you have shell access to the VM:

```bash
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/ | head -n 12
```

Expected:

- `/health` returns JSON with `"status":"healthy"`
- `/` returns the GUI HTML shell with `Palo Alto Upgrade GUI` in the title
