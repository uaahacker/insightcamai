from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet

app_name = 'auditlogs'

router = DefaultRouter()
router.register(r'', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('', include(router.urls)),
]
