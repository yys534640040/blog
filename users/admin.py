from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
# Register your models here.

# 用户自定义模型
User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('nickname', 'email', 'mobile', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'nickname',  'mobile', 'email', 'is_staff', 'is_active', 'is_superuser')


admin.site.register(User, UserAdmin)







