from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
    price = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0.01)
    stock = serializers.IntegerField(min_value=0)
    created_by = serializers.CharField(max_length=100, default='system')


class UpdateProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
    price = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0.01)
    stock = serializers.IntegerField(min_value=0)
    updated_by = serializers.CharField(max_length=100, default='system')
