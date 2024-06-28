"""Admin panel."""

from django.contrib import admin

from .models import MyUser


class UserAdmin(admin.ModelAdmin):
    """Панель пользователей."""

    search_fields = ('first_name', 'email')


admin.site.register(MyUser, UserAdmin)
