"""Operational metrics without contract text or request identifiers."""

from time import perf_counter

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    make_asgi_app,
)

REQUESTS = Counter(
    "contract_review_requests_total",
    "Completed POST /review requests by HTTP status.",
    ["status"],
)

DURATION = Histogram(
    "contract_review_duration_seconds",
    "POST /review processing time through response preparation.",
    ["status"],
    buckets=(
        0.01, 0.025, 0.05, 0.1, 0.25, 0.5,
        1, 2, 5, 10, 20, 30, 60, 120,
    ),
)

IN_PROGRESS = Gauge(
    "contract_review_in_progress",
    "POST /review requests currently being processed.",
)


def install_monitoring(app):
    """Install single-process request instrumentation and metrics endpoint."""
    app.mount("/metrics", make_asgi_app())

    @app.middleware("http")
    async def measure_review(request, call_next):
        if request.method != "POST" or request.url.path != "/review":
            return await call_next(request)

        started = perf_counter()
        status = "500"
        IN_PROGRESS.inc()

        try:
            response = await call_next(request)
            status = str(response.status_code)
            return response
        finally:
            elapsed = perf_counter() - started
            REQUESTS.labels(status=status).inc()
            DURATION.labels(status=status).observe(elapsed)
            IN_PROGRESS.dec()
