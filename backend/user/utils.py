from typing import Type

from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer


def is_subscribed(user, author):
    """Проверяет подписан ли user на author"""
    return user.subscriptions.filter(id=author.id).exists()


def post_delete_action(request, obj, related_name: str,
                       serializer: Type[Serializer]):
    """Реализует post и delete методы для связи многие-ко-многим.
    Связь многие-ко-многим между авторизированным пользователем и obj.
    "related_name" - название связующего поля в таблице User."""

    user = request.user

    if request.method == 'POST':
        if getattr(user, related_name).filter(id=obj.id).exists():
            return Response(
                {'error': f'This record already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        getattr(user, related_name).add(obj)
        serializer = serializer(obj, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    getattr(user, related_name).remove(obj)
    return Response(status=status.HTTP_204_NO_CONTENT)
