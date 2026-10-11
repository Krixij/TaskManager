from collections import defaultdict

from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import Http404
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from datetime import date, timedelta


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
    # Руководитель видит только созданные им проекты
    if request.user.profile.role == 'manager':
        projects = Project.objects.filter(created_by=request.user)
    # Исполнитель видит проекты групп, в которых состоит
    else:
        user_groups = request.user.participant_groups.all()
        projects = Project.objects.filter(group__in=user_groups)
    return render(request, 'projects/project_list.html', {'object_list': projects})

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

    tasks = project.tasks.all()
    return render(request, 'projects/project_detail.html', {'project': project, 'tasks': tasks})


# Создание проекта (с формой)
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


# Редактирование проекта (с формой)
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
    role = request.user.profile.role

    # Руководитель может создавать задачи только в своих проектах
    if role == 'manager':
        if project.created_by != request.user:
            raise Http404
        # Руководитель назначает исполнителя из участников группы проекта
        assigned_queryset = project.group.participant.all()
    # Исполнитель может создавать задачи только в проектах своих групп и только для себя
    else:
        if not project.group.participant.filter(id=request.user.id).exists():
            raise Http404
        assigned_queryset = User.objects.filter(id=request.user.id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        # Ограничиваем выбор исполнителя
        form.fields['assigned_to'].queryset = assigned_queryset
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = TaskForm()
        # Ограничиваем выбор исполнителя только участниками проекта
        form.fields['assigned_to'].queryset = assigned_queryset

    return render(request, 'tasks/task_form.html', {'form': form, 'project': project})


# Редактирование задачи (с формой)
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


# Удаление задачи
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
    return render(request, 'tasks/task_confirm_delete.html', {'object': task})


# Выход
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