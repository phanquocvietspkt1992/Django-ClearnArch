import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from infrastructure import jwt_utils


class AuthenticatedUser:
    """Thin wrapper so DRF's IsAuthenticated check works."""
    is_authenticated = True

    def __init__(self, user_id):
        self.id = user_id


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None  # no credentials — let permission class decide

        token = auth_header[len('Bearer '):]
        try:
            user_id = jwt_utils.decode_access_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Access token has expired.')
        except jwt.PyJWTError:
            raise AuthenticationFailed('Access token is invalid.')

        return (AuthenticatedUser(user_id), token)


class IsJWTAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, AuthenticatedUser)
