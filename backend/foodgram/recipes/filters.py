from django_filters import rest_framework as filters

from .models import Recipe, Ingredient


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='get_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
