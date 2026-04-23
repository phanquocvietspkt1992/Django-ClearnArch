import uuid
from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_price = models.DecimalField(max_digits=18, decimal_places=2)
    created_by = models.CharField(max_length=100, default='system')
    updated_by = models.CharField(max_length=100, default='system')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'

    @classmethod
    def create(cls, user, items, created_by='system'):
        from apps.orders.exceptions import DomainException
        if not items:
            raise DomainException('An order must have at least one item.')
        total = sum(item.unit_price * item.quantity for item in items)
        return cls(
            user=user,
            status=OrderStatus.PENDING,
            total_price=total,
            created_by=created_by,
            updated_by=created_by,
        )

    def confirm(self, updated_by='system'):
        from apps.orders.exceptions import DomainException
        if self.status != OrderStatus.PENDING:
            raise DomainException(f"Cannot confirm an order with status '{self.status}'.")
        self._transition(OrderStatus.CONFIRMED, updated_by)

    def ship(self, updated_by='system'):
        from apps.orders.exceptions import DomainException
        if self.status != OrderStatus.CONFIRMED:
            raise DomainException(f"Cannot ship an order with status '{self.status}'.")
        self._transition(OrderStatus.SHIPPED, updated_by)

    def deliver(self, updated_by='system'):
        from apps.orders.exceptions import DomainException
        if self.status != OrderStatus.SHIPPED:
            raise DomainException(f"Cannot deliver an order with status '{self.status}'.")
        self._transition(OrderStatus.DELIVERED, updated_by)

    def cancel(self, updated_by='system'):
        from apps.orders.exceptions import DomainException
        if self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise DomainException(f"Cannot cancel an order with status '{self.status}'.")
        self._transition(OrderStatus.CANCELLED, updated_by)

    def _transition(self, new_status, updated_by):
        from django.utils import timezone
        self.status = new_status
        self.updated_by = updated_by
        self.updated_at = timezone.now()


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 'order_items'

    @classmethod
    def create(cls, product, quantity):
        from apps.orders.exceptions import DomainException
        if quantity <= 0:
            raise DomainException('Quantity must be greater than zero.')
        if product.stock < quantity:
            raise DomainException(f"Insufficient stock for product '{product.name}'.")
        return cls(product=product, quantity=quantity, unit_price=product.price)
