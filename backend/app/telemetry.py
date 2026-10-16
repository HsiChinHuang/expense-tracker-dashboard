"""OpenTelemetry metrics substrate for the expense tracker API (t78).

This module is the substrate, not a business metric: it installs the
OTel ``MeterProvider`` with the Prometheus exposition reader, pins the
three resource identity keys, exposes ``get_meter(name)`` for the
instrumentation card (t79), and serves the local-only ``/metrics``
endpoint. No business metric, counter or alert expression is declared
here; ``observability/alerts.yaml`` stays the single metric-name authority.

The named mechanism: ``/metrics`` is local-only by an in-process loopback
gate on the direct ASGI peer. The handler resolves ``request.client.host``
with ``ipaddress`` and serves the exposition only when ``is_loopback`` is
true (``127.0.0.1`` and ``::1``); every other peer gets a ``404`` that is
indistinguishable from an unknown path, and ``X-Forwarded-For`` is never
consulted (``app.auth.dependencies.get_client_ip`` returns the first XFF
hop and the rate limiter trusts it, so the header is a spoofing hazard
this gate must not import). In addition the route is mounted only when
``get_settings().ENVIRONMENT`` is ``development``, read at ``create_app()``
time, so a production-configured app does not carry the route at all. The
route is declared with ``include_in_schema=False`` so the frozen
``openapi.yaml`` contract and the ``docs_verification`` parity gate stay
byte-clean.

``setup_telemetry()`` is idempotent because ``create_app()`` runs once at
import and again per test application: a second ``set_meter_provider()``
would log ``Overriding of current MeterProvider is not allowed`` and
silently keep the first provider, so the guard returns before
constructing anything.

t79 adds the business instruments INSIDE that idempotent provider block,
on their own ``t79.telemetry.business`` scope: the two expense-creation
counters, the category-creation counter, and the ``db_fallback_active``
callback gauge that reads the merged startup latch. Their names are the
``observability/alerts.yaml`` inventory strings verbatim - that file
stays the single metric-name authority and this module is the only
permitted code-side mirror; the services import these constants and
never restate a name. No ``main.py`` call-site is added: registering
here keeps ``create_app()`` the single wiring point.
"""

import ipaddress
from collections.abc import Iterable
from time import monotonic

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import (
    CallbackOptions,
    Counter,
    Meter,
    Observation,
    get_meter_provider,
    set_meter_provider,
)
from opentelemetry.metrics import get_meter as api_get_meter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

from app.config import get_settings
from app.database import is_fallback

SERVICE_NAME: str = "expense-tracker-api"
"""The pinned ``service.name`` value (a literal, not a setting)."""

METRICS_PATH: str = "/metrics"
"""The exposition path this substrate serves (out of the OpenAPI contract)."""

SUBSTRATE_METER_SCOPE: str = "t78.telemetry.substrate"
"""Instrumentation-scope name of the substrate-owned runtime instrument."""

UPTIME_INSTRUMENT: str = "process.uptime"
"""OTel process semantic-convention instrument that keeps the exposition live.

It is a runtime instrument (the OpenTelemetry process semantic conventions),
declared so that a scrape always carries at least one sample line and the
``target_info`` series; it is not a business metric and names no alert.
"""

RESOURCE_KEY_SERVICE_NAME: str = "service.name"
"""Resource attribute key pinned by the card for the service identity."""

RESOURCE_KEY_DEPLOYMENT_ENVIRONMENT: str = "deployment.environment"
"""Resource attribute key pinned by the card for the deployment environment."""

RESOURCE_KEY_SERVICE_VERSION: str = "service.version"
"""Resource attribute key pinned by the card for the application version."""

UNKNOWN_PATH_DETAIL: str = "Not Found"
"""The body a stranger sees: identical to Starlette's unknown-path 404."""

_EXPOSITION_REGISTRY = CollectorRegistry()
"""Dedicated registry so the exposition carries only this app's series."""

_PROCESS_START = monotonic()
"""Monotonic origin for the substrate uptime instrument."""

BUSINESS_METER_SCOPE: str = "t79.telemetry.business"
"""Instrumentation-scope name of the business instruments t79 adds."""

EXPENSE_CREATED_TOTAL: str = "expense_created_total"
"""Expense success counter; the literal is the alerts.yaml inventory string."""

EXPENSE_CREATE_FAILURES_TOTAL: str = "expense_create_failures_total"
"""Expense failure counter; the literal is the alerts.yaml inventory string."""

CATEGORY_CREATED_TOTAL: str = "category_created_total"
"""Category success counter; the literal is the alerts.yaml inventory string."""

DB_FALLBACK_ACTIVE: str = "db_fallback_active"
"""Fallback-latch gauge; the literal is the alerts.yaml inventory string."""

_BUSINESS_COUNTERS: dict[str, Counter] = {}
"""Counters registered by :func:`setup_telemetry`, keyed by pinned name."""


def build_resource() -> Resource:
    """Build the OTel resource carrying the three pinned identity keys.

    Returns:
        Resource: Resource whose attributes are the pinned ``service.name``
            literal plus the configured ``deployment.environment`` and
            ``service.version`` values.
    """
    settings = get_settings()
    return Resource.create(
        {
            RESOURCE_KEY_SERVICE_NAME: SERVICE_NAME,
            RESOURCE_KEY_DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
            RESOURCE_KEY_SERVICE_VERSION: settings.APP_VERSION,
        }
    )


def _report_uptime(options: CallbackOptions) -> Iterable[Observation]:
    """Report the process uptime for the substrate liveness instrument.

    Args:
        options: Callback timeout supplied by the SDK (unused).

    Returns:
        Iterable[Observation]: One observation carrying seconds since the
            substrate module was imported.
    """
    return [Observation(round(monotonic() - _PROCESS_START, 3))]


