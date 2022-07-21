from django.contrib import admin

from .models import User, Subscribe, Tag, Ingredient, Recipe, IngredientRecipe


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
    model = IngredientRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'image', 'text',
        'author', 'tags', 'cooking_time'
    )
    inlines = [IngredientRecipeTabular, ]

    def tags(self, obj):
        return "\n".join([r.tags for r in obj.tags.all()])


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
