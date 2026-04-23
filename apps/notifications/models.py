import uuid
from datetime import datetime, timezone


class NotificationType:
    ORDER_CREATED = 'order_created'
    PRODUCT_CREATED = 'product_created'


class Notification:
    COLLECTION = 'notifications'

    def __init__(self, user_id, notification_type, title, message, metadata=None,
                 is_read=False, created_at=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = str(user_id)
        self.notification_type = notification_type
        self.title = title
        self.message = message
        self.metadata = metadata or {}
        self.is_read = is_read
        self.created_at = created_at or datetime.now(timezone.utc)

    @classmethod
    def for_order_created(cls, user_id, order_id, total_price):
        return cls(
            user_id=user_id,
            notification_type=NotificationType.ORDER_CREATED,
            title='Order Placed',
            message=f'Your order has been placed successfully. Total: {total_price}',
            metadata={'order_id': str(order_id)},
        )

    @classmethod
    def for_product_created(cls, product_id, product_name, price):
        return cls(
            user_id='system',
            notification_type=NotificationType.PRODUCT_CREATED,
            title='New Product Available',
            message=f'New product "{product_name}" is now available at {price}',
            metadata={'product_id': str(product_id)},
        )

    def to_doc(self):
        return {
            '_id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'metadata': self.metadata,
            'is_read': self.is_read,
            'created_at': self.created_at,
        }

    @classmethod
    def from_doc(cls, doc):
        return cls(
            id=str(doc['_id']),
            user_id=doc['user_id'],
            notification_type=doc['notification_type'],
            title=doc['title'],
            message=doc['message'],
            metadata=doc.get('metadata', {}),
            is_read=doc.get('is_read', False),
            created_at=doc.get('created_at'),
        )
