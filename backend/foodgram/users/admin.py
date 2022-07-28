from django.contrib import admin

from users import models


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'email', 'username',
        'first_name', 'last_name', 'password',
    )
    list_filter = ('email', 'username')

    def save_model(self, request, obj, form, change):
        if obj.pk:
            orig_obj = models.User.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Subscribe, SubscribeAdmin)
