from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_id', 'user_name', 'product_id', 'product_name',
                  'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user_id', 'user_name', 'product_id', 'product_name', 'created_at']


class CreateReviewSerializer(serializers.Serializer):
    user_id    = serializers.UUIDField()
    product_id = serializers.UUIDField()
    rating     = serializers.IntegerField(min_value=1, max_value=5)
    comment    = serializers.CharField(max_length=1000, required=False, default='')
    created_by = serializers.CharField(max_length=100, default='system')
