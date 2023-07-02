from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username',)
    search_fields = ('email', 'username')


admin.site.register(User, UserAdmin)
