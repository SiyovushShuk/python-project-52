from django.contrib.auth.models import User
from django.db import connection
from django.test import TransactionTestCase
from django.urls import reverse

from .models import Status


class StatusCrudTestCase(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', password='StrongPass123!'
        )
        self.status_new = Status.objects.create(name='новый')
        self.status_work = Status.objects.create(name='в работе')

    def _auth(self):
        self.client.login(username='tester', password='StrongPass123!')

    def test_list_requires_login(self):
        url = reverse('statuses_list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login'))

    def test_list_accessible_for_authenticated(self):
        self._auth()
        url = reverse('statuses_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Статусы')
        self.assertContains(response, 'новый')
        self.assertContains(response, 'в работе')
        self.assertContains(response, 'Создать статус')
        self.assertContains(response, 'Изменить')
        self.assertContains(response, 'Удалить')

    def test_create_page_requires_login(self):
        response = self.client.get(reverse('status_create'))
        self.assertRedirects(response, reverse('login'))

    def test_create_page_rendered(self):
        self._auth()
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Имя')
        self.assertContains(response, 'Создать')

    def test_create_success(self):
        self._auth()
        url = reverse('status_create')
        response = self.client.post(url, {'name': 'на тестировании'}, follow=True)
        self.assertRedirects(response, reverse('statuses_list'))
        self.assertTrue(Status.objects.filter(name='на тестировании').exists())
        self.assertContains(response, 'Статус успешно создан')

    def test_create_duplicate_name(self):
        self._auth()
        url = reverse('status_create')
        response = self.client.post(url, {'name': 'новый'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Status.objects.filter(name='новый').count() > 1)
        text = response.content.decode('utf-8')
        self.assertTrue(
            'уже существует' in text or 'already exists' in text,
            msg='Ошибка уникальности не найдена. Ответ: ' + text,
        )

    def test_update_page_requires_login(self):
        response = self.client.get(
            reverse('status_update', kwargs={'pk': self.status_new.pk})
        )
        self.assertRedirects(response, reverse('login'))

    def test_update_page_rendered(self):
        self._auth()
        url = reverse('status_update', kwargs={'pk': self.status_new.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Изменить')

    def test_update_success(self):
        self._auth()
        url = reverse('status_update', kwargs={'pk': self.status_new.pk})
        response = self.client.post(
            url, {'name': 'Новый обновленный'}, follow=True
        )
        self.assertRedirects(response, reverse('statuses_list'))
        self.status_new.refresh_from_db()
        self.assertEqual(self.status_new.name, 'Новый обновленный')
        self.assertContains(response, 'Статус успешно изменен')

    def test_update_duplicate_name(self):
        self._auth()
        url = reverse('status_update', kwargs={'pk': self.status_new.pk})
        response = self.client.post(url, {'name': 'в работе'})
        self.assertEqual(response.status_code, 200)
        self.status_new.refresh_from_db()
        self.assertNotEqual(self.status_new.name, 'в работе')
        text = response.content.decode('utf-8')
        self.assertTrue(
            'уже существует' in text or 'already exists' in text,
            msg='Ошибка уникальности не найдена. Ответ: ' + text,
        )

    def test_delete_page_requires_login(self):
        response = self.client.get(
            reverse('status_delete', kwargs={'pk': self.status_new.pk})
        )
        self.assertRedirects(response, reverse('login'))

    def test_delete_page_rendered(self):
        self._auth()
        url = reverse('status_delete', kwargs={'pk': self.status_new.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Да, удалить')

    def test_delete_success(self):
        self._auth()
        url = reverse('status_delete', kwargs={'pk': self.status_work.pk})
        pk = self.status_work.pk
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('statuses_list'))
        self.assertFalse(Status.objects.filter(pk=pk).exists())
        self.assertContains(response, 'Статус успешно удален')

    def test_delete_protected_by_task(self):
        from django.contrib.auth.models import User as U
        from tasks.models import Task
        from labels.models import Label

        tmp_user = U.objects.create_user(
            username='tmpuser_task_protection', password='Pass12345!'
        )
        task = Task.objects.create(
            name='tmp_protection_task',
            status=self.status_new,
            author=tmp_user,
        )
        try:
            self._auth()
            url = reverse('status_delete', kwargs={'pk': self.status_new.pk})
            response = self.client.post(url, follow=True)
            self.assertRedirects(response, reverse('statuses_list'))
            self.assertTrue(Status.objects.filter(pk=self.status_new.pk).exists())
            self.assertContains(response, 'Невозможно удалить статус')
        finally:
            task.delete()
            tmp_user.delete()

    def test_form_fields_name_and_id(self):
        self._auth()
        response = self.client.get(reverse('status_create'))
        html = response.content.decode('utf-8')
        self.assertIn('name="name"', html)
        self.assertIn('id="id_name"', html)
