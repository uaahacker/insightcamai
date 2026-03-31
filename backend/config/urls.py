from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/cameras/', include('apps.cameras.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/events/', include('apps.events.urls')),
    path('api/v1/alerts/', include('apps.alerts.urls')),
    path('api/v1/rules/', include('apps.rules.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/audit-logs/', include('apps.auditlogs.urls')),
    path('api/v1/subscriptions/', include('apps.subscriptions.urls')),
    path('api/v1/health/', include('core.urls')),
]
