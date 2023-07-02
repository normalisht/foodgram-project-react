# Generated by Django 4.2.2 on 2023-07-02 12:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_subscriptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='subscriptions',
            field=models.ManyToManyField(blank=True, null=True, related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Подписки'),
        ),
    ]
