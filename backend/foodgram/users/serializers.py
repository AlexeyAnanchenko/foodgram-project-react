from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Subscribe
from recipes.models import Recipe


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

    def validate_author(self, value):
        if self.initial_data['user'] == value.id:
            raise serializers.ValidationError(
                {'error': 'Невозможно подписаться на себя'})
        return value
