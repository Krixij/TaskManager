from django import forms
from django.contrib.auth.models import User

from .models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'group']
        labels = {
            'name': 'Название проекта',
            'description': 'Описание',
            'group': 'Группа',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-field__input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-field__input',
                'rows': 3,
                'placeholder': 'Краткое описание проекта (необязательно)',
            }),
            'group': forms.Select(attrs={'class': 'form-field__input'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'assigned_to']
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'status': 'Статус',
            'priority': 'Приоритет',
            'assigned_to': 'Исполнитель',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-field__input'}),
            'description': forms.Textarea(attrs={'class': 'form-field__input', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-field__input'}),
            'priority': forms.Select(attrs={'class': 'form-field__input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-field__input'}),
        }


class DateFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        label='Дата создания с',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False,
        label='Дата создания по',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        if date_from and date_to and date_from > date_to:
            self.add_error('date_to', 'Конечная дата не может быть раньше начальной.')
        return cleaned_data


class ProjectFilterForm(DateFilterForm):
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Название или описание проекта/задачи',
            'autocomplete': 'off',
        }),
    )
    status = forms.ChoiceField(
        required=False,
        label='Статус задачи в проекте',
        choices=[('', 'Все статусы')] + Task.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'select'}),
    )
    priority = forms.ChoiceField(
        required=False,
        label='Приоритет задачи',
        choices=[('', 'Все приоритеты')] + Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'select'}),
    )
    assigned_to = forms.ModelChoiceField(
        required=False,
        label='Исполнитель задачи',
        queryset=User.objects.none(),
        empty_label='Все исполнители',
        widget=forms.Select(attrs={'class': 'select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_from'].label = 'Дата создания проекта с'
        self.fields['date_to'].label = 'Дата создания проекта по'
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.order_fields(['search', 'status', 'priority', 'assigned_to', 'date_from', 'date_to'])


class TaskFilterForm(DateFilterForm):
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Название или описание задачи',
            'autocomplete': 'off',
        }),
    )
    status = forms.ChoiceField(
        required=False,
        label='Статус',
        choices=[('', 'Все статусы')] + Task.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'select'}),
    )
    priority = forms.ChoiceField(
        required=False,
        label='Приоритет',
        choices=[('', 'Все приоритеты')] + Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(['search', 'status', 'priority', 'date_from', 'date_to'])
