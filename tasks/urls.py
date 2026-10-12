
from django.urls import path
from . import views
from .views import CustomLoginView

app_name = 'tasks'

urlpatterns = [
    path('', views.project_list, name='project_list'),

    # Проекты
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),

    # Задачи
    path(
        'projects/<int:project_pk>/tasks/create/',
        views.task_create,
        name='task_create'
    ),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Подзадачи
    path(
        'tasks/<int:task_pk>/subtasks/create/',
        views.subtask_create,
        name='subtask_create'
    ),
    path(
        'subtasks/<int:pk>/toggle/',
        views.subtask_toggle,
        name='subtask_toggle'
    ),

    # Мои задачи и авторизация
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('calendar/', views.calendar_view, name='calendar'),  #тест календарь
    path('login/', CustomLoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
