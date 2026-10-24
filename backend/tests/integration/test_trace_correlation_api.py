# mypy: disable-error-code="import-untyped"
"""Integration tests for t122 trace-ID correlation (REQ-OPS-070..072).

The contract under test: every request that produces an app log line carries
exactly ONE trace id, and that id equals the id of the span the request
exported. The two driven requests are the 401 pair (GET /api/v1/expenses and
GET /api/v1/categories with no Authorization header), because a missing
credential emits exactly one correlated app log line (the auth WARNING) and
needs no database fixture.

The four negative controls named by the ac1 fence:

1. ``00000000`` - the all-zero id is the instrumentation-collapse signature;
   every id asserted here must NOT be it.
2/3. ``distinct`` - hardcoded-id collapse and parallel-uuid mismatch are both
   caught only by an explicit distinctness assertion across the two requests.
4. ``out_of_request`` - a process-scoped id is caught only by a probe span
   created OUTSIDE any request carrying a third distinct id.

Log-volume truth (locked finding of the card): a correlated request emits
EXACTLY ONE app log line, so every assertion here counts one line per
request - never two. TestClient emits no uvicorn access lines by default, so
the correlation is driven through the handler path: the capture handler uses
the production ``CorrelatedAccessFormatter`` and the handler-level
``TraceCorrelationFilter`` installed by ``install_log_correlation`` (a
root-logger filter never sees propagated records - also a locked finding).
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from app.database import get_db
from app.main import create_app
from app.trace import (
    TRACER_SCOPE,
    CorrelatedAccessFormatter,
    install_log_correlation,
    install_tracing,
)

ALL_ZERO_ID = "00000000000000000000000000000000"
"""Control 1: the all-zero id a stripped instrumentation would emit."""


class _CaptureHandler(logging.Handler):
    """Handler that records the FORMATTED lines the production path emits.

    Formatting goes through ``CorrelatedAccessFormatter`` so the assertion
    covers the exact string a reader of the access log would see, including
    the ``"trace_id": "<32hex>"`` fragment the filter stamps.
    """

    def __init__(self) -> None:
        """Start with empty captures."""
        super().__init__(level=logging.WARNING)
        self.formatter = CorrelatedAccessFormatter()
        self.records: list[logging.LogRecord] = []
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Store the record and its formatted line.

        Args:
            record: The propagated log record this handler received.
        """
        self.records.append(record)
        self.lines.append(self.format(record))

    def reset(self) -> None:
        """Drop everything captured so far."""
        self.records.clear()
        self.lines.clear()

    def correlated(self) -> list[tuple[logging.LogRecord, str]]:
        """Return app/uvicorn records with their formatted lines.

        Returns:
            list: (record, formatted line) for every app-origin record.
        """
        out = []
        for record, line in zip(self.records, self.lines, strict=False):
            if record.name.startswith("app.") or record.name.startswith("uvicorn"):
                out.append((record, line))
        return out


@pytest.fixture()
def exporter() -> Generator[InMemorySpanExporter, None, None]:
    """Attach an in-memory exporter through the install_tracing hook.

    install_tracing is idempotent: if a provider already exists (another
    test session installed one), the processor hook is skipped by the guard,
    so the processor is attached to the returned provider directly - the
    documented tolerance for the guard across test sessions.

    Yields:
        InMemorySpanExporter: The exporter receiving finished spans.
    """
    mem = InMemorySpanExporter()
    provider = install_tracing(processor=SimpleSpanProcessor(mem))
    attached = any(
        getattr(p, "span_exporter", None) is mem
        for p in provider._active_span_processor._span_processors  # noqa: SLF001
    )
    if not attached:  # tolerate the idempotent provider guard
        provider.add_span_processor(SimpleSpanProcessor(mem))
    yield mem


@pytest.fixture()
def capture() -> Generator[_CaptureHandler, None, None]:
    """Install a production-shaped capture handler on the root logger.

    install_log_correlation attaches the handler-level TraceCorrelationFilter
    to this handler (idempotently), so the capture path is the same filter +
    formatter pair the deployed uvicorn access handler uses.

    Yields:
        _CaptureHandler: The empty capture handler.
    """
    handler = _CaptureHandler()
    root = logging.getLogger()
    previous = root.level
    root.setLevel(logging.WARNING)
    root.addHandler(handler)
    install_log_correlation()
    try:
        yield handler
    finally:
        root.removeHandler(handler)
        root.setLevel(previous)


def _client() -> TestClient:
    """Build a client whose DB dependency is never touched.

    The 401 pair is raised by the auth dependency before any session use;
    the override keeps the test free of any database fixture.

    Returns:
        TestClient: A client over a freshly created app.
    """
    application = create_app()

    def _unused_db() -> Generator[Any, None, None]:
        yield None

    application.dependency_overrides[get_db] = _unused_db
    return TestClient(application)


