#!/usr/bin/env bash
# collect-evidence.sh - incident-response evidence collector (card t80).
#
# Gathers four artifact legs into incidents/<incident-id>/evidence/:
#   health    -> health.json   (the health payload, captured verbatim)
#   metrics   -> metrics.txt   (the /metrics snapshot, disclosed gap if absent)
#   log_tail  -> log_tail.txt  (tail of an explicit --log-file path)
#   version   -> version.txt   (the deployed version)
# plus a self-describing manifest.json with the pinned keys incident_id,
# collected_at, endpoint, legs, tree_hash and script_sha256.
#
# Local endpoints only. The default base URL is the pinned t41 verification
# endpoint http://127.0.0.1:8137/api/v1; a non-loopback --base-url value is
# refused BEFORE any request is made and before any file is written.
#
# The bundle is secret-free by construction: this script never reads any
# secret-bearing file, never dumps the environment, and the log tail comes
# from an explicit --log-file path so no ambient value can leak.
#
# --simulate-fallback points DATABASE_URL at the pinned dead loopback
# PostgreSQL target 127.0.0.1:55432 (change-me-locally placeholder style,
# never a real credential) and lets the merged product produce the degraded
# state itself via the merged startup probe. The restore is UNCONDITIONAL
# via the trap-on-EXIT below, following the merged t41 gate rule: a backend
# that cannot be answered from makes the leg FAIL rather than fake an
# offline PASS. The measured degraded drill itself is t84's deliverable.

set -u

BASE_URL_DEFAULT="http://127.0.0.1:8137/api/v1"
DEAD_DSN="postgresql+psycopg://expense:change-me-locally@127.0.0.1:55432/expense_tracker"
LOG_TAIL_LINES=200
READY_TRIES=30

SCRIPT_PATH="$0"
CHILD_PID=""
SCRATCH=""

usage() {
  echo "usage: collect-evidence.sh <incident-id> [--base-url URL] [--log-file PATH]"
  echo "       [--dry-run] [--print-manifest] [--simulate-fallback]"
  echo "refusing to guess the incident id: usage shown, exiting non-zero"
}

cleanup() {
  if [ -n "${CHILD_PID}" ]; then
    kill "${CHILD_PID}" 2>/dev/null
    wait "${CHILD_PID}" 2>/dev/null
    CHILD_PID=""
  fi
  unset DATABASE_URL
  if [ -n "${SCRATCH}" ] && [ -d "${SCRATCH}" ]; then
    rm -rf "${SCRATCH}"
    SCRATCH=""
  fi
}
trap cleanup EXIT

INCIDENT_ID=""
BASE_URL="${BASE_URL_DEFAULT}"
LOG_FILE=""
DRY_RUN=0
PRINT_MANIFEST=0
SIMULATE=0

if [ $# -lt 1 ]; then
  usage
  exit 2
fi
case "$1" in
  -*) echo "error: the incident id is required and must come first" >&2; usage; exit 2 ;;
esac
INCIDENT_ID="$1"
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --base-url)
      [ $# -ge 2 ] || { echo "error: --base-url needs a value" >&2; exit 2; }
      BASE_URL="$2"; shift 2 ;;
    --log-file)
      [ $# -ge 2 ] || { echo "error: --log-file needs a value" >&2; exit 2; }
      LOG_FILE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --print-manifest) PRINT_MANIFEST=1; shift ;;
    --simulate-fallback) SIMULATE=1; shift ;;
    *) echo "error: unknown option $1" >&2; usage; exit 2 ;;
  esac
done

# Refuse any non-loopback base URL BEFORE any request and before any write.
case "${BASE_URL}" in
  http://127.0.0.1:*|http://localhost:*) : ;;
  *)
    echo "error: refusing non-loopback base URL '${BASE_URL}' - local endpoints only" >&2
    echo "error: the collector talks to loopback addresses (127.0.0.1) only" >&2
    exit 3
    ;;
esac

COLLECTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SCRIPT_SHA256="$(sha256sum "${SCRIPT_PATH}" | awk '{print $1}')"
TREE_SRC=$( { git rev-parse HEAD 2>/dev/null || printf 'no-git-tree'; } )
TREE_HASH=$(printf '%s' "${TREE_SRC}" | sha256sum | awk '{print $1}')

ST_HEALTH=unavailable
ST_METRICS=unavailable
ST_LOGTAIL=unavailable
ST_VERSION=unavailable
BY_HEALTH=0
BY_METRICS=0
BY_LOGTAIL=0
BY_VERSION=0

