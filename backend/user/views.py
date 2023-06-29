from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from recipe.serializers import UserFullDataSerializer
from .models import User, UserSubscribe
from .serializers import UserCreateSerializer, UserProfileSerializer


class UserViewSet(DjoserUserViewSet):
    def get_object(self):
        user_id = self.kwargs.get('id')
        return get_object_or_404(User, id=user_id)

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(subscribers__user=self.request.user
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

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User.objects.prefetch_related('recipes'),
                                   id=id)
        if author == request.user:
            return Response(
                {'error': "You can't subscribe on yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            _, create = UserSubscribe.objects.get_or_create(
                user=request.user, author=author
            )
            if not create:
                return Response(
                    {'error': 'You already subscribe to this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserFullDataSerializer(author,
                                                context={'request': request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        UserSubscribe.objects.filter(
            user=request.user, author=author
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Список подписок. В get_serializer_class и get_queryset
        устанавливаются необходимые сериализатор и выборка."""
        return super().list(request)
