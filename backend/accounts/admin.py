from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model=User

    list_display=('email', 'full_name', 'is_active', 'is_staff', 'is_superuser',)

    list_filter=('is_active', 'is_staff', 'is_superuser',)

    ordering=('email',)

    search_fields=('email',)

    fieldsets=((None, {'fields':(
        'full_name',
        'email',
        'password',
    )}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)}),
    )

    add_fieldsets=(('fields', {'classes': ('wide',), 'fields': ('full_name', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser',)}),)

