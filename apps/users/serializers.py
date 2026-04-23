from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone_number', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200)
    full_name = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(min_length=8, write_only=True)
    created_by = serializers.CharField(max_length=100, default='system')


class UpdateUserSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=20)
    updated_by = serializers.CharField(max_length=100, default='system')
