from django.contrib import admin

from recipes import models


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'email', 'username',
        'first_name', 'last_name', 'password',
    )


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')


class IngredientRecipeTabular(admin.TabularInline):
    model = models.IngredientRecipe


class TagsTabular(admin.TabularInline):
    model = models.Tag.recipes.through


class RecipeAdmin(admin.ModelAdmin):
    fields = (
        'name', 'image', 'text',
        'author', 'cooking_time'
    )
    list_display = (
        'pk', 'name', 'image', 'text',
        'author', 'Tags', 'cooking_time',
        'Ingredients'
    )
    inlines = [IngredientRecipeTabular, TagsTabular, ]

    def Tags(self, obj):
        return "\n; ".join([r.slug for r in obj.tags.all()])

    def Ingredients(self, obj):
        return "\n; ".join([r.name for r in obj.ingredients.all()])


class IngrediantRecipeAdmin(admin.ModelAdmin):
    pass


class RecipeTabular(admin.TabularInline):
    model = models.Recipe.shopping_cart.through


class ShoppingCartAdmin(admin.ModelAdmin):
    fields = ('user',)
    list_display = ('pk', 'user', 'Recipe')
    inlines = [RecipeTabular]

    def Recipe(self, obj):
        return "\n; ".join([f'{r.id}' for r in obj.recipe.all()])


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Subscribe, SubscribeAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.ShoppingCart, ShoppingCartAdmin)
admin.site.register(models.IngredientRecipe, IngrediantRecipeAdmin)
