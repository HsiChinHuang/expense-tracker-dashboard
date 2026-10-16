#!/usr/bin/env bash
# verify-recovery.sh - measure recovery, never assert it (card t82).
#
# The recovery condition is a merged contract, not an invention of this
# runbook: backend/app/routers/health.py returns status "degraded"
# exactly when the fallback latch is active, so recovery is ONE payload
# read as a conjunction - status "ok" AND fallback_active false. A
# script that checked only one of the two fields would accept the two
# contradictory shapes this runbook must reject, so both are asserted.
#
# The default endpoint is the pinned local verification endpoint
# http://127.0.0.1:8137/api/v1/health; an argument may override it, but
# a non-loopback override is REFUSED before any request is made, and
# this script never contacts anything else. Exit 0 is earned only by
# the accepting shape and prints RECOVERY_VERIFIED; every failure shape
# prints a readable reason and exits non-zero. A read that could not be
# taken (missing curl, missing python3, unreachable endpoint) FAILS -
# a skipped read is never a recovery.

set -u

ENDPOINT_DEFAULT="http://127.0.0.1:8137/api/v1/health"
URL="${1:-$ENDPOINT_DEFAULT}"

if ! command -v curl >/dev/null 2>&1; then
  echo "verify-recovery: FAIL - curl is missing and the recovery leg may never be skipped" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "verify-recovery: FAIL - python3 is missing, so the payload cannot be parsed" >&2
  exit 1
fi

case "$URL" in
  "http://127.0.0.1" | "http://localhost" | "http://127.0.0.1:"* | "http://localhost:"*)
    ;;
  *)
    echo "verify-recovery: REFUSED - only a loopback endpoint (127.0.0.1 or" >&2
    echo "verify-recovery: localhost) may be read; refused before any request." >&2
    echo "verify-recovery: rejected url: $URL" >&2
    exit 2
    ;;
esac

BODY=""
BODY=$(curl -s -m 5 "$URL")
CURL_RC=$?

if [ "$CURL_RC" -ne 0 ]; then
  echo "verify-recovery: FAIL - endpoint unreachable at $URL (curl exit $CURL_RC)" >&2
  echo "verify-recovery: an endpoint that cannot be answered from is NOT a" >&2
  echo "verify-recovery: recovered service." >&2
  exit 1
fi

python3 - "$BODY" <<'PY'
import json
import sys

try:
    doc = json.loads(sys.argv[1])
except Exception as exc:
    print("verify-recovery: NOT_RECOVERED - body is not JSON (%s)" % exc)
    sys.exit(1)

if not isinstance(doc, dict) or "status" not in doc or "fallback_active" not in doc:
    print("verify-recovery: NOT_RECOVERED - payload lacks the health contract "
          "fields status/fallback_active: %r" % (doc,))
    sys.exit(1)

status = doc.get("status")
fallback = doc.get("fallback_active")

if status == "ok" and fallback is False:
    print("RECOVERY_VERIFIED: status ok AND fallback_active false "
          "(database=%s version=%s)" % (doc.get("database"), doc.get("version")))
    sys.exit(0)

print("verify-recovery: NOT_RECOVERED - status=%r fallback_active=%r; the "
      "recovery condition is status ok AND fallback_active false, so a "
      "fallback-active or degraded payload fails even when the other "
      "field looks healthy" % (status, fallback))
sys.exit(1)
PY
