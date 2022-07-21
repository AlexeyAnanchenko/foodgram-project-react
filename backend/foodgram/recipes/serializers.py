from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

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


class Read_IngredientRecipeSerializerClass(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True,
    )
    name = serializers.CharField(
        source='ingredient',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient',
        read_only=True,
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = '__all__'


class IngredientRecipeSerializerClass(serializers.ModelSerializer):
    key = serializers.PrimaryKeyRelatedField(read_only=True, source='id')
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('name', 'measurement_unit')


class Base64Decoder(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        import base64
        from django.core.files.base import ContentFile
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(
            base64.b64decode(imgstr),
            name=imgstr[20:] + '.' + ext
        )
        return data


class Read_RecipeSerializerClass(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = Read_IngredientRecipeSerializerClass(many=True)
    tags = TagSerializerClass

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeSerializerClass(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializerClass(many=True)
    image = Base64Decoder()
    tags =TagSerializerClass

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for i in ingredients:
            i_dict = dict(i)
            IngredientRecipe.objects.create(
                ingredient=Ingredient.objects.get(pk=i_dict['id']),
                recipe=recipe, amount=i_dict['amount']
            )
        return recipe

    """
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.ingredients = validated_data.get('tags', instance.tags)
        for ing in ingredients:
            d = dict(ing)
            IngredientRecipe.objects.create(
                ingredient=Ingredient.objects.get(pk=d['id']),
                recipe=recipe, amount=d['amount']
            )
        return instance
    """