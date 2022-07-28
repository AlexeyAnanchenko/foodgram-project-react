from django.contrib import admin

from recipes import models


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)


class IngredientRecipeTabular(admin.TabularInline):
    model = models.IngredientRecipe


class TagsTabular(admin.TabularInline):
    model = models.Tag.recipes.through


class RecipeAdmin(admin.ModelAdmin):
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
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('added_to_favorite', )

    def Tags(self, obj):
        return "\n; ".join([r.slug for r in obj.tags.all()])

    def Ingredients(self, obj):
        return "\n; ".join([r.name for r in obj.ingredients.all()])

    def added_to_favorite(self, obj):
        return obj.favorites.all().count()


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
