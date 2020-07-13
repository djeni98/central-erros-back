from api.tests.TestCase import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from rest_framework_simplejwt.tokens import AccessToken

from logs.models import User


class ResetRouteCase(TestCase):
    invalid_token = 'invalid_token'

    non_matching_user = {
        'username': 'non_matching',
        'password': 'MYPASSWORD_myp455w0rd'
    }

    invalid_form = {
        'username': 'valid',
        'password': '1234567890'
    }

    valid_form = {
        'username': 'valid',
        'password': 'MYPASSWORD_myp455w0rd'
    }

    previous_password = 'previous_password'

    route = '/api/reset/'

    def set_authorization_header(self):
        user = User.objects.get(username='valid')
        token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

    def setUp(self):
        self.client = APIClient()
        user = User.objects.create(username='valid', email='valid@email.com')
        user.set_password(self.previous_password)
        user.save()

    def tests_invalid_auth(self):
        response = self.client.post(self.route, data={}, format='json')
        with self.subTest('Must return Unauthorized, token not provided', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('authentication', body.get('detail').lower())

        query = '?token=' + self.invalid_token

        response = self.client.post(f'{self.route}{query}', data={}, format='json')
        with self.subTest('Must return Unauthorized, invalid token', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('not valid', body.get('detail').lower())

        query = '?token=' + str(AccessToken.for_user(User.objects.get(username='valid')))

        data = self.non_matching_user
        response = self.client.post(f'{self.route}{query}', data=data, format='json')
        with self.subTest('Must return Forbidden, user and username does not match', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.invalid_token)

        response = self.client.post(self.route, data={}, format='json')
        with self.subTest('Must return Unauthorized, invalid token', response=response):
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('not valid', body.get('detail').lower())

        self.set_authorization_header()

        data = self.non_matching_user
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('Must return Forbidden, user and username does not match', response=response):
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('permission', body.get('detail').lower())

    def tests_valid_header_auth(self):
        self.set_authorization_header()

        data = self.invalid_form
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('Password must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('password', body)
            self.assertSubstringIn('common', body.get('password'))
            self.assertSubstringIn('numeric', body.get('password'))

        data = self.valid_form
        response = self.client.post(self.route, data=data, format='json')
        with self.subTest('Must return ok, password must be changed', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('change', body.get('detail'))

            user = User.objects.get(username=data.get('username'))
            self.assertTrue(user.check_password(data.get('password')))
            self.assertFalse(user.check_password(self.previous_password))

    def tests_valid_query_auth(self):
        token = AccessToken.for_user(User.objects.get(username='valid'))
        query = '?token=' + str(token)

        data = self.invalid_form
        response = self.client.post(f'{self.route}{query}', data=data, format='json')
        with self.subTest('Password must be valid', response=response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            body = response.json()
            self.assertIn('password', body)
            self.assertSubstringIn('common', body.get('password'))
            self.assertSubstringIn('numeric', body.get('password'))

        data = self.valid_form
        response = self.client.post(f'{self.route}{query}', data=data, format='json')
        with self.subTest('Must return ok, password must be changed', response=response):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            body = response.json()
            self.assertIn('detail', body)
            self.assertIn('change', body.get('detail'))

            user = User.objects.get(username=data.get('username'))
            self.assertTrue(user.check_password(data.get('password')))
            self.assertFalse(user.check_password(self.previous_password))
