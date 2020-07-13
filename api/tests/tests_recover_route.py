from django.test import override_settings
from api.tests.TestCase import TestCase, PermissionUtilities

from django.core import mail

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from logs.models import User
from api.email_templates import subject

@override_settings(DEBUG=False)
class RecoverRouteCase(TestCase, PermissionUtilities):
    invalid_form = {'email': 'invalid_email'}
    valid_non_user = {'email': 'some_permission@email.com'}
    simple_valid_form = {'email': 'view@email.com'}
    full_valid_form = {
        'email': 'view@email.com',
        'link': 'www.centralerros.com.br/reset-password'
    }

    route = '/api/recover/'

    def setUp(self):
        self.client = APIClient()
        self.create_users_with_permissions(User)

    def test_list_method_not_allowed(self):
        response = self.client.get(self.route)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertIn('detail', response.json())
        self.assertIn('not allowed', response.json().get('detail').lower())

    def test_single_resource_not_found(self):
        response = self.client.get(f'{self.route}{2}/')
        with self.subTest('List must return method not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('error', response.json())
            self.assertIn('not found', response.json().get('error').lower())

        response = self.client.put(f'{self.route}{2}/')
        with self.subTest('Update must return method not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('error', response.json())
            self.assertIn('not found', response.json().get('error').lower())

        response = self.client.patch(f'{self.route}{2}/')
        with self.subTest('Partial update must return method not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('error', response.json())
            self.assertIn('not found', response.json().get('error').lower())

        response = self.client.delete(f'{self.route}{2}/')
        with self.subTest('Delete must return method not found', response=response):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('error', response.json())
            self.assertIn('not found', response.json().get('error').lower())

    def test_non_user_recover_form(self):
        response = self.client.post(self.route, data={}, format='json')
        with self.subTest('Email must be required', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertSubstringIn('required', body.get('email'))

        response = self.client.post(self.route, data=self.invalid_form, format='json')
        with self.subTest('Email must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('email', body)
            self.assertSubstringIn('valid', body.get('email'))

        data = self.valid_non_user
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('Must return success but email will no be sent', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('sent', body.get('detail'))

            self.assertEqual(len(mail.outbox), 0)

    def test_valid_recover(self):
        data = self.simple_valid_form
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('Must return success and link redirects to api', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('sent', body.get('detail'))

            self.assertEqual(len(mail.outbox), 1)
            sended = mail.outbox[-1]
            self.assertEqual(sended.subject, subject)
            self.assertIn(data.get('email'), sended.to)
            self.assertIn(data.get('email'), sended.body)
            self.assertIn(reverse('reset-password'), sended.body)

        data = self.full_valid_form
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('Must return success and link redirects to link', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('sent', body.get('detail'))

            self.assertEqual(len(mail.outbox), 2)
            sended = mail.outbox[-1]
            self.assertEqual(sended.subject, subject)
            self.assertIn(data.get('email'), sended.to)
            self.assertIn(data.get('email'), sended.body)
            self.assertIn(data.get('link'), sended.body)
