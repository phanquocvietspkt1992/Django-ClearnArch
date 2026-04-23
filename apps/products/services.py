from django.core.cache import cache
from .models import Product
from apps.users.exceptions import NotFoundException
from infrastructure.messaging import publish_message

CACHE_TTL = 300  # 5 minutes


def get_all_products():
    return Product.objects.all()


def get_product_by_id(product_id):
    cache_key = f'product:{product_id}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise NotFoundException(f"Entity 'Product' with key '{product_id}' was not found.")

    cache.set(cache_key, product, CACHE_TTL)
    return product


def create_product(name, description, price, stock, created_by='system'):
    product = Product.create(name, description, price, stock, created_by)
    product.save()
    publish_message('product-created', {'id': str(product.id), 'name': product.name, 'price': str(product.price)})
    return product


def update_product(product_id, name, description, price, stock, updated_by='system'):
    product = get_product_by_id(product_id)
    product.update(name, description, price, stock, updated_by)
    product.save()
    cache.delete(f'product:{product_id}')
    return product


def delete_product(product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise NotFoundException(f"Entity 'Product' with key '{product_id}' was not found.")
    product.delete()
    cache.delete(f'product:{product_id}')
