from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ProjectForm, TaskForm, ProjectFilterForm, TaskFilterForm
from .models import Project, Task


# Если пользователь уже вошёл, повторно открывать страницу входа не нужно.
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('tasks:project_list')
        return super().get(request, *args, **kwargs)


# Главная — список проектов с поиском и фильтрами.
@login_required
def project_list(request):
    user_groups = request.user.participant_groups.all()
    group_projects = Project.objects.filter(group__in=user_groups)
    user_projects = Project.objects.filter(created_by=request.user)
    projects = (group_projects | user_projects).distinct()

    filter_form = ProjectFilterForm(request.GET or None)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        assigned_to = filter_form.cleaned_data.get('assigned_to')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')

        if search:
            projects = projects.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(tasks__title__icontains=search)
                | Q(tasks__description__icontains=search)
            ).distinct()

        # На странице проектов даты относятся к дате создания проекта.
        if date_from:
            projects = projects.filter(created_at__date__gte=date_from)
        if date_to:
            projects = projects.filter(created_at__date__lte=date_to)

        # Статус, приоритет и исполнитель относятся к задачам внутри проекта.
        if status or priority or assigned_to:
            matching_tasks = Task.objects.filter(project__in=projects)
            if status:
                matching_tasks = matching_tasks.filter(status=status)
            if priority:
                matching_tasks = matching_tasks.filter(priority=priority)
            if assigned_to:
                matching_tasks = matching_tasks.filter(assigned_to=assigned_to)
            projects = projects.filter(pk__in=matching_tasks.values('project_id'))

    return render(request, 'projects/project_list.html', {
        'object_list': projects.order_by('-created_at').distinct(),
        'filter_form': filter_form,
    })


# Детали проекта.
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    return render(request, 'projects/project_detail.html', {'project': project, 'tasks': tasks})


# Создание проекта.
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


# Редактирование проекта.
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
    return render(request, 'projects/project_form.html', {'form': form, 'object': project})


# Удаление проекта.
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('tasks:project_list')
    return render(request, 'projects/project_confirm_delete.html', {'object': project})


# Мои задачи — поиск и фильтры применяются только к задачам текущего пользователя.
@login_required
def my_tasks(request):
    filter_form = TaskFilterForm(request.GET or None)
    tasks = Task.objects.filter(assigned_to=request.user).select_related('project')

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')

        if search:
            tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))
        if status:
            tasks = tasks.filter(status=status)
        if priority:
            tasks = tasks.filter(priority=priority)
        if date_from:
            tasks = tasks.filter(created_at__date__gte=date_from)
        if date_to:
            tasks = tasks.filter(created_at__date__lte=date_to)

    return render(request, 'tasks/my_tasks.html', {
        'active_tasks': tasks.filter(status='in_progress'),
        'completed_tasks': tasks.filter(status='done'),
        'filter_form': filter_form,
    })


# Создание задачи в проекте.
@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    project_participants = project.group.participant.all() if project.group else User.objects.none()
    allowed_assignees = (project_participants | User.objects.filter(id=request.user.id)).distinct()

    if request.method == 'POST':
        form = TaskForm(request.POST)
    else:
        form = TaskForm()

    # Исполнителем может быть участник группы проекта или текущий пользователь.
    # Ограничение применяется и при GET, и при POST.
    form.fields['assigned_to'].queryset = allowed_assignees

    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        return redirect('tasks:project_detail', pk=project.pk)

    return render(request, 'tasks/task_form.html', {'form': form, 'project': project})


# Редактирование задачи.
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


# Удаление задачи.
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk
    if request.method == 'POST':
        task.delete()
        return redirect('tasks:project_detail', pk=project_pk)
    return render(request, 'tasks/task_confirm_delete.html', {'object': task})


# Выход.
def logout_view(request):
    logout(request)
    return redirect('tasks:login')
