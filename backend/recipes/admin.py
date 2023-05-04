from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 3


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe')
    list_filter = ('author',)
    search_fields = ('author',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', "user", "author")
    list_filter = ('author',)
    search_fields = ('user',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'pub_date', 'in_favorite')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients',)
    inlines = [IngredientsInline]

    def in_favorite(self, obj):
        return obj.favorite.all().count()

    in_favorite.short_description = 'В избранном'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('name',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'recipe')
    list_filter = ('author',)
    search_fields = ('author',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
