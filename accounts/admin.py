from django.contrib import admin
from .models import User, DAISYUI_THEMES

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'theme', 'personal_printer', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'theme', 'personal_printer')
    list_filter = ('is_staff', 'is_active', 'theme')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informazioni personali', {'fields': ('first_name', 'last_name', 'email', 'theme', 'personal_printer')}),
        ('Permessi', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Date importanti', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'theme', 'personal_printer'),
        }),
    )
