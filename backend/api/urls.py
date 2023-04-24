from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
# router.register(r'recipes',)
# router.register(r'recipes/(?P<recipes_id>\d+)')
# router.register()

router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    # path('auth/token/login/', SignupView.as_view(), name='signup'),
    # path('auth/token/logout/', GetTokenView.as_view(), name='token'),
]
