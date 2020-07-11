from api.tests.TestCase import TestCase, PermissionUtilities

from rest_framework import status
from rest_framework.test import APIClient

from logs.models import Permission

class PermissionRouteCase(TestCase, PermissionUtilities):
    route = '/api/permissions/'

    def setUp(self):
        self.client = APIClient()
        self.create_users_with_permissions(Permission)
        self.permissions_list = [p for p in Permission.objects.all()]

    def test_list_permission(self):
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
            permissions = response.json()
            for i, permission in enumerate(permissions):
                expected_permission = self.permissions_list[i]
                self.assertEqual(expected_permission.name, permission.get('name'))
                self.assertEqual(expected_permission.codename, permission.get('codename'))

    def test_create_permission(self):
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
        with self.subTest('Update must return method not allowed', response=response):
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            self.assertIn('detail', response.json())
            self.assertIn('not allowed', response.json().get('detail').lower())

    def test_list_one_permission(self):
        pk = len(self.permissions_list) + 2

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

        pk = 2

        response = self.client.get(f'{self.route}{pk}/')
        with self.subTest('Must return the correct permission', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            permission = response.json()
            expected_permission = self.permissions_list[pk-1]
            self.assertEqual(pk, permission.get('id'))
            self.assertEqual(expected_permission.id, permission.get('id'))
            self.assertEqual(expected_permission.name, permission.get('name'))
            self.assertEqual(expected_permission.codename, permission.get('codename'))

    def test_update_permission(self):
        pk = len(self.permissions_list) + 2

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
        with self.subTest('Update must return method not allowed', response=response):
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            self.assertIn('detail', response.json())
            self.assertIn('not allowed', response.json().get('detail').lower())

    def test_partial_update_permission(self):
        pk = len(self.permissions_list) + 2

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
        with self.subTest('Partial update must return method not allowed', response=response):
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            self.assertIn('detail', response.json())
            self.assertIn('not allowed', response.json().get('detail').lower())

    def test_delete_permission(self):
        pk = len(self.permissions_list) + 2

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
        with self.subTest('Delete must return method not allowed', response=response):
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
            self.assertIn('detail', response.json())
            self.assertIn('not allowed', response.json().get('detail').lower())
