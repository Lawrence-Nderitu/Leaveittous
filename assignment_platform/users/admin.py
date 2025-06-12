from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Define a custom User admin if you need to add user_type, profile_picture, bio to list_display or fieldsets
# For now, a simple registration or extending UserAdmin slightly

class CustomUserAdmin(UserAdmin):
    model = User
    # Add user_type to list_display, list_filter, fieldsets, etc. as needed
    list_display = UserAdmin.list_display + ('user_type',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'profile_picture', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'profile_picture', 'bio', 'first_name', 'last_name', 'email')}),
    )

admin.site.register(User, CustomUserAdmin)
