from api.tests.TestCase import TestCase, PermissionUtilities

from rest_framework import status
from rest_framework.test import APIClient

from logs.models import Group, Permission


class GroupRouteCase(TestCase, PermissionUtilities):
    invalid_group = {
        'name': 'group' + 'g' * 150
    }

    simple_valid_group = {
        'name': 'simple group'
    }

    full_valid_group = {
        'name': 'view all resources',
        # permissions declared in setUp 
    }

    route = '/api/groups/'

    def setUp(self):
        self.client = APIClient()
        self.create_users_with_permissions(Group)
        self.groups_list = []

        for i in range(10):
            group = Group.objects.create(name=f'group{i+1}')
            self.groups_list.append(group)

        self.full_valid_group['permissions'] = [
            p.id for p in Permission.objects.filter(codename__contains='view')
        ]

    def test_list_group(self):
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
            groups = response.json()
            for i, group in enumerate(groups):
                expected_group = self.groups_list[i]
                self.assertEqual(expected_group.name, group.get('name'))
                expected_group_permissions = [p.id for p in expected_group.permissions.all()]
                self.assertEqual(expected_group_permissions, group.get('permissions'))

    def test_create_group(self):
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
        with self.subTest('Name must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertSubstringIn('required', body.get('name'))

        response = self.client.post(f'{self.route}', data=self.invalid_group, format='json')
        with self.subTest('Name must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertSubstringIn('Ensure', body.get('name'))

        data = self.simple_valid_group
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('Group must created with only required fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            group = response.json()
            self.assertEqual(data.get('name'), group.get('name'))

            expected_groups = len(self.groups_list) + 1
            db_groups = Group.objects.count()
            self.assertEqual(expected_groups, db_groups)
            
        data = self.full_valid_group
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('Group must be created with all fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            group = response.json()
            self.assertEqual(data.get('name'), group.get('name'))

            expected_groups = len(self.groups_list) + 2
            db_groups = Group.objects.count()
            self.assertEqual(expected_groups, db_groups)

    def test_list_one_group(self):
        pk = len(self.groups_list) + 2

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
        with self.subTest('Must return the correct group', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            group = response.json()
            expected_group = self.groups_list[pk-1]
            self.assertEqual(pk, group.get('id'))
            self.assertEqual(expected_group.id, group.get('id'))
            self.assertEqual(expected_group.name, group.get('name'))

    def test_update_group(self):
        pk = len(self.groups_list) + 2

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

        pk = 2
        response = self.client.put(f'{self.route}{pk}/', data={}, format='json')
        with self.subTest('Name must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertSubstringIn('required', body.get('name'))

        data = self.invalid_group
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Name must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertSubstringIn('Ensure', body.get('name'))

        data = self.full_valid_group
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Group must be updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            group = response.json()
            expected_group = self.groups_list[pk-1]
            self.assertEqual(pk, group.get('id'))
            self.assertEqual(expected_group.id, group.get('id'))
            self.assertEqual(data.get('name'), group.get('name'))
            self.assertEqual(data.get('permissions'), group.get('permissions'))

            self.assertNotEqual(expected_group.name, group.get('name'))

    def test_partial_update_group(self):
        pk = len(self.groups_list) + 2

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
        with self.subTest('Partial update must return not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('detail', response.json())
            self.assertIn('not found', response.json().get('detail').lower())

        pk = 2
        data = {'name': self.invalid_group.get('name')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Field must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('name', body)
            self.assertSubstringIn('Ensure', body.get('name'))

        data = {'name': self.full_valid_group.get('name')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Group must be partial updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            group = response.json()
            expected_group = self.groups_list[pk-1]
            self.assertEqual(pk, group.get('id'))
            self.assertEqual(expected_group.id, group.get('id'))

            self.assertEqual(data.get('name'), group.get('name'))
            self.assertNotEqual(expected_group.name, group.get('name'))

    def test_delete_group(self):
        pk = len(self.groups_list) + 2

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

        pk = 2
        response = self.client.delete(f'{self.route}{pk}/')
        with self.subTest('Group must be deleted', response=response):
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            total_groups = len(self.groups_list) - 1
            db_groups = Group.objects.count()
            self.assertEqual(total_groups, db_groups)
            self.assertRaises(Group.DoesNotExist, Group.objects.get, pk=pk)
