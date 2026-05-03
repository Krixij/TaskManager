from django.urls import path
from . import views

app_name = 'taskManager'  # пространство имён

urlpatterns = [
    path('', views.projects_with_tasks, name='projects_root'),
    path('<int:project_id>/', views.projects_with_tasks, name='projects_with_tasks'),
]