import time
from prometheus_client import Counter, Histogram, Summary
from django.utils.deprecation import MiddlewareMixin

# Histogram for tracking request latency
REQUEST_LATENCY = Histogram(
    'django_request_latency_seconds',
    'Time spent processing a request.',
    ['method', 'endpoint']
)

# Counter for tracking the number of requests
REQUEST_COUNT = Counter(
    'django_request_count',
    'Total count of requests',
    ['method', 'endpoint', 'http_status']
)

# Summary for tracking the size of requests
REQUEST_SIZE = Summary(
    'django_request_size_bytes',
    'Size of HTTP requests',
    ['method', 'endpoint']
)

# Summary for tracking the size of responses
RESPONSE_SIZE = Summary(
    'django_response_size_bytes',
    'Size of HTTP responses',
    ['method', 'endpoint']
)

class PrometheusMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

        # Estimate request size
        request_size = int(request.META.get('CONTENT_LENGTH') or 0)
        REQUEST_SIZE.labels(request.method, request.path).observe(request_size)

    def process_response(self, request, response):
        # Calculate request latency
        if hasattr(request, 'start_time'):
            latency = time.time() - request.start_time
            REQUEST_LATENCY.labels(request.method, request.path).observe(latency)

        # Count the request
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

        # Estimate response size
        response_size = len(response.content)
        RESPONSE_SIZE.labels(request.method, request.path).observe(response_size)

        return response
