from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'quantity', 'unit_price']
        read_only_fields = ['id', 'product_id', 'product_name', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'status', 'total_price', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'status', 'total_price', 'created_at', 'updated_at']


class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    items = CreateOrderItemSerializer(many=True, min_length=1)
    created_by = serializers.CharField(max_length=100, default='system')


class UpdateOrderStatusSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['confirm', 'ship', 'deliver', 'cancel'])
    updated_by = serializers.CharField(max_length=100, default='system')
