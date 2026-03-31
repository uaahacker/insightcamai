from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)
    
    if response is None:
        return Response(
            {'detail': str(exc), 'error_code': 'INTERNAL_ERROR'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    if isinstance(exc, APIException):
        response.data = {
            'detail': response.data.get('detail', str(exc)),
            'error_code': getattr(exc, 'error_code', 'API_ERROR'),
        }
    
    return response


class InvalidStreamError(APIException):
    status_code = 400
    default_detail = 'Cannot connect to the stream'
    error_code = 'INVALID_STREAM'


class CameraNotFoundError(APIException):
    status_code = 404
    default_detail = 'Camera not found'
    error_code = 'CAMERA_NOT_FOUND'


class OrganizationNotFoundError(APIException):
    status_code = 404
    default_detail = 'Organization not found'
    error_code = 'ORGANIZATION_NOT_FOUND'
