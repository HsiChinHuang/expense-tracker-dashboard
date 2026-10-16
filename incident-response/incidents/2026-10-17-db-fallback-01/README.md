# Incident 2026-10-17-db-fallback-01

This directory is the incident record for the operator-approved drill
2026-10-17-db-fallback-01. The ID obeys the incident-ID grammar
declared in incident-response/incidents/README.md: the marker is
YYYY-MM-DD-<slug>-<NN> and the exact regex is

^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z][a-z0-9]*(-[a-z0-9]+)*-[0-9]{2}$

The date in the ID is the operator-approved drill date; no event
timeline is authored here.

## What this directory holds

| Artifact | Writing card | Status at t83 |
|---|---|---|
| README.md | t83 | present (this file) |
| alert.json | t83 | present: verbatim copy of the DBFallbackActive entry of observability/alerts.yaml |
| evidence/ | t80 | absent: t80 harness runtime output, written when the drill runs |
| evidence.json | t84 | absent: t84 writes the measured trio |
| response.json | t84 | absent: t84 writes the measured trio |
| resolution.md | t84 | absent: t84 writes the measured trio |

## Deliberately incomplete

This directory is deliberately incomplete. t83 scaffolds the record and
the alert copy only; t84 is the completer that runs the measured drill
and writes evidence.json, response.json and resolution.md inside this
directory. t84 may write ONLY inside this incident directory and may
not edit either README or alert.json.

The alert.json copy names observability/alerts.yaml as its single
source; if that entry ever changes, this record must be re-checked
against the pinned canonical digest (see the incidents README).
