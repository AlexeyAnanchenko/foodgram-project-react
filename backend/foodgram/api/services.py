from recipes.models import ShoppingCart, IngredientRecipe


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
        if (f'{obj.ingredient.name} '
                f'({obj.ingredient.measurement_unit})') in result.keys():
            result[
                f'{obj.ingredient.name} ({obj.ingredient.measurement_unit})'
            ] = result[
                f'{obj.ingredient.name} ({obj.ingredient.measurement_unit})'
            ] + obj.amount
        else:
            result[
                f'{obj.ingredient.name} ({obj.ingredient.measurement_unit})'
            ] = obj.amount
    content = 'НАЗВАНИЕ ПРОДУКТА (ед. изм.) - КОЛИЧЕСТВО\n'
    for key, value in result.items():
        content = content + f'{key} - {value}\n'
    return content