emit_manifest() {
  printf '{\n'
  printf '  "incident_id": "%s",\n' "${INCIDENT_ID}"
  printf '  "collected_at": "%s",\n' "${COLLECTED_AT}"
  printf '  "endpoint": "%s",\n' "${BASE_URL}"
  printf '  "legs": {\n'
  printf '    "health": {"status": "%s", "file": "health.json", "bytes": %s},\n' \
    "${ST_HEALTH}" "${BY_HEALTH}"
  printf '    "log_tail": {"status": "%s", "file": "log_tail.txt", "bytes": %s},\n' \
    "${ST_LOGTAIL}" "${BY_LOGTAIL}"
  printf '    "metrics": {"status": "%s", "file": "metrics.txt", "bytes": %s},\n' \
    "${ST_METRICS}" "${BY_METRICS}"
  printf '    "version": {"status": "%s", "file": "version.txt", "bytes": %s}\n' \
    "${ST_VERSION}" "${BY_VERSION}"
  printf '  },\n'
  printf '  "tree_hash": "%s",\n' "${TREE_HASH}"
  printf '  "script_sha256": "%s"\n' "${SCRIPT_SHA256}"
  printf '}\n'
}

if [ "${DRY_RUN}" -eq 1 ]; then
  echo "dry-run: incident ${INCIDENT_ID} planned against ${BASE_URL}" >&2
  echo "dry-run: no requests, no writes, no spawned child" >&2
  if [ "${PRINT_MANIFEST}" -eq 1 ]; then
    emit_manifest
  fi
  exit 0
fi

if [ "${SIMULATE}" -eq 1 ]; then
  SCRATCH="$(mktemp -d)"
  export DATABASE_URL="${DEAD_DSN}"
  echo "simulate-fallback: DATABASE_URL aimed at the dead loopback target 127.0.0.1:55432" >&2
  SPORT="$(printf '%s' "${BASE_URL}" | sed -nE 's|^http://[^:/]+:([0-9]+).*|\1|p')"
  python3 -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port "${SPORT:-8137}" \
    >"${SCRATCH}/uvicorn.log" 2>&1 &
  CHILD_PID=$!
  if [ -z "${LOG_FILE}" ]; then
    LOG_FILE="${SCRATCH}/uvicorn.log"
  fi
  READY=0
  TRIES=0
  while [ "${TRIES}" -lt "${READY_TRIES}" ]; do
    if curl -fsS -m 2 "${BASE_URL}/health" >/dev/null 2>&1; then
      READY=1
      break
    fi
    sleep 1
    TRIES=$((TRIES + 1))
  done
  if [ "${READY}" -ne 1 ]; then
    echo "error: the spawned backend never answered on ${BASE_URL}" >&2
    echo "error: failing loudly, never faking an offline PASS" >&2
    exit 5
  fi
fi

if ! curl -s -m 3 -o /dev/null "${BASE_URL}/health"; then
  echo "error: the endpoint ${BASE_URL} is unreachable" >&2
  echo "error: the t41 gate rule makes the leg FAIL, not fake an offline PASS" >&2
  exit 4
fi

EV="incidents/${INCIDENT_ID}/evidence"
mkdir -p "${EV}"

if curl -fsS -m 5 "${BASE_URL}/health" >"${EV}/health.json" 2>/dev/null; then
  ST_HEALTH=ok
else
  : >"${EV}/health.json"
fi

if curl -fsS -m 5 "${BASE_URL}/metrics" >"${EV}/metrics.txt" 2>/dev/null; then
  ST_METRICS=ok
else
  # Disclosed gap: /metrics may not exist yet (the endpoint is t78's surface);
  # a missing metrics snapshot is recorded as unavailable, never as a crash.
  : >"${EV}/metrics.txt"
fi

if [ -n "${LOG_FILE}" ] && [ -f "${LOG_FILE}" ]; then
  if tail -n "${LOG_TAIL_LINES}" -- "${LOG_FILE}" >"${EV}/log_tail.txt" 2>/dev/null; then
    ST_LOGTAIL=ok
  fi
fi
[ -f "${EV}/log_tail.txt" ] || : >"${EV}/log_tail.txt"

if curl -fsS -m 5 "${BASE_URL}/version" >"${EV}/version.txt" 2>/dev/null; then
  ST_VERSION=ok
elif git rev-parse HEAD >"${EV}/version.txt" 2>/dev/null; then
  ST_VERSION=ok
else
  : >"${EV}/version.txt"
fi

BY_HEALTH="$(wc -c <"${EV}/health.json" | tr -dc '0-9')"
BY_METRICS="$(wc -c <"${EV}/metrics.txt" | tr -dc '0-9')"
BY_LOGTAIL="$(wc -c <"${EV}/log_tail.txt" | tr -dc '0-9')"
BY_VERSION="$(wc -c <"${EV}/version.txt" | tr -dc '0-9')"

emit_manifest >"${EV}/manifest.json"
echo "evidence bundle written to ${EV} (incident ${INCIDENT_ID})" >&2
if [ "${PRINT_MANIFEST}" -eq 1 ]; then
  emit_manifest
fi
exit 0
