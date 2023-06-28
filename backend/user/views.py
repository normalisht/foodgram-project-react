from djoser.views import UserViewSet

from .models import User
from .serializers import CustomUserCreateSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):

    def get_object(self):
        user_id = self.kwargs.get('id')
        return User.objects.get(pk=user_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action in ('me', 'retrieve', 'list'):
            return CustomUserSerializer
        return super().get_serializer_class()
