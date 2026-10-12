from collections import defaultdict
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ProjectForm, TaskForm, ProjectFilterForm, TaskFilterForm, SubtaskForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.http import Http404
from .forms import ProjectForm, TaskForm
from datetime import date, timedelta
from .models import Project, Task, Subtask


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
    # Руководитель видит созданные им проекты,
    # исполнитель — проекты групп, в которых состоит.
    if request.user.profile.role == 'manager':
        projects = Project.objects.filter(created_by=request.user)
    # Исполнитель видит проекты групп, в которых состоит
    else:
        user_groups = request.user.participant_groups.all()
        projects = Project.objects.filter(group__in=user_groups)

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

# Детали проекта
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Проверка доступа
    if request.user.profile.role == 'manager':
        if project.created_by != request.user:
            raise Http404
    else:
        if not project.group.participant.filter(id=request.user.id).exists():
            raise Http404

    #tasks = project.tasks.all()
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
    # Создавать проекты может только руководитель
    if request.user.profile.role != 'manager':
        raise Http404

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        # Ограничиваем выбор группы только теми, где состоит руководитель
        form.fields['group'].queryset = request.user.participant_groups.all()
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect('tasks:project_list')
    else:
        form = ProjectForm()
        # Ограничиваем выбор группы только теми, где состоит руководитель
        form.fields['group'].queryset = request.user.participant_groups.all()
    return render(request, 'projects/project_form.html', {'form': form})

# Редактирование проекта.
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Редактировать может только автор проекта
    if project.created_by != request.user:
        raise Http404

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        # Ограничиваем выбор группы только теми, где состоит руководитель
        form.fields['group'].queryset = request.user.participant_groups.all()
        if form.is_valid():
            form.save()
            # Переход к проекту сразу после редактирования
            #return redirect('tasks:project_detail', pk=project.pk)
            # Переход к списку проектов
            return redirect('tasks:project_list')
    else:
        form = ProjectForm(instance=project)
         # Ограничиваем выбор группы только теми, где состоит руководитель
        form.fields['group'].queryset = request.user.participant_groups.all()

    return render(request, 'projects/project_form.html', {'form': form, 'object': project})


# Удаление проекта.
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

    """return render(
        request,
        'tasks/my_tasks.html',
        {
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
        }
    )"""

# Создание задачи в проекте.
@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    role = request.user.profile.role

    # Проверка прав доступа к проекту
    if role == 'manager':
        # Руководитель может создавать задачи только в своих проектах
        if project.created_by != request.user:
            raise Http404
        # Руководитель назначает исполнителя из участников группы проекта
        if project.group:
            allowed_assignees = project.group.participant.all()
        else:
            allowed_assignees = User.objects.none()
    else:
        # Исполнитель может создавать задачи только в проектах своих групп
        if not project.group or not project.group.participant.filter(id=request.user.id).exists():
            raise Http404
        # И назначать задачу только себе
        allowed_assignees = User.objects.filter(id=request.user.id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
    else:
        form = TaskForm()

    # Ограничение применяется и при GET, и при POST
    form.fields['assigned_to'].queryset = allowed_assignees

    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        return redirect('tasks:project_detail', pk=project.pk)

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


# Редактирование задачи.
@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Определяем, кем является пользователь по отношению к задаче
    is_author = task.created_by == request.user
    is_executor = task.assigned_to == request.user

    # Если пользователь не автор и не исполнитель — доступ запрещён
    if not is_author and not is_executor:
        raise Http404

    # Определяем, кого можно назначать исполнителем
    if request.user.profile.role == 'manager':
        assigned_queryset = task.project.group.participant.all()
    else:
        # Исполнитель может назначить только себя
        assigned_queryset = User.objects.filter(id=request.user.id)

    if request.method == 'POST':
        # Автор задачи может менять все поля
        if is_author:
            form = TaskForm(request.POST, instance=task)
            form.fields['assigned_to'].queryset = assigned_queryset
            if form.is_valid():
                form.save()
                return redirect('tasks:project_detail', pk=task.project.pk)
        # Исполнитель (не автор) может менять только статус
        else:
            # Принудительно сохраняем только статус, остальное игнорируем
            new_status = request.POST.get('status')
            valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
            if new_status in valid_statuses:
                task.status = new_status
                task.save()
            return redirect('tasks:project_detail', pk=task.project.pk)
    else:
        form = TaskForm(instance=task)
        form.fields['assigned_to'].queryset = assigned_queryset
        # Если это только исполнитель (не автор) — делаем все поля readonly, кроме статуса
        if is_executor and not is_author:
            for field_name, field in form.fields.items():
                if field_name != 'status':
                    field.widget.attrs['readonly'] = True
                    field.widget.attrs['disabled'] = True

    return render(request, 'tasks/task_form.html', {'form': form, 'object': task, 'project': task.project})


# Удаление задачи.
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Удалять может только автор задачи
    if task.created_by != request.user:
        raise Http404
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


# Выход.
def logout_view(request):
    logout(request)
    return redirect('tasks:login')

# Функциональный календарь
@login_required
def calendar_view(request):
    # Стартовая дата (из ?start=YYYY-MM-DD или сегодня)
    start_param = request.GET.get('start')
    try:
        start_date = date.fromisoformat(start_param) if start_param else date.today()
    except (ValueError, TypeError):
        start_date = date.today()

    # Сдвигаем к понедельнику (находим сколько дней нужно вычесть, чтобы получить понедельник)
    start_date = start_date - timedelta(days=start_date.weekday())
    # Сдвигаем к воскресенью (из найденного понедельника находим воскресенье прибавляя 6 дней)
    end_date = start_date + timedelta(days=6)

    # Доступ: та же логика, что и в project_list
    if request.user.profile.role == 'manager':
        tasks = Task.objects.filter(
            created_by=request.user,
            # только те задачи что "в работе"

            status='in_progress',
            due_date__gte=start_date,
            due_date__lte=end_date,
        ).select_related('project', 'assigned_to')
    else:
        user_groups = request.user.participant_groups.all()
        tasks = Task.objects.filter(
            project__group__in=user_groups,
            # только те задачи что "в работе"
            status='in_progress',
            due_date__gte=start_date,
            due_date__lte=end_date,
        ).select_related('project', 'assigned_to').distinct()

    # Получаем все задачи и раскидываем их в список с ключем в виде дня дедлайна
    by_day = defaultdict(list)
    for task in tasks:
        by_day[task.due_date].append(task)

    # Группируем по дням
    weekday_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                     'Пятница', 'Суббота', 'Воскресенье']
    today = date.today()

    days = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        days.append({
            'date': day,
            'name': weekday_names[i],
            'is_today': day == today,
            'tasks': by_day[day],
        })

    return render(request, 'calendar/calendar.html', {
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'prev_week': start_date - timedelta(days=7),
        'next_week': start_date + timedelta(days=7),
        'today': today,
    })