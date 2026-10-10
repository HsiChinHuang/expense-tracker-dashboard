// Playwright project configuration (REQ-TEST-040, REQ-TECH-075).
//
// t27 lands the E2E harness as a SELF-CONTAINED workspace: the only
// dependency admitted by this card is @playwright/test 1.58.0 in
// e2e/package.json (REQ-TECH-075 - Playwright is the E2E tool), and the
// root / frontend manifests stay frozen (no workspaces key, ac6 diff gate).
//
// The numerics below are AC-pinned line-anchored values (REQ-TEST-040):
// timeout 60 s, retries 1, workers 1, HTML reporter, trace on first
// retry, screenshot on failure only, and an env-driven baseURL
// (E2E_BASE_URL) defaulting to the local frontend at localhost:5173.
//
// Execution is DEFERRED (plan.md phase_5 ruling 3): the browser store is
// absent on this host and network egress is forbidden, so the first real
// run happens in the t26 e2e.yml workflow on a browser-equipped runner.

import { defineConfig } from '@playwright/test';

/** Env-driven base URL; the local dev frontend is the default target. */
const BASE_URL = process.env.E2E_BASE_URL ?? 'http://localhost:5173';

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  retries: 1,
  workers: 1,
  reporter: [['html', { open: 'never' }], ['list']],
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  }
});
