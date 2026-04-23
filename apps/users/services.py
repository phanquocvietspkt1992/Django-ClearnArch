from .models import User
from .exceptions import NotFoundException


def get_all_users():
    return User.objects.all()


def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFoundException(f"Entity 'User' with key '{user_id}' was not found.")


def create_user(email, full_name, phone_number, password, created_by='system'):
    user = User.create(email, full_name, phone_number, password, created_by)
    user.save()
    return user


def get_user_by_email(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        raise NotFoundException(f"Entity 'User' with email '{email}' was not found.")


def update_user_profile(user_id, full_name, phone_number, updated_by='system'):
    user = get_user_by_id(user_id)
    user.update_profile(full_name, phone_number, updated_by)
    user.save()
    return user


def deactivate_user(user_id, updated_by='system'):
    user = get_user_by_id(user_id)
    user.deactivate(updated_by)
    user.save()
