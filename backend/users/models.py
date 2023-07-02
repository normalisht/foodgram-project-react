from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    subscriptions = models.ManyToManyField(
        'User', related_name='subscribers', verbose_name='Подписки',
        blank=True,
    )
