from rest_framework import status
from django.http import JsonResponse


def not_found(request, *args, **kwargs):
    """Generic 404 error handler."""
    data = {'error': 'Not Found (404)'}
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
