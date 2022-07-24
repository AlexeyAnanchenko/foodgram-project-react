from django.http import HttpResponse
from djoser.views import viewsets, UserViewSet
from rest_framework.decorators import action
from rest_framework import permissions
from django.contrib.auth import get_user_model

from .models import Tag, Ingredient, Recipe
from .serializers import IngredientSerializerClass, TagSerializerClass
from .serializers import RecipeSerializerClass
# from .mixins import CreateDeleteViewSet


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        return User.objects.all()

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [permissions.IsAuthenticated, ]
        return super().get_permissions()

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializerClass
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializerClass
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerClass

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(["get"], detail=False)
    def download_shopping_cart(self, request):
        recipes = self.request.user.shopping_cart.recipe.all()
        result = {}
        for recipe in recipes:
            for i in recipe.ingredient_recipe.all():
                if i.ingredient.name in result.keys():
                    result[
                        f'{i.ingredient.name} '
                        f'({i.ingredient.measurement_unit})'
                    ] = result[
                        f'{i.ingredient.name} '
                        f'({i.ingredient.measurement_unit})'
                    ] + i.amount
                else:
                    result[
                        f'{i.ingredient.name} '
                        f'({i.ingredient.measurement_unit})'
                    ] = i.amount
        content = 'НАЗВАНИЕ ПРОДУКТА: КОЛИЧЕСТВО\n'
        for key, value in result.items():
            content = content + f'{key}: - {value}\n'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="shopping_list.txt"'
        )
        return response


"""
class ShoppingCartViewSet(CreateDeleteViewSet):
    serializer_class = 

    def get_queryset(self):
        return Recipe.objects.get(pk=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
"""
