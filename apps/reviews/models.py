import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000, blank=True, default='')
    created_by = models.CharField(max_length=100, default='system')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('user', 'product')  # one review per user per product

    @classmethod
    def create(cls, user, product, rating, comment='', created_by='system'):
        from .exceptions import DomainException
        if not (1 <= rating <= 5):
            raise DomainException('Rating must be between 1 and 5.')
        return cls(
            user=user,
            product=product,
            rating=rating,
            comment=comment,
            created_by=created_by,
        )
