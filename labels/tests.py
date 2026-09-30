from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse

from .models import Label


class LabelCrudTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='tester_labels', password='StrongPass123!'
        )
        self.label_bug = Label.objects.create(name='bug')
        self.label_feature = Label.objects.create(name='feature')

    def _auth(self) -> None:
        self.client.login(
            username='tester_labels', password='StrongPass123!'
        )

    def test_list_requires_login(self) -> None:
        url = reverse('labels_list')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login'))

    def test_list_accessible_for_authenticated(self) -> None:
        self._auth()
        url = reverse('labels_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Метки')
        self.assertContains(response, 'bug')
        self.assertContains(response, 'feature')
        self.assertContains(response, 'Создать метку')
        self.assertContains(response, 'Изменить')
        self.assertContains(response, 'Удалить')

    def test_create_page_requires_login(self) -> None:
        response = self.client.get(reverse('label_create'))
        self.assertRedirects(response, reverse('login'))

    def test_create_page_rendered(self) -> None:
        self._auth()
        response = self.client.get(reverse('label_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Имя')
        self.assertContains(response, 'Создать')

    def test_create_success(self) -> None:
        self._auth()
        url = reverse('label_create')
        response = self.client.post(url, {'name': 'critical'}, follow=True)
        self.assertRedirects(response, reverse('labels_list'))
        self.assertTrue(Label.objects.filter(name='critical').exists())
        self.assertContains(response, 'Метка успешно создана')

    def test_create_duplicate_name(self) -> None:
        self._auth()
        url = reverse('label_create')
        response = self.client.post(url, {'name': 'bug'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Label.objects.filter(name='bug').count() > 1)
        text = response.content.decode('utf-8')
        self.assertTrue(
            'уже существует' in text or 'already exists' in text,
            msg='Ошибка уникальности не найдена. Ответ: ' + text,
        )

    def test_update_page_requires_login(self) -> None:
        response = self.client.get(
            reverse('label_update', kwargs={'pk': self.label_bug.pk})
        )
        self.assertRedirects(response, reverse('login'))

    def test_update_page_rendered(self) -> None:
        self._auth()
        url = reverse('label_update', kwargs={'pk': self.label_bug.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Изменить')

    def test_update_success(self) -> None:
        self._auth()
        url = reverse('label_update', kwargs={'pk': self.label_bug.pk})
        response = self.client.post(url, {'name': 'БАГ'}, follow=True)
        self.assertRedirects(response, reverse('labels_list'))
        self.label_bug.refresh_from_db()
        self.assertEqual(self.label_bug.name, 'БАГ')
        self.assertContains(response, 'Метка успешно изменена')

    def test_update_duplicate_name(self) -> None:
        self._auth()
        url = reverse('label_update', kwargs={'pk': self.label_bug.pk})
        response = self.client.post(url, {'name': 'feature'})
        self.assertEqual(response.status_code, 200)
        self.label_bug.refresh_from_db()
        self.assertNotEqual(self.label_bug.name, 'feature')
        text = response.content.decode('utf-8')
        self.assertTrue(
            'уже существует' in text or 'already exists' in text,
            msg='Ошибка уникальности не найдена. Ответ: ' + text,
        )

    def test_delete_page_requires_login(self) -> None:
        response = self.client.get(
            reverse('label_delete', kwargs={'pk': self.label_bug.pk})
        )
        self.assertRedirects(response, reverse('login'))

    def test_delete_page_rendered(self) -> None:
        self._auth()
        url = reverse('label_delete', kwargs={'pk': self.label_bug.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Да, удалить')

    def test_delete_success(self) -> None:
        self._auth()
        url = reverse('label_delete', kwargs={'pk': self.label_feature.pk})
        pk = self.label_feature.pk
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('labels_list'))
        self.assertFalse(Label.objects.filter(pk=pk).exists())
        self.assertContains(response, 'Метка успешно удалена')

    def test_delete_protected_by_task(self) -> None:
        from statuses.models import Status
        from tasks.models import Task as T

        tmp_user = User.objects.create_user(
            username='tmp_label_protect', password='Pass12345!'
        )
        tmp_status = Status.objects.create(name='tmpstatus4label')
        task = T.objects.create(
            name='tmp_task_label_protect',
            status=tmp_status,
            author=tmp_user,
        )
        task.labels.add(self.label_bug)
        try:
            self._auth()
            url = reverse('label_delete', kwargs={'pk': self.label_bug.pk})
            response = self.client.post(url, follow=True)
            self.assertRedirects(response, reverse('labels_list'))
            self.assertTrue(
                Label.objects.filter(pk=self.label_bug.pk).exists()
            )
            self.assertContains(response, 'Невозможно удалить метку')
        finally:
            task.delete()
            tmp_status.delete()
            tmp_user.delete()

    def test_form_fields_name_and_id(self) -> None:
        self._auth()
        response = self.client.get(reverse('label_create'))
        html = response.content.decode('utf-8')
        self.assertIn('name="name"', html)
        self.assertIn('id="id_name"', html)
