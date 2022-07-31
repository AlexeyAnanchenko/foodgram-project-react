from recipes.models import IngredientRecipe, ShoppingCart


def make_shopping_list(user):
    shopping_cart, result = ShoppingCart.objects.get_or_create(
        user_id=user
    )
    recipes = list(shopping_cart.recipe.values_list('id', flat=True))
    ingredient_recipe = IngredientRecipe.objects.filter(
        recipe_id__in=recipes
    ).select_related('ingredient')
    result = {}
    for obj in ingredient_recipe:
        try:
            result[obj.ingredient] += obj.amount
        except KeyError:
            result[obj.ingredient] = obj.amount
    content = 'НАЗВАНИЕ ПРОДУКТА (ед. изм.) - КОЛИЧЕСТВО\n'
    for key, value in result.items():
        content += f'{key.name} ({key.measurement_unit}) - {value}\n'
    return content
