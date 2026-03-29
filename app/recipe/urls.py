"""
URL mappings for the recipe app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()
router.register('tags', views.TagViewSet, basename='tag')
router.register('ingredients', views.IngredientViewSet, basename='ingredient')
router.register('', views.RecipeViewSet, basename='recipe')

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
