from django.urls import path
from .views import health_check

app_name = 'core'

urlpatterns = [
    path('check/', health_check, name='health_check'),
]
