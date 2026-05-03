from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Task, Project


# Create your views here.
def projects_with_tasks(request, project_id=None):
    projects = Project.objects.all().order_by('id')

    # Если нет проектов - показываем пустую страницу
    if not projects.exists():
        return render(request, 'projects_with_tasks.html', {
            'projects': [],
            'selected_project': None,
            'tasks': None,
        })

    # Если ID не указан - берём первый проект
    if project_id is None:
        return render(request, 'projects_with_tasks.html', {
            'projects': projects,
            'selected_project': None,
            'tasks': None,
        })

    # Показываем выбранный проект
    selected_project = get_object_or_404(Project, id=project_id)
    tasks = selected_project.tasks.all().order_by('-created_at')

    context = {
        'projects': projects,
        'selected_project': selected_project,
        'selected_project_id': project_id,
        'tasks': tasks,
    }

    return render(request, 'projects_with_tasks.html', context)



