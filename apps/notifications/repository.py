from infrastructure.mongo import get_db
from .models import Notification


def save(notification):
    db = get_db()
    db[Notification.COLLECTION].insert_one(notification.to_doc())
    return notification


def find_by_user(user_id, limit=50):
    db = get_db()
    docs = db[Notification.COLLECTION].find(
        {'user_id': str(user_id)},
        sort=[('created_at', -1)],
        limit=limit,
    )
    return [Notification.from_doc(doc) for doc in docs]


def find_by_id(notification_id):
    db = get_db()
    doc = db[Notification.COLLECTION].find_one({'_id': str(notification_id)})
    return Notification.from_doc(doc) if doc else None


def mark_as_read(notification_id):
    db = get_db()
    result = db[Notification.COLLECTION].update_one(
        {'_id': str(notification_id)},
        {'$set': {'is_read': True}},
    )
    return result.modified_count > 0


def mark_all_as_read(user_id):
    db = get_db()
    result = db[Notification.COLLECTION].update_many(
        {'user_id': str(user_id), 'is_read': False},
        {'$set': {'is_read': True}},
    )
    return result.modified_count
