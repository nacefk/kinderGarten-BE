from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/children/', include('children.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/planning/', include('planning.urls')),
    path("api/attendance/", include("attendance.urls")),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
