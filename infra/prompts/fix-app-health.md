The generated app at `apps/{app-name}` FAILED its functional health check.

Here is exactly what failed (real evidence captured by the checker):

```
{diagnostics}
```

Fix ONLY the responsible file(s) so the app passes the health check. The health
check, in order, verifies:
1. Required files exist (`server.py`, `index.html`, `js/*.js`, `css/*.css`).
2. `server.py` starts and binds its port.
3. `GET /api/state` returns 404 before any push; `PUT /api/state` returns 200;
   `GET /api/state` then returns 200 with the same JSON; `POST /api/reset` returns 200.
4. When `index.html` is loaded in a browser, the app's own JavaScript PUTs its full
   state to `/api/state` on load.

Do NOT rewrite working parts of the app. Do NOT change `server.py` if the failure is
in the browser JavaScript (most "did not PUT state" failures are JS-init bugs — an
uncaught exception in `app.js`/`state.js`/`views.js` prevents the state push). Make the
smallest change that fixes the reported failure, then stop.
