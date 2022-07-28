from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscribe
from .serializers import SubscribeSerializer, SubscribeUserSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'subscriptions' or self.action == 'subscribe':
            return SubscribeUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [permissions.AllowAny, ]
        if self.action == 'subscribe' or self.action == 'subscription':
            self.permission_classes = [permissions.IsAuthenticated, ]
        return super().get_permissions()

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(["get"], detail=False)
    def subscriptions(self, request):
        subscribed = User.objects.filter(
            id__in=request.user.subscribed.values_list('author', flat=True)
        )
        page = self.paginate_queryset(subscribed)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscribed, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(["post", "delete"], detail=True)
    def subscribe(self, request, id=None):
        data = {'author': self.get_object().id, 'user': request.user.id}
        serializer = SubscribeSerializer(data=data)
        if request.method == "DELETE":
            if serializer.is_valid():
                raise serializers.ValidationError(
                    {'errors': 'Вы не подписаны на этого автора!'})
            data = {'author': self.get_object(), 'user': request.user}
            Subscribe.objects.get(**data).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {'author': self.get_object().id, 'user': request.user.id}
        serializer.is_valid(raise_exception=True)
        serializer.save()
        resp_serializer = self.get_serializer(self.get_object())
        return Response(resp_serializer.data, status=status.HTTP_201_CREATED)
