"""Модели."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class MyUser(AbstractUser):
    """Кастомная модель пользователя."""

    MAX_EMAIL_LENGTH = 254
    MAX_LENGTH_DEFAULT = 150

    avatar = models.ImageField(upload_to='users/', blank=True, null=True)
    is_subscribed = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), max_length=MAX_EMAIL_LENGTH,
                              unique=True)
    username = models.CharField(max_length=MAX_LENGTH_DEFAULT,
                                null=True,
                                blank=True,
                                unique=True)
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=MAX_LENGTH_DEFAULT)
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=MAX_LENGTH_DEFAULT)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_username(self):
        """Возвращение email."""
        return self.email

    def __str__(self):
        """Возвращение пользователя."""
        return self.username
