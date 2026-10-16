# incident-response/incidents/ - the incident record scaffold

This directory is the single place where incident records live. t83
created the scaffold and owns the incident-ID constant and the ID grammar
below; no other card may define, rename or renumber an incident ID.

## Incident-ID grammar

The incident-ID grammar is YYYY-MM-DD-<slug>-<NN> and the exact regex
this README declares (and that every tool and every later card must
obey) is:

^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z][a-z0-9]*(-[a-z0-9]+)*-[0-9]{2}$

The ONE incident ID owned by this milestone is 2026-10-17-db-fallback-01.
The date inside the ID is the operator-approved drill date, not a
fabricated event timeline. incidents/ holds exactly that one incident
directory plus this README.

## Artifact owner table

Every incident directory follows this contract. The writing-card column
names the card that WRITES the artifact; the scaffold is deliberately
incomplete until those cards run their own measured work.

| Artifact | Writing card | Contract |
|---|---|---|
| README.md | t83 | the directory contract, written by t83 |
| alert.json | t83 | verbatim copy of the DBFallbackActive entry |
| evidence/ | t80 | raw evidence bundle, t80 harness runtime output |
| evidence.json | t84 | measured trio, never authored before the drill |
| response.json | t84 | measured trio, never authored before the drill |
| resolution.md | t84 | measured trio, never authored before the drill |

## Copy source and the re-check rule

alert.json is a verbatim copy of the DBFallbackActive entry of
observability/alerts.yaml, produced by extraction, never by hand-typing.
If that entry ever changes, this card and the t84 record must be
re-checked: ac2 re-extracts the entry live and the pinned canonical
digest REDs on any key or value drift.

## Write boundary

t84 may write ONLY inside the incident directory and may not edit either
README or alert.json. The t80 harness writes evidence/ when the drill
runs; this scaffold creates no bundle and no trio of its own.
