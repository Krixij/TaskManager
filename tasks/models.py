from django.contrib.auth.models import User
from django.db import models

#Модель для группы людей
class GroupPeople(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    participant = models.ManyToManyField(
        User,
        blank=True,
        related_name='participant_groups',
        verbose_name='Участник'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_groups',
        verbose_name='Создатель группы'
    )
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['-created_at']


#Модель для пользователей
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Руководитель'),
        ('executor', 'Исполнитель'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='executor', verbose_name='Роль')
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name='Руководитель'
    )

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

#Модель для проектов
class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название проекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects',
        verbose_name='Создатель'
    )
    group = models.ForeignKey(
        GroupPeople,
        on_delete=models.SET_NULL,
        null=True,
        related_name='group_projects',
        verbose_name='Группа'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

# Модель для задач
class Task(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В работе'),
        ('done', 'Выполнено'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критичный'),
    ]
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='Статус'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='low',
        verbose_name='Приоритет'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Проект'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Исполнитель'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    due_date = models.DateField(null=True, blank=True ,verbose_name='Срок выполнения')

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']


# Модель для подзадач
class Subtask(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='subtasks',
        verbose_name='Задача'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название подзадачи'
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Выполнена'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Подзадача'
        verbose_name_plural = 'Подзадачи'
        ordering = ['created_at']
