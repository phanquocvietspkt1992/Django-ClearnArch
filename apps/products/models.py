import uuid
from django.db import models


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_by = models.CharField(max_length=100, default='system')
    updated_by = models.CharField(max_length=100, default='system')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'products'

    @classmethod
    def create(cls, name, description, price, stock, created_by='system'):
        return cls(
            name=name,
            description=description,
            price=price,
            stock=stock,
            created_by=created_by,
            updated_by=created_by,
        )

    def update(self, name, description, price, stock, updated_by='system'):
        from django.utils import timezone
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.updated_by = updated_by
        self.updated_at = timezone.now()
