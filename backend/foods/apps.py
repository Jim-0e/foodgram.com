"""Apps.py."""

from django.apps import AppConfig


class FoodsConfig(AppConfig):
    """FoodsCongig."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foods'
