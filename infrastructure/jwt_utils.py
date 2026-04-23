import jwt
import uuid
from datetime import datetime, timedelta, timezone
from django.conf import settings

ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(days=7)

_REFRESH_KEY_PREFIX = 'refresh_token:'


def _secret():
    return settings.SECRET_KEY


def generate_access_token(user_id):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': now + ACCESS_TOKEN_TTL,
        'type': 'access',
    }
    return jwt.encode(payload, _secret(), algorithm='HS256')


def generate_refresh_token(user_id):
    token = str(uuid.uuid4())
    from django.core.cache import cache
    cache.set(f'{_REFRESH_KEY_PREFIX}{token}', str(user_id), int(REFRESH_TOKEN_TTL.total_seconds()))
    return token


def decode_access_token(token):
    """Returns user_id str or raises jwt.PyJWTError."""
    payload = jwt.decode(token, _secret(), algorithms=['HS256'])
    if payload.get('type') != 'access':
        raise jwt.InvalidTokenError('Not an access token.')
    return payload['sub']


def rotate_refresh_token(old_token):
    """Validates old refresh token, invalidates it, returns (user_id, new_refresh_token)."""
    from django.core.cache import cache
    from apps.users.exceptions import DomainException
    key = f'{_REFRESH_KEY_PREFIX}{old_token}'
    user_id = cache.get(key)
    if not user_id:
        raise DomainException('Refresh token is invalid or expired.')
    cache.delete(key)
    new_token = generate_refresh_token(user_id)
    return user_id, new_token


def revoke_refresh_token(token):
    from django.core.cache import cache
    cache.delete(f'{_REFRESH_KEY_PREFIX}{token}')
