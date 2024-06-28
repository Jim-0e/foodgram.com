"""Views.py."""

from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated

from .filters import IngredientFilter, RecipeFilter
from .models import (
    Favorites,
    Ingredients,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from .serializers import (
    FavoriteOrShoppingCartSerializer,
    FavoriteSerializer,
    IngredientsSerializers,
    RecipeListSerializers,
    RecipeShortLink,
    RecipeWriteSerializers,
    TagsSerializers,
)


class RecipeListView(viewsets.ModelViewSet):
    """Viewset рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Получение определенного сериализатора."""
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializers
        return RecipeWriteSerializers

    def perform_create(self, serializer):
        """Присвоение автору рецепта пользователя."""
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['get'],
            url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeShortLink(recipe, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Добавление в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже добавлен в список покупок.'
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = FavoriteOrShoppingCartSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в списке покупок.'
                )
            shopping_cart = get_object_or_404(
                ShoppingCart,
                user=request.user,
                recipe=recipe
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        shopping_list = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'name__name', 'name__measurement_unit'
        ).annotate(name_total=Sum('amount'))

        text = 'Список покупок:\n\n'
        for item in shopping_list:
            text += (
                f'{item["name__name"]}: {item["name_total"]}'
                f' {item["name__measurement_unit"]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            queryset=Favorites.objects.all(),
            )
    def favorite(self, request, pk):
        """Добавление удаление избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            if Favorites.objects.filter(user=user,
                                        recipe=recipe).exists():
                return Response({'errors': 'Ошибка добавления'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if not Favorites.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        Favorites.objects.get(recipe=recipe).delete()
        return Response('Рецепт успешно удалён из избранного.',
                        status=status.HTTP_204_NO_CONTENT)


class TagsListView(viewsets.ModelViewSet):
    """ViewSet тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializers
    pagination_class = None
    permission_classes = []


class IngredientsListView(viewsets.ReadOnlyModelViewSet):
    """ViewSet ингредиентов."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializers
    pagination_class = None
    permission_classes = []
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
