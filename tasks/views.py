from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import Http404
from .models import Project, Task
from .forms import ProjectForm, TaskForm

# Для защиты, если вышел то на страницу выхода не зайти еще раз в случае чего
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('tasks:project_list')
        return super().get(request, *args, **kwargs)

# Главная - список проектов
@login_required
def project_list(request):
    # Проекты из групп пользователя
    user_groups = request.user.participant_groups.all()
    group_projects = Project.objects.filter(group__in=user_groups)

    # Проекты, созданные пользователем
    user_projects = Project.objects.filter(created_by=request.user)

    # Объединяем и убираем дубликаты
    projects = (group_projects | user_projects).distinct()
    return render(request, 'projects/project_list.html', {'object_list': projects})


# Детали проекта
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    return render(request, 'projects/project_detail.html', {'project': project, 'tasks': tasks})


# Создание проекта (с формой)
@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect('tasks:project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})


# Редактирование проекта (с формой)
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            # Переход к проекту сразу после редактирования
            #return redirect('tasks:project_detail', pk=project.pk)
            # Переход к списку проектов
            return redirect('tasks:project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'object': project})


# Удаление проекта
@login_required
def project_delete(request, pk):

    project = get_object_or_404(Project, pk=pk)
    " добавил невозможность удалить если не автор (возможно также использовать группы людей по доступу к редактированию в будущем)"
    if project.created_by != request.user:
        raise Http404

    if request.method == 'POST':
        project.delete()
        return redirect('tasks:project_list')
    return render(request, 'projects/project_confirm_delete.html', {'object': project})


# Мои задачи (добавлен select_related для отбора всех проектов сразу за один запрос к БД)
@login_required
def my_tasks(request):
    active_tasks = Task.objects.filter(assigned_to=request.user, status='in_progress').select_related('project')
    completed_tasks = Task.objects.filter(assigned_to=request.user, status='done').select_related('project')

    return render(request, 'tasks/my_tasks.html', {
        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,
    })


# Создание задачи в проекте (с формой)
@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    project_participants = project.group.participant.all()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = TaskForm()
        # Ограничиваем выбор исполнителя только участниками проекта
        form.fields['assigned_to'].queryset = project_participants | User.objects.filter(id=request.user.id)

    return render(request, 'tasks/task_form.html', {'form': form, 'project': project})


# Редактирование задачи (с формой)
@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks:project_detail', pk=task.project.pk)
    else:
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {'form': form, 'object': task, 'project': task.project})


# Удаление задачи
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk
    if request.method == 'POST':
        task.delete()
        return redirect('tasks:project_detail', pk=project_pk)
    return render(request, 'tasks/task_confirm_delete.html', {'object': task})


# Выход
def logout_view(request):
    logout(request)
    return redirect('tasks:login')

#тест календарь
def calendar_view(request):
    return render(request, "calendar/calendar.html")