from api.tests.TestCase import TestCase, PermissionUtilities

from rest_framework import status
from rest_framework.test import APIClient

from django.utils import timezone

from logs.models import User, Permission


class UserRouteCase(TestCase, PermissionUtilities):
    invalid_user = {
        'username': 'denis' + 'd' * 150,
        'email': 'denisemailcom',
        'password': '1234567890'
    }

    simple_valid_user = {
        'username': 'denise',
        'email': 'denise@email.com',
        'password': 'MYPASSWORD_myp455w0rd',
    }

    full_valid_user = {
        'username': 'denis',
        'email': 'denis@email.com',
        'password': 'MYPASSWORD_myp455w0rd',
        'first_name': 'Denis',
        'last_name': 'Lastname',
        'is_staff': True,
        'is_active': True,
        'is_superuser': True,
        'groups': [],
        'user_permissions': []
    }

    read_only_fields = ['id', 'last_login', 'date_joined']

    route = '/api/users/'

    def setUp(self):
        self.post_fields = list(self.full_valid_user.keys())
        self.post_fields.remove('password')

        self.client = APIClient()
        self.user_list = []
        for i in range(10):
            user = User.objects.create(username=f'user{i+1}', email=f'user{i+1}@email.com')
            user.set_password('mypassword')
            user.save()
            self.user_list.append(user)

        # Assign permission instead of calling create_users_with_permissions
        self.permission_users = {}
        for i, permission in enumerate(['view', 'add', 'change', 'delete']):
            user = User.objects.get(username=f'user{i+1}')
            codename = f'{permission}_{User._meta.model_name}'
            user.user_permissions.set([Permission.objects.get(codename=codename)])
            self.permission_users[permission] = {
                'username': user.username, 'password': 'mypassword'
            }

    def test_list_users(self):
        response = self.client.get(f'{self.route}')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.get(f'{self.route}')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='view')
        response = self.client.get(f'{self.route}')
        with self.subTest('Must return data and a success code', response=response):
            users = response.json()
            for i, user in enumerate(users):
                for field in self.read_only_fields + self.post_fields:
                    self.assertIn(field, user)

                expected_user = self.user_list[i]
                self.assertEqual(expected_user.email, user.get('email'))
                self.assertEqual(expected_user.username, user.get('username'))

    def test_create_user(self):
        response = self.client.post(f'{self.route}', data={}, format='json')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.post(f'{self.route}', data={}, format='json')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='add')
        response = self.client.post(f'{self.route}', data={}, format='json')
        with self.subTest('Username, email and password must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('required', body.get('username'))
            self.assertSubstringIn('required', body.get('email'))
            self.assertSubstringIn('required', body.get('password'))

        response = self.client.post(f'{self.route}', data=self.invalid_user, format='json')
        with self.subTest('User fields must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('Ensure', body.get('username'))
            self.assertSubstringIn('valid', body.get('email'))
            self.assertSubstringIn('common', body.get('password'))
            self.assertSubstringIn('numeric', body.get('password'))

        data = self.simple_valid_user
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('User must be created with only required fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            user = response.json()
            for field in self.read_only_fields + self.post_fields:
                self.assertIn(field, user)

            self.assertEqual(data.get('email'), user.get('email'))
            self.assertEqual(data.get('username'), user.get('username'))

            expected_users = len(self.user_list) + 1
            db_users = User.objects.count()
            self.assertEqual(expected_users, db_users)

        data = self.full_valid_user
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('User must be created with all fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            user = response.json()

            for field in self.read_only_fields:
                self.assertIn(field, user)

            for field in self.post_fields:
                self.assertEqual(data.get(field), user.get(field))

            expected_users = len(self.user_list) + 2
            db_users = User.objects.count()
            self.assertEqual(expected_users, db_users)

    def test_list_one_user(self):
        pk = len(self.user_list) + 5

        response = self.client.get(f'{self.route}{pk}/')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.get(f'{self.route}{pk}/')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='view')
        response = self.client.get(f'{self.route}{pk}/')

        with self.subTest('List must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        response = self.client.get(f'{self.route}{pk}/')
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

        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='change')
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Username, email and password must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertIn('password', body)
            self.assertIn('username', body)
            self.assertSubstringIn('required', body.get('username'))
            self.assertSubstringIn('required', body.get('email'))
            self.assertSubstringIn('required', body.get('password'))

        response = self.client.put(f'{self.route}{pk}/', data=self.invalid_user, format='json')
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

        data = dict(self.simple_valid_user)
        data['last_login'] = timezone.now()
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')

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

        response = self.client.patch(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.patch(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='change')
        response = self.client.patch(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        data = {'username': self.invalid_user.get('username')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Username must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('username', body)
            self.assertSubstringIn('Ensure', body.get('username'))

        data = {'email': self.invalid_user.get('email')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Email must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertSubstringIn('valid', body.get('email'))

        data = {'password': self.invalid_user.get('password')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Password must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('password', body)
            self.assertSubstringIn('numeric', body.get('password'))
            self.assertSubstringIn('common', body.get('password'))

        data = {'last_login': timezone.now()}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Last login must not been changed', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user = response.json()
            expected_user = self.user_list[pk-1]
            self.assertEqual(pk, user.get('id'))
            self.assertEqual(expected_user.id, user.get('id'))
            self.assertEqual(expected_user.last_login, user.get('last_login'))
            self.assertNotEqual(data.get('last_login'), user.get('last_login'))

        data = {'first_name': self.full_valid_user.get('first_name')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
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

        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('Must return Unauthorized', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        self.login(permission='add')
        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('Must return Forbidden', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.login(permission='delete')
        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('Delete must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 5
        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('User must be deleted', response=response):
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            total_users = len(self.user_list) - 1
            db_users = User.objects.count()
            self.assertEqual(total_users, db_users)
            self.assertRaises(User.DoesNotExist, User.objects.get, pk=5)
