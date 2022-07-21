"""
from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet

app_name = 'users'

router = routers.SimpleRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', ),
    path('users/set_password/', ),
    path('users/subscriptions/',),
    path('users/<int:user_id>/subscribe/',),
    path('auth/token/login/', ),
    path('auth/token/logout/', ),
]
"""