from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = [
        'email', 'first_name', 'last_name',
    ]


class UserSubscribe(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='subscribers',
                               on_delete=models.CASCADE)
