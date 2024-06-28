"""Сериализаторы."""
import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from urlshortner.utils import shorten_url

from .models import (Favorites, Follow, IngredientRecipe, Ingredients, Recipe,
                     ShoppingCart, Tag)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор изображений."""

    is_subscribed = serializers.SerializerMethodField()

    def to_internal_value(self, data):
        """Преобразование изображения в строковый формат."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserViewSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Метаданные."""

        model = User
        fields = ("email", "id", "username", "first_name",
                  "last_name", 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Получение подписчиков."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj
        ).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки/отписки от пользователей."""

    class Meta:
        """Метаданные."""

        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        """Проверка подписки на самого себя."""
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        """Информация об авторе, на которого оформлена подписка."""
        request = self.context.get('request')
        return FollowSerializer(
            instance.author, context={'request': request}
        ).data


class FollowSerializer(UserViewSerializer):
    """Сериализатор подписчиков."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """Метаданные."""

        model = User
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed", "recipes", "recipes_count")

    def get_recipes(self, obj):
        """Получение рецептов подписчиков."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeListSerializers(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Получение количества рецептов."""
        return Recipe.objects.filter(author=obj).count()


class IngredientsSerializers(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        """Метаданные."""

        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингедиентов."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        """Метаданные."""

        model = IngredientRecipe
        fields = ('id', 'amount')


class TagsSerializers(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        """Метаданные."""

        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeShortLink(serializers.ModelSerializer):
    """Сериализатор короткой ссылки."""

    short_link = serializers.SerializerMethodField()

    class Meta:
        """Метаданные."""

        model = Recipe
        fields = ('short_link',)

    def get_short_link(self, obj):
        """Создание короткой ссылки."""
        base_url = 'https://foodgram-eats.ddns.net/'
        created = shorten_url(
            f'{base_url}recipes/{obj.id}',
            is_permanent=False)
        return f'{base_url}s/{created}'

    def to_representation(self, instance):
        """Изменение название ключа."""
        data = super().to_representation(instance)
        data['short-link'] = data.pop('short_link')
        return data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    amount = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        """Метаданные."""

        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        """Получение количества."""
        ingredient_recipe = IngredientRecipe.objects.filter(
            name__name=obj).first()
        return f'{ingredient_recipe.amount}'

    def get_measurement_unit(self, obj):
        """Получение измерения."""
        measurement_unit = IngredientRecipe.objects.filter(
            name__name=obj).first()
        return f'{measurement_unit.name.measurement_unit}'


class RecipeListSerializers(serializers.ModelSerializer):
    """Сериализатор безопасных запросов рецептов."""

    image = Base64ImageField(required=True, allow_null=True)
    ingredients = IngredientRecipeSerializer(read_only=True, many=True)
    tags = TagsSerializers(read_only=True, many=True)
    author = UserViewSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Метаданные."""

        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time',)

    def get_is_favorited(self, obj):
        """Получения избранных."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorites.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        """Получения списка покупок."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class RecipeWriteSerializers(serializers.ModelSerializer):
    """Сериализатор изменения рецептов."""

    image = Base64ImageField(required=True, allow_null=True)
    ingredients = AddIngredientSerializer(
        many=True, write_only=True)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Tag.objects.all(),
        many=True
    )

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.')

        tag_ids = [tag for tag in tags]
        if len(set(tag_ids)) != len(tag_ids):
            raise serializers.ValidationError('Теги должны быть уникальными.')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_list = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(Ingredients,
                                                   id=ingredient.get('id'))
            amount = ingredient.get('amount')
            ingredient_list.append(
                IngredientRecipe(
                    recipe=recipe,
                    name=current_ingredient,
                    amount=amount
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_list)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)

        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        ingredient_list = []

        for ingredient in ingredients:
            current_ingredient = get_object_or_404(Ingredients,
                                                   id=ingredient.get('id'))
            amount = ingredient.get('amount')
            ingredient_list.append(
                IngredientRecipe(
                    recipe=instance,
                    name=current_ingredient,
                    amount=amount
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_list)
        instance.save()
        return instance

    class Meta:
        """Метаданные."""

        model = Recipe
        fields = "__all__"


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор  для вывода  в FollowSerializer."""

    class Meta:
        """Метаданные."""

        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных."""

    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    coocking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)

    class Meta:
        """Метаданные."""

        model = Favorites
        fields = ('id', 'name', 'image', 'coocking_time')


class FavoriteOrShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок или избранных."""

    class Meta:
        """Метаданные."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
