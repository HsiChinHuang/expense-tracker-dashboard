# Incident-response evidence collector

`collect-evidence.sh` is the incident-response evidence harness for this
repository. Given an incident ID it captures the four artifacts an on-call
engineer asks for first into a self-describing evidence bundle, and it can
produce a REAL degraded state on demand via `--simulate-fallback`.

This card ships the harness only. The measured degraded drill, the incident
records, the responder task, the autonomy policy and the runbooks belong to
the sibling cards (t81/t82/t83/t84); the raw bundle under `incidents/` is a
runtime output, never a committed artifact of this directory.

## Usage

```
bash incident-response/collect-evidence.sh <incident-id> \
  [--base-url URL] [--log-file PATH] [--dry-run] [--print-manifest] \
  [--simulate-fallback]
```

## Options

- `--base-url URL` - Backend base URL. Default `http://127.0.0.1:8137/api/v1`,
  the pinned local verification endpoint. Non-loopback values are REFUSED
  before any request or write.
- `--log-file PATH` - Explicit path whose last 200 lines become the `log_tail`
  artifact. No ambient log location is guessed.
- `--dry-run` - Print the plan and exit. Starts nothing, binds nothing, writes
  nothing. With `--print-manifest` it also prints a dry manifest with the same
  schema as a real bundle.
- `--print-manifest` - Print the manifest to stdout in addition to writing it.
- `--simulate-fallback` - Aim `DATABASE_URL` at the dead loopback PostgreSQL
  target `127.0.0.1:55432` and start a local uvicorn child so the merged
  startup probe engages the fallback and health reports the degraded state.

## The four artifact legs

Each leg writes one file into `incidents/<incident-id>/evidence/`:

- `health` -> `health.json` - `GET <base-url>/health`, captured verbatim.
- `metrics` -> `metrics.txt` - `GET <base-url>/metrics`; recorded as
  `unavailable` while the endpoint is missing: a disclosed gap, never a crash.
- `log_tail` -> `log_tail.txt` - `tail -n 200` of the explicit `--log-file`.
- `version` -> `version.txt` - `GET <base-url>/version`, falling back to the
  git commit.

## Manifest schema

`manifest.json` is machine-readable and self-describing. Keys:

- `incident_id` - the incident the bundle belongs to.
- `collected_at` - ISO-8601 UTC timestamp to the second.
- `endpoint` - the base URL used; always `http://127.0.0.1:<port>...`.
- `legs` - exactly `health`, `log_tail`, `metrics`, `version`, each with
  `status` (`ok` / `unavailable` / `failed`), `file`, and `bytes`.
- `tree_hash` - sha256 digest of the captured tree identity (64 hex).
- `script_sha256` - sha256 digest of this script (64 hex).

## Pinned endpoints

- Default base URL: `http://127.0.0.1:8137/api/v1` - the pinned local
  verification endpoint shared with the t41 gate. This script never re-pins
  or re-binds that port itself.
- Dead PostgreSQL target: `127.0.0.1:55432` - loopback on a port nothing
  listens on, used ONLY by `--simulate-fallback` with the merged
  `change-me-locally` placeholder credential style. It is never a remote
  host and never the compose `db` service.

## Refusals (the script refuses to guess)

- No incident ID: prints `usage` and exits non-zero.
- Unreachable endpoint: prints `unreachable` and exits non-zero - a backend
  that cannot be answered from makes the leg FAIL rather than fake an
  offline PASS.
- Non-loopback `--base-url`: prints `loopback` and exits non-zero BEFORE any
  request and before any file is written. Local endpoints only.

## Self-restoring simulate mode

`--simulate-fallback` restores `DATABASE_URL`, stops the uvicorn child it
spawned itself, and removes its scratch files UNCONDITIONALLY via a
`trap cleanup EXIT`. A failed capture never leaves the operator host in the
degraded state it was meant to observe. The only process this script may
ever stop is the child it started itself.

## No-secrets rule

The bundle is secret-free by construction. The collector never reads `.env`,
never dumps the environment, never reads `~/.ssh`, and never captures
tokens or password values. The log tail comes from an explicit `--log-file`
path so no ambient value can leak into the evidence.

## Windows / WSL note

The script is bash and runs under the same WSL bash used by the merged
verification gates. Committed blobs are pure-ASCII with LF endings; a fresh
Windows checkout may SMUDGE the working copy to CRLF (`core.autocrlf=true`),
which is a checkout artifact, not a change to the committed bytes.
