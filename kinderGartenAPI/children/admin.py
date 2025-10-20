# children/admin.py
from django.contrib import admin
from .models import ClassRoom, Child

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher_name", "age_range", "tenant")
    search_fields = ("name", "teacher_name", "assistant_name")

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("name", "birthdate", "classroom", "tenant")
    search_fields = ("name", "parent_name")
