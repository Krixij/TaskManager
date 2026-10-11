from django import forms
from .models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'group']
        labels = {
            'name': 'Название проекта',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-field__input'}),
            'group': forms.Select(attrs={'class': 'form-field__input'}),

        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # !!Добавить сюда поле дедлайна!!
        fields = ['title', 'description', 'assigned_to', 'status']
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'assigned_to': 'Исполнитель',
            'status': 'Статус',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-field__input'}),
            'description': forms.Textarea(attrs={'class': 'form-field__input', 'rows': 4}),
            'assigned_to': forms.Select(attrs={'class': 'form-field__input'}),
            'status': forms.Select(attrs={'class': 'form-field__input'}),
        }