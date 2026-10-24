"""SDK-only trace substrate and log correlation for the expense tracker API (t122).

This module is the trace half of the observability trio: an OpenTelemetry
``TracerProvider`` plus one ASGI middleware that opens one server span per
request, and the log-correlation plumbing that puts the ACTIVE span's
32-hex ``trace_id`` on every app log line the request emits.

The named mechanism: ``TraceContextMiddleware`` extracts the W3C
``traceparent`` header (when a caller sends one), activates the resulting
context, and starts a SERVER span named after the route. The OTel context
is a ContextVar, so any log record emitted while the request is active can
read the same trace id: :class:`TraceCorrelationFilter` is a
``logging.Filter`` attached at the HANDLER level (a root-logger filter
never sees propagated records - measured, locked finding of this card) and
sets ``record.trace_id`` to the 32-hex id of the current span, or ``None``
when no recording span is active. :func:`install_trace_correlation` wires
the filter onto every handler of the root logger and of the uvicorn
loggers, and patches the uvicorn access formatter so the one access line
per request carries ``"trace_id": "<hex>"`` inside its JSON payload.

SDK-only by constraint: ``backend/pyproject.toml`` and ``backend/uv.lock``
are byte-frozen (leg 227), so this module imports ONLY ``opentelemetry-sdk``
surface that the lockfile already declares. No OTLP exporter package exists
in the locked environment; the collector/Tempo/Loki stack in
``observability/compose.yaml`` is therefore the staged destination for the
trace data, and the correlation itself is measured in-process (an
InMemorySpanExporter in the test, the process-wide provider in dev). The
hosted ``render.yaml`` deployment runs none of that stack.

Idempotence: like ``setup_telemetry``, installation is guarded so a second
``create_app()`` (which the test suite runs per test) never overrides the
process-wide provider.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable, MutableMapping
from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import SpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode
from starlette.types import ASGIApp, Receive, Scope, Send

TRACER_SCOPE: str = "t122.trace.correlation"
"""Instrumentation-scope name of the request middleware's tracer."""

TRACEPARENT_HEADER: str = "traceparent"
"""The W3C trace context header this middleware extracts (never invented)."""

TRACE_ID_FIELD: str = "trace_id"
"""The structured log field this card adds to every correlated line."""

INVALID_TRACE_ID: str = "0" * 32
"""The all-zero id: the instrumentation-collapse signature the tests reject."""


class FileSpanExporter(SpanExporter):
    """Export finished spans as JSON lines to a file-like sink.

    The locked environment has no OTLP exporter package (pyproject/uv.lock
    are byte-frozen), so the local pipeline's collector leg is fed by this
    stdlib exporter instead: one JSON object per finished span, written to
    a sink the caller owns (a file in development, an in-memory list in
    tests). It never raises into the SDK.
    """

    def __init__(self, sink: Any) -> None:
        """Bind the exporter to a writable text sink.

        Args:
            sink: Any object with a ``write(str)`` method.
        """
        self._sink = sink

    def export(self, spans: Iterable[ReadableSpan]) -> Any:
        """Serialize each span as one JSON line.

        Args:
            spans: The finished spans the processor hands over.

        Returns:
            Any: Always SUCCESS; export failures must never crash a request.
        """
        for span in spans:
            ctx = span.get_span_context()
            if ctx is None:
                continue
            line = {
                "name": span.name,
                "trace_id": format(ctx.trace_id, "032x"),
                "span_id": format(ctx.span_id, "016x"),
                "kind": str(span.kind),
                "status": span.status.status_code.name if span.status else None,
            }
            try:
                self._sink.write(json.dumps(line) + "\n")
            except Exception:  # noqa: BLE001 - export must never raise
                pass
        return None

    def shutdown(self) -> None:
        """No resources to release."""

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Text sinks are unbuffered from this exporter's point of view.

        Args:
            timeout_millis: Ignored.

        Returns:
            bool: Always True.
        """
        return True


def install_tracing(
    resource: Resource | None = None,
    processor: SpanProcessor | None = None,
) -> TracerProvider:
    """Install the process-wide TracerProvider exactly once.

    Args:
        resource: Optional resource override (tests pin their own).
        processor: Optional span processor to attach to the provider
            (the test harness attaches an in-memory exporter; the default
            production install keeps spans in-process because the locked
            environment ships no network exporter).

    Returns:
        TracerProvider: The provider now installed (or the pre-existing one).
    """
    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider):
        return current
    provider = TracerProvider(resource=resource)
    if processor is not None:
        provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return provider


class TraceContextMiddleware:
    """Pure ASGI middleware: one SERVER span (one trace id) per request.

    A pure-ASGI class (not BaseHTTPMiddleware) so streaming responses and
    exception propagation stay byte-for-byte what Starlette does today; the
    only added behaviour is the extracted context, the span, and the
    ``trace_id`` the correlation filter reads from the activated context.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Wrap the application.

        Args:
            app: The next ASGI layer.
        """
        self._app = app
        self._tracer = trace.get_tracer(TRACER_SCOPE)

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Open one span around one HTTP request.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive channel.
            send: The ASGI send channel.
        """
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        headers: MutableMapping[str, str] = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in scope.get("headers") or []
        }
        parent: Context = extract(headers)
        route = scope.get("route")
        method = scope.get("method", "HTTP")
        name = f"{method} {route.path}" if route is not None else str(scope.get("path", "HTTP"))
        with self._tracer.start_as_current_span(
            name, context=parent, kind=SpanKind.SERVER, attributes={"http.method": method}
        ) as span:
            span.set_attribute("http.target", str(scope.get("path", "")))
            try:
                await self._app(scope, receive, send)
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))
                raise


