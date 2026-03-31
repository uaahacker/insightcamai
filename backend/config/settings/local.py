from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES['default']['ATOMIC_REQUESTS'] = True

INSTALLED_APPS += ['django_extensions']

REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = 'rest_framework.pagination.PageNumberPagination'

SIMPLE_JWT['ALGORITHM'] = 'HS256'

CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING['loggers']['django'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}
LOGGING['loggers']['apps'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}
