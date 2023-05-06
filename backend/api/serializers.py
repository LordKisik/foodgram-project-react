from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator


from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import User


class GetUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True},
                        'is_subscribed': {'read_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(
                user=obj.user,
                author=obj.author).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = GetUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(author=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(author=user,
                                               recipe=obj).exists()
        return False


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class FavoriteSerializer(serializers.Serializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user'],
                message='Этот рецепт уже добавлен в избранное'
            )
        ]
# class FavoriteSerializer(serializers.ModelSerializer):
#     name = serializers.ReadOnlyField(
#         source='recipe.name',
#         read_only=True)
#     image = serializers.ImageField(
#         source='recipe.image',
#         read_only=True)
#     cooking_time = serializers.IntegerField(
#         source='recipe.cooking_time',
#         read_only=True)
#     id = serializers.PrimaryKeyRelatedField(
#         source='recipe',
#         read_only=True)

#     class Meta:
#         model = Favorite
#         fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user'],
                message='Этот рецепт уже добавлен в список покупок'
            )
        ]
    # name = serializers.ReadOnlyField(
    #     source='recipe.name',
    #     read_only=True)
    # image = serializers.ImageField(
    #     source='recipe.image',
    #     read_only=True)
    # cooking_time = serializers.IntegerField(
    #     source='recipe.cooking_time',
    #     read_only=True)
    # id = serializers.PrimaryKeyRelatedField(
    #     source='recipe',
    #     read_only=True)

    # class Meta:
    #     model = ShoppingCart
    #     fields = ('id', 'name', 'image', 'cooking_time')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Необходимо выбрать ингредиент'})
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, name=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients': 'Ингридиенты не должны повторяться'})
            if int(item['amount']) <= 0:
                raise ValidationError(
                    {'amount': 'Количество должно быть больше 0!'})
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                {'tags': 'Необходимо выбрать тег'})
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги не должны повторяться'})
            tags_list.append(tag)
        return value

    def to_representation(self, instance):
        recipe = super().to_representation(instance)
        recipe['ingredients'] = RecipeIngredientSerializer(
            instance.recipe_ingredients.all(), many=True).data
        recipe['tags'] = TagSerializer(
            instance.tags.all(), many=True).data
        return recipe

    def add_tags_ingredients(self, ingredients, tags, model):
        recipe_ingredients = [
            RecipeIngredient(recipe=model,
                             ingredient=ingredient['id'],
                             amount=ingredient['amount'])
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        model.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_tags_ingredients(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.add_tags_ingredients(ingredients, tags, instance)
        return super().update(instance, validated_data)
