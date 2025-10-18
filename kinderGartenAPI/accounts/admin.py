from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "tenant", "is_staff")
    list_filter = ("role", "tenant")
