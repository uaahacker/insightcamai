from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RuleViewSet

app_name = 'rules'

router = DefaultRouter()
router.register(r'', RuleViewSet, basename='rule')

urlpatterns = [
    path('', include(router.urls)),
]
