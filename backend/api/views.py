from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import (UserSerializer, TagSerializer, IngredientSerializer,
                          RecipeSerializer)


from recipes.models import Tag, Ingredient, Recipe
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post']

    def list(self, request):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'next': 'http://foodgram.example.org/api/users/?page=4',
            'previous': 'http://foodgram.example.org/api/users/?page=2',
            'results': serializer.data
        })


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
