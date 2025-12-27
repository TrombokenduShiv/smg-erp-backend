from django.contrib import admin
from .models import InternProfile

@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    # Columns to show
    list_display = ('user_email', 'department', 'monthly_stipend', 'joining_date')
    
    # Filters
    list_filter = ('department', 'is_active')
    
    # Search
    search_fields = ('user__email', 'user__first_name')

    # Helper to show email directly in the list (since 'user' is a relation)
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Intern Email'