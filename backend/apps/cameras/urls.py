from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CameraViewSet

app_name = 'cameras'

router = DefaultRouter()
router.register(r'', CameraViewSet, basename='camera')

urlpatterns = [
    path('', include(router.urls)),
]
