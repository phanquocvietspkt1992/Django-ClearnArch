from .models import Notification
from . import repository
from .exceptions import NotFoundException


def get_notifications_by_user(user_id, limit=50):
    return repository.find_by_user(user_id, limit=limit)


def create_order_notification(user_id, order_id, total_price):
    notification = Notification.for_order_created(user_id, order_id, total_price)
    return repository.save(notification)


def create_product_notification(product_id, product_name, price):
    notification = Notification.for_product_created(product_id, product_name, price)
    return repository.save(notification)


def mark_as_read(notification_id):
    updated = repository.mark_as_read(notification_id)
    if not updated:
        raise NotFoundException(f"Entity 'Notification' with key '{notification_id}' was not found.")


def mark_all_as_read(user_id):
    return repository.mark_all_as_read(user_id)
