"""Lightweight, dependency-free security-headers middleware (CN-006).

Adds a baseline Content-Security-Policy and related hardening headers to every
response. Kept intentionally small — for richer CSP needs use django-csp.
"""


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # The API serves only JSON; lock the document down hard. The DRF
        # browsable API (dev only) still works because DEBUG responses are HTML
        # served same-origin under these directives.
        response.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'; base-uri 'self'; "
            "object-src 'none'",
        )
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        return response