class TraceCorrelationFilter(logging.Filter):
    """Handler-level filter that stamps ``record.trace_id`` from the span.

    Deliberately NOT a root-logger filter: a filter attached to a logger is
    consulted only for records logged THROUGH that logger, never for
    propagated ones (locked finding). Attaching it at the handler level
    makes the stamp apply to every record the handler emits, whatever
    logger produced it. ``filter()`` always returns True - it annotates,
    it never suppresses.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Attach the active trace id (or None) to the record.

        Args:
            record: The log record about to be emitted.

        Returns:
            bool: Always True.
        """
        ctx = trace.get_current_span().get_span_context()
        record.trace_id = (
            format(ctx.trace_id, "032x")
            if ctx.is_valid and ctx.trace_id
            else None
        )
        return True


class CorrelatedAccessFormatter(logging.Formatter):
    """Formatter whose lines carry the correlated trace id as JSON.

    Used for the uvicorn access logger: the ONE app line per request gains
    a ``"trace_id": "<32hex>"`` fragment. When no span is active the field
    reads null, which is the honest rendering of "no correlated request".
    """

    def format(self, record: logging.LogRecord) -> str:
        """Render the base line plus the trace_id JSON fragment.

        Args:
            record: The access record (carries ``trace_id`` via the filter).

        Returns:
            str: The formatted line ending with the trace_id fragment.
        """
        base = super().format(record)
        trace_id = getattr(record, TRACE_ID_FIELD, None)
        return f'{base} "{TRACE_ID_FIELD}": {json.dumps(trace_id)}'


def install_log_correlation() -> None:
    """Attach the correlation filter to every emitting handler, once.

    Covers the root logger's handlers and the three uvicorn loggers
    (uvicorn, uvicorn.error, uvicorn.access). Idempotent: a handler that
    already carries a TraceCorrelationFilter is skipped, so repeated
    ``create_app()`` calls cannot stack filters.
    """
    def _attach(logger: logging.Logger | None) -> None:
        if logger is None:
            return
        for handler in logger.handlers:
            if not any(isinstance(f, TraceCorrelationFilter) for f in handler.filters):
                handler.addFilter(TraceCorrelationFilter())

    _attach(logging.getLogger())
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        _attach(logging.getLogger(name))


def install_trace_correlation(application: FastAPI) -> FastAPI:
    """Single wiring point: provider, middleware, filter, access formatter.

    Called from ``create_app()`` before the routers matter, so every
    request - including the 401-producing ones the correlation test drives
    - runs inside a server span whose id the log lines carry.

    Args:
        application: The application being created.

    Returns:
        FastAPI: The same application, with the middleware added.
    """
    install_tracing()
    install_log_correlation()
    application.add_middleware(TraceContextMiddleware)
    return application


__all__ = [
    "TRACE_ID_FIELD",
    "TRACEPARENT_HEADER",
    "TRACER_SCOPE",
    "CorrelatedAccessFormatter",
    "FileSpanExporter",
    "INVALID_TRACE_ID",
    "TraceContextMiddleware",
    "TraceCorrelationFilter",
    "install_log_correlation",
    "install_trace_correlation",
    "install_tracing",
]
