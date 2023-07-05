from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from .models import User
from .utils import is_subscribed


class UserCreateSerializer(DjoserUserCreateSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')

    def validate_email(self, email: str):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Another user with this email already exists')
        return email


class UserProfileSerializer(DjoserUserSerializer):
    id = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, author):
        return is_subscribed(self.context['request'].user, author)
