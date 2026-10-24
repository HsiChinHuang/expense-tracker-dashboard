# Observability skeleton

This directory holds the local observability stack for THIS repo: a second,
separate compose file (`observability/compose.yaml`) that runs alongside the
application stack in `docker-compose.yml`. The application stack is frozen for
this milestone and is not modified by this skeleton; nothing here starts
automatically, and no gate in this milestone depends on a container being up.

This stack is LOCAL ONLY and is never exposed to public traffic.

## Start command

```
docker compose -f observability/compose.yaml up
```

Run it from the repository root. To bring it down again use
`docker compose -f observability/compose.yaml down`.

## Components

- Prometheus (host port 9090) scrapes metrics and evaluates alert rules, so
  the app's request, error and database-fallback signals become queryable
  series.
- Alertmanager (host port 9093) receives the alerts Prometheus fires and
  routes them to local receivers, where the fallback alert lands once its
  rules exist.
- Grafana (host port 3000) visualises the Prometheus queries as dashboards
  for the operator.

The Grafana admin credentials in `observability/compose.yaml` are local
placeholders in the same `change-me-locally` style the application stack
already uses. They are not secrets and must be replaced locally before any use
beyond a laptop.

## Port table

The mappings use the quoted `HOST:CONTAINER` form with host and container
ports equal, matching the style of `docker-compose.yml`:

| Service | Mapping |
|---|---|
| Prometheus | `9090:9090` |
| Alertmanager | `9093:9093` |
| Grafana | `3000:3000` |

This band is pinned once in `docs/plan.md` so that no card invents its own.
This card owns it; the alert-rule and dashboard cards reference it.

## Ports this stack must never bind

Five host ports are already spoken for and none of them may appear as a host
binding under `observability/`:

- `8000` - the application stack publishes it (`docker-compose.yml` maps
  `"8000:8000"`), and it is the first entry of `DEV_PORTS` in
  `scripts/dev/common.ts`.
- `5173` - the vite dev server, the second entry of the same `DEV_PORTS`
  array.
- `8001` - the recorded alternate Docker-stack mapping, held by the concurrent
  stack in the t41 evidence.
- `8137` - the pinned local verification endpoint used by the security and
  operations verification run and reused by the incident drill. Binding it
  here would silently break that gate.
- `18137` - appears as a host port in the t41 infrastructure evidence, so this
  card refuses it as a host binding as well.

The band above (3000, 9090, 9093) is disjoint from all five.

## Traces and logs block

The OTel collector, Loki and Tempo block is enabled for this milestone. It
runs as three active services in `observability/compose.yaml`:

- `otel-collector` receives and fans out traces, mounting
  `observability/collector.yaml` as its live configuration.
- `tempo` stores and serves those traces for query; the collector exports to
  the in-cluster endpoint `tempo:4317` (never scheme-qualified).
- `loki` aggregates logs that Grafana can query.

These three services publish no host ports, so the published host band stays
exactly 3000 / 9090 / 9093. The trace ids they carry are the `trace_id` the
API puts on every correlated request log line (backend/app/trace.py), and
the measured two-request journey is recorded in
`docs/criteria/trace_correlation_verification.md`.

Like the rest of this stack this block is LOCAL ONLY: `render.yaml` deploys
none of it, and nothing here starts automatically.

## Files owned elsewhere

`observability/prometheus.yml` and `observability/alerts.yaml` (scrape config
and alert rules) and `observability/dashboard.json` and
`observability/collector.yaml` (dashboard and collector config) are delivered
by the follow-up cards in this milestone. This skeleton only fixes the layout
and the port band they build on, so the Prometheus config mount point is
declared but the file itself arrives with the alert-rule card.
