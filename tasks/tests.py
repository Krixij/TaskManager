from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import GroupPeople, Project, Task


class SearchAndFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test-user', password='test-password')
        self.other_user = User.objects.create_user(username='other-user', password='test-password')
        self.group = GroupPeople.objects.create(title='Команда', created_by=self.user)
        self.group.participant.add(self.user)
        self.project = Project.objects.create(
            name='Учебный проект',
            description='Подготовка документации',
            created_by=self.user,
            group=self.group,
        )
        self.task = Task.objects.create(
            title='Настроить поиск',
            description='Добавить фильтрацию по приоритету',
            status='in_progress',
            priority='high',
            project=self.project,
            assigned_to=self.user,
            created_by=self.user,
        )
        self.client.login(username='test-user', password='test-password')

    def test_project_search_finds_project_description(self):
        response = self.client.get('/', {'search': 'документации'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Учебный проект')

    def test_project_filters_by_related_task_priority_and_assignee(self):
        response = self.client.get('/', {
            'priority': 'high',
            'assigned_to': str(self.user.pk),
            'status': 'in_progress',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Учебный проект')

    def test_my_tasks_searches_title_and_description(self):
        response = self.client.get('/my-tasks/', {'search': 'приоритету'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Настроить поиск')

    def test_my_tasks_filters_by_priority(self):
        response = self.client.get('/my-tasks/', {'priority': 'low'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Настроить поиск')

    def test_my_tasks_only_shows_tasks_assigned_to_current_user(self):
        other_project = Project.objects.create(name='Другой проект', created_by=self.user, group=self.group)
        Task.objects.create(
            title='Чужая задача',
            project=other_project,
            assigned_to=self.other_user,
            created_by=self.user,
        )
        response = self.client.get('/my-tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Чужая задача')
