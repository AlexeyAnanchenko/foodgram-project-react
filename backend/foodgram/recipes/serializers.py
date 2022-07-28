from datetime import datetime

from django.contrib.auth import get_user_model
from django.core import exceptions
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)

User = get_user_model()


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
        format, imgstr = data.split(';base64,')
        data = ContentFile(
            base64.b64decode(imgstr),
            name="{:%Y-%m-%d %H-%M-%S}.png".format(datetime.now())
        )
        return data


class Read_IngredientRecipeSerializerClass(serializers.ModelSerializer):
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


class Read_RecipeSerializerClass(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = Read_IngredientRecipeSerializerClass(
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
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )

    def validate_ingredients(self, value):
        objects = []
        for i in value:
            i = dict(i)
            if i['ingredient'] in objects:
                raise serializers.ValidationError(
                    {'errors': 'Нельзя дублировать ингридиенты!'})
            objects.append(i['ingredient'])
        return value

    def validate_tags(self, value):
        objects = []
        for i in value:
            if i in objects:
                raise serializers.ValidationError(
                    {'errors': 'Нельзя дублировать теги!'})
            objects.append(i)
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for i in ingredients:
            i = dict(i)
            i['recipe'] = recipe
            IngredientRecipe.objects.create(**i)
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
        current_tags = list(instance.tags.all())
        if current_tags != tags:
            for tag in current_tags:
                if tag not in tags:
                    instance.tags.through.objects.filter(
                        recipe=instance,
                        tag=tag
                    ).delete()
            instance.tags.set(tags)
        current_ing = list(instance.ingredient_recipe.all())
        ingredients_set = []
        for i in ingredients:
            i = dict(i)
            try:
                obj = IngredientRecipe.objects.get(
                    ingredient=i['ingredient'],
                    recipe=instance
                )
                obj.amount = i['amount']
                obj.save()
                ingredients_set.append(obj)
            except exceptions.ObjectDoesNotExist:
                i['recipe'] = instance
                obj = IngredientRecipe.objects.create(**i)
                ingredients_set.append(obj)
        for i in current_ing:
            if i not in ingredients_set:
                i.delete()
        instance.save()
        return instance
