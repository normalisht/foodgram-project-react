from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers

from user.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
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


class CustomUserSerializer(UserSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',)
        # TODO Добавить поле 'is_subscribed'
