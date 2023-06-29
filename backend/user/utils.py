from .models import UserSubscribe


def is_subscribed(user, author):
    """Проверяет подписан ли user на author"""
    return UserSubscribe.objects.filter(author=author, user=user).exists()
