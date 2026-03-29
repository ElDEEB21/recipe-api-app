"""
Recipe app configuration.
"""
from django.apps import AppConfig


class RecipeConfig(AppConfig):
    """Recipe app configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe'
