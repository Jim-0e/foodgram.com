"""Модели."""

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField('Название',
                            max_length=32,
                            unique=True)
    slug = models.SlugField('Слаг',
                            max_length=32,
                            unique=True)

    def __str__(self):
        """Возвращение названия тега."""
        return self.name


class Ingredients(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('Название',
                            max_length=255,
                            unique=True)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=255,
                                        blank=False)

    def __str__(self):
        """Возвращение названия ингредиента."""
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название',
                            max_length=256, blank=False)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField('Описание',)
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги',
    )
    cooking_time = models.IntegerField('Время приготовления',
                                       blank=False,
                                       validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now=True)

    class Meta:
        """Метаданные."""

        ordering = ("-pub_date",)
        constraints = (
            UniqueConstraint(
                fields=("name", "author"),
                name="unique_for_author",
            ),)

    def __str__(self):
        """Возвращение названия рецепта."""
        return self.name


class TagRecipe(models.Model):
    """Связная модель тегов и рецептов."""

    name = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )


class IngredientRecipe(models.Model):
    """Связная модель ингредиентов и рецептов."""

    name = models.ForeignKey(Ingredients,
                             on_delete=models.CASCADE,
                             verbose_name='Ингредиент',
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    amount = models.IntegerField('Количество',
                                 validators=[MinValueValidator(1)],
                                 )

    class Meta:
        """Метаданные."""

        unique_together = ('name', 'recipe')


class Favorites(models.Model):
    """Модель избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт')

    def __str__(self):
        """Какой рецепт добавил пользователь в избранное."""
        return f'{self.user.username} добавил {self.recipe.name} в избраннное'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='carts',
                               verbose_name='Рецепт')


class Follow(models.Model):
    """Модель подписчиков."""

    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='followed',
        on_delete=models.CASCADE,
        verbose_name='Пользователь')

    def __str__(self):
        """На кого подписался пользователь."""
        return f'Пользователь {self.user} подписан на {self.author}'
