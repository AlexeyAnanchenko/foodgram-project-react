from rest_framework import mixins


class CreateDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin):
    pass
