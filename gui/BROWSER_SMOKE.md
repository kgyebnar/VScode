# Browser Smoke Test

Use this checklist after deploying the GUI on the VM or OM2248 container.

## URL

- `http://192.168.113.128:8080`

## Expected page

- The React dashboard shell should load.
- The page title should be `Palo Alto Upgrade GUI`.
- The top navigation should show `Dashboard`, `New Session`, `Session Detail`, and `Audit`.

## Quick verification steps

1. Open the URL in a browser.
2. Confirm the page does not show the default nginx welcome page.
3. Confirm the API health endpoint works in the same browser session:
   - `http://192.168.113.128:8080/health`
4. Open DevTools and confirm there are no red console errors.
5. Click `New Session` and verify the form loads.
6. Click `Audit` and verify the filter panel loads.
7. Open an existing session and verify:
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
