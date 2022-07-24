from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, TagViewSet, RecipeViewSet
from .views import IngredientViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    #path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartViewSet),
    #path('recipes/<int:recipe_id>/favorite/', ),
    # path('users/subscriptions/',),
    # path('users/<int:user_id>/subscribe/',),
    path('auth/', include('djoser.urls.authtoken')),
]
