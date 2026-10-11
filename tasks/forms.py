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
        fields = ['title', 'description', 'assigned_to', 'status', "due_date", "priority"]
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'assigned_to': 'Исполнитель',
            'status': 'Статус',
            'due_date': 'Срок выполнения',
            "priority": "Приоритет",
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-field__input'}),
            'description': forms.Textarea(attrs={'class': 'form-field__input', 'rows': 4}),
            'assigned_to': forms.Select(attrs={'style': 'max-width: 300px;', 'class': 'form-field__input'}),
            'status': forms.Select(attrs={'style': 'max-width: 200px;', 'class': 'form-field__input'}),
            'priority': forms.Select(attrs={'style': 'max-width: 200px;', 'class': 'form-field__input'}),
            'due_date': forms.DateInput(
                attrs={'class': 'form-field__input', 'type': 'date', 'style': 'max-width: 200px;',
},
                format='%Y-%m-%d',
            ),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['due_date'].input_formats = ['%Y-%m-%d']