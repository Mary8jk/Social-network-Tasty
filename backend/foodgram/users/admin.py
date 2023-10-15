from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('email',)
    list_filter = ('email', 'first_name',)


admin.site.register(User)
