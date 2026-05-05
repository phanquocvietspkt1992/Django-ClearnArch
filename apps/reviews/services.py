from .models import Review
from .exceptions import DomainException, NotFoundException
from apps.users.services import get_user_by_id
from apps.products.services import get_product_by_id
from apps.orders.models import Order, OrderStatus


def _assert_user_has_delivered_order(user, product):
    delivered = Order.objects.filter(
        user=user,
        status=OrderStatus.DELIVERED,
        items__product=product,
    ).exists()
    if not delivered:
        raise DomainException(
            'You can only review a product from a delivered order.'
        )


def get_reviews_by_product(product_id):
    get_product_by_id(product_id)  # raises NotFoundException if not found
    return Review.objects.select_related('user').filter(product_id=product_id).order_by('-created_at')


def get_reviews_by_user(user_id):
    get_user_by_id(user_id)  # raises NotFoundException if not found
    return Review.objects.select_related('product').filter(user_id=user_id).order_by('-created_at')


def create_review(user_id, product_id, rating, comment='', created_by='system'):
    user    = get_user_by_id(user_id)
    product = get_product_by_id(product_id)

    _assert_user_has_delivered_order(user, product)

    if Review.objects.filter(user=user, product=product).exists():
        raise DomainException('You have already reviewed this product.')

    review = Review.create(user, product, rating, comment, created_by)
    review.save()
    return review


def delete_review(review_id, user_id):
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        raise NotFoundException(f"Entity 'Review' with key '{review_id}' was not found.")

    if str(review.user_id) != str(user_id):
        raise DomainException('You can only delete your own reviews.')

    review.delete()
