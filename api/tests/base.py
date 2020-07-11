from api.tests.TestCase import TestCase, PermissionUtilities

from rest_framework import status
from rest_framework.test import APIClient


class BaseCase(TestCase, PermissionUtilities):
    invalid_item = {}
    simple_valid_item = {}
    full_valid_item = {}

    route = '/api/'

    def setUp(self):
        self.client = APIClient()
        #self.create_users_with_permissions(Model)
        #self.items_list = []

        #for i in range(10):
        #    item = Model.objects.create(name=f'item{i+1}')
        #    self.items_list.append(item)

    def test_list_item(self)
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
            items = response.json()
            #for i, item in enumerate(items):
            #    expected_item = self.items_list[i]
            #    self.assertEqual(expected_item.field, item.get('field'))

    def test_create_item(self):
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
        with self.subTest('Fields must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            #self.assertIn('field', body)
            #self.assertSubstringIn('required', body.get('field'))

        response = self.client.post(f'{self.route}', data=self.invalid_item, format='json')
        with self.subTest('Fields must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            #self.assertIn('field', body)
            #self.assertSubstringIn('valid', body.get('field'))

        data = self.simple_valid_item
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('Model must created with only required fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            item = response.json()
            #self.assertEqual(data.get('field'), item.get('field'))

            #expected_items = len(self.items_list) + 1
            #db_items = Model.objects.count()
            #self.assertEqual(expected_items, db_items)
            
        data = self.full_valid_item
        response = self.client.post(f'{self.route}', data=data, format='json')
        with self.subTest('Model must be created with all fields', response=response):
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            item = response.json()
            #self.assertEqual(data.get('field'), item.get('field'))

            #expected_items = len(self.items_list) + 2
            #db_items = Model.objects.count()
            #self.assertEqual(expected_items, db_items)

    def test_list_one_item(self):
        pk = len(self.items_list) + 2

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
        with self.subTest('Must return the correct item', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            item = response.json()
            expected_item = self.items_list[pk-1]
            self.assertEqual(pk, item.get('id'))
            self.assertEqual(expected_item.id, item.get('id'))
            #self.assertEqual(expected_item.field, item.get('field'))

    def test_update_item(self):
        pk = len(self.items_list) + 2

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
        with self.subTest('Fields must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            #self.assertIn('field', body)
            #self.assertSubstringIn('required', body.get('field'))

        data = self.invalid_item
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Fields must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            #self.assertIn('field', body)
            #self.assertSubstringIn('valid', body.get('field'))

        data = self.full_valid_item
        response = self.client.put(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Model must be updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            item = response.json()
            expected_item = self.items_list[pk-1]
            self.assertEqual(pk, item.get('id'))
            self.assertEqual(expected_item.id, item.get('id'))
            #self.assertEqual(data.get('field'), item.get('field'))

    def test_partial_update_item(self):
        pk = len(self.items_list) + 2

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
        data = {'field': self.invalid_item.get('field')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Field must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            #self.assertIn('field', body)
            #self.assertSubstringIn('valid', body.get('field'))

        data = {'field': self.full_valid_item.get('field')}
        response = self.client.patch(f'{self.route}{pk}/', data=data, format='json')
        with self.subTest('Model must be partial updated', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            item = response.json()
            expected_item = self.items_list[pk-1]
            self.assertEqual(pk, item.get('id'))
            self.assertEqual(expected_item.id, item.get('id'))

            #self.assertEqual(data.get('field'), item.get('field'))
            #self.assertNotEqual(expected_item.field, item.get('field'))

    def test_delete_item(self):
        pk = len(self.items_list) + 2

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
        with self.subTest('Model must be deleted', response=response):
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            #total_items = len(self.items_list) - 1
            #db_items = Model.objects.count()
            #self.assertEqual(total_items, db_items)
            #self.assertRaises(Model.DoesNotExist, Model.objects.get, pk=pk)
