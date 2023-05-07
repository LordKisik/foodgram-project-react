from datetime import date

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .paginations import MyPagination
from .permissions import (IsAuthorOrAdminOrReadOnly,
                          IsCurrentUserOrAdminOrReadOnly)
from .serializers import (FavoriteSerializer, FollowSerializer,
                          GetUserSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, TagSerializer)
from users.models import User


def get_shopping_list_data(author):
    return RecipeIngredient.objects.filter(
        recipe__shopping_cart__author=author
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)
    ).order_by('amounts')


def generate_shopping_list_response(data):
    today = date.today().strftime("%d-%m-%Y")
    shopping_list = f'Список покупок на: {today}\n\n'
    for ingredient in data:
        shopping_list += (
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) — '
            f'{ingredient["amounts"]}\n'
        )
    return HttpResponse(shopping_list, content_type='text/plain')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = MyPagination
    permission_classes = (IsCurrentUserOrAdminOrReadOnly,)
    serializer_class = GetUserSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user
        serializer = GetUserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if self.request.user.is_anonymous:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Пароль успешно изменен'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        follows = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=request.data,
                context={'request': request, 'author': author})
            subscription = Follow.objects.filter(author=author, user=user)
            if author == user:
                return Response({'errors': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if subscription.exists():
                return Response({'errors': 'Подписка уже существует'},
                                status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if Follow.objects.filter(author=author, user=user).exists():
            Follow.objects.get(author=author, user=user).delete()
            return Response({'message': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы не подписаны на данного пользователя'},
                        status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = MyPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeWriteSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if Favorite.objects.filter(author=user,
                                       recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(data={
                'recipe': recipe.id,
                'author': user.id
            })
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if not Favorite.objects.filter(author=user,
                                       recipe=recipe).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        get_object_or_404(Favorite, author=user, recipe=recipe).delete()
        return Response({'message': 'Рецепт удалён из избранного'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(author=user,
                                           recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data={
                'recipe': recipe.id,
                'author': user.id
            })
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if not ShoppingCart.objects.filter(author=user,
                                           recipe=recipe).exists():
            return Response({'errors': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        get_object_or_404(ShoppingCart, author=user, recipe=recipe).delete()
        return Response({'message': 'Рецепт удалён из списка покупок'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        author = get_object_or_404(User, id=self.request.user.pk)
        if author.shopping_cart.exists():
            data = get_shopping_list_data(author)
            response = generate_shopping_list_response(data)
            filename = 'shopping_list.txt'
            response['Content-Disposition'] = (f'attachment; '
                                               f'filename={filename}')
            return response
        return Response({'message': 'Список покупок пуст'},
                        status=status.HTTP_404_NOT_FOUND)
