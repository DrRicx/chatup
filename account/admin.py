from django.contrib import admin

from .models import *


# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'user_type')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
