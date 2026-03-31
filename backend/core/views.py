from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache
import json


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    status_data = {
        'status': 'ok',
        'service': 'cctv-analytics-api',
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        status_data['database'] = 'ok'
    except Exception as e:
        status_data['database'] = f'error: {str(e)}'
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        status_data['cache'] = 'ok'
    except Exception as e:
        status_data['cache'] = f'error: {str(e)}'
    
    return Response(status_data)