def _report_fallback_active(options: CallbackOptions) -> Iterable[Observation]:
    """Report the merged fallback latch for the ``DBFallbackActive`` series.

    The value is computed at SCRAPE time from the one latch the process
    already owns (:func:`app.database.is_fallback`, startup-only by
    construction); nothing here caches it or re-probes the database.

    Args:
        options: Callback timeout supplied by the SDK (unused).

    Returns:
        Iterable[Observation]: A LIST holding one observation, 1 while
            the latch is engaged and 0 otherwise. The list is load-
            bearing: a callback returning a bare Observation fails
            inside the SDK and the series silently vanishes.
    """
    return [Observation(1 if is_fallback() else 0)]


def _register_business_instruments(provider: MeterProvider) -> None:
    """Declare the three business counters and the fallback gauge, once.

    Called from :func:`setup_telemetry` inside the idempotent provider
    block, so the instruments exist exactly once per process on their
    own scope and the alert rules in ``observability/alerts.yaml`` read
    the same strings the exposition carries.

    Args:
        provider: The meter provider about to become process-wide.
    """
    meter = provider.get_meter(BUSINESS_METER_SCOPE)
    _BUSINESS_COUNTERS[EXPENSE_CREATED_TOTAL] = meter.create_counter(
        name=EXPENSE_CREATED_TOTAL,
        description="Expense creations that reached persistence.",
    )
    _BUSINESS_COUNTERS[EXPENSE_CREATE_FAILURES_TOTAL] = meter.create_counter(
        name=EXPENSE_CREATE_FAILURES_TOTAL,
        description="Expense creations rejected by a domain error.",
    )
    _BUSINESS_COUNTERS[CATEGORY_CREATED_TOTAL] = meter.create_counter(
        name=CATEGORY_CREATED_TOTAL,
        description="Custom categories that reached persistence.",
    )
    meter.create_observable_gauge(
        name=DB_FALLBACK_ACTIVE,
        callbacks=[_report_fallback_active],
        description="1 while the SQLite fallback latch is engaged.",
    )


def setup_telemetry(application: FastAPI) -> None:
    """Install the OTel meter provider with the Prometheus reader, once.

    Args:
        application: The application being created. The provider is global
            (the OTel process-wide meter provider), so the argument only
            keeps the wiring call-site readable and testable.
    """
    if isinstance(get_meter_provider(), MeterProvider):
        return

    reader = PrometheusMetricReader(registry=_EXPOSITION_REGISTRY)
    provider = MeterProvider(resource=build_resource(), metric_readers=[reader])
    provider.get_meter(SUBSTRATE_METER_SCOPE).create_observable_gauge(
        name=UPTIME_INSTRUMENT,
        callbacks=[_report_uptime],
        unit="s",
        description="Seconds this API process has been running (substrate liveness).",
    )
    _register_business_instruments(provider)
    set_meter_provider(provider)


def get_meter(name: str) -> Meter:
    """Return a meter from the installed provider (the t79 entry point).

    Args:
        name: Instrumentation-scope name chosen by the caller.

    Returns:
        Meter: A meter bound to the process-wide provider installed by
            :func:`setup_telemetry`.
    """
    return api_get_meter(name)


def get_business_counter(name: str) -> Counter:
    """Return a business counter registered on the t79 scope.

    Services call this with a module constant from this file, never with
    a restated metric string. ``create_counter`` on the OTel API is a
    get-or-deduplicate lookup by name, so the fallback path cannot
    register a second instrument even if it is reached.

    Args:
        name: One of the pinned counter constants in this module.

    Returns:
        Counter: The instrument registered by :func:`setup_telemetry`.
    """
    counter = _BUSINESS_COUNTERS.get(name)
    if counter is not None:
        return counter
    return get_meter(BUSINESS_METER_SCOPE).create_counter(name=name)


def exposition_body() -> bytes:
    """Render the Prometheus exposition text for the current collection.

    Returns:
        bytes: The exposition body served on ``/metrics``, including the
            ``target_info`` series that carries the pinned resource keys.
    """
    return generate_latest(_EXPOSITION_REGISTRY)


def is_loopback_peer(request: Request) -> bool:
    """Report whether the DIRECT ASGI peer is a loopback address.

    ``X-Forwarded-For`` is deliberately never read: the header is the
    spoofable client identity the rate limiter already trusts.

    Args:
        request: The incoming request whose client tuple is checked.

    Returns:
        bool: True only for a resolvable loopback peer (``127.0.0.1``,
            ``::1``); False for any other address and for a missing or
            non-IP peer such as the ``TestClient`` default.
    """
    client = request.client
    if client is None:
        return False
    try:
        address = ipaddress.ip_address(client.host)
    except ValueError:
        return False
    return address.is_loopback


def register_metrics(application: FastAPI) -> None:
    """Mount the local-only ``/metrics`` exposition route on the app.

    The route is mounted only in ``development`` and answers only the
    loopback peer; a refused peer receives the same 404 body an unknown
    path produces.

    Args:
        application: The application to extend.
    """
    if get_settings().ENVIRONMENT != "development":
        return

    @application.get(METRICS_PATH, include_in_schema=False)
    def serve_metrics(request: Request) -> Response:
        """Serve the Prometheus exposition to a loopback peer only.

        Args:
            request: The incoming request, used for the direct-peer check.

        Returns:
            Response: The exposition body for a loopback peer, else the
                unknown-path 404 shape.
        """
        if not is_loopback_peer(request):
            return JSONResponse(status_code=404, content={"detail": UNKNOWN_PATH_DETAIL})
        return Response(content=exposition_body(), media_type=CONTENT_TYPE_LATEST)
