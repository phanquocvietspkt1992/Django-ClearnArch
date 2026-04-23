from apps.users import services as user_services
from apps.users.exceptions import DomainException, NotFoundException
from infrastructure import jwt_utils


def login(email, password):
    try:
        user = user_services.get_user_by_email(email)
    except NotFoundException:
        raise DomainException('Invalid email or password.')

    if not user.is_active:
        raise DomainException('User account is inactive.')

    if not user.check_password(password):
        raise DomainException('Invalid email or password.')

    access_token = jwt_utils.generate_access_token(user.id)
    refresh_token = jwt_utils.generate_refresh_token(user.id)
    return {'access_token': access_token, 'refresh_token': refresh_token}


def refresh(refresh_token):
    user_id, new_refresh_token = jwt_utils.rotate_refresh_token(refresh_token)
    access_token = jwt_utils.generate_access_token(user_id)
    return {'access_token': access_token, 'refresh_token': new_refresh_token}


def logout(refresh_token):
    jwt_utils.revoke_refresh_token(refresh_token)
