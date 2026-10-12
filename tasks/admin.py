from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Project, Task, GroupPeople, UserProfile, Subtask

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Профиль'
    verbose_name_plural = 'Профиль'
    fk_name = 'user'
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

#Настройка отображения пользователей в админке
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    inlines = [UserProfileInline]

    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Роль'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Админка для групп людей
@admin.register(GroupPeople)
class GroupPeopleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_participant_count', 'created_by', 'created_at']
    list_filter = ['created_by', 'created_at']
    search_fields = ['title']
    filter_horizontal = ('participant',)

    readonly_fields = ['created_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title',),
        }),
        ('Участники', {
            'fields': ('participant',),
            'description': 'Выберите пользователей, которые будут входить в группу'
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_participant_count(self, obj):
        """Отображает количество участников в группе"""
        return obj.participant.count()

    get_participant_count.short_description = 'Кол-во участников'
    get_participant_count.admin_order_field = 'participant__count'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Оптимизация запроса с подсчетом участников"""
        return super().get_queryset(request).prefetch_related('participant')

#Админка для проектов
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_by', 'created_at']
    list_filter = ['created_by', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    raw_id_fields = ['group']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

#Админка дял задач
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'project', 'status', 'priority', 'assigned_to','due_date', 'created_at']
    list_filter = ['project', 'status', 'priority', 'assigned_to', 'created_at']
    search_fields = ['title', 'description']
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
            'fields': ('status', 'priority', 'due_date','assigned_to'),
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),

    )
# Register your models here.

# Админка для подзадач
@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'task', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at']
    search_fields = ['title', 'task__title']
    list_editable = ['is_completed']
    readonly_fields = ['created_at']
