import hmac
import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Client, TourResult
from .serializers import (
    ClientSerializer,
    ReceiveResultSerializer,
    TourResultSerializer,
)

# Dedicated security logger (CN-010). Never log secrets/tokens themselves.
security_log = logging.getLogger("api.security")


class LoggingTokenObtainPairView(TokenObtainPairView):
    """JWT login that logs success/failure and is rate-limited (CN-005, CN-010)."""

    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "<missing>")
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            security_log.info("Login success for user=%s", username)
        else:
            security_log.warning(
                "Login failure for user=%s (status=%s)",
                username,
                response.status_code,
            )
        return response


class LogoutView(APIView):
    """POST /api/auth/logout/ — blacklist the supplied refresh token (CN-008).

    Makes logout actually revoke the session server-side instead of relying
    only on the client dropping the in-memory token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "refresh token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            # Already expired/blacklisted — treat as a successful logout.
            pass
        security_log.info("Logout for user=%s", getattr(request.user, "username", "?"))
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ClientListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/clients/"""

    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/clients/:id/"""

    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientResultsView(generics.ListCreateAPIView):
    """GET/POST /api/clients/:id/results/"""

    serializer_class = TourResultSerializer

    def get_client(self):
        return get_object_or_404(Client, pk=self.kwargs["pk"])

    def get_queryset(self):
        return TourResult.objects.filter(client=self.get_client())

    def perform_create(self, serializer):
        serializer.save(client=self.get_client())


class ReceiveResultView(APIView):
    """POST /api/results/receive/ — PUBLIC ingest for 3DVista tours.

    No JWT required (the tour can't authenticate), but hardened (CN-004):
      - optional shared token via the X-Ingest-Token header (enforced when
        INGEST_TOKEN is configured; constant-time compared),
      - rate-limited via the 'ingest' throttle scope,
      - non-enumerable errors (does not reveal whether a client exists),
      - security logging of accepted/rejected submissions.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "ingest"

    def post(self, request):
        expected = settings.INGEST_TOKEN
        if expected:
            provided = request.headers.get("X-Ingest-Token", "")
            if not hmac.compare_digest(provided, expected):
                security_log.warning("Ingest rejected: bad/missing X-Ingest-Token")
                return Response(
                    {"detail": "Unauthorized."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        serializer = ReceiveResultSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            result = serializer.save()
        except DRFValidationError:
            # Generic 400 — do not leak which client names exist (CN-004).
            security_log.info("Ingest rejected: invalid payload")
            return Response(
                {"detail": "Invalid submission."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        security_log.info(
            "Ingest accepted: client_id=%s employee=%s",
            result.client_id,
            result.employee_name,
        )
        return Response(
            TourResultSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )
