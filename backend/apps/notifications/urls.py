from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationChannelViewSet, NotificationDeliveryViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register(r'channels', NotificationChannelViewSet, basename='notification-channel')
router.register(r'deliveries', NotificationDeliveryViewSet, basename='notification-delivery')

urlpatterns = [
    path('', include(router.urls)),
]
