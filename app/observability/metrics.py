# app/metrics.py

from prometheus_client import Counter, Histogram


# =========================
# HTTP METRICS
# =========================

HTTP_REQUEST_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_LATENCY = Histogram(
    "http_requests_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["method", "endpoint", "status_code"],
)


# =========================
# REDIS METRICS
# =========================

REDIS_HITS = Counter(
    "redis_cache_hits_total",
    "Cache hits",
    ["endpoint", "service", "cache_type"],
)

REDIS_MISSES = Counter(
    "redis_cache_misses_total",
    "Cache misses",
    ["endpoint", "service", "cache_type"],
)


# =========================
# EXTERNAL API METRICS
# =========================

EXTERNAL_API_REQUESTS_TOTAL = Counter(
    "external_api_requests_total",
    "Total number of requests made to external APIs",
    ["external_source", "media_type", "endpoint"],
)

EXTERNAL_API_FAILURES_TOTAL = Counter(
    "external_api_failures_total",
    "Total number of failed requests to external APIs",
    ["external_source", "media_type", "endpoint"],
)

EXTERNAL_API_LATENCY_SECONDS = Histogram(
    "external_api_latency_seconds",
    "Latency of external API requests in seconds",
    ["external_source", "media_type", "endpoint"],
)


# =========================
# MONGODB METRICS
# =========================

MONGO_QUERY_DURATION = Histogram(
    "mongo_query_duration_seconds",
    "MongoDB query execution time",
    ["operation", "collection"],
)

MONGO_QUERY_SUCCESS = Counter(
    "mongo_query_success_count",
    "MongoDB query success count",
    ["operation", "collection"],
)

MONGO_QUERY_FAILURE = Counter(
    "mongo_query_failure_count",
    "MongoDB query failure count",
    ["operation", "collection"],
)

MONGO_SLOW_QUERY = Counter(
    "mongo_slow_query_count",
    "MongoDB slow query count",
    ["operation", "collection"],
)