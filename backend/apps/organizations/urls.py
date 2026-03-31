from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, SiteViewSet

app_name = 'organizations'

router = DefaultRouter()
router.register(r'', OrganizationViewSet, basename='organization')
router.register(r'sites', SiteViewSet, basename='site')

urlpatterns = [
    path('', include(router.urls)),
]
