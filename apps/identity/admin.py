from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# If you created forms.py earlier, import them. If not, use standard forms for now.
# from .forms import CustomUserCreationForm, CustomUserChangeForm 

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Standard UserAdmin configuration adapted for 'email' instead of 'username'
    list_display = ('email', 'display_id', 'role', 'department', 'is_staff')
    list_filter = ('role', 'department', 'is_staff')
    search_fields = ('email', 'display_id', 'first_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('SMG Operations', {'fields': ('role', 'department', 'display_id')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password_2', 'role', 'department'),
        }),
    )
    
    readonly_fields = ('display_id',)