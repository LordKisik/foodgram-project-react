from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Введите уникальное название тега',
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        help_text='Введите уникальный цвет в формате HEX',
        verbose_name='Цвет в HEX',
        validators=[RegexValidator(regex='^#[A-Fa-f0-9]{6}$',
                                   message='Неверный HEX-код')]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text='Введите уникальный слаг',
        verbose_name='Уникальный слаг'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='tags'
    )
    image = models.ImageField(
        upload_to='dishes/',
        verbose_name='Изображение блюда'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        db_index=True
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_recipe'
            ),
        )


class RecipeIngredient(models.Model):
    """Связующая модель между рецептом и ингредиентом."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_recipes'
            ),
        )


class BaseItem(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f'{self.recipe}'

    class Meta:
        abstract = True


class ShoppingCart(BaseItem):
    """Модель списка покупок."""

    class Meta(BaseItem.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_cart'
            ),
        )


class Favorite(BaseItem):
    """Модель избранных рецептов."""

    class Meta(BaseItem.Meta):
        default_related_name = 'favorite'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_favorite'
            ),
        )


class Follow(models.Model):
    """Модель подписки на аторов рецептов."""
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
        verbose_name='Подписка',
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_following'
            )
        )
