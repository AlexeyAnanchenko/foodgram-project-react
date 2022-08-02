from datetime import datetime

from django.contrib.auth import get_user_model
from django.core import exceptions
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscribed.filter(user=user, author=obj).exists()
        return False


class RecipeActionSerializerClass(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeUserSerializer(CustomUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeActionSerializerClass(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ['user', 'author']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже оформлена'
            )
        ]

    def validate(self, data):
        data = dict(data)
        if data['user'] == data['author']:
            raise serializers.ValidationError('Невозможно подписаться на себя')
        return data


class TagSerializerClass(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'color', 'slug')


class IngredientSerializerClass(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart.recipe.through
        fields = ['shoppingcart', 'recipe']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.recipe.through.objects.all(),
                fields=('shoppingcart', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite.recipe.through
        fields = ['favorite', 'recipe']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.recipe.through.objects.all(),
                fields=('favorite', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]


class Base64Decoder(serializers.ImageField):
    def to_representation(self, value):
        return super().to_representation(value)

    def to_internal_value(self, data):
        import base64

        from django.core.files.base import ContentFile
        try:
            format, imgstr = data.split(';base64,')
            return ContentFile(
                base64.b64decode(imgstr),
                name="{:%Y-%m-%d %H-%M-%S}.png".format(datetime.now())
            )
        except AttributeError:
            return data


class ReadIngredientRecipeSerializerClass(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerializerClass(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = ReadIngredientRecipeSerializerClass(
        many=True,
        source='ingredient_recipe')
    tags = TagSerializerClass(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            try:
                return obj in user.favorite.recipe.all()
            except exceptions.ObjectDoesNotExist:
                pass
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            try:
                return obj in user.shopping_cart.recipe.all()
            except exceptions.ObjectDoesNotExist:
                pass
        return False


class IngredientRecipeSerializer(serializers.ModelSerializer):
    key = serializers.PrimaryKeyRelatedField(read_only=True, source='pk')
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount', 'recipe', 'key')
        read_only_fields = ('key', 'recipe')


class RecipeSerializerClass(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64Decoder()
    ingredients = IngredientRecipeSerializer(many=True, )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )

    def validate(self, data):
        data = dict(data)
        tags = data['tags']
        ingredients = [dict(obj)['ingredient'] for obj in data['ingredients']]
        if ingredients == []:
            raise serializers.ValidationError(
                'поле ingredients обязательное для заполнения')

        def verify(list_obj, text):
            objects = []
            for obj in list_obj:
                if obj in objects:
                    raise serializers.ValidationError(
                        f'Нельзя дублировать {text}!')
                objects.append(obj)

        verify(ingredients, 'ингредиенты')
        verify(tags, 'теги')
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredients_obj = []
        for ingredient in ingredients:
            ingredient = dict(ingredient)
            ingredients_obj.append(IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ))
        IngredientRecipe.objects.bulk_create(ingredients_obj)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        current_tags = list(
            instance.tags.through.objects.filter(recipe=instance)
        )
        current_ing = list(instance.ingredient_recipe.all())

        def relation_objs(update_list, current_list, model, key):
            data = {'recipe': instance}
            renew_obj = []
            for obj in update_list:
                if key == 'ingredient':
                    obj = dict(obj)
                    result, bool = model.objects.update_or_create(
                        recipe=data['recipe'], ingredient=obj[key],
                        defaults={'amount': obj['amount']}
                    )
                    renew_obj.append(result)
                else:
                    data[key] = obj
                    result, bool = model.objects.update_or_create(**data)
                    renew_obj.append(result)
            for obj in current_list:
                if obj not in renew_obj:
                    obj.delete()

        relation_objs(ingredients, current_ing, IngredientRecipe, 'ingredient')
        relation_objs(tags, current_tags, Tag.recipes.through, 'tag')
        instance.save()
        return instance
