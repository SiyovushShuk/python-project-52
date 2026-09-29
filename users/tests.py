from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class UserViewsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='StrongPass123!',
            first_name='Иван',
            last_name='Иванов',
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='StrongPass456!',
            first_name='Петр',
            last_name='Петров',
        )

    def test_users_list_accessible_without_auth(self):
        url = reverse('users_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user1')
        self.assertContains(response, 'user2')

    def test_register_page(self):
        url = reverse('user_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Имя')
        self.assertContains(response, 'Фамилия')
        self.assertContains(response, 'Имя пользователя')
        self.assertContains(response, 'Пароль')
        self.assertContains(response, 'Подтверждение')
        self.assertContains(response, 'Зарегистрировать')

    def test_register_success(self):
        url = reverse('user_create')
        data = {
            'first_name': 'Сидор',
            'last_name': 'Сидоров',
            'username': 'sidor',
            'password1': 'NewStrongPass789!',
            'password2': 'NewStrongPass789!',
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='sidor').exists())
        self.assertContains(response, 'Пользователь успешно зарегистрирован')

    def test_register_duplicate_username(self):
        url = reverse('user_create')
        data = {
            'first_name': 'Иван',
            'last_name': 'Другой',
            'username': 'user1',
            'password1': 'StrongPass111!',
            'password2': 'StrongPass111!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(first_name='Иван', last_name='Другой').exists())
        text = response.content.decode('utf-8')
        self.assertTrue(
            'уже существует' in text or 'already exists' in text or 'exists' in text,
            msg="Ошибка уникальности username не найдена. Ответ: " + text,
        )

    def test_login_page(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Имя пользователя')
        self.assertContains(response, 'Пароль')
        self.assertContains(response, 'Войти')

    def test_login_success(self):
        url = reverse('login')
        data = {
            'username': 'user1',
            'password': 'StrongPass123!',
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, 'Вы вошли')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user1.pk)

    def test_logout_success(self):
        self.client.login(username='user1', password='StrongPass123!')
        url = reverse('logout')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, 'Вы вышли')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_update_self_page(self):
        self.client.login(username='user1', password='StrongPass123!')
        url = reverse('user_update', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Изменить')

    def test_update_other_forbidden(self):
        self.client.login(username='user2', password='StrongPass456!')
        url = reverse('user_update', kwargs={'pk': self.user1.pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users_list'))
        self.assertContains(response, 'У вас нет прав для изменения')

    def test_update_unauthenticated_redirect(self):
        url = reverse('user_update', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login'))

    def test_update_success(self):
        self.client.login(username='user1', password='StrongPass123!')
        url = reverse('user_update', kwargs={'pk': self.user1.pk})
        data = {
            'first_name': 'ИванUpdated',
            'last_name': 'ИвановUpdated',
            'username': 'user1',
            'password1': '',
            'password2': '',
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('users_list'))
        self.assertContains(response, 'Пользователь успешно изменён')
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'ИванUpdated')
        self.assertEqual(self.user1.last_name, 'ИвановUpdated')

    def test_delete_self_page(self):
        self.client.login(username='user1', password='StrongPass123!')
        url = reverse('user_delete', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Да, удалить')

    def test_delete_other_forbidden(self):
        self.client.login(username='user2', password='StrongPass456!')
        url = reverse('user_delete', kwargs={'pk': self.user1.pk})
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('users_list'))
        self.assertContains(response, 'У вас нет прав для изменения')

    def test_delete_success(self):
        self.client.login(username='user1', password='StrongPass123!')
        url = reverse('user_delete', kwargs={'pk': self.user1.pk})
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('users_list'))
        self.assertContains(response, 'Пользователь успешно удалён')
        self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())

    def test_users_list_has_action_links(self):
        url = reverse('users_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Изменить')
        self.assertContains(response, 'Удалить')
