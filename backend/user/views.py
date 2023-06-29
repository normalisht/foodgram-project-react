from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, UserSubscribe
from .serializers import UserCreateSerializer, UserProfileSerializer
from recipe.serializers import UserFullDataSerializer


class UserViewSet(DjoserUserViewSet):
    def get_object(self):
        user_id = self.kwargs.get('id')
        return get_object_or_404(User, id=user_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ('me', 'retrieve', 'list'):
            return UserProfileSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            _, create = UserSubscribe.objects.get_or_create(
                user=request.user,
                author=author
            )
            # if not create:
            #     return Response(
            #         {'error': 'You already subscribe to this user'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            serializer = UserFullDataSerializer(author,
                                                context={'request': request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['get'])
    def subscriptions(self, request):

