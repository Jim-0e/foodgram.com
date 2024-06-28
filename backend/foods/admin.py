"""Admin panel."""
from django.contrib import admin

from .models import (Favorites, Follow, IngredientRecipe, Ingredients, Recipe,
                     Tag, TagRecipe)


class RecipeInline(admin.TabularInline):
    """Модель ингридиентов."""

    model = IngredientRecipe
    extra = 1


class RecipesInline(admin.TabularInline):
    """Модель тегов."""

    model = TagRecipe
    extra = 1


class IngredientsAdmin(admin.ModelAdmin):
    """Модель ингридиентов."""

    inlines = [RecipeInline]


class TagsAdmin(admin.ModelAdmin):
    """Модель тегов."""

    inlines = [RecipeInline]


class RecipeAdmin(admin.ModelAdmin):
    """Настройки рецептов."""

    list_display = ('name', 'author', 'count_favorites')
    search_fields = ('author__username', 'name')
    list_filter = ('tags',)
    inlines = [RecipeInline, RecipesInline]

    def count_favorites(self, obj):
        """Количество добавлений репецта в избранное."""
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    """Настройки ингедиентов."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredients, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Follow)
admin.site.register(Favorites)
