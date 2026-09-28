from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse

from labels.models import Label
from statuses.models import Status

from .models import Task


class TaskCrudTestCase(TransactionTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='author1', password='StrongPass1!'
        )
        self.user2 = User.objects.create_user(
            username='executor1', password='StrongPass2!'
        )
        self.status_new = Status.objects.create(name='новый')
        self.status_work = Status.objects.create(name='в работе')
        self.label_bug = Label.objects.create(name='bug')
        self.label_feature = Label.objects.create(name='feature')
        self.task = Task.objects.create(
            name='Задача автора',
            description='Описание задачи',
            status=self.status_new,
            author=self.user1,
            executor=self.user2,
        )
        self.task.labels.add(self.label_bug)

    def _auth(self, user=None):
        if user is None:
            user = self.user1
        self.client.login(username=user.username, password='StrongPass1!' if user == self.user1 else 'StrongPass2!')

    def test_list_requires_login(self):
        response = self.client.get(reverse('tasks_list'))
        self.assertRedirects(response, reverse('login'))

    def test_list_authenticated(self):
        self._auth()
        response = self.client.get(reverse('tasks_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Задачи')
        self.assertContains(response, 'Создать задачу')
        self.assertContains(response, self.task.name)
        self.assertContains(response, self.status_new.name)
        self.assertContains(response, 'Показать')
        self.assertContains(response, 'Изменить')
        self.assertContains(response, 'Удалить')

    def test_detail_requires_login(self):
        response = self.client.get(reverse('task_detail', kwargs={'pk': self.task.pk}))
        self.assertRedirects(response, reverse('login'))

    def test_detail_authenticated(self):
        self._auth()
        response = self.client.get(reverse('task_detail', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.name)
        self.assertContains(response, self.task.description)
        self.assertContains(response, self.status_new.name)
        self.assertContains(response, self.user1.username)
        self.assertContains(response, self.user2.username)
        self.assertContains(response, self.label_bug.name)

    def test_create_requires_login(self):
        response = self.client.get(reverse('task_create'))
        self.assertRedirects(response, reverse('login'))

    def test_create_form_labels(self):
        self._auth()
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        for label in ['Имя', 'Описание', 'Статус', 'Исполнитель', 'Метки', 'Создать']:
            self.assertContains(response, label)

    def test_create_success(self):
        self._auth()
        url = reverse('task_create')
        data = {
            'name': 'Новая задача curl',
            'description': 'Привет мир',
            'status': self.status_work.pk,
            'executor': self.user2.pk,
            'labels': [self.label_bug.pk, self.label_feature.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('tasks_list'))
        task = Task.objects.get(name='Новая задача curl')
        self.assertEqual(task.author, self.user1)
        self.assertEqual(task.status, self.status_work)
        self.assertEqual(task.executor, self.user2)
        self.assertEqual(set(task.labels.values_list('pk', flat=True)), {self.label_bug.pk, self.label_feature.pk})
        self.assertContains(response, 'Задача успешно создана')

    def test_create_duplicate_name(self):
        self._auth()
        url = reverse('task_create')
        data = {
            'name': self.task.name,
            'description': '',
            'status': self.status_new.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(name=self.task.name).count() > 1)
        text = response.content.decode('utf-8')
        self.assertTrue(
            'уже существует' in text or 'already exists' in text,
            msg='Ошибка уникальности имени задачи не найдена: ' + text,
        )

    def test_update_requires_login(self):
        response = self.client.get(reverse('task_update', kwargs={'pk': self.task.pk}))
        self.assertRedirects(response, reverse('login'))

    def test_update_success(self):
        self._auth()
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        data = {
            'name': 'Обновленная задача',
            'description': 'Новое описание',
            'status': self.status_work.pk,
            'executor': '',
            'labels': [self.label_feature.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('tasks_list'))
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Обновленная задача')
        self.assertEqual(self.task.status, self.status_work)
        self.assertIsNone(self.task.executor)
        self.assertEqual(list(self.task.labels.values_list('pk', flat=True)), [self.label_feature.pk])
        self.assertContains(response, 'Задача успешно изменена')

    def test_delete_requires_login(self):
        response = self.client.get(reverse('task_delete', kwargs={'pk': self.task.pk}))
        self.assertRedirects(response, reverse('login'))

    def test_delete_by_author_success(self):
        self._auth(self.user1)
        pk = self.task.pk
        response = self.client.post(reverse('task_delete', kwargs={'pk': pk}), follow=True)
        self.assertRedirects(response, reverse('tasks_list'))
        self.assertFalse(Task.objects.filter(pk=pk).exists())
        self.assertContains(response, 'Задача успешно удалена')

    def test_delete_by_non_author_forbidden(self):
        self._auth(self.user2)
        pk = self.task.pk
        response = self.client.post(reverse('task_delete', kwargs={'pk': pk}), follow=True)
        self.assertRedirects(response, reverse('tasks_list'))
        self.assertTrue(Task.objects.filter(pk=pk).exists())
        self.assertContains(response, 'Задачу может удалить только ее автор')

    def test_delete_page_has_confirm_button(self):
        self._auth(self.user1)
        response = self.client.get(reverse('task_delete', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Да, удалить')

    def test_form_fields_exist(self):
        self._auth()
        response = self.client.get(reverse('task_create'))
        html = response.content.decode('utf-8')
        self.assertIn('name="name"', html)
        self.assertIn('id="id_name"', html)
        self.assertIn('name="description"', html)
        self.assertIn('id="id_description"', html)
        self.assertIn('name="status"', html)
        self.assertIn('id="id_status"', html)
        self.assertIn('name="executor"', html)
        self.assertIn('id="id_executor"', html)
        self.assertIn('name="labels"', html)
        self.assertIn('id="id_labels"', html)


class UserStatusDeleteProtectionTestCase(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='StrongPass1!')
        self.status = Status.objects.create(name='новый')
        self.task = Task.objects.create(
            name='Незащищенная задача?',
            status=self.status,
            author=self.user,
        )

    def test_delete_user_with_task_protected(self):
        self.client.login(username='bob', password='StrongPass1!')
        response = self.client.post(
            reverse('user_delete', kwargs={'pk': self.user.pk}), follow=True
        )
        self.assertRedirects(response, reverse('users_list'))
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.assertContains(response, 'Невозможно удалить пользователя')

    def test_delete_status_with_task_protected(self):
        self.client.login(username='bob', password='StrongPass1!')
        response = self.client.post(
            reverse('status_delete', kwargs={'pk': self.status.pk}), follow=True
        )
        self.assertRedirects(response, reverse('statuses_list'))
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())
        self.assertContains(response, 'Невозможно удалить статус')
