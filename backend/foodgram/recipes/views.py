from djoser.views import viewsets, UserViewSet
from rest_framework.decorators import action
from rest_framework import permissions
from django.contrib.auth import get_user_model

from .models import Tag, Ingredient, Recipe
from .serializers import Read_RecipeSerializerClass, TagSerializerClass, RecipeSerializerClass


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
    serializer_class = TagSerializerClass
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerClass

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return Read_RecipeSerializerClass
        return RecipeSerializerClass

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
