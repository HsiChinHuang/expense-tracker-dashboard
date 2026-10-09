// Unique test users (REQ-TEST-041, REQ-TEST-045).
//
// Every test creates its OWN account: a timestamp (toISOString, compacted)
// plus a random id (Math.random, base36) folded into an `e2e+...@example.test`
// address, so parallel/retried runs never collide and no test can observe
// another test's data (REQ-TEST-045).
//
// NO CLEANUP RUNS BETWEEN TESTS - the suite deliberately leaves its data
// behind (REQ-TEST-045: "no cleanup between tests"). For an OPTIONAL manual
// sweep of the harness data after a CI run, the documented SQL is:
//
//   DELETE FROM users WHERE email LIKE 'e2e+%@example.test';
//
// (run via `docker compose exec db psql ...` or an equivalent client; it is
// documentation only - nothing in this workspace executes it).

/** The account shape every spec registers for itself. */
export interface UniqueUser {
  email: string;
  username: string;
  password: string;
}

/** Password shared by every generated E2E account (>= 8 chars, REQ-FE-061). */
export const E2E_PASSWORD = 'e2e-password-1';

/**
 * Build a fresh, never-used account (REQ-TEST-045): timestamp + random id
 * into the `e2e+<ts>-<rand>@example.test` address space.
 */
export const uniqueUser = (): UniqueUser => {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, '');
  const rand = Math.random().toString(36).slice(2, 10);
  const tag = `e2e+${stamp}-${rand}`;
  return {
    email: `${tag}@example.test`,
    username: tag.slice(4),
    password: E2E_PASSWORD
  };
};
