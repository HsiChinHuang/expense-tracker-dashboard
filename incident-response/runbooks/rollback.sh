#!/usr/bin/env bash
# rollback.sh - gated, print-only rollback plan (card t82, criterion 13).
#
# This repository owns no production orchestrator, so an automated
# rollback performed by this script would be a fake. The honest shape
# is a PLAN: this script refuses to print anything unless a human has
# explicitly supplied the target, the previous image reference and the
# human flag; it then prints the steps and executes NONE of them.
#
# The authority this runbook defers to is incident-response/
# autonomy-policy.yaml. A redeployment is OUTSIDE that policy's
# allowed_actions, so a responder that runs this script without a
# human operator is out of policy even when every argument parses -
# the gate below is a floor, never a permission.
#
# Safe by construction: this script executes no step, opens no
# connection, writes no file anywhere. The denied command classes of
# the policy (service and container control, database mutation,
# version-control integration) appear in this file only as comments
# naming the denial, never on an executable line.

set -u

TARGET=""
IMAGE=""
HUMAN=0
REASON=""

usage() {
  echo "usage: rollback.sh --target <target> --image <image-ref>" >&2
  echo "       --i-am-human [--reason <text>]" >&2
  echo "refused: this runbook is argument-gated and prints a plan only for a human operator." >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || { echo "rollback: --target needs a value" >&2; usage; exit 2; }
      TARGET="$2"; shift 2 ;;
    --image)
      [ "$#" -ge 2 ] || { echo "rollback: --image needs a value" >&2; usage; exit 2; }
      IMAGE="$2"; shift 2 ;;
    --reason)
      [ "$#" -ge 2 ] || { echo "rollback: --reason needs a value" >&2; usage; exit 2; }
      REASON="$2"; shift 2 ;;
    --i-am-human)
      HUMAN=1; shift ;;
    *)
      echo "rollback: unknown argument rejected: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$TARGET" ] || [ -z "$IMAGE" ] || [ "$HUMAN" -ne 1 ]; then
  echo "rollback: REFUSED - an explicit --target, an explicit --image reference" >&2
  echo "rollback: and the --i-am-human flag are ALL mandatory before any plan" >&2
  echo "rollback: is printed." >&2
  usage
  exit 2
fi

echo "ROLLBACK PLAN (printed, executed by NOBODY here)"
echo "  target:      $TARGET"
echo "  image ref:   $IMAGE"
if [ -n "$REASON" ]; then
  echo "  reason:      $REASON"
fi
echo "  authority:   incident-response/autonomy-policy.yaml"
echo "  policy note: a redeployment is OUTSIDE allowed_actions, so running this"
echo "               plan without a human operator is out of policy."
echo "  step 1:      confirm the previous image against the deployment record"
echo "               that owns $TARGET - the record, not this script, is the"
echo "               source of the image reference to roll back to."
echo "  step 2:      redeploy that reference through the tooling that owns"
echo "               that target - this script performs no deploy itself."
echo "  step 3:      prove recovery with incident-response/runbooks/"
echo "               verify-recovery.sh and paste its measured output."
echo "Nothing was executed, no connection was opened, no file was written."
exit 0
