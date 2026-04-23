from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from apps.users.exceptions import DomainException, NotFoundException


def custom_exception_handler(exc, context):
    if isinstance(exc, NotFoundException):
        return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, DomainException):
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return exception_handler(exc, context)
