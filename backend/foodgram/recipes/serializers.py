from datetime import datetime
from django.db import IntegrityError
from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core import exceptions

from .models import Ingredient, IngredientRecipe, Recipe, Subscribe, Tag


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
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializerClass(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'color', 'slug')


class IngredientSerializerClass(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


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


class IngredientRecipeSerializerClass(serializers.ModelSerializer):
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


class RecipeSerializerClass(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializerClass(
        many=True,
        source='ingredient_recipe')
    image = Base64Decoder()
    tags = TagSerializerClass(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        tags = self.initial_data['tags']
        ingredients = self.initial_data['ingredients']
        validated_data.pop('ingredient_recipe')
        recipe = Recipe.objects.create(**validated_data)
        tags_set = []
        for t in tags:
            try:
                tag = Tag.objects.get(pk=t)
                tags_set.append(tag)
            except exceptions.ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f'Тега с таким ID не существует - {t}!'
                )
        recipe.tags.set(tags_set)
        ingredients_list = []
        ing_keys = []
        for i in ingredients:
            try:
                obj_ing = Ingredient.objects.get(pk=i['id'])
                if i['id'] in ing_keys:
                    raise serializers.ValidationError(
                        'Нельзя дублировать ингридиенты!'
                    )
                ing_keys.append(i['id'])
                obj = IngredientRecipe.objects.create(
                    ingredient=obj_ing,
                    recipe=recipe, amount=i['amount'])
                ingredients_list.append(obj)
            except exceptions.ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f'Ингридиента с таким ID не существует - {i["id"]}!'
                )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        # Теги
        tags = self.initial_data['tags']
        current_tags = list(instance.tags.all())
        tags_set = []
        for t in tags:
            try:
                tag = Tag.objects.get(pk=t)
                tags_set.append(tag)
            except exceptions.ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f'Тега с таким ID не существует - {t}!'
                )
        if tags_set != current_tags:
            for tag in current_tags:
                if tag not in tags_set:
                    instance.tags.through.objects.filter(
                        recipe=instance,
                        tag=tag
                    ).delete()
        instance.tags.set(tags_set)
        # Ингридиенты
        ingredients = self.initial_data['ingredients']
        current_ingred = list(instance.ingredient_recipe.all())
        ingredients_list = []
        ing_keys = []
        for i in ingredients:
            try:
                obj = Ingredient.objects.get(pk=i['id'])
                if i['id'] in ing_keys:
                    raise serializers.ValidationError(
                        'Нельзя дублировать ингридиенты!'
                    )
                ing_keys.append(i['id'])
                ingredients_list.append(
                    {'ingredient': obj, 'amount': i['amount']}
                )
            except exceptions.ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f'Ингридиента с таким ID не существует - {i["id"]}!'
                )
        ingredients_set = []
        for i in ingredients_list:
            try:
                obj, result = IngredientRecipe.objects.get_or_create(
                    ingredient=i['ingredient'],
                    recipe=instance, amount=i['amount'])
                ingredients_set.append(obj)
            except IntegrityError:
                obj = IngredientRecipe.objects.get(
                    ingredient=i['ingredient'],
                    recipe=instance
                )
                obj.amount = i['amount']
                obj.save()
                ingredients_set.append(obj)
        if ingredients_set != current_ingred:
            for i in current_ingred:
                if i not in ingredients_set:
                    IngredientRecipe.objects.filter(pk=i.id).delete()
        instance.ingredient_recipe.set(ingredients_set)
        return instance


class RecipeShoppingSerializerClass(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')