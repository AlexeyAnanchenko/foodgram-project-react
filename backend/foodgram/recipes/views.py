from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.serializers import RecipeActionSerializerClass

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializerClass,
                          Read_RecipeSerializerClass, RecipeSerializerClass,
                          ShoppingCartSerializer, TagSerializerClass)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializerClass
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializerClass
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializerClass
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorAdminOrReadOnly, ]

    def get_queryset(self):
        return Recipe.objects.all().order_by('-pub_date')

    def get_permissions(self):
        if (self.action == 'download_shopping_cart'
                or self.action == 'shopping_cart'
                or self.action == 'favorite'):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return Read_RecipeSerializerClass
        if self.action == 'shopping_cart' or self.action == 'favorite':
            return RecipeActionSerializerClass
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_create(serializer)
        self.action = 'retrieve'
        serializer = self.get_serializer(
            recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        kwargs.pop('partial', None)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=False
        )
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_update(serializer)
        self.action = 'retrieve'
        serializer = self.get_serializer(
            recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    @action(["get"], detail=False)
    def download_shopping_cart(self, request):
        recipes = self.request.user.shopping_cart.recipe.all()
        result = {}
        for recipe in recipes:
            for i in recipe.ingredient_recipe.all():
                if (f'{i.ingredient.name} '
                        f'({i.ingredient.measurement_unit})') in result.keys():
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
        content = 'НАЗВАНИЕ ПРОДУКТА (ед. изм.) - КОЛИЧЕСТВО\n'
        for key, value in result.items():
            content = content + f'{key} - {value}\n'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="shopping-list.txt"'
        )
        return response

    def action_func(self, request, model, serializer, key):
        model_obj, result = model.objects.get_or_create(
            user=request.user
        )
        data = {'recipe': self.get_object().id, key: model_obj.id}
        serializer = serializer(data=data)
        if request.method == 'DELETE':
            if serializer.is_valid():
                raise serializers.ValidationError(
                    {'errors': f'Рецепта нет в {model._meta.verbose_name}'})
            obj = model_obj.recipe.through.objects.get(
                recipe=self.get_object()
            )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        resp_serializer = self.get_serializer(self.get_object())
        return Response(resp_serializer.data, status=status.HTTP_201_CREATED)

    @action(["post", "delete"], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.action_func(
            request, ShoppingCart, ShoppingCartSerializer, 'shoppingcart')

    @action(["post", "delete"], detail=True)
    def favorite(self, request, pk=None):
        return self.action_func(
            request, Favorite, FavoriteSerializer, 'favorite')
