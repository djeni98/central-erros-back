from django.test import TestCase
from django.test.testcases import safe_repr

from rest_framework import status
from rest_framework.test import APIClient

from datetime import datetime, timezone, timedelta

from api.models import User


class UserRouteCase(TestCase):
    valid_name = 'denis'
    valid_username = 'denis'
    valid_email = 'denis@email.com'
    valid_password = 'MYPASSWORD_myp455w0rd'

    invalid_username = 'denis' + 'd' * 150
    invalid_email = 'denisemail'
    invalid_password = '1234567890'

    def assertSubstringIn(self, substring, container, msg=None):
        result = any(substring in item for item in container)
        if not result:
            msg = self._formatMessage(
                msg, f'{substring} is not substring in {safe_repr(container)}'
            )
            self.fail(msg)

    def setUp(self):
        self.client = APIClient()
        self.user_list = []
        for i in range(10):
            user = User.objects.create(username=f'user{i+1}', email=f'user{i+1}@email.com')
            user.set_password('mypassword')
            user.save()
            self.user_list.append(user)

    def test_list_users(self):
        response = self.client.get('/api/users/')
        users = response.json()

        for i, user in enumerate(users):
            expected_user = self.user_list[i]
            self.assertEqual(expected_user.email, user.get('email'))
            self.assertEqual(expected_user.username, user.get('username'))

    def test_create_user(self):
        data = {'first_name': self.valid_name}
        response = self.client.post('/api/users/', data=data, format='json')

        with self.subTest('Username, email and password must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('required', body.get('username'))
            self.assertSubstringIn('required', body.get('email'))
            self.assertSubstringIn('required', body.get('password'))

        data = {
            'username': self.invalid_username,
            'email': self.invalid_email,
            'password': self.invalid_password
        }
        response = self.client.post('/api/users/', data=data, format='json')

        with self.subTest('Username, email and password must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('Ensure', body.get('username'))
            self.assertSubstringIn('valid', body.get('email'))
            self.assertSubstringIn('common', body.get('password'))
            self.assertSubstringIn('numeric', body.get('password'))

        data = {
            'username': self.valid_username,
            'email': self.valid_email,
            'password': self.valid_password
        }
        response = self.client.post('/api/users/', data=data, format='json')

        with self.subTest('User must be created', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            user = response.json()
            self.assertIn('date_joined', user)
            self.assertEqual(data.get('email'), user.get('email'))
            self.assertEqual(data.get('username'), user.get('username'))
            self.assertIsNone(user.get('last_login'))

            expected_users = len(self.user_list) + 1
            db_users = User.objects.count()
            self.assertEqual(expected_users, db_users)

    def test_list_one_user(self):
        pk = len(self.user_list) + 5
        response = self.client.get(f'/api/users/{pk}/')

        with self.subTest('List must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        response = self.client.get(f'/api/users/{pk}/')
        with self.subTest('Must return the correct user', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            expected_user = self.user_list[pk-1]
            self.assertEqual(pk, user.get('id'))
            self.assertEqual(expected_user.id, user.get('id'))
            self.assertEqual(expected_user.email, user.get('email'))
            self.assertEqual(expected_user.username, user.get('username'))

    def test_update_user(self):
        pk = len(self.user_list) + 5
        data = {}
        response = self.client.put(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        data = {'first_name': self.valid_name}
        response = self.client.put(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Username, email and password must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('required', body.get('username'))
            self.assertSubstringIn('required', body.get('email'))
            self.assertSubstringIn('required', body.get('password'))

        data = {
            'username': self.invalid_username,
            'email': self.invalid_email,
            'password': self.invalid_password
        }
        response = self.client.put(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Username, email and password must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('Ensure', body.get('username'))
            self.assertSubstringIn('valid', body.get('email'))
            self.assertSubstringIn('common', body.get('password'))
            self.assertSubstringIn('numeric', body.get('password'))

        data = {
            'username': self.valid_username,
            'email': self.valid_email,
            'password': self.valid_password,
            'last_login': datetime.now(timezone(timedelta(hours=-3)))
        }
        response = self.client.put(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('User must be updated and last_login must not change', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            expected_user = self.user_list[pk-1]
            self.assertEqual(pk, user.get('id'))
            self.assertEqual(expected_user.id, user.get('id'))
            self.assertEqual(data.get('email'), user.get('email'))
            self.assertEqual(data.get('username'), user.get('username'))
            self.assertNotEqual(expected_user.email, user.get('email'))
            self.assertNotEqual(expected_user.username, user.get('username'))
            self.assertEqual(expected_user.last_login, user.get('last_login'))

    def test_partial_update_user(self):
        pk = len(self.user_list) + 5
        data = {'email': self.valid_email}
        response = self.client.patch(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        data = {'username': self.invalid_username}
        response = self.client.patch(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Username must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('username', body)
            self.assertSubstringIn('Ensure', body.get('username'))

        data = {'email': self.invalid_email}
        response = self.client.patch(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Email must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertSubstringIn('valid', body.get('email'))

        data = {'password': self.invalid_password}
        response = self.client.patch(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Password must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('password', body)
            self.assertSubstringIn('numeric', body.get('password'))
            self.assertSubstringIn('common', body.get('password'))

        data = {'last_login': datetime.now(timezone(timedelta(hours=-3)))}
        response = self.client.patch(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('Last login must not been changed', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            expected_user = self.user_list[pk-1]
            self.assertEqual(pk, user.get('id'))
            self.assertEqual(expected_user.id, user.get('id'))
            self.assertEqual(expected_user.last_login, user.get('last_login'))
            self.assertNotEqual(data.get('last_login'), user.get('last_login'))

        data = {'first_name': self.valid_name}
        response = self.client.patch(f'/api/users/{pk}/', data=data, format='json')

        with self.subTest('User must be partial updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            expected_user = self.user_list[pk-1]
            self.assertEqual(pk, user.get('id'))
            self.assertEqual(expected_user.id, user.get('id'))
            self.assertEqual(data.get('first_name'), user.get('first_name'))
            self.assertNotEqual(expected_user.first_name, user.get('first_name'))

    def test_delete_user(self):
        pk = len(self.user_list) + 5
        response = self.client.delete(f'/api/users/{pk}/')

        with self.subTest('Delete must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        response = self.client.delete(f'/api/users/{pk}/')

        with self.subTest('User must be deleted', response=response):
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            total_users = len(self.user_list) - 1
            db_users = User.objects.count()
            self.assertEqual(total_users, db_users)
            self.assertRaises(User.DoesNotExist, User.objects.get, pk=5)
