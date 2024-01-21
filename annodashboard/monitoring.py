import time
from prometheus_client import Counter, Histogram
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

class PrometheusMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Start timing the request
        request.start_time = time.time()

    def process_response(self, request, response):
        # Calculate and record request latency
        if hasattr(request, 'start_time'):
            latency = time.time() - request.start_time
            REQUEST_LATENCY.labels(request.method, request.path).observe(latency)

        # Count and record the request
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

        return response

# Make sure to add the middleware to your Django settings
