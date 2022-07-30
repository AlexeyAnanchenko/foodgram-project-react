from django import forms
from django.contrib import admin

from recipes import models


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


class IngredientRecipeTabular(admin.TabularInline):
    model = models.IngredientRecipe


class TagsTabular(admin.TabularInline):
    model = models.Tag.recipes.through


class MyForm(forms.ModelForm):

    class Meta:
        model = models.Recipe
        fields = '__all__'

    def clean(self):
        data = dict(self.data)
        empty_ingredients = 0
        total_forms = int(data['ingredient_recipe-TOTAL_FORMS'][0])
        for num in range(total_forms):
            if (data[f'ingredient_recipe-{num}-ingredient'][0] == '' or
                (data[f'ingredient_recipe-{num}-ingredient'][0] != '' and
                    data.get(f'ingredient_recipe-{num}-DELETE') == ['on'])):
                empty_ingredients += 1
        if empty_ingredients == total_forms:
            raise forms.ValidationError(
                "Поле 'Ингредиенты' обязательно для заполнения!")
        return super().clean()


class RecipeAdmin(admin.ModelAdmin):
    form = MyForm
    fields = (
        'name', 'image', 'text',
        'author', 'cooking_time',
        'added_to_favorite'
    )
    list_display = (
        'pk', 'name', 'image', 'text',
        'author', 'Tags', 'cooking_time',
        'pub_date', 'Ingredients',
    )
    inlines = [IngredientRecipeTabular, TagsTabular, ]
    readonly_fields = ('added_to_favorite', )
    search_fields = ('author', 'name', 'tags')

    def Tags(self, obj):
        return "\n; ".join([r.slug for r in obj.tags.all()])

    def Ingredients(self, obj):
        return "\n; ".join([r.name for r in obj.ingredients.all()])

    def added_to_favorite(self, obj):
        return obj.favorites.all().count()


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'recipe', 'amount')


class RecipeShoppingCartTabular(admin.TabularInline):
    model = models.Recipe.shopping_cart.through


class ShoppingCartAdmin(admin.ModelAdmin):
    fields = ('user',)
    list_display = ('pk', 'user', 'Recipe')
    inlines = [RecipeShoppingCartTabular]

    def Recipe(self, obj):
        return "\n; ".join([f'{r.id}' for r in obj.recipe.all()])


class RecipeFavoriteTabular(admin.TabularInline):
    model = models.Recipe.favorites.through


class FavoriteAdmin(admin.ModelAdmin):
    fields = ('user',)
    list_display = ('pk', 'user', 'Recipe')
    inlines = [RecipeFavoriteTabular]

    def Recipe(self, obj):
        return "\n; ".join([f'{r.id}' for r in obj.recipe.all()])


admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.ShoppingCart, ShoppingCartAdmin)
admin.site.register(models.Favorite, FavoriteAdmin)
admin.site.register(models.IngredientRecipe, IngredientRecipeAdmin)