def _drain(exporter: InMemorySpanExporter) -> list[str]:
    """Return the 32-hex trace ids of all spans exported so far.

    Args:
        exporter: The in-memory exporter under test.

    Returns:
        list: Hex trace ids of the finished spans, in export order.
    """
    ids = []
    for s in exporter.get_finished_spans():
        ctx = s.get_span_context()
        if ctx is not None:
            ids.append(format(ctx.trace_id, "032x"))
    return ids


class TestTraceCorrelation:
    """ac1 contract: one trace id per request, one correlated line each."""

    def test_two_401_requests_carry_distinct_span_equal_trace_ids(
        self, exporter: InMemorySpanExporter, capture: _CaptureHandler
    ) -> None:
        """Two 401 requests: one correlated line each, ids span-equal and distinct.

        Args:
            exporter: In-memory span exporter fixture.
            capture: Handler-level capture fixture.
        """
        client = _client()

        capture.reset()
        first = client.get("/api/v1/expenses")
        assert first.status_code == 401
        lines_one = capture.correlated()
        assert len(lines_one) == 1, (
            "exactly ONE correlated app log line per request is the measured "
            f"truth; got {len(lines_one)}: {[ln for _, ln in lines_one]}"
        )
        record_one, line_one = lines_one[0]
        trace_id_one = record_one.trace_id  # type: ignore[attr-defined]

        capture.reset()
        second = client.get("/api/v1/categories")
        assert second.status_code == 401
        lines_two = capture.correlated()
        assert len(lines_two) == 1, (
            f"exactly ONE correlated app log line per request; got {len(lines_two)}"
        )
        record_two, line_two = lines_two[0]
        trace_id_two = record_two.trace_id  # type: ignore[attr-defined]

        # Control 1: neither id is the all-zero collapse signature.
        assert trace_id_one != ALL_ZERO_ID
        assert trace_id_two != ALL_ZERO_ID
        # Controls 2/3: the ids are distinct across the two requests.
        assert trace_id_one != trace_id_two, "trace ids must be distinct per request"
        # The log trace_id equals the exported span id, request by request.
        exported = _drain(exporter)
        assert trace_id_one in exported, "log trace_id != any exported span id"
        assert trace_id_two in exported, "log trace_id != any exported span id"
        # The formatted line carries the same id in the access-line fragment.
        assert f'"trace_id": "{trace_id_one}"' in line_one
        assert f'"trace_id": "{trace_id_two}"' in line_two
        # Journey record markers (printed, never invented, for ac4's record).
        print(
            "TRACE_JOURNEY_MEASURED journey=expenses-list-401 "
            f"trace_id={trace_id_one} log_lines=1 stack=testclient"
        )
        print(
            "TRACE_JOURNEY_MEASURED journey=categories-list-401 "
            f"trace_id={trace_id_two} log_lines=1 stack=testclient"
        )

    def test_out_of_request_probe_span_carries_a_third_distinct_id(
        self, exporter: InMemorySpanExporter, capture: _CaptureHandler
    ) -> None:
        """A span opened OUTSIDE any request gets its own out_of_request id.

        A process-scoped id would make the probe id equal a request id; the
        distinctness assertion below is control 4 against that collapse.

        Args:
            exporter: In-memory span exporter fixture.
            capture: Handler-level capture fixture.
        """
        client = _client()
        capture.reset()
        response = client.get("/api/v1/expenses")
        assert response.status_code == 401
        request_id = capture.correlated()[0][0].trace_id  # type: ignore[attr-defined]

        tracer = trace.get_tracer(TRACER_SCOPE)
        capture.reset()
        with tracer.start_as_current_span("out_of_request_probe"):
            logging.getLogger("app.probe").warning("out_of_request probe span")
        probe_record, probe_line = capture.correlated()[0]
        out_of_request_id = probe_record.trace_id  # type: ignore[attr-defined]

        assert out_of_request_id != ALL_ZERO_ID
        assert out_of_request_id != request_id, "out_of_request id must be distinct"
        assert out_of_request_id in _drain(exporter)
        assert f'"trace_id": "{out_of_request_id}"' in probe_line

    def test_correlated_line_is_a_single_line_carrying_the_field(
        self, exporter: InMemorySpanExporter, capture: _CaptureHandler
    ) -> None:
        """The correlated line is ONE line and carries the trace_id fragment.

        Args:
            exporter: In-memory span exporter fixture.
            capture: Handler-level capture fixture.
        """
        client = _client()
        capture.reset()
        assert client.get("/api/v1/categories").status_code == 401
        record, line = capture.correlated()[0]
        assert "\n" not in line, "one log line must be one line"
        assert line.rstrip().endswith(
            f'"trace_id": "{record.trace_id}"'  # type: ignore[attr-defined]
        )
        assert record.trace_id != ALL_ZERO_ID  # type: ignore[attr-defined]
        assert record.levelname == "WARNING"
