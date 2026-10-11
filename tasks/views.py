
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout

from .models import Project, Task, Subtask
from .forms import ProjectForm, TaskForm, SubtaskForm


# Для защиты, если пользователь уже вошёл в систему
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('tasks:project_list')
        return super().get(request, *args, **kwargs)


# Главная - список проектов
@login_required
def project_list(request):
    user_groups = request.user.participant_groups.all()
    group_projects = Project.objects.filter(group__in=user_groups)
    user_projects = Project.objects.filter(created_by=request.user)

    projects = (group_projects | user_projects).distinct()

    return render(
        request,
        'projects/project_list.html',
        {'object_list': projects}
    )


# Детали проекта
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    tasks = project.tasks.annotate(
        subtasks_count=Count('subtasks', distinct=True),
        completed_subtasks_count=Count(
            'subtasks',
            filter=Q(subtasks__is_completed=True),
            distinct=True
        )
    ).prefetch_related('subtasks')

    for task in tasks:
        if task.subtasks_count > 0:
            task.subtasks_progress = round(
                task.completed_subtasks_count / task.subtasks_count * 100
            )
        else:
            task.subtasks_progress = 0

    return render(
        request,
        'projects/project_detail.html',
        {
            'project': project,
            'tasks': tasks,
        }
    )

# Создание проекта
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

    return render(
        request,
        'projects/project_form.html',
        {'form': form}
    )


# Редактирование проекта
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        'projects/project_form.html',
        {
            'form': form,
            'object': project,
        }
    )


# Удаление проекта
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('tasks:project_list')

    return render(
        request,
        'projects/project_confirm_delete.html',
        {'object': project}
    )


# Мои задачи
@login_required
def my_tasks(request):
    active_tasks = Task.objects.filter(
        assigned_to=request.user,
        status='in_progress'
    ).select_related('project')

    completed_tasks = Task.objects.filter(
        assigned_to=request.user,
        status='done'
    ).select_related('project')

    return render(
        request,
        'tasks/my_tasks.html',
        {
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
        }
    )


# Создание задачи в проекте
@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)

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

        if project.group:
            project_participants = project.group.participant.all()
            form.fields['assigned_to'].queryset = (
                project_participants |
                User.objects.filter(pk=request.user.pk)
            ).distinct()
        else:
            form.fields['assigned_to'].queryset = User.objects.filter(
                pk=request.user.pk
            )

    return render(
        request,
        'tasks/task_form.html',
        {
            'form': form,
            'project': project,
        }
    )


# Редактирование задачи
@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            return redirect(
                'tasks:project_detail',
                pk=task.project.pk
            )
    else:
        form = TaskForm(instance=task)

    return render(
        request,
        'tasks/task_form.html',
        {
            'form': form,
            'object': task,
            'project': task.project,
        }
    )


# Удаление задачи
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk

    if request.method == 'POST':
        task.delete()
        return redirect('tasks:project_detail', pk=project_pk)

    return render(
        request,
        'tasks/task_confirm_delete.html',
        {'object': task}
    )


# Создание подзадачи
@login_required
@require_POST
def subtask_create(request, task_pk):
    task = get_object_or_404(
        Task.objects.filter(
            Q(project__created_by=request.user) |
            Q(project__group__participant=request.user)
        ).distinct(),
        pk=task_pk
    )

    form = SubtaskForm(request.POST)

    if form.is_valid():
        subtask = form.save(commit=False)
        subtask.task = task
        subtask.save()

    return redirect(
        'tasks:project_detail',
        pk=task.project_id
    )


# Изменение статуса подзадачи
@login_required
@require_POST
def subtask_toggle(request, pk):
    subtask = get_object_or_404(
        Subtask.objects.filter(
            Q(task__project__created_by=request.user) |
            Q(task__project__group__participant=request.user)
        ).distinct(),
        pk=pk
    )

    subtask.is_completed = not subtask.is_completed
    subtask.save(update_fields=['is_completed'])

    return redirect(
        'tasks:project_detail',
        pk=subtask.task.project_id
    )


# Выход
def logout_view(request):
    logout(request)
    return redirect('tasks:login')
