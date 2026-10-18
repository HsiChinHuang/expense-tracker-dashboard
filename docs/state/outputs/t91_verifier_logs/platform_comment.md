## t91 verify_issue: PASS (reached_state: verified)

Independently re-ran all five AC fences VERBATIM from docs/issues/t91.md at the exact built bytes (branch_sha 90de37048d038d7b94e20e05bd3b6d99e6d42aed, parent d9c090f98d12c43f87bfe39b184b75e1d51c7ee0). Builder rc not trusted; every leg re-measured.

- ac_hash recomputed from the on-disk card: sha256:1819a5061853f59d03dbd15c57fdfe7ccc118f95b1d43ea8c35e89aa03011f4b — MATCHES the card and the groom handoff. Probe payload sha256 1aca80712da2332e68b97710af2f082fba5b0a063ead1f1cf2a76d025fae9e47; all five fences carry the identical payload.
- ac1 GREEN rc=0: CORS_ORIGINS is exactly ["https://expense-tracker-dashboard-1qtu.onrender.com"] (live -1qtu origin present as exact JSON-array element; old no-suffix origin absent as element; raw line is the quoted JSON-array form).
- ac2 GREEN rc=0: APP_VERSION parses via js-yaml as the STRING '1.0.0' (not float); raw line is the quoted form value: "1.0.0".
- ac3 GREEN rc=0: tests[134] command byte-identical to BASE 890680e (len=2403, sha256 636d912f307b1945ad2da88c198556e81bdbf87b0522dd59fa802310f71cfbf2, issue_id t26 — no amendment); verbatim re-run rc=0.
- ac4 GREEN rc=0: render.yaml delta vs BASE is exactly the two value lines; the old origin literal is absent from the whole file; committed delta vs merge-base is render.yaml alone (working tree additionally carries the tolerated uncommitted t90 deploy.yml dirt).
- ac5 GREEN rc=0: gate scan set from all 318 index entries = [134,135,170,227,255]; no gate command pins the old origin. Legs: tests[134] rc=0, tests[135] rc=0, tests[170] rc=0, tests[255] rc=0; tests[227] rc=1 is the SANCTIONED parked RED (README pin-2 drift: gate pins 308 lines/a64efaa2, main carries 398/ca9343a8; its render.yaml digest leg never runs) — pre-existing, not owned by t91.
- Lint: ruff check on backend via the shared venv: rc=0, [] (0 errors, 0 warnings; delta touches no Python).
- Supplementary backend pytest (shared venv 2876b1d8c5e8a14c, Windows host): 2 failed / 300 passed. Both failures reproduce IDENTICALLY in the parent tree (8122b56, no t91 commit) and backend is byte-identical to BASE (git diff 890680e..HEAD -- backend is empty): test_static_serving CRLF autocrlf artifact and test_sqlite_fallback_api Windows temp-file lock (WinError 32). Environmental, pre-existing, not t91-owned (t89 precedent: 302 passed on the Linux venv).
- Environment disclosures: frontend/node_modules (gitignored) was absent in the worktree; js-yaml+argparse copied from the parent tree so tests[134] could run. UV_PROJECT_ENVIRONMENT/PYTHONPATH were empty at session start ([VENV_UNAVAILABLE] WARN); the shared venv was used explicitly for the backend legs.

Verdict: all five fences GREEN, ac_hash three-way match, no non-sanctioned failures. reached_state: verified. Handoff: docs/state/outputs/t91_verifier_verify_issue.json.
