"""
Views for the recipe API.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing recipe APIs."""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a comma-separated string of IDs to a list of integers."""
        try:
            return [int(str_id) for str_id in qs.split(',') if str_id.strip()]
        except ValueError:
            return []

    def get_queryset(self):
        """Retrieve recipes for authenticated user with optimized queries."""
        queryset = self.queryset.filter(user=self.request.user)

        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        if tags:
            tag_ids = self._params_to_ints(tags)
            if tag_ids:
                queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            if ingredient_ids:
                queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.prefetch_related('tags', 'ingredients').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        if self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe for the authenticated user."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes (tags, ingredients)."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user with optional filtering."""
        queryset = self.queryset.filter(user=self.request.user)

        assigned_only = self.request.query_params.get('assigned_only', '0')
        if assigned_only.lower() in ('1', 'true'):
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """ViewSet for managing tags in the database."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ViewSet for managing ingredients in the database."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
