from django.db import transaction
from .models import Order, OrderItem
from .exceptions import NotFoundException
from apps.users.models import User
from apps.products.models import Product
from infrastructure.messaging import publish_message


def get_order_by_id(order_id):
    try:
        return Order.objects.prefetch_related('items__product').select_related('user').get(id=order_id)
    except Order.DoesNotExist:
        raise NotFoundException(f"Entity 'Order' with key '{order_id}' was not found.")


def get_orders_by_user(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFoundException(f"Entity 'User' with key '{user_id}' was not found.")
    return Order.objects.prefetch_related('items__product').filter(user=user)


@transaction.atomic
def create_order(user_id, items_data, created_by='system'):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFoundException(f"Entity 'User' with key '{user_id}' was not found.")

    order_items = []
    for item_data in items_data:
        try:
            product = Product.objects.select_for_update().get(id=item_data['product_id'])
        except Product.DoesNotExist:
            raise NotFoundException(f"Entity 'Product' with key '{item_data['product_id']}' was not found.")
        order_item = OrderItem.create(product, item_data['quantity'])
        order_items.append((product, order_item))

    order = Order.create(user, [oi for _, oi in order_items], created_by)
    order.save()

    for product, order_item in order_items:
        order_item.order = order
        order_item.save()
        product.stock -= order_item.quantity
        product.save(update_fields=['stock'])

    publish_message('order-created', {
        'id': str(order.id),
        'user_id': str(user.id),
        'total_price': str(order.total_price),
    })
    return order


@transaction.atomic
def update_order_status(order_id, action, updated_by='system'):
    order = get_order_by_id(order_id)
    handler = getattr(order, action)
    handler(updated_by)

    if action == 'cancel':
        for item in order.items.select_related('product').all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])

    order.save()
    return order
