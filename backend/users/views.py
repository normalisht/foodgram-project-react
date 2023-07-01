from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from recipes.serializers import UserFullDataSerializer
from .models import User
from .permissions import IsAuthor
from .serializers import UserCreateSerializer, UserProfileSerializer
from .utils import post_delete_action


class UserViewSet(DjoserUserViewSet):
    def get_object(self):
        user_id = self.kwargs.get('id')
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(subscribers=self.request.user
                                       ).prefetch_related('recipes').all()
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ('me', 'retrieve', 'list'):
            return UserProfileSerializer
        elif self.action == 'subscriptions':
            return UserFullDataSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action != 'create':
            self.permission_classes = [IsAdminUser | IsAuthor]
        return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User.objects.prefetch_related('recipes'),
                                   id=id)
        if author == request.user:
            return Response(
                {'error': "You can't subscribe on yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return post_delete_action(request, author, 'subscriptions',
                                  UserFullDataSerializer)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        """Список подписок. В get_serializer_class и get_queryset
        устанавливаются необходимые сериализатор и выборка."""
        return super().list(request, *args, **kwargs)
