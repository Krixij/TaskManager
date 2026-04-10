from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Project, Task

#НАстройка отображения пользователей в админке
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email', 'first_name', 'last_name']

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

#Админка для проектов
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_by', 'created_at']
    list_filter = ['created_by', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

#Админка дял задач
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'project', 'status', 'assigned_to', 'created_at']
    list_filter = ['project', 'status']
    search_fields = ['title']
    list_editable = ['status', 'assigned_to']
    readonly_fields = ['created_at', 'created_by']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'project'),
        }),
        ('Статус и назначение', {
            'fields': ('status', 'assigned_to'),
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),

    )
# Register your models here.
