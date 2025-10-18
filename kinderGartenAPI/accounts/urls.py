from django.urls import path
from .views import TenantAwareTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", TenantAwareTokenObtainPairView.as_view(), name="tenant_token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
