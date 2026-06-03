from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Auth (JWT)
    path("auth/login/", views.LoggingTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    # Clients
    path("clients/", views.ClientListCreateView.as_view(), name="client-list"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client-detail"),
    path(
        "clients/<int:pk>/results/",
        views.ClientResultsView.as_view(),
        name="client-results",
    ),
    # Public ingest endpoint for 3DVista tours
    path("results/receive/", views.ReceiveResultView.as_view(), name="results-receive"),
]
